from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ColumnSchema(BaseModel):
    name: str
    type: str
    nullable: bool = False


class TableSchema(BaseModel):
    name: str
    columns: list[ColumnSchema]


class ApiEndpointSchema(BaseModel):
    path: str
    method: str
    table: str | None = None
    roles: list[str]


class AuthSchema(BaseModel):
    roles: list[str]


def generate_schemas(design: dict[str, Any]) -> dict[str, Any]:
    entities = design.get("entities", [])
    roles = design.get("roles", [])
    features = design.get("features", [])

    db_tables = [_build_table(entity) for entity in entities]
    api_endpoints = []

    for entity in entities:
        api_endpoints.extend(_build_crud_endpoints(entity, roles))

    if "auth" in features:
        api_endpoints.extend(
            [
                ApiEndpointSchema(
                    path="/auth/login",
                    method="POST",
                    table="users",
                    roles=roles or ["user"],
                ),
                ApiEndpointSchema(
                    path="/auth/register",
                    method="POST",
                    table="users",
                    roles=roles or ["user"],
                ),
            ]
        )

    return {
        "db": {
            "tables": [table.dict() for table in db_tables],
        },
        "api": {
            "endpoints": [endpoint.dict() for endpoint in api_endpoints],
        },
        "auth": AuthSchema(roles=roles).dict(),
    }


def _build_table(entity: dict[str, Any]) -> TableSchema:
    columns = [
        ColumnSchema(
            name=field["name"],
            type=field["type"],
            nullable=not field.get("required", False),
        )
        for field in entity.get("fields", [])
    ]
    return TableSchema(name=entity["table_name"], columns=columns)


def _build_crud_endpoints(entity: dict[str, Any], roles: list[str]) -> list[ApiEndpointSchema]:
    table_name = entity["table_name"]
    resource_path = f"/{table_name}"
    allowed_roles = roles or ["user"]

    return [
        ApiEndpointSchema(path=resource_path, method="GET", table=table_name, roles=allowed_roles),
        ApiEndpointSchema(path=resource_path, method="POST", table=table_name, roles=allowed_roles),
        ApiEndpointSchema(
            path=f"{resource_path}/{{item_id}}",
            method="GET",
            table=table_name,
            roles=allowed_roles,
        ),
        ApiEndpointSchema(
            path=f"{resource_path}/{{item_id}}",
            method="PUT",
            table=table_name,
            roles=allowed_roles,
        ),
        ApiEndpointSchema(
            path=f"{resource_path}/{{item_id}}",
            method="DELETE",
            table=table_name,
            roles=allowed_roles,
        ),
    ]
