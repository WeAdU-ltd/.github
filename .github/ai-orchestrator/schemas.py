"""Schémas Pydantic alignés sur specs/api_contract.md (RunRequest / RunResponse)."""

from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

TaskType = Literal["classification", "generation", "extraction", "coding", "analysis"]
Complexity = Literal["low", "medium", "high"]
PrivacyLevel = Literal["local_only", "standard", "external_allowed"]
Status = Literal["success", "error", "fallback"]
class RunInput(BaseModel):
    model_config = ConfigDict(extra="allow")

    prompt: str = Field(..., min_length=1)
    context: dict[str, Any] = Field(default_factory=dict)
    data: list[Any] = Field(default_factory=list)


class RunOptions(BaseModel):
    """Options §3.4 — défauts alignés WEA-171 / api_contract."""

    model_config = ConfigDict(extra="allow")

    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, gt=0)
    timeout_ms: int = Field(default=30000, ge=1000)


class RunRequest(BaseModel):
    """Requête universelle §3 api_contract.md."""

    model_config = ConfigDict(extra="forbid")

    task_id: UUID
    task_type: TaskType
    complexity: Complexity
    privacy_level: PrivacyLevel
    preferred_model: str = Field(..., min_length=1)
    max_cost_usd: float | None = None
    input: RunInput
    options: RunOptions = Field(default_factory=RunOptions)

    @field_validator("preferred_model")
    @classmethod
    def preferred_model_strip(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("preferred_model must be non-empty")
        return s

    @field_validator("max_cost_usd")
    @classmethod
    def max_cost_non_negative(cls, v: float | None) -> float | None:
        if v is None:
            return v
        if v < 0:
            raise ValueError("max_cost_usd must be >= 0 when provided")
        return v


class UsageBlock(BaseModel):
    model_config = ConfigDict(extra="allow")

    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float
    duration_ms: int
    estimated_cloud_equivalent_cost_usd: float | None = None
    estimated_savings_usd: float | None = None


class ErrorDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    retryable: bool = False


class RunResponse(BaseModel):
    """Réponse universelle §4 api_contract.md."""

    model_config = ConfigDict(extra="allow")

    task_id: str
    status: Status
    provider_used: str
    model_used: str
    output: dict[str, Any]
    usage: UsageBlock
    routing_reason: str
    error: ErrorDetail | None = None


_CLOUD_ENUM = frozenset({"gemini_flash", "claude_haiku"})
def is_cloud_preferred_model_enum(value: str) -> bool:
    return value in _CLOUD_ENUM
