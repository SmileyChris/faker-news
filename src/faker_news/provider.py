"""Faker provider implementation."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import List, Optional

from faker.providers import BaseProvider

from .client import LLMClient, LLMClientConfig
from .store import NewsStore


class NewsProvider(BaseProvider):
    """Faker provider that yields cached LLM-generated news content.

    Methods exposed on Faker instance:
      - news_headline(consume: bool = True, allow_used: bool = False)
      - news_intro(headline: Optional[str] = None, consume: bool = True, allow_used: bool = False)
      - news_article(headline: Optional[str] = None, words: int = 500, consume: bool = True, allow_used: bool = False)
      - news_preload_headlines(n: int)
      - news_reset(mode: str = 'reuse' | 'clear')
      - news_stats() -> dict

    Parameters:
      - consume: If True (default), marks items as "used" after fetching.
                 Set to False to fetch without consuming.
      - allow_used: If False (default), only fetches from unused items.
                    Set to True to fetch from all items (used + unused).

    Two ways to reuse content:
      1. Reset usage flags: news_reset("reuse") - marks ALL items as unused (persistent)
      2. Allow used items: allow_used=True - fetches from both pools without resetting (temporary)

    Config knobs (constructor kwargs):
      - db_path (str | Path)
      - min_headline_pool (int)
      - headline_batch (int)
      - intro_batch (int)
      - article_batch (int)
      - llm_config (LLMClientConfig)
    """

    def __init__(
        self,
        generator,
        db_path: str | Path | None = None,
        min_headline_pool: int = 30,
        headline_batch: int = 40,
        intro_batch: int = 20,
        article_batch: int = 10,
        llm_config: Optional[LLMClientConfig] = None,
    ):
        super().__init__(generator)
        self.store = NewsStore(db_path)
        self._llm_config = llm_config
        self._client: LLMClient | None = None
        self.min_headline_pool = min_headline_pool
        self.headline_batch = headline_batch
        self.intro_batch = intro_batch
        self.article_batch = article_batch

    # --------- public API (Faker methods) ---------
    def news_headline(self, consume: bool = True, allow_used: bool = False) -> str:
        self._ensure_headline_pool()
        h = self.store.fetch_headline(consume=consume, allow_used=allow_used)
        if h:
            return h
        # Pool might be empty if generation failed; try once more
        self._top_up_headlines(self.headline_batch)
        h = self.store.fetch_headline(consume=consume, allow_used=allow_used)
        if not h:
            raise RuntimeError("Unable to generate or retrieve a headline")
        return h

    def news_intro(self, headline: Optional[str] = None, consume: bool = True, allow_used: bool = False) -> str:
        # If specific headline requested, ensure it has an intro
        if headline:
            intros = self._ensure_intro_for([headline])
            if not intros:
                # Already existed, fetch from DB
                with sqlite3.connect(self.store.db_path) as cx:
                    r = cx.execute("SELECT intro FROM items WHERE headline = ?", (headline,)).fetchone()
                    if not r or not r[0]:
                        raise RuntimeError("Intro generation failed for the requested headline")
                    if consume:
                        self.store.mark_intro_used_for(headline)
                    return r[0]
            # Return the generated intro
            if consume:
                self.store.mark_intro_used_for(headline)
            return intros[0][1]
        # Otherwise, use any available intro; generate in batch if needed
        intro = self.store.fetch_intro(consume=consume, allow_used=allow_used)
        if intro:
            return intro[1]
        # Try to generate intros for existing headlines without intros
        intros = self._ensure_intro_for([])  # batch-generate for random set
        if not intros:
            # No headlines available - generate new headlines first
            self._top_up_headlines(self.intro_batch)
            intros = self._ensure_intro_for([])
            if not intros:
                raise RuntimeError("Failed to generate intros")
        # Return first generated intro
        headline, intro_text = intros[0]
        if consume:
            self.store.mark_intro_used_for(headline)
        return intro_text

    def news_article(
        self, headline: Optional[str] = None, words: int = 500, consume: bool = True, allow_used: bool = False
    ) -> str:
        if headline:
            # ensure intro exists first, then generate article
            intro = self._get_intro_for(headline)
            if not intro:
                # Generate intro if missing
                self._ensure_intro_for([headline])
                intro = self._get_intro_for(headline)
            # ensure article for selected headline
            arts = self._ensure_article_for([(headline, intro)], words=words)
            if not arts:
                raise RuntimeError("Article generation failed for the requested headline")
            # Return the generated article
            if consume:
                self.store.mark_article_used_for(headline)
            return arts[0][1]
        # otherwise serve any unused article with at least the requested word count
        row = self.store.fetch_article(consume=consume, allow_used=allow_used, min_words=words)
        if row:
            return row[1]
        # generate batch
        need_pairs = self.store.fetch_headlines_needing_articles(self.article_batch)
        if not need_pairs:
            # No headlines available - generate new ones
            self._top_up_headlines(self.article_batch)
            need_pairs = self.store.fetch_headlines_needing_articles(self.article_batch)
            if not need_pairs:
                raise RuntimeError("Failed to generate headlines for articles")
        # Ensure all headlines have intros before generating articles
        headlines_without_intro = [h for h, intro in need_pairs if not intro]
        if headlines_without_intro:
            self._ensure_intro_for(headlines_without_intro)
            # Re-fetch pairs to get the newly generated intros
            need_pairs = [(h, self._get_intro_for(h)) for h, _ in need_pairs]
        arts = self._ensure_article_for(need_pairs, words=words)
        if not arts:
            raise RuntimeError("No articles were generated")
        # Return first generated article, marking it as used if requested
        headline, article = arts[0]
        if consume:
            self.store.mark_article_used_for(headline)
        return article

    def news_preload_headlines(self, n: int = 50):
        self._top_up_headlines(n)

    def news_reset(self, mode: str = "reuse"):
        self.store.reset(mode)

    def news_stats(self) -> dict:
        return self.store.stats()

    # --------- internals ---------
    def _ensure_headline_pool(self):
        stats = self.store.stats()
        if stats["unused_headlines"] < self.min_headline_pool:
            top_up = max(self.headline_batch, self.min_headline_pool - stats["unused_headlines"])
            self._top_up_headlines(top_up)

    def _top_up_headlines(self, n: int):
        headlines = self.client.generate_headlines(n)
        self.store.insert_headlines(headlines)

    def _ensure_intro_for(self, must_include: List[str]) -> List[tuple[str, str]]:
        # Select a batch of headlines that are missing intros, making sure to include required ones.
        missing = set(self.store.fetch_missing_intros(self.intro_batch))
        missing.update(must_include)
        missing = [m for m in missing if m]
        if not missing:
            return []
        pairs = self.client.generate_intros(missing)
        self.store.set_intros(pairs)
        return pairs

    def _get_intro_for(self, headline: str) -> Optional[str]:
        with sqlite3.connect(self.store.db_path) as cx:
            r = cx.execute("SELECT intro FROM items WHERE headline = ?", (headline,)).fetchone()
            return r[0] if r and r[0] else None

    def _ensure_article_for(self, pairs: List[tuple[str, Optional[str]]], words: int = 500) -> List[tuple[str, str]]:
        # Call LLM to generate articles for the given headlines (with optional intros)
        arts = self.client.generate_articles(pairs, words=words)
        self.store.set_articles(arts)
        return arts

    @property
    def client(self) -> LLMClient:
        """Instantiate the LLM client lazily so CLI usage without API keys still works."""
        if self._client is None:
            self._client = LLMClient(self._llm_config)
        return self._client
