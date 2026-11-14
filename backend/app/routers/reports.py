"""Report endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.schemas.sale import SalesReport
from app.services import report_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/sales", response_model=SalesReport)
def sales_report(
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return report_service.sales_report(db, user.id, date_from, date_to)


@router.get("/sales/export")
def export_sales(
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    # Materialise rows first so the request-scoped DB session outlives the query.
    chunks = list(report_service.export_sales_csv(db, user.id, date_from, date_to))
    return StreamingResponse(
        iter(chunks),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="sales.csv"'},
    )
