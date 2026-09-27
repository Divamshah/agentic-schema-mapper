import os
from google import genai
from app.models.plan import ExtractionPlan

# Note: In a real app we'd inject this via config, but we are keeping it simple for now!
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", "dummy-key-for-now"))

SYSTEM_PROMPT = """You are an expert Data Engineer AI. 
Your goal is to map messy ERP CSV exports into a canonical double-entry ledger schema.
You will be provided with the first 15-20 rows of a raw CSV file.
Generate a deterministic extraction plan in strict JSON format.

Rules:
1. Handle garbage headers by setting `skip_header_rows`.
2. Handle garbage footers by setting `skip_footer_rows`.
3. If a column represents parent data and is blank on child rows, add it to `forward_fill_columns`.
4. Map the source columns to the Target schema using the appropriate `transformation_type`. 
   - If a single column contains the amount with a sign (e.g. -1500), map it twice: once to 'amount' and once to 'direction' using INFER_DIRECTION_FROM_SIGN.
   - If there is a "DR/CR" column, map it to 'direction' using MAP_DR_CR_STRING.
   - For dates (especially in non-ISO formats like YYYYMMDD), use PARSE_DATE.
   - For European currency formats (e.g. "1.450,00 €"), use PARSE_EU_CURRENCY.
"""

import time
import logging

def generate_extraction_plan(csv_sample: str) -> ExtractionPlan:
    """
    Passes the raw CSV sample to the LLM and forces it to return 
    a strict JSON object matching the ExtractionPlan schema.
    """
    max_retries = 3
    base_wait = 2
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=f"Here is the raw CSV sample:\n\n{csv_sample}",
                config=genai.types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    response_schema=ExtractionPlan,
                    temperature=0.0
                )
            )
            return ExtractionPlan.model_validate_json(response.text)
        except Exception as e:
            if "503" in str(e) and attempt < max_retries - 1:
                wait_time = base_wait ** attempt
                logging.warning(f"Gemini API 503 error, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise e
