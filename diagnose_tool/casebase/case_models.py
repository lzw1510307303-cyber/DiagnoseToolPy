"""Case models for fault case storage."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class CaseSourceType(str, Enum):
    AUTO = "auto"
    MANUAL = "manual"
    IMPORTED = "imported"
    TEMPLATE = "template"


class CaseStatus(str, Enum):
    DRAFT = "draft"
    REVIEWING = "reviewing"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"


class CaseConfidence(str, Enum):
    UNCONFIRMED = "unconfirmed"
    LIKELY = "likely"
    CONFIRMED = "confirmed"


@dataclass
class FaultCaseMetadata:
    case_id: str
    title: str
    slug: str
    source_type: CaseSourceType
    status: CaseStatus
    confidence: CaseConfidence
    tags: list[str] = field(default_factory=list)
    components: list[str] = field(default_factory=list)
    fault_modes: list[str] = field(default_factory=list)
    exception_classes: list[str] = field(default_factory=list)
    key_phrases: list[str] = field(default_factory=list)
    created_at: str = ""

    def __post_init__(self) -> None:
        if not self.created_at:
            self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "title": self.title,
            "slug": self.slug,
            "source_type": self.source_type.value,
            "status": self.status.value,
            "confidence": self.confidence.value,
            "tags": self.tags,
            "components": self.components,
            "fault_modes": self.fault_modes,
            "exception_classes": self.exception_classes,
            "key_phrases": self.key_phrases,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FaultCaseMetadata:
        return cls(
            case_id=data["case_id"],
            title=data["title"],
            slug=data["slug"],
            source_type=CaseSourceType(data["source_type"]),
            status=CaseStatus(data["status"]),
            confidence=CaseConfidence(data["confidence"]),
            tags=data.get("tags", []),
            components=data.get("components", []),
            fault_modes=data.get("fault_modes", []),
            exception_classes=data.get("exception_classes", []),
            key_phrases=data.get("key_phrases", []),
            created_at=data.get("created_at", ""),
        )


@dataclass
class CaseIndexEntry:
    case_id: str
    title: str
    slug: str
    status: CaseStatus
    source_type: CaseSourceType
    created_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "title": self.title,
            "slug": self.slug,
            "status": self.status.value,
            "source_type": self.source_type.value,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CaseIndexEntry:
        return cls(
            case_id=data["case_id"],
            title=data["title"],
            slug=data["slug"],
            status=CaseStatus(data["status"]),
            source_type=CaseSourceType(data["source_type"]),
            created_at=data.get("created_at", ""),
        )

    @classmethod
    def from_metadata(cls, metadata: FaultCaseMetadata) -> CaseIndexEntry:
        return cls(
            case_id=metadata.case_id,
            title=metadata.title,
            slug=metadata.slug,
            status=metadata.status,
            source_type=metadata.source_type,
            created_at=metadata.created_at,
        )


@dataclass
class FaultCase:
    metadata: FaultCaseMetadata
    case_path: str
    evidence_path: str | None = None
    case_md_content: str | None = None
