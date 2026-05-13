"""Pydantic contracts — RunRequest / RunResponse (WEA-170 / WEA-171)."""

from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

TaskType = Literal["classification", "generation", "extraction", "coding", "analysis"]
Complexity = Literal["low", "medium", "high"]
PrivacyLevel = Literal["local_only", "standard", "external_allowed"]
_ENUM_TASK = frozenset(
    {"classification", "generation", "extraction", "coding", "analysis"}
)
_ENUM_COMPLEXITY = frozenset({"low", "medium", "high"})
_ENUM_PRIVACY = frozenset({"local_only", "standard", "external_allowed"})
_ENUM_PREFERRED = frozenset({"auto", "local", "gemini_flash", "claude_haiku"})


class RunInput(BaseModel):
    model_config = ConfigDict(extra="allow")

    prompt: str = Field(..., min_length=1)
    context: dict[str, Any] = Field(default_factory=dict)
    data: list[Any] = Field(default_factory=list)

    @field_validator("prompt")
    @classmethod
    def prompt_non_empty(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("input.prompt must be a non-empty string")
        return v.strip()


class RunOptions(BaseModel):
    model_config = ConfigDict(extra="allow")

    temperature: float | None = None
    max_tokens: int | None = None
    timeout_ms: int | None = None

    @field_validator("temperature")
    @classmethod
    def temperature_range(cls, v: float | None) -> float | None:
        if v is None:
            return v
        if v < 0 or v > 2:
            raise ValueError("options.temperature must be between 0 and 2")
        return v

    @field_validator("max_tokens")
    @classmethod
    def max_tokens_positive(cls, v: int | None) -> int | None:
        if v is None:
            return v
        if v <= 0:
            raise ValueError("options.max_tokens must be > 0 when provided")
        return v

    @field_validator("timeout_ms")
    @classmethod
    def timeout_min(cls, v: int | None) -> int | None:
        if v is None:
            return v
        if v < 1000:
            raise ValueError("options.timeout_ms must be >= 1000 when provided")
        return v


class RunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_id: UUID
    task_type: TaskType
    complexity: Complexity
    privacy_level: PrivacyLevel
    preferred_model: str = Field(default="auto")
    max_cost_usd: float | None = None
    input: RunInput
    options: RunOptions | None = None

    @field_validator("task_type", mode="before")
    @classmethod
    def task_type_enum(cls, v: object) -> object:
        if isinstance(v, str) and v not in _ENUM_TASK:
            raise ValueError("invalid task_type")
        return v

    @field_validator("complexity", mode="before")
    @classmethod
    def complexity_enum(cls, v: object) -> object:
        if isinstance(v, str) and v not in _ENUM_COMPLEXITY:
            raise ValueError("invalid complexity")
        return v

    @field_validator("privacy_level", mode="before")
    @classmethod
    def privacy_enum(cls, v: object) -> object:
        if isinstance(v, str) and v not in _ENUM_PRIVACY:
            raise ValueError("invalid privacy_level")
        return v

    @field_validator("preferred_model", mode="before")
    @classmethod
    def preferred_strip_default(cls, v: object) -> str:
        if v is None:
            return "auto"
        if not isinstance(v, str):
            raise ValueError("preferred_model must be a string")
        s = v.strip()
        if not s:
            return "auto"
        return s

    @field_validator("preferred_model")
    @classmethod
    def preferred_known_or_freeform(cls, v: str) -> str:
        """Enum values or any other non-empty string (LM Studio model id) — api_contract §2.4."""
        if v in _ENUM_PREFERRED:
            return v
        if v:
            return v
        raise ValueError("preferred_model must not be empty")

    @field_validator("max_cost_usd")
    @classmethod
    def max_cost_non_negative(cls, v: float | None) -> float | None:
        if v is None:
            return v
        if v < 0:
            raise ValueError("max_cost_usd must be >= 0 when provided")
        return v

    @model_validator(mode="before")
    @classmethod
    def merge_options_defaults(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        base_opt = {"temperature": 0.2, "max_tokens": 1000, "timeout_ms": 30000}
        raw = data.get("options")
        if isinstance(raw, dict):
            data = {**data, "options": {**base_opt, **raw}}
        else:
            data = {**data, "options": base_opt}
        return data

    def to_adapter_dict(self) -> dict[str, Any]:
        """JSON-like dict for adapters (task_id as UUID string)."""
        d = self.model_dump(mode="python")
        d["task_id"] = str(d["task_id"])
        return d


def is_cloud_preferred_model(value: str) -> bool:
    return value.strip() in ("gemini_flash", "claude_haiku")
