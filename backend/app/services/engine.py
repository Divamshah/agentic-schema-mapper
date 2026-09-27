import io
import pandas as pd
from typing import List
from app.models.plan import ExtractionPlan
from app.models.domain import CanonicalLedgerEntry

def _clean_eu_currency(val) -> float:
    if pd.isna(val): return 0.0
    val_str = str(val).replace('€', '').strip()
    # Remove thousands separator (period) and replace decimal separator (comma) with period
    val_str = val_str.replace('.', '').replace(',', '.')
    try:
        return float(val_str)
    except ValueError:
        return 0.0

def _clean_us_currency(val) -> float:
    if pd.isna(val): return 0.0
    val_str = str(val).replace('$', '').replace(',', '').strip()
    try:
        return float(val_str)
    except ValueError:
        return 0.0

def execute_plan(csv_content: str, plan: ExtractionPlan) -> List[CanonicalLedgerEntry]:
    """
    The deterministic Muscle.
    Reads the CSV, applies the ExtractionPlan strictly using Pandas, 
    and validates the final data against the CanonicalLedgerEntry schema.
    """
    # 1. Read CSV using pandas, safely dropping garbage headers and footers
    df = pd.read_csv(
        io.StringIO(csv_content),
        skiprows=plan.skip_header_rows,
        skipfooter=plan.skip_footer_rows,
        engine='python', # Required for skipfooter
        on_bad_lines='skip' # Gracefully drop malformed rows
    )
    
    df.columns = df.columns.str.strip() # Clean column names

    # 2. Handle Parent-Child Denormalized Data
    for col in plan.forward_fill_columns:
        if col in df.columns:
            df[col] = df[col].ffill()

    # 3. Apply Column Mappings to a new Target DataFrame
    target_df = pd.DataFrame()

    for mapping in plan.column_mappings:
        src = mapping.source_column
        tgt = mapping.target_column
        transform = mapping.transformation_type

        if src not in df.columns:
            continue

        if transform == "NONE":
            target_df[tgt] = df[src]
            
        elif transform == "CLEAN_CURRENCY":
            parsed_vals = df[src].apply(_clean_us_currency)
            target_df[tgt] = parsed_vals.abs() # Ensure positive amount per canonical schema
            
        elif transform == "PARSE_EU_CURRENCY":
            parsed_vals = df[src].apply(_clean_eu_currency)
            target_df[tgt] = parsed_vals.abs()
            
        elif transform == "PARSE_DATE":
            # Convert to string first so YYYYMMDD integers aren't treated as nanoseconds (1970-01-01)
            target_df[tgt] = pd.to_datetime(df[src].astype(str), errors='coerce').dt.strftime('%Y-%m-%d')
            
        elif transform == "MAP_DR_CR_STRING":
            target_df[tgt] = df[src].apply(
                lambda x: "DEBIT" if str(x).strip().upper() in ["DR", "DEBIT"] else "CREDIT"
            )
            
        elif transform == "INFER_DIRECTION_FROM_SIGN":
            def infer_dir(val):
                val_str = str(val).strip()
                # Negative or bracketed numbers mean CREDIT
                if val_str.startswith('-') or (val_str.startswith('(') and val_str.endswith(')')):
                    return "CREDIT"
                return "DEBIT"
            target_df[tgt] = df[src].apply(infer_dir)

    # 4. Fill in defaults & Validate Data via Pydantic
    if "currency" not in target_df.columns:
        target_df["currency"] = "USD"
    if "description" not in target_df.columns:
        target_df["description"] = None
        
    if "transaction_id" in target_df.columns:
        target_df = target_df.dropna(subset=["transaction_id"])
        # Ensure it's a string, otherwise Pydantic will reject ints!
        target_df["transaction_id"] = target_df["transaction_id"].astype(str)
        
    records = target_df.to_dict(orient="records")
    
    validated_results = []
    for record in records:
        try:
            # Convert keys to strings to satisfy type checkers (target_df.columns can be Hashable)
            str_record = {str(k): v for k, v in record.items()}
            validated_results.append(CanonicalLedgerEntry(**str_record))
        except Exception as e:
            # In a robust pipeline, this would route to a Dead Letter Queue for human review!
            print(f"Validation Error for record {record}: {e}")
            pass
            
    return validated_results
