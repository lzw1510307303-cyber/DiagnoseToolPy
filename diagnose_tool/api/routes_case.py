"""Case management API routes."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from diagnose_tool.casebase.case_models import CaseConfidence, CaseStatus
from diagnose_tool.casebase.case_service import create_manual_case


router = APIRouter(prefix="/api/cases", tags=["cases"])


class CreateCaseRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(default="")
    status: str = Field(default="draft")
    confidence: str = Field(default="unconfirmed")
    slug: str | None = Field(default=None, max_length=50)
    tags: list[str] = Field(default_factory=list)
    components: list[str] = Field(default_factory=list)
    fault_modes: list[str] = Field(default_factory=list)
    exception_classes: list[str] = Field(default_factory=list)
    key_phrases: list[str] = Field(default_factory=list)


class CaseResponse(BaseModel):
    case_id: str
    title: str
    slug: str
    status: str
    source_type: str
    message: str


def _status_from_str(status_str: str) -> CaseStatus:
    try:
        return CaseStatus(status_str.lower())
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid status: {status_str}. Must be one of: draft, reviewing, archived, deprecated",
        )


def _confidence_from_str(confidence_str: str) -> CaseConfidence:
    try:
        return CaseConfidence(confidence_str.lower())
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid confidence: {confidence_str}. Must be one of: unconfirmed, likely, confirmed",
        )


@router.post("", response_model=CaseResponse)
def create_case(request: CreateCaseRequest) -> dict[str, Any]:
    status = _status_from_str(request.status)
    confidence = _confidence_from_str(request.confidence)

    fault_case = create_manual_case(
        title=request.title,
        content=request.content,
        status=status,
        confidence=confidence,
        slug=request.slug,
        tags=request.tags,
        components=request.components,
        fault_modes=request.fault_modes,
        exception_classes=request.exception_classes,
        key_phrases=request.key_phrases,
    )

    return {
        "case_id": fault_case.metadata.case_id,
        "title": fault_case.metadata.title,
        "slug": fault_case.metadata.slug,
        "status": fault_case.metadata.status.value,
        "source_type": fault_case.metadata.source_type.value,
        "message": "Case created successfully",
    }
