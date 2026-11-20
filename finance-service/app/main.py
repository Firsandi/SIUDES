from contextlib import asynccontextmanager
from decimal import Decimal

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_roles
from app.database import get_db, init_db
from app.models import Invoice
from app.schemas import ApiResponse, InvoiceOut, SummaryOut, UnitSummaryOut

ZERO_AMOUNT = Decimal("0.00")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="SIUDES Finance Service", lifespan=lifespan)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict):
        code = exc.detail.get("code", "HTTP_ERROR")
        message = exc.detail.get("message", str(exc.detail))
    else:
        code = f"HTTP_{exc.status_code}"
        message = str(exc.detail)

    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "data": None, "error": {"code": code, "message": message}},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "data": None,
            "error": {"code": "VALIDATION_ERROR", "message": str(exc.errors())},
        },
    )


@app.get("/api/finance/health")
@app.get("/health")
async def health():
    return {
        "success": True,
        "data": {
            "status": "ok",
            "service": "finance-service",
        },
        "error": None,
    }


@app.get("/api/finance/invoices", response_model=ApiResponse[list[InvoiceOut]])
async def list_invoices(
    status_filter: str | None = Query(default=None, alias="status"),
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_roles("KASIR", "KEPALA_DESA")),
):
    stmt = select(Invoice).order_by(Invoice.issued_at.desc(), Invoice.id.desc())
    if status_filter:
        stmt = stmt.where(Invoice.status == status_filter.strip().upper())

    result = await db.execute(stmt)
    invoices = result.scalars().all()
    data = [InvoiceOut.model_validate(inv) for inv in invoices]
    return ApiResponse(success=True, data=data, error=None)


@app.get("/api/finance/summary", response_model=ApiResponse[SummaryOut])
async def get_summary(
    db: AsyncSession = Depends(get_db),
    _role: str = Depends(require_roles("KEPALA_DESA", "KASIR")),
):
    stmt = select(
        Invoice.unit_type,
        Invoice.status,
        func.coalesce(func.sum(Invoice.total_amount), Decimal("0.00")).label("total"),
    ).group_by(Invoice.unit_type, Invoice.status)

    result = await db.execute(stmt)
    rows = result.all()

    total_revenue = ZERO_AMOUNT
    total_unpaid = ZERO_AMOUNT
    by_unit: dict[str, dict[str, Decimal]] = {}

    for unit_type, inv_status, total in rows:
        amount = Decimal(total).quantize(ZERO_AMOUNT)
        if unit_type not in by_unit:
            by_unit[unit_type] = {"paid": ZERO_AMOUNT, "unpaid": ZERO_AMOUNT}

        if inv_status == "PAID":
            total_revenue += amount
            by_unit[unit_type]["paid"] += amount
        elif inv_status == "UNPAID":
            total_unpaid += amount
            by_unit[unit_type]["unpaid"] += amount

    summary = SummaryOut(
        total_revenue=total_revenue.quantize(ZERO_AMOUNT),
        total_unpaid=total_unpaid.quantize(ZERO_AMOUNT),
        by_unit={
            unit: UnitSummaryOut(
                paid=vals["paid"].quantize(ZERO_AMOUNT),
                unpaid=vals["unpaid"].quantize(ZERO_AMOUNT),
            )
            for unit, vals in by_unit.items()
        },
    )
    return ApiResponse(success=True, data=summary, error=None)
