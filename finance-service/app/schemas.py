import uuid
from datetime import datetime
from decimal import Decimal
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: T | None = None
    error: ErrorDetail | None = None


class InvoiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_code: str
    event_id: uuid.UUID
    customer_code: str
    unit_type: str
    usage_amount: Decimal
    tariff_rate: Decimal
    total_amount: Decimal
    status: str
    issued_at: datetime
    paid_at: datetime | None = None


class UnitSummaryOut(BaseModel):
    paid: Decimal
    unpaid: Decimal


class SummaryOut(BaseModel):
    total_revenue: Decimal
    total_unpaid: Decimal
    by_unit: dict[str, UnitSummaryOut]
