# Agentic ERP Schema Mapper

An autonomous, full-stack data integration platform built to map messy, unpredictable ERP exports into a strict canonical double-entry ledger format using LLMs and deterministic Pandas execution.

## The Problem
Standard ETL pipelines break when onboarding new customers because legacy ERP exports contain denormalized parent-child rows, garbage report headers, and unpredictable currency formats (e.g., EU vs. US decimals). Hardcoding Python/SQL rules for every new customer is not scalable.

## The Solution
This project utilizes a "Plan-and-Execute" architecture:
1. **The Brain (OpenAI + Pydantic):** An LLM analyzes a sample of the raw CSV and generates a strict JSON `ExtractionPlan`. It detects garbage rows, identifies currency formats, and maps messy columns to the target schema.
2. **The Muscle (Pandas):** A deterministic Python execution engine reads the `ExtractionPlan` and applies the physical transformations safely. **No LLM code execution (`eval`) is used.**

## Architecture Stack
* **Backend:** FastAPI, Python, Pandas, OpenAI native SDK (Structured Outputs)
* **Frontend:** NextJS, React, TailwindCSS
* **Target Schema:** Enforced via strict Pydantic models.

## Edge Cases Handled Autonomously
* **Legacy Reports:** Automatically detects and strips visual report headers/footers.
* **EU Number Formats:** Identifies and casts `1.450,00 €` to canonical floats `1450.00`.
* **Denormalized Parent-Child Data:** Recognizes invoice headers vs. line items and applies forward-filling to flatten the data.