# Agentic ERP Schema Mapper

An autonomous, full-stack data integration platform built to map messy, unpredictable ERP exports into a strict canonical double-entry ledger format using LLMs and deterministic Pandas execution.

## The Problem
Standard ETL pipelines break when onboarding new customers because legacy ERP exports contain denormalized parent-child rows, garbage report headers, and unpredictable currency formats (e.g., EU vs. US decimals). Hardcoding Python/SQL rules for every new customer is not scalable.

## The Solution
This project utilizes a "Plan-and-Execute" architecture:
1. **The Brain (Google Gemini + Pydantic):** An LLM analyzes a sample of the raw CSV and generates a strict JSON `ExtractionPlan`. It detects garbage rows, identifies currency formats, and maps messy columns to the target schema.
2. **The Muscle (Pandas):** A deterministic Python execution engine reads the `ExtractionPlan` and applies the physical transformations safely. **No LLM code execution (`eval`) is used.**

## Architecture Stack
* **Backend:** FastAPI, Python, Pandas, Google GenAI SDK (Gemini 3.8 Flash)
* **Frontend:** NextJS, React, TailwindCSS
* **Target Schema:** Enforced via strict Pydantic models.

## Edge Cases Handled Autonomously
* **Legacy Reports:** Automatically detects and strips visual report headers/footers.
* **EU Number Formats:** Identifies and casts `1.450,00 €` to canonical floats `1450.00`.
* **Denormalized Parent-Child Data:** Recognizes invoice headers vs. line items and applies forward-filling to flatten the data.

## Quickstart (Run Locally)

You will need **Python 3.11+** and **Node.js 18+** installed.

### 1. Backend (FastAPI)
Open a terminal and run:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Export your Gemini API key
export GEMINI_API_KEY="your-api-key-here"

# Start the server on port 8000
python3 -m uvicorn app.main:app --reload
```

### 2. Frontend (Next.js)
Open a new terminal tab and run:
```bash
cd frontend
npm install
npm run dev
```

Visit **http://localhost:3000** in your browser to use the interface!