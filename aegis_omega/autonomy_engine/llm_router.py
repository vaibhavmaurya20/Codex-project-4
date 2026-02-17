from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field


@dataclass
class MultiLLMRouter:
    providers: list[str]
    _cursor: int = 0
    _quality: dict[str, float] = field(default_factory=dict)

    def choose_provider(self) -> str:
        if not self.providers:
            return "local_fallback"
        provider = self.providers[self._cursor % len(self.providers)]
        self._cursor += 1
        return provider

    def parallel_advice(self, prompt: str, fanout: int = 2) -> list[dict[str, str]]:
        fanout = max(1, min(fanout, len(self.providers) or 1))

        def ask(provider: str) -> dict[str, str]:
            # Offline-safe deterministic fallback. External API calls can be plugged here.
            return {
                "provider": provider,
                "content": f"[{provider}] plan for: {prompt[:120]}",
            }

        providers = [self.choose_provider() for _ in range(fanout)]
        with ThreadPoolExecutor(max_workers=fanout) as pool:
            return list(pool.map(ask, providers))

    def record_quality(self, provider: str, score: float) -> None:
        prev = self._quality.get(provider, score)
        self._quality[provider] = (prev + score) / 2
