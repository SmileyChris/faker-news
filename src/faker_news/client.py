"""LLM client for OpenAI-compatible APIs."""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import List, Optional, Tuple

import keyring
from openai import OpenAI


SERVICE_NAME = "faker-news"


@dataclass
class LLMClientConfig:
    """Configuration for OpenAI-compatible LLM client.

    Supports any OpenAI-compatible API including:
    - OpenAI (gpt-4, gpt-3.5-turbo, etc.)
    - Alibaba Cloud Model Studio / Qwen (qwen-flash, qwen-plus, etc.)
    - Azure OpenAI
    - Other OpenAI-compatible providers

    API Key Sources (checked in order):
    1. System keyring:
       - keyring.get_password("faker-news", "openai")
       - keyring.get_password("faker-news", "dashscope")
    2. Environment variables:
       - OPENAI_API_KEY: API key for OpenAI or compatible provider
       - OPENAI_BASE_URL: Base URL for API (optional)
       - DASHSCOPE_API_KEY: API key for Alibaba DashScope
       - DASHSCOPE_BASE_URL: Base URL for DashScope (defaults if DASHSCOPE_API_KEY is set)
    3. Config passed explicitly to api_key parameter

    Use 'faker-news setup' to store API keys securely in system keyring.
    """
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model_headlines: str = "gpt-4o-mini"  # fast & cheap model for headlines
    model_writing: str = "gpt-4o-mini"    # model for intros/articles

    def __post_init__(self):
        # Auto-detect API key from keyring first, then environment
        if not self.api_key:
            # Try keyring first
            self.api_key = keyring.get_password(SERVICE_NAME, "openai") or keyring.get_password(
                SERVICE_NAME, "dashscope"
            )
            # Fall back to environment variables
            if not self.api_key:
                self.api_key = os.getenv("OPENAI_API_KEY") or os.getenv("DASHSCOPE_API_KEY")

        # Auto-detect base URL from environment
        if not self.base_url:
            # Check if we're using DashScope (from keyring or env)
            is_dashscope = (
                keyring.get_password(SERVICE_NAME, "dashscope")
                or os.getenv("DASHSCOPE_API_KEY")
                or os.getenv("DASHSCOPE_BASE_URL")
            )

            if is_dashscope:
                self.base_url = os.getenv(
                    "DASHSCOPE_BASE_URL", "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
                )
            else:
                self.base_url = os.getenv("OPENAI_BASE_URL")

        # Auto-select Qwen models if using DashScope
        if self.base_url and "dashscope" in self.base_url.lower():
            if self.model_headlines == "gpt-4o-mini":
                self.model_headlines = "qwen-flash"
            if self.model_writing == "gpt-4o-mini":
                self.model_writing = "qwen-flash"


class LLMClient:
    def __init__(self, config: Optional[LLMClientConfig] = None):
        self.config = config or LLMClientConfig()
        if not self.config.api_key:
            raise RuntimeError(
                "API key is not set. Please set OPENAI_API_KEY or DASHSCOPE_API_KEY environment variable, "
                "or pass api_key in LLMClientConfig"
            )
        self.client = OpenAI(api_key=self.config.api_key, base_url=self.config.base_url)

    def gen_json(self, model: str, system: str, user: str, max_retries: int = 2):
        """Call chat.completions and parse a JSON response safely."""
        last_err = None
        for _ in range(max_retries + 1):
            try:
                resp = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                    temperature=0.9,
                )
                content = resp.choices[0].message.content
                # Try to locate a JSON blob even if the model adds prose
                start = content.find("[")
                brace = content.find("{")
                if brace != -1 and (start == -1 or brace < start):
                    start = brace
                end = content.rfind("]")
                brace_end = content.rfind("}")
                if brace_end != -1 and (end == -1 or brace_end > end):
                    end = brace_end
                if start != -1 and end != -1 and end > start:
                    content = content[start : end + 1]
                return json.loads(content)
            except Exception as e:
                last_err = e
                time.sleep(0.8)
        raise RuntimeError(f"Failed to parse JSON from model: {last_err}")

    # --------------- PROMPTS ---------------
    def generate_headlines(self, n: int) -> List[str]:
        system = (
            "You are a witty newsroom editor who crafts intriguing, plausible, but clearly fake news headlines.\n"
            "Return ONLY JSON: an array of unique headline strings. No explanations."
        )
        user = (
            "Produce {n} original fake news headlines spanning world, tech, sports, science, business, culture.\n"
            "They should be interesting, imaginative, and safe for work; avoid real tragedies or defamation.\n"
            "Keep each under 110 characters. Return JSON array only."
        ).format(n=n)
        data = self.gen_json(self.config.model_headlines, system, user)
        return [str(x).strip() for x in data if str(x).strip()]

    def generate_intros(self, headlines: List[str]) -> List[Tuple[str, str]]:
        system = (
            "You are a news writer. For each headline, write a punchy 1-2 sentence intro (max 40 words).\n"
            "Return ONLY JSON: a list of {headline:intro} objects or tuples."
        )
        payload = {"headlines": headlines}
        user = (
            "Write intros for the following headlines. Keep tone playful and fictional, no harmful claims.\n"
            f"Return JSON array of objects with keys 'headline' and 'intro'.\n\n{json.dumps(payload)}"
        )
        data = self.gen_json(self.config.model_writing, system, user)
        results = []
        # Accept either [{headline, intro}] or [[headline, intro]]
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and "headline" in item and "intro" in item:
                    results.append((item["headline"], item["intro"]))
                elif (
                    isinstance(item, list) and len(item) >= 2 and isinstance(item[0], str) and isinstance(item[1], str)
                ):
                    results.append((item[0], item[1]))
        return results

    def generate_articles(self, pairs: List[Tuple[str, Optional[str]]], words: int = 500) -> List[Tuple[str, str]]:
        # Adjust structure based on article length
        if words < 300:
            structure = "1-2 short sub-sections with markdown `##` subheads"
        elif words < 600:
            structure = "2-4 short sub-sections with markdown `##` subheads, and a crisp kicker"
        else:
            structure = "3-6 sub-sections with markdown `##` subheads, and a strong conclusion"

        system = (
            "You are a skilled feature writer. For each item, craft a fictional but tasteful news article.\n"
            "Write ~{w} words, with a clear lede, {structure}.\n"
            "Avoid real people or organizations unless used generically. Keep it safe and non-defamatory.\n"
            "Return ONLY JSON: array of objects with keys 'headline' and 'article'."
        ).format(w=words, structure=structure)
        payload = {
            "items": [
                {"headline": h, "intro": i} for (h, i) in pairs
            ]
        }
        user = (
            "Write feature articles for these headlines (use intro when given as context).\n"
            f"Return JSON array of objects with keys 'headline' and 'article'.\n\n{json.dumps(payload)}"
        )
        data = self.gen_json(self.config.model_writing, system, user)
        results = []
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and "headline" in item and "article" in item:
                    results.append((item["headline"], item["article"]))
        return results
