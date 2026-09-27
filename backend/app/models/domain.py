from typing import Literal, Optional
import datetime
from pydantic import BaseModel, Field

class CanonicalLedgerEntry(BaseModel):
    """
    The strict, canonical target schema that Campfire needs all customer data to conform to.
    This represents a single line in a double-entry accounting ledger.
    """
    transaction_id: str = Field(..., description="Unique identifier for the transaction")
    date: datetime.date = Field(..., description="Date of the transaction in ISO format (YYYY-MM-DD)")
    account_name: str = Field(..., description="The General Ledger account name")
    direction: Literal["DEBIT", "CREDIT"] = Field(..., description="Accounting direction")
    amount: float = Field(..., ge=0, description="Absolute transaction amount")
    currency: str = Field(default="USD", description="3-letter currency code")
    description: Optional[str] = Field(None, description="Optional text describing the line item")
