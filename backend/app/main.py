from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.services.agent import generate_extraction_plan
from app.services.engine import execute_plan

app = FastAPI(
    title="Agentic ERP Schema Mapper API",
    description="Backend API for mapping messy ERP CSVs to canonical ledger format using LLMs.",
    version="1.0.0"
)

# Crucial for NextJS to be able to communicate with our FastAPI backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Usually you restrict this in production (e.g. to localhost:3000)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/process-csv")
async def process_csv(file: UploadFile = File(...)):
    """
    Main orchestration endpoint.
    Takes a messy CSV upload, gets the Agentic extraction plan, 
    executes it deterministically, and returns the canonical data.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
        
    try:
        content = await file.read()
        # Decode the file safely
        csv_string = content.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {str(e)}")
    
    # 1. Grab a sample of the first 20 lines for the LLM
    # We never send massive files to the LLM (costly and slow)
    lines = csv_string.splitlines()
    sample_string = "\n".join(lines[:20])
    
    try:
        # 2. The Brain: Generate the deterministic extraction plan
        plan = generate_extraction_plan(sample_string)
        
        # 3. The Muscle: Execute the plan against the entire file deterministically
        ledger_entries = execute_plan(csv_string, plan)
        
        return {
            "status": "success",
            "message": "File processed successfully.",
            "plan": plan.model_dump(),
            "records_processed": len(ledger_entries),
            "data": [entry.model_dump() for entry in ledger_entries]
        }
    except Exception as e:
        logging.error(f"Error processing CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
