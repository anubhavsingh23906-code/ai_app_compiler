print("DEBUG: design.py is loading")
def design_system(ir: dict):
    entities = []

    for entity in ir.get("entities", []):
        entities.append({
            "name": entity,
            "fields": ["id", "name", "created_at"]
        })

    return {
        "modules": ir.get("features", []),
        "entities": entities,
        "roles": ir.get("roles", ["user"])
    }