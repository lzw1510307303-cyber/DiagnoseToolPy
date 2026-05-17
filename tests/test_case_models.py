"""Tests for case models."""

from __future__ import annotations



from diagnose_tool.casebase.case_models import (
    CaseConfidence,
    CaseIndexEntry,
    CaseSourceType,
    CaseStatus,
    FaultCase,
    FaultCaseMetadata,
)


class TestFaultCaseMetadata:
    def test_fault_case_metadata_has_required_fields(self):
        metadata = FaultCaseMetadata(
            case_id="CASE-001",
            title="Redis连接池耗尽",
            slug="redis-pool-exhausted",
            source_type=CaseSourceType.AUTO,
            status=CaseStatus.DRAFT,
            confidence=CaseConfidence.UNCONFIRMED,
        )
        assert metadata.case_id == "CASE-001"
        assert metadata.title == "Redis连接池耗尽"
        assert metadata.slug == "redis-pool-exhausted"
        assert metadata.source_type == CaseSourceType.AUTO
        assert metadata.status == CaseStatus.DRAFT
        assert metadata.confidence == CaseConfidence.UNCONFIRMED
        assert isinstance(metadata.tags, list)
        assert isinstance(metadata.components, list)
        assert isinstance(metadata.fault_modes, list)
        assert isinstance(metadata.exception_classes, list)
        assert isinstance(metadata.key_phrases, list)
        assert metadata.created_at != ""

    def test_fault_case_metadata_default_created_at(self):
        metadata = FaultCaseMetadata(
            case_id="CASE-001",
            title="Test",
            slug="test",
            source_type=CaseSourceType.MANUAL,
            status=CaseStatus.DRAFT,
            confidence=CaseConfidence.UNCONFIRMED,
        )
        assert metadata.created_at != ""

    def test_fault_case_metadata_to_dict(self):
        metadata = FaultCaseMetadata(
            case_id="CASE-001",
            title="Test",
            slug="test",
            source_type=CaseSourceType.AUTO,
            status=CaseStatus.ARCHIVED,
            confidence=CaseConfidence.CONFIRMED,
            tags=["redis", "pool"],
            components=["order-core"],
            fault_modes=["resource-exhaustion"],
            exception_classes=["JedisConnectionException"],
            key_phrases=["connection pool"],
        )
        d = metadata.to_dict()
        assert d["case_id"] == "CASE-001"
        assert d["source_type"] == "auto"
        assert d["status"] == "archived"
        assert d["confidence"] == "confirmed"
        assert d["tags"] == ["redis", "pool"]

    def test_fault_case_metadata_from_dict(self):
        data = {
            "case_id": "CASE-002",
            "title": "From dict",
            "slug": "from-dict",
            "source_type": "manual",
            "status": "reviewing",
            "confidence": "likely",
            "tags": [],
            "components": [],
            "fault_modes": [],
            "exception_classes": [],
            "key_phrases": [],
            "created_at": "2026-05-17 10:00:00",
        }
        metadata = FaultCaseMetadata.from_dict(data)
        assert metadata.case_id == "CASE-002"
        assert metadata.source_type == CaseSourceType.MANUAL
        assert metadata.status == CaseStatus.REVIEWING
        assert metadata.confidence == CaseConfidence.LIKELY


class TestCaseIndexEntry:
    def test_case_index_entry_has_required_fields(self):
        entry = CaseIndexEntry(
            case_id="CASE-001",
            title="Test Case",
            slug="test-case",
            status=CaseStatus.ARCHIVED,
            source_type=CaseSourceType.AUTO,
            created_at="2026-05-17 10:00:00",
        )
        assert entry.case_id == "CASE-001"
        assert entry.title == "Test Case"
        assert entry.slug == "test-case"
        assert entry.status == CaseStatus.ARCHIVED
        assert entry.source_type == CaseSourceType.AUTO
        assert entry.created_at == "2026-05-17 10:00:00"

    def test_case_index_entry_from_metadata(self):
        metadata = FaultCaseMetadata(
            case_id="CASE-003",
            title="From Metadata",
            slug="from-metadata",
            source_type=CaseSourceType.IMPORTED,
            status=CaseStatus.REVIEWING,
            confidence=CaseConfidence.LIKELY,
        )
        entry = CaseIndexEntry.from_metadata(metadata)
        assert entry.case_id == metadata.case_id
        assert entry.title == metadata.title
        assert entry.slug == metadata.slug
        assert entry.status == metadata.status
        assert entry.source_type == metadata.source_type

    def test_case_index_entry_to_dict(self):
        entry = CaseIndexEntry(
            case_id="CASE-001",
            title="Test",
            slug="test",
            status=CaseStatus.ARCHIVED,
            source_type=CaseSourceType.AUTO,
            created_at="2026-05-17 10:00:00",
        )
        d = entry.to_dict()
        assert d["case_id"] == "CASE-001"
        assert d["status"] == "archived"
        assert d["source_type"] == "auto"

    def test_case_index_entry_from_dict(self):
        data = {
            "case_id": "CASE-004",
            "title": "From Dict",
            "slug": "from-dict",
            "status": "deprecated",
            "source_type": "template",
            "created_at": "2026-05-17 10:00:00",
        }
        entry = CaseIndexEntry.from_dict(data)
        assert entry.case_id == "CASE-004"
        assert entry.status == CaseStatus.DEPRECATED
        assert entry.source_type == CaseSourceType.TEMPLATE


class TestFaultCase:
    def test_fault_case_creation(self):
        metadata = FaultCaseMetadata(
            case_id="CASE-001",
            title="Test",
            slug="test",
            source_type=CaseSourceType.AUTO,
            status=CaseStatus.DRAFT,
            confidence=CaseConfidence.UNCONFIRMED,
        )
        case = FaultCase(
            metadata=metadata,
            case_path="/data/cases/CASE-001_test/",
            evidence_path="/data/cases/CASE-001_test/",
        )
        assert case.metadata == metadata
        assert case.case_path == "/data/cases/CASE-001_test/"
        assert case.evidence_path == "/data/cases/CASE-001_test/"
