from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class ColumnMapping(BaseModel):
    source_column: str = Field(..., description="Exact column name in the source CSV")
    target_column: Literal["transaction_id", "date", "account_name", "direction", "amount", "currency", "description"]
    transformation_type: Literal[
        "NONE", 
        "CLEAN_CURRENCY",             # e.g., $1,450.00 -> 1450.00
        "PARSE_EU_CURRENCY",          # e.g., -1.450,00 € -> 1450.00
        "PARSE_DATE",                 # e.g., 20260926 -> 2026-09-26
        "MAP_DR_CR_STRING",           # e.g., "DR" -> "DEBIT", "CR" -> "CREDIT"
        "INFER_DIRECTION_FROM_SIGN"   # e.g., negative amount -> CREDIT, positive -> DEBIT
    ] = Field(
        default="NONE", 
        description="Deterministic transformation to apply to the data."
    )

class ExtractionPlan(BaseModel):
    """
    This is the JSON structure the LLM 'Brain' will generate. 
    It is a deterministic recipe that the Pandas 'Muscle' will execute.
    """
    skip_header_rows: int = Field(default=0, description="Number of garbage rows at the top of the file to skip.")
    skip_footer_rows: int = Field(default=0, description="Number of garbage rows at the bottom of the file to skip.")
    forward_fill_columns: List[str] = Field(
        default_factory=list, 
        description="Columns that should be forward-filled to handle denormalized parent-child data."
    )
    column_mappings: List[ColumnMapping] = Field(..., description="How to map source columns to the canonical schema.")
