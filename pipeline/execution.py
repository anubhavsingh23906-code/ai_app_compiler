from __future__ import annotations

from typing import Any


def simulate_execution(schemas: dict[str, Any]) -> dict[str, Any]:
    endpoints = schemas.get("api", {}).get("endpoints", [])
    tables = schemas.get("db", {}).get("tables", [])

    routes_available = [
        f"{endpoint.get('method')} {endpoint.get('path')}"
        for endpoint in endpoints
        if isinstance(endpoint, dict) and endpoint.get("method") and endpoint.get("path")
    ]
    tables_created = [
        table.get("name")
        for table in tables
        if isinstance(table, dict) and table.get("name")
    ]

    return {
        "routes_available": routes_available,
        "tables_created": tables_created,
        "status": "executable",
    }
