"""Retrieval module for case search without embeddings."""

from __future__ import annotations

from diagnose_tool.retrieval.bm25_search import search_bm25
from diagnose_tool.retrieval.keyword_search import search_by_keywords
from diagnose_tool.retrieval.prompt_context import generate_prompt_context
from diagnose_tool.retrieval.query_builder import build_retrieval_query
from diagnose_tool.retrieval.rule_matcher import match_by_rules

__all__ = [
    "build_retrieval_query",
    "generate_prompt_context",
    "match_by_rules",
    "search_bm25",
    "search_by_keywords",
]
