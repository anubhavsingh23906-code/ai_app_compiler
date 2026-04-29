from __future__ import annotations

import json
import re
from typing import Any


FEATURE_KEYWORDS = {
    "auth": ["auth", "login", "signup", "register", "authentication"],
    "dashboard": ["dashboard", "admin panel"],
    "analytics": ["analytics", "metrics", "reporting", "reports"],
    "notifications": ["notifications", "alerts", "emails"],
    "payments": ["payments", "billing", "checkout", "subscriptions"],
    "search": ["search", "filter"],
    "chat": ["chat", "messaging", "messages"],
    "file_uploads": ["upload", "file", "attachment"],
    "booking": ["booking", "appointment", "reservation"],
}

ROLE_KEYWORDS = {
    "admin": ["admin", "administrator"],
    "manager": ["manager"],
    "user": ["user", "users", "customer", "customers", "member", "members"],
    "guest": ["guest", "visitor"],
    "staff": ["staff", "operator", "agent"],
}

ENTITY_KEYWORDS = {
    "user": ["user", "users", "customer", "customers", "member", "members"],
    "project": ["project", "projects"],
    "task": ["task", "tasks", "todo", "todos"],
    "order": ["order", "orders"],
    "product": ["product", "products", "catalog"],
    "booking": ["booking", "bookings", "appointment", "appointments", "reservation"],
    "message": ["message", "messages", "chat"],
    "report": ["report", "reports"],
    "team": ["team", "teams", "workspace", "workspaces"],
    "course": ["course", "courses"],
    "ticket": ["ticket", "tickets", "support"],
    "invoice": ["invoice", "invoices"],
    "notification": ["notification", "notifications", "alert", "alerts"],
}

DEFAULT_VAGUE_INTENT = {
    "features": ["auth"],
    "roles": ["user"],
    "entities": ["item"],
}

GENERIC_PROMPT_WORDS = {
    "a",
    "an",
    "app",
    "application",
    "build",
    "create",
    "make",
    "platform",
    "software",
    "system",
    "tool",
    "web",
    "website",
}


def extract_intent(prompt: str) -> dict[str, list[str]]:
    intent, _ = extract_intent_with_assumptions(prompt)
    return intent


def extract_intent_with_assumptions(prompt: str) -> tuple[dict[str, list[str]], list[str]]:
    raw_response = _simulate_llm_response(prompt)
    parsed = _parse_llm_json(raw_response)
    if not parsed:
        parsed = _fallback_intent(prompt)

    intent = _normalize_intent(parsed)
    assumptions = _apply_default_assumptions(prompt, intent)
    return intent, assumptions


def _simulate_llm_response(prompt: str) -> str:
    heuristic_intent = _fallback_intent(prompt)
    return (
        "Intent analysis\n"
        "```json\n"
        f"{json.dumps(heuristic_intent)}\n"
        "```"
    )


def _parse_llm_json(raw_response: str) -> dict[str, Any] | None:
    try:
        return json.loads(raw_response)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", raw_response, flags=re.DOTALL)
    if not match:
        return None

    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def _fallback_intent(prompt: str) -> dict[str, list[str]]:
    lowered = prompt.lower()

    features = _extract_matches(lowered, FEATURE_KEYWORDS)
    roles = _extract_matches(lowered, ROLE_KEYWORDS)
    entities = _extract_matches(lowered, ENTITY_KEYWORDS)

    if "auth" in features and "user" not in entities:
        entities.append("user")
    if not roles and ("auth" in features or "user" in entities):
        roles.append("user")

    return {
        "features": features,
        "roles": roles,
        "entities": entities,
    }


def _extract_matches(text: str, mapping: dict[str, list[str]]) -> list[str]:
    matches: list[str] = []
    for label, keywords in mapping.items():
        if any(keyword in text for keyword in keywords):
            matches.append(label)
    return matches


def _normalize_intent(payload: dict[str, Any]) -> dict[str, list[str]]:
    normalized: dict[str, list[str]] = {}
    for key in ("features", "roles", "entities"):
        values = payload.get(key, [])
        if not isinstance(values, list):
            values = []

        cleaned: list[str] = []
        for value in values:
            if not isinstance(value, str):
                continue
            item = value.strip().lower()
            if item and item not in cleaned:
                cleaned.append(item)
        normalized[key] = cleaned

    return normalized


def _apply_default_assumptions(prompt: str, intent: dict[str, list[str]]) -> list[str]:
    assumptions: list[str] = []
    if not _is_vague_prompt(prompt, intent):
        return assumptions

    if not intent["features"]:
        intent["features"] = list(DEFAULT_VAGUE_INTENT["features"])
        assumptions.append("Auth added as default feature")

    if not intent["roles"]:
        intent["roles"] = list(DEFAULT_VAGUE_INTENT["roles"])
        assumptions.append("Default role 'user' used due to vague input")

    if not intent["entities"]:
        intent["entities"] = list(DEFAULT_VAGUE_INTENT["entities"])
        assumptions.append("Default entity 'Item' used due to vague input")

    return assumptions


def _is_vague_prompt(prompt: str, intent: dict[str, list[str]]) -> bool:
    words = re.findall(r"[a-zA-Z]+", prompt.lower())
    meaningful_words = [word for word in words if word not in GENERIC_PROMPT_WORDS]
    extracted_groups = sum(1 for key in ("features", "roles", "entities") if intent.get(key))

    if not words:
        return True
    if not meaningful_words:
        return True
    if extracted_groups == 0:
        return True
    if len(meaningful_words) <= 1 and extracted_groups <= 1:
        return True
    if not intent.get("entities") and len(meaningful_words) <= 2:
        return True

    return False
