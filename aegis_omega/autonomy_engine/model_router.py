from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor


class ModelRouter:
    """Parallel, multi-provider response adapter (lightweight stub for local-first use)."""

    def __init__(self) -> None:
        self.providers = {
            "openai": os.getenv("OPENAI_API_KEY", ""),
            "anthropic": os.getenv("ANTHROPIC_API_KEY", ""),
            "groq": os.getenv("GROQ_API_KEY", ""),
            "local": "available",
        }

    def available(self) -> list[str]:
        return [name for name, key in self.providers.items() if key]

    def ask_parallel(self, prompt: str) -> dict[str, str]:
        targets = self.available() or ["local"]
        with ThreadPoolExecutor(max_workers=min(3, len(targets))) as pool:
            futures = {pool.submit(self._simulate_provider, name, prompt): name for name in targets}
            return {futures[f]: f.result() for f in futures}

    @staticmethod
    def _simulate_provider(provider: str, prompt: str) -> str:
        trimmed = prompt.strip().replace("\n", " ")[:140]
        return f"[{provider}] plan-fragment: {trimmed}"
