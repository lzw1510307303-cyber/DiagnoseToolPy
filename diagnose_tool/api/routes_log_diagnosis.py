"""Log diagnosis API - send selected logs to LLM for analysis."""

from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from diagnose_tool.core.llm_client import LLMClient, LLMClientError
from diagnose_tool.core.llm_config import AppLLMConfig

router = APIRouter(prefix="/api/logs", tags=["logs"])


# MiniMax LLM Configuration
MINIMAX_CONFIG = {
    "model": "MiniMax-M2.7-32K",
    "base_url": "https://api.minimax.chat/v1",
    "timeout": 120,
}


class LogDiagnosisRequest(BaseModel):
    """Request to diagnose selected logs with LLM."""

    logs: list[dict[str, Any]] = Field(
        ..., min_length=1, max_length=100,
        description="Selected log entries to diagnose"
    )
    model: str = Field(
        default="MiniMax-M2.7-32K",
        description="LLM model to use for diagnosis"
    )
    system_prompt: str | None = Field(
        default=None,
        description="Optional system prompt override"
    )


class LogDiagnosisResponse(BaseModel):
    """Response from log diagnosis."""

    diagnosis: str
    model_used: str
    logs_analyzed: int


def _build_diagnosis_prompt(logs: list[dict[str, Any]]) -> str:
    """Build a prompt from selected logs for LLM analysis."""
    logs_text = []
    for i, log in enumerate(logs, 1):
        timestamp = log.get("timestamp", "N/A")
        level = log.get("level", "N/A")
        source = log.get("source", "N/A")
        message = log.get("message", "")
        logs_text.append(f"[{i}] {timestamp} [{level}] [{source}] {message}")

    logs_content = "\n".join(logs_text)

    prompt = f"""你是一个日志诊断专家。请分析以下日志条目，识别可能的错误模式、异常行为或潜在问题。

日志条目:
{logs_content}

请提供:
1. 问题概述：这些日志反映了什么主要问题？
2. 可能的原因：最可能导致这些问题的原因是什么？
3. 建议的排查步骤：应该如何进一步诊断这个问题？
4. 优先级建议：这个问题的紧急程度如何？

请用中文回答。"""
    return prompt


@router.post("/diagnose", response_model=LogDiagnosisResponse)
def diagnose_logs(request: LogDiagnosisRequest) -> LogDiagnosisResponse:
    """Send selected logs to LLM for diagnosis."""
    if not request.logs:
        raise HTTPException(status_code=400, detail="No logs provided for diagnosis")

    if len(request.logs) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 logs can be diagnosed at once")

    # Get API key from environment variable
    api_key = os.environ.get("LLM_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="LLM_API_KEY environment variable is not set"
        )

    # Determine LLM configuration
    if request.model.startswith("MiniMax") or request.model == "MiniMax-M2.7-32K":
        llm_config_dict = MINIMAX_CONFIG.copy()
        llm_config_dict["api_key"] = api_key
        llm_config = AppLLMConfig(
            enabled=True,
            model=llm_config_dict["model"],
            base_url=llm_config_dict["base_url"],
            api_key=api_key,
            timeout=llm_config_dict["timeout"],
            data_dir=None,  # Not used for diagnosis
        )
    else:
        # Generic OpenAI-compatible configuration
        llm_config = AppLLMConfig(
            enabled=True,
            model=request.model,
            base_url="https://api.openai.com/v1",
            api_key=api_key,
            timeout=120,
            data_dir=None,
        )

    # Build messages
    user_prompt = _build_diagnosis_prompt(request.logs)
    system_prompt = request.system_prompt or "你是一个专业的日志诊断专家，擅长分析系统日志来识别问题和故障根因。"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    # Call LLM
    client = LLMClient(llm_config)
    try:
        diagnosis = client.chat(messages, model=llm_config.model)
    except LLMClientError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"LLM diagnosis failed: {str(exc)}"
        )

    return LogDiagnosisResponse(
        diagnosis=diagnosis,
        model_used=request.model,
        logs_analyzed=len(request.logs),
    )
