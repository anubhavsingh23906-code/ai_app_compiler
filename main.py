from __future__ import annotations

from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from pipeline.design import build_system_design
from pipeline.execution import simulate_execution
from pipeline.intent import extract_intent_with_assumptions
from pipeline.repair import repair_schemas
from pipeline.schemas import generate_schemas
from pipeline.validator import validate_schemas


app = FastAPI(
    title="AI App Compiler",
    version="1.0.0",
    description="Compile a natural language prompt into a validated app configuration.",
)

METRICS: dict[str, Any] = {
    "total_requests": 0,
    "repairs_triggered": 0,
    "error_counts": {},
}


class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="Natural language app prompt.")


class GenerateResponse(BaseModel):
    intent: dict[str, Any]
    assumptions: list[str]
    design: dict[str, Any]
    schemas: dict[str, Any]
    execution: dict[str, Any]
    repair_log: list[str]
    errors: list[dict[str, Any]]


class MetricsResponse(BaseModel):
    total_requests: int
    repairs_triggered: int
    error_counts: dict[str, int]


def _record_request_metrics(errors: list[dict[str, Any]]) -> None:
    METRICS["total_requests"] += 1

    if errors:
        METRICS["repairs_triggered"] += 1

    error_counts = METRICS["error_counts"]
    for error in errors:
        error_type = error.get("type")
        if not error_type:
            continue
        error_counts[error_type] = error_counts.get(error_type, 0) + 1


def _get_metrics_snapshot() -> dict[str, Any]:
    return {
        "total_requests": METRICS["total_requests"],
        "repairs_triggered": METRICS["repairs_triggered"],
        "error_counts": dict(METRICS["error_counts"]),
    }


@app.post("/generate", response_model=GenerateResponse)
def generate_config(payload: GenerateRequest) -> GenerateResponse:
    intent, assumptions = extract_intent_with_assumptions(payload.prompt)
    design = build_system_design(intent)
    schemas = generate_schemas(design)
    repair_log: list[str] = []

    errors = validate_schemas(schemas)
    _record_request_metrics(errors)

    if errors:
        schemas, repair_log = repair_schemas(schemas, errors)
        errors = validate_schemas(schemas)

    execution = simulate_execution(schemas)

    return GenerateResponse(
        intent=intent,
        assumptions=assumptions,
        design=design,
        schemas=schemas,
        execution=execution,
        repair_log=repair_log,
        errors=errors,
    )


@app.get("/metrics", response_model=MetricsResponse)
def get_metrics() -> MetricsResponse:
    return MetricsResponse(**_get_metrics_snapshot())
