"""Source directory API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from diagnose_tool.analyzer.scanner import scan_directory
from diagnose_tool.core.config import load_config
from diagnose_tool.core.security import PathValidationError, validate_server_directory


router = APIRouter(prefix="/api/source", tags=["source"])


class SourcePathRequest(BaseModel):
    path: str = Field(min_length=1)


@router.post("/check")
def check_source_directory(request: SourcePathRequest) -> dict[str, object]:
    path = _validate_source_path(request.path)
    return {"allowed": True, "path": str(path), "name": path.name}


@router.post("/scan")
def scan_source_directory(request: SourcePathRequest) -> dict[str, object]:
    path = _validate_source_path(request.path)
    return scan_directory(path).to_dict()


def _validate_source_path(path: str):
    config = load_config()
    try:
        return validate_server_directory(path, config.allowed_input_roots)
    except PathValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
