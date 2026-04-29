# 🧠 AI App Compiler

A compiler-style system that converts natural language into a **validated, executable application configuration**.

---

## 🎯 Overview

This project treats app generation as a **systems problem, not a prompt problem**.

Instead of using a single LLM call, it implements a **multi-stage pipeline**:

Natural Language → Structured IR → System Design → Schemas → Validation → Repair → Execution

---

## ⚙️ Architecture

The system is divided into deterministic stages:

1. **Intent Extraction**
   - Converts user input into structured JSON (features, roles, entities)

2. **System Design**
   - Expands intent into application architecture (modules, entities, roles)

3. **Schema Generation**
   - Generates:
     - Database schema
     - API endpoints
     - Authentication rules

4. **Validation Engine**
   - Cross-layer checks:
     - API routes ↔ DB tables
     - Schema completeness
     - Role consistency

5. **Repair Engine**
   - Fixes inconsistencies incrementally
   - Avoids full regeneration
   - Logs all fixes

6. **Execution Simulation**
   - Verifies generated config is usable
   - Confirms routes and tables exist

---

## 🔥 Key Features

- ✅ Multi-stage compiler-like pipeline  
- ✅ Deterministic system design  
- ✅ Cross-layer validation  
- ✅ Intelligent repair engine (rule-based)  
- ✅ Execution awareness  
- ✅ Handles vague inputs with assumptions  
- ✅ Metrics tracking (`/metrics`)  

---

## 🧪 Example

### Input

```json
{
  "prompt": "Build a CRM with contacts and admin dashboard"
}
