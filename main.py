from fastapi import FastAPI
from pipeline.intent import extract_intent
from pipeline.design import design_system
from pipeline.schemas import generate_schemas
from pipeline.validator import validate
from pipeline.repair import repair

app = FastAPI()

@app.post("/generate")
def generate(prompt: str):
    # 1. Intent
    ir = extract_intent(prompt)

    # 2. Design
    design = design_system(ir)

    # 3. Schemas
    schemas = generate_schemas(design)

    # 4. Validate
    errors = validate(schemas)

    # 5. Repair if needed
    if errors:
        schemas = repair(schemas, errors)

    return {
        "intent": ir,
        "design": design,
        "schemas": schemas,
        "errors": errors
    }