"""Optional real-LLM provider.

Not used by default anywhere in this project — the CLI, the demo, and the
test suite all use `RulesProvider`. This exists so the same `revise()`
interface can be pointed at a real model later. Requires `openai` and
`OPENAI_API_KEY`; both are optional installs/config (see
requirements-optional.txt and .env.example).
"""

from __future__ import annotations

import os

from .criteria import QualityCriteria
from .prompts import REVISE_SYSTEM_PROMPT, build_revise_prompt


class LLMProvider:
    name = "llm"

    def __init__(self, model: str | None = None) -> None:
        self.model = model or os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

    def revise(self, text: str, criteria: QualityCriteria) -> tuple[str, list[str]]:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "LLMProvider requires OPENAI_API_KEY. Copy .env.example to .env "
                "and add your own key, or use RulesProvider instead (no key needed)."
            )

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "LLMProvider requires the 'openai' package: "
                "pip install -r requirements-optional.txt"
            ) from exc

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": REVISE_SYSTEM_PROMPT},
                {"role": "user", "content": build_revise_prompt(text, criteria)},
            ],
            temperature=0.3,
        )
        revised = (response.choices[0].message.content or "").strip()
        return revised, ["revised by LLM provider (see prompt in content_qa/prompts.py)"]
