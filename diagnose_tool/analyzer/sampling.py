"""Bounded sample collection utilities."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field


DEFAULT_MAX_SAMPLES = 20


@dataclass
class BoundedSamples:
    max_per_category: int = DEFAULT_MAX_SAMPLES
    _samples: dict[str, list] = field(default_factory=lambda: defaultdict(list))

    def add(self, category: str, item: object) -> None:
        if len(self._samples[category]) < self.max_per_category:
            self._samples[category].append(item)

    def get(self, category: str) -> list:
        return list(self._samples.get(category, []))

    def get_all(self) -> dict[str, list]:
        return {cat: list(items) for cat, items in self._samples.items()}

    def __len__(self) -> int:
        return sum(len(items) for items in self._samples.values())

    def category_count(self, category: str) -> int:
        return len(self._samples.get(category, []))

    def is_full(self, category: str) -> bool:
        return self.category_count(category) >= self.max_per_category
