from __future__ import annotations

from copy import deepcopy
from typing import Any


DEFAULT_ROLE = "user"


def repair_schemas(
    schemas: dict[str, Any], errors: list[dict[str, Any]]
) -> tuple[dict[str, Any], list[str]]:
    repaired = deepcopy(schemas)
    db_tables = repaired.setdefault("db", {}).setdefault("tables", [])
    auth = repaired.setdefault("auth", {})
    repair_log: list[str] = []

    existing_tables = {
        table["name"]
        for table in db_tables
        if isinstance(table, dict) and "name" in table
    }

    for error in errors:
        if error.get("type") == "missing_db_table":
            table_name = _resolve_missing_table_name(error)
            if table_name and table_name not in existing_tables:
                db_tables.append(_build_default_table(table_name))
                existing_tables.add(table_name)
                repair_log.append(f"Added missing table: {table_name}")

        if error.get("type") == "missing_roles":
            current_roles = auth.get("roles", [])
            if not isinstance(current_roles, list):
                current_roles = []
            if DEFAULT_ROLE not in current_roles:
                auth["roles"] = current_roles + [DEFAULT_ROLE]
                repair_log.append(f"Added default role: {DEFAULT_ROLE}")

    return repaired, repair_log


def _build_default_table(table_name: str) -> dict[str, Any]:
    return {
        "name": table_name,
        "columns": [
            {"name": "id", "type": "uuid", "nullable": False},
            {"name": "name", "type": "string", "nullable": False},
        ],
    }


def _extract_table_name_from_path(path: str) -> str | None:
    if not path:
        return None

    segments = [segment for segment in path.strip("/").split("/") if segment]
    if not segments:
        return None

    first_segment = segments[0]
    if first_segment.startswith("{") and first_segment.endswith("}"):
        return None

    return first_segment


def _resolve_missing_table_name(error: dict[str, Any]) -> str | None:
    table_name = error.get("table")
    path = error.get("path", "")
    path_table_name = _extract_table_name_from_path(path)

    if path.startswith("/auth/") and table_name:
        return table_name
    if path_table_name:
        return path_table_name

    return table_name
