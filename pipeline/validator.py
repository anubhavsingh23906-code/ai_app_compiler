from __future__ import annotations

from typing import Any


def validate_schemas(schemas: dict[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    tables = schemas.get("db", {}).get("tables", [])
    table_names = {
        table["name"]
        for table in tables
        if isinstance(table, dict) and "name" in table
    }

    for table in tables:
        if not isinstance(table, dict):
            continue

        columns = table.get("columns", [])
        if not isinstance(columns, list) or not columns:
            errors.append(
                {
                    "type": "empty_table_columns",
                    "message": f"DB table '{table.get('name', 'unknown')}' must define at least one column.",
                    "severity": "high",
                    "table": table.get("name"),
                }
            )

    for endpoint in schemas.get("api", {}).get("endpoints", []):
        if not isinstance(endpoint, dict):
            continue

        table_name = endpoint.get("table")
        if table_name and table_name not in table_names:
            errors.append(
                {
                    "type": "missing_db_table",
                    "message": (
                        f"API route {endpoint.get('method')} {endpoint.get('path')} "
                        f"references missing table '{table_name}'."
                    ),
                    "severity": "high",
                    "table": table_name,
                    "path": endpoint.get("path"),
                }
            )

    roles = schemas.get("auth", {}).get("roles", [])
    if not roles:
        errors.append(
            {
                "type": "missing_roles",
                "message": "Auth schema does not define any roles.",
                "severity": "high",
            }
        )

    return errors
