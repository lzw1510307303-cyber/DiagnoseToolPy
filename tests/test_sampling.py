"""Tests for bounded sampling."""

from __future__ import annotations


from diagnose_tool.analyzer.sampling import BoundedSamples, DEFAULT_MAX_SAMPLES


class TestBoundedSamples:
    def test_add_within_limit(self):
        sampler = BoundedSamples(max_per_category=3)
        sampler.add("error", "sample1")
        sampler.add("error", "sample2")
        assert sampler.category_count("error") == 2
        assert sampler.get("error") == ["sample1", "sample2"]

    def test_respects_max_per_category(self):
        sampler = BoundedSamples(max_per_category=2)
        sampler.add("error", "sample1")
        sampler.add("error", "sample2")
        sampler.add("error", "sample3")
        assert sampler.category_count("error") == 2
        assert "sample3" not in sampler.get("error")

    def test_categories_are_isolated(self):
        sampler = BoundedSamples(max_per_category=2)
        sampler.add("error", "e1")
        sampler.add("error", "e2")
        sampler.add("warn", "w1")
        assert sampler.category_count("error") == 2
        assert sampler.category_count("warn") == 1
        assert sampler.get("error") == ["e1", "e2"]
        assert sampler.get("warn") == ["w1"]

    def test_get_all_returns_copy(self):
        sampler = BoundedSamples(max_per_category=3)
        sampler.add("cat1", "item1")
        all_items = sampler.get_all()
        assert "cat1" in all_items
        assert all_items["cat1"] == ["item1"]

    def test_is_full(self):
        sampler = BoundedSamples(max_per_category=2)
        assert not sampler.is_full("error")
        sampler.add("error", "e1")
        sampler.add("error", "e2")
        assert sampler.is_full("error")

    def test_default_max(self):
        assert DEFAULT_MAX_SAMPLES == 20

    def test_len_returns_total(self):
        sampler = BoundedSamples(max_per_category=3)
        sampler.add("error", "e1")
        sampler.add("warn", "w1")
        sampler.add("warn", "w2")
        assert len(sampler) == 3

    def test_get_missing_category_returns_empty(self):
        sampler = BoundedSamples(max_per_category=3)
        assert sampler.get("nonexistent") == []
