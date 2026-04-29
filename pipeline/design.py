from __future__ import annotations

from typing import Any


DEFAULT_ENTITY_FIELDS = [
    {"name": "id", "type": "uuid", "required": True},
    {"name": "created_at", "type": "datetime", "required": True},
    {"name": "updated_at", "type": "datetime", "required": True},
]


def build_system_design(intent: dict[str, list[str]]) -> dict[str, Any]:
    roles = list(intent.get("roles", []))
    features = list(intent.get("features", []))
    entities = list(intent.get("entities", []))

    entity_designs = [_build_entity_design(entity, roles) for entity in entities]
    modules = ["intent", "design", "schemas", "validator", "repair"]
    modules.extend(features)

    return {
        "app_name": _build_app_name(entities),
        "features": features,
        "roles": roles,
        "modules": _unique(modules),
        "entities": entity_designs,
    }


def _build_entity_design(entity_name: str, roles: list[str]) -> dict[str, Any]:
    return {
        "name": entity_name,
        "table_name": _pluralize(entity_name),
        "fields": list(DEFAULT_ENTITY_FIELDS),
        "owned_by_roles": roles,
    }


def _build_app_name(entities: list[str]) -> str:
    if not entities:
        return "generated_app"
    return "_".join(entities[:2]) + "_app"


def _pluralize(name: str) -> str:
    if name.endswith("y") and len(name) > 1 and name[-2] not in "aeiou":
        return f"{name[:-1]}ies"
    if name.endswith("s"):
        return name
    return f"{name}s"


def _unique(values: list[str]) -> list[str]:
    seen: list[str] = []
    for value in values:
        if value not in seen:
            seen.append(value)
    return seen
