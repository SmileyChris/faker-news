"""SQLite storage for cached news content."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable, List, Optional, Tuple

from platformdirs import user_cache_dir


def get_default_db_path() -> Path:
    """Get the default database path in the user's cache directory."""
    cache_dir = Path(user_cache_dir("faker-news", "smileychris"))
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / "cache.sqlite3"


class NewsStore:
    def __init__(self, db_path: str | Path | None = None):
        if db_path is None:
            db_path = get_default_db_path()
        self.db_path = str(db_path)
        self._init()

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def _init(self):
        with self._conn() as cx:
            cx.execute(
                """
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    headline TEXT UNIQUE,
                    intro TEXT,
                    article TEXT,
                    word_count INTEGER,
                    used_headline INTEGER DEFAULT 0,
                    used_intro INTEGER DEFAULT 0,
                    used_article INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_used_at TEXT
                );
                """
            )
            cx.execute("CREATE INDEX IF NOT EXISTS idx_used_headline ON items(used_headline)")
            cx.execute("CREATE INDEX IF NOT EXISTS idx_used_intro ON items(used_intro)")
            cx.execute("CREATE INDEX IF NOT EXISTS idx_used_article ON items(used_article)")

    # ---------- inserts & updates ----------
    def insert_headlines(self, headlines: Iterable[str]):
        with self._conn() as cx:
            for h in headlines:
                try:
                    cx.execute("INSERT OR IGNORE INTO items(headline) VALUES (?)", (h,))
                except sqlite3.IntegrityError:
                    pass

    def set_intros(self, pairs: Iterable[Tuple[str, str]]):
        with self._conn() as cx:
            for h, intro in pairs:
                cx.execute("UPDATE items SET intro = COALESCE(intro, ? ) WHERE headline = ?", (intro, h))

    def set_articles(self, pairs: Iterable[Tuple[str, str]]):
        with self._conn() as cx:
            for h, art in pairs:
                # Calculate word count (simple split on whitespace)
                word_count = len(art.split()) if art else 0
                cx.execute(
                    "UPDATE items SET article = COALESCE(article, ?), word_count = COALESCE(word_count, ?) WHERE headline = ?",
                    (art, word_count, h)
                )

    def fetch_headline(self, consume: bool = True, allow_used: bool = False) -> Optional[str]:
        """Fetch a headline from the cache.

        Args:
            consume: If True, mark the headline as used after fetching
            allow_used: If False (default), only fetch unused headlines.
                       If True, fetch from all headlines (used or unused)
        """
        with self._conn() as cx:
            if allow_used:
                query = "SELECT headline FROM items ORDER BY RANDOM() LIMIT 1"
            else:
                query = "SELECT headline FROM items WHERE used_headline = 0 ORDER BY RANDOM() LIMIT 1"

            row = cx.execute(query).fetchone()
            if row:
                h = row[0]
                if consume:
                    cx.execute(
                        "UPDATE items SET used_headline = 1, last_used_at = CURRENT_TIMESTAMP WHERE headline = ?",
                        (h,),
                    )
                return h
            return None

    def fetch_missing_intros(self, limit: int) -> List[str]:
        with self._conn() as cx:
            rows = cx.execute(
                "SELECT headline FROM items WHERE intro IS NULL ORDER BY RANDOM() LIMIT ?",
                (limit,),
            ).fetchall()
            return [r[0] for r in rows]

    def fetch_multiple_headlines(self, limit: int, unused_only: bool = True) -> List[str]:
        """Fetch multiple headlines at once."""
        with self._conn() as cx:
            if unused_only:
                query = "SELECT headline FROM items WHERE used_headline = 0 ORDER BY RANDOM() LIMIT ?"
            else:
                query = "SELECT headline FROM items ORDER BY RANDOM() LIMIT ?"
            rows = cx.execute(query, (limit,)).fetchall()
            return [r[0] for r in rows]

    def fetch_headlines_needing_content(self, limit: int) -> List[str]:
        """Fetch unused headlines prioritizing those missing intros/articles."""
        with self._conn() as cx:
            # First, get headlines missing content (intro OR article)
            query = """
                SELECT headline FROM items
                WHERE used_headline = 0
                  AND (intro IS NULL OR article IS NULL)
                ORDER BY RANDOM()
                LIMIT ?
            """
            rows = cx.execute(query, (limit,)).fetchall()
            headlines = [r[0] for r in rows]

            # If we don't have enough, fill with complete unused headlines
            if len(headlines) < limit:
                needed = limit - len(headlines)
                query = """
                    SELECT headline FROM items
                    WHERE used_headline = 0
                      AND intro IS NOT NULL
                      AND article IS NOT NULL
                    ORDER BY RANDOM()
                    LIMIT ?
                """
                rows = cx.execute(query, (needed,)).fetchall()
                headlines.extend([r[0] for r in rows])

            return headlines

    def fetch_intro(self, consume: bool = True, allow_used: bool = False) -> Optional[Tuple[str, str]]:
        """Fetch an intro from the cache.

        Args:
            consume: If True, mark the intro as used after fetching
            allow_used: If False (default), only fetch unused intros.
                       If True, fetch from all intros (used or unused)
        """
        with self._conn() as cx:
            if allow_used:
                query = "SELECT headline, intro FROM items WHERE intro IS NOT NULL ORDER BY RANDOM() LIMIT 1"
            else:
                query = (
                    "SELECT headline, intro FROM items WHERE intro IS NOT NULL "
                    "AND used_intro = 0 ORDER BY RANDOM() LIMIT 1"
                )

            row = cx.execute(query).fetchone()
            if row:
                h, i = row
                if consume:
                    cx.execute(
                        "UPDATE items SET used_intro = 1, last_used_at = CURRENT_TIMESTAMP WHERE headline = ?",
                        (h,),
                    )
                return h, i
            return None

    def fetch_headlines_needing_articles(self, limit: int) -> List[Tuple[str, Optional[str]]]:
        with self._conn() as cx:
            rows = cx.execute(
                "SELECT headline, intro FROM items WHERE article IS NULL ORDER BY RANDOM() LIMIT ?",
                (limit,),
            ).fetchall()
            return [(r[0], r[1]) for r in rows]

    def fetch_article(self, consume: bool = True, allow_used: bool = False, min_words: int = 0, longest: bool = False) -> Optional[Tuple[str, str]]:
        """Fetch an article from the cache.

        Args:
            consume: If True, mark the article as used after fetching
            allow_used: If False (default), only fetch unused articles.
                       If True, fetch from all articles (used or unused)
            min_words: Minimum word count required (0 = no minimum)
            longest: If True, fetch the longest article; otherwise random
        """
        with self._conn() as cx:
            order_by = "ORDER BY word_count DESC" if longest else "ORDER BY RANDOM()"

            if allow_used:
                if min_words > 0:
                    query = f"SELECT headline, article FROM items WHERE article IS NOT NULL AND word_count >= ? {order_by} LIMIT 1"
                    params = (min_words,)
                else:
                    query = f"SELECT headline, article FROM items WHERE article IS NOT NULL {order_by} LIMIT 1"
                    params = ()
            else:
                if min_words > 0:
                    query = (
                        f"SELECT headline, article FROM items WHERE article IS NOT NULL "
                        f"AND used_article = 0 AND word_count >= ? {order_by} LIMIT 1"
                    )
                    params = (min_words,)
                else:
                    query = (
                        f"SELECT headline, article FROM items WHERE article IS NOT NULL "
                        f"AND used_article = 0 {order_by} LIMIT 1"
                    )
                    params = ()

            row = cx.execute(query, params).fetchone()
            if row:
                h, a = row
                if consume:
                    cx.execute(
                        "UPDATE items SET used_article = 1, last_used_at = CURRENT_TIMESTAMP WHERE headline = ?",
                        (h,),
                    )
                return h, a
            return None

    def mark_intro_used_for(self, headline: str):
        with self._conn() as cx:
            cx.execute(
                "UPDATE items SET used_intro = 1, last_used_at = CURRENT_TIMESTAMP WHERE headline = ?",
                (headline,),
            )

    def mark_article_used_for(self, headline: str):
        with self._conn() as cx:
            cx.execute(
                "UPDATE items SET used_article = 1, last_used_at = CURRENT_TIMESTAMP WHERE headline = ?",
                (headline,),
            )

    def reset(self, mode: str = "reuse"):
        mode = mode.lower()
        with self._conn() as cx:
            if mode == "reuse":
                cx.execute(
                    "UPDATE items SET used_headline=0, used_intro=0, used_article=0"
                )
            elif mode == "clear":
                cx.execute("DELETE FROM items")
            else:
                raise ValueError("mode must be 'reuse' or 'clear'")

    def stats(self) -> dict:
        with self._conn() as cx:
            total = cx.execute("SELECT COUNT(*) FROM items").fetchone()[0]
            have_intro = cx.execute("SELECT COUNT(*) FROM items WHERE intro IS NOT NULL").fetchone()[0]
            have_article = cx.execute("SELECT COUNT(*) FROM items WHERE article IS NOT NULL").fetchone()[0]
            unused_h = cx.execute("SELECT COUNT(*) FROM items WHERE used_headline = 0").fetchone()[0]
            unused_i = cx.execute(
                "SELECT COUNT(*) FROM items WHERE intro IS NOT NULL AND used_intro = 0"
            ).fetchone()[0]
            unused_a = cx.execute(
                "SELECT COUNT(*) FROM items WHERE article IS NOT NULL AND used_article = 0"
            ).fetchone()[0]
            avg_words = cx.execute(
                "SELECT AVG(word_count) FROM items WHERE word_count IS NOT NULL"
            ).fetchone()[0]
            min_words = cx.execute(
                "SELECT MIN(word_count) FROM items WHERE word_count IS NOT NULL"
            ).fetchone()[0]
            max_words = cx.execute(
                "SELECT MAX(word_count) FROM items WHERE word_count IS NOT NULL"
            ).fetchone()[0]
            return {
                "total": total,
                "with_intro": have_intro,
                "with_article": have_article,
                "unused_headlines": unused_h,
                "unused_intros": unused_i,
                "unused_articles": unused_a,
                "avg_article_words": int(avg_words) if avg_words else 0,
                "min_article_words": int(min_words) if min_words else 0,
                "max_article_words": int(max_words) if max_words else 0,
            }

    def fetch_items_metadata(self, headlines: List[str]) -> dict[str, dict]:
        """Fetch intro and article status for multiple headlines in a single query.

        Returns a dict mapping headline -> {intro: str|None, article: str|None}
        """
        if not headlines:
            return {}

        with self._conn() as cx:
            # Use parameterized query with IN clause
            placeholders = ",".join("?" * len(headlines))
            query = f"SELECT headline, intro, article FROM items WHERE headline IN ({placeholders})"
            rows = cx.execute(query, headlines).fetchall()

            return {
                row[0]: {"intro": row[1], "article": row[2]}
                for row in rows
            }

    def load_example_data(self) -> int:
        """Load example news data from bundled fixtures.

        Returns the number of items loaded.
        """
        fixtures_path = Path(__file__).parent / "fixtures" / "example_news.json"
        if not fixtures_path.exists():
            raise FileNotFoundError(f"Example data not found at {fixtures_path}")

        with open(fixtures_path) as f:
            items = json.load(f)

        with self._conn() as cx:
            loaded = 0
            for item in items:
                try:
                    headline = item["headline"]
                    intro = item["intro"]
                    article = item["article"]
                    word_count = len(article.split()) if article else 0

                    cx.execute(
                        """
                        INSERT OR IGNORE INTO items(headline, intro, article, word_count)
                        VALUES (?, ?, ?, ?)
                        """,
                        (headline, intro, article, word_count)
                    )
                    if cx.total_changes > 0:
                        loaded += 1
                except (KeyError, sqlite3.IntegrityError):
                    continue

        return loaded
