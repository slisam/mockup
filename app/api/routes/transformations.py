
from __future__ import annotations
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query, Depends
import json
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session

from app.schemas.transformations import (
    TransformationInput,
    StatusDetails,
    StatusEnum,
    TransformationList,
)
from app.services.transformations import TransformationsService
from app.db.session import get_db

router = APIRouter()


def get_transformations_service(db: Session = Depends(get_db)) -> TransformationsService:
    return TransformationsService(db=db)


@router.post("/transformations", response_model=TransformationList, status_code=201)
async def create_transformation(
    excel_file: UploadFile = File(..., description="Excel file"),
    word_file: UploadFile = File(..., description="Word file"),
    data: str = Form(..., description="JSON string containing TransformationInput"),
    service: TransformationsService = Depends(get_transformations_service),
):
    try:
        data_dict = json.loads(data)
        transformation_data = TransformationInput(**data_dict)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in data field")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid data format: {str(e)}")

    if not excel_file.filename or not excel_file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="Excel file must be .xlsx or .xls")
    if not word_file.filename or not word_file.filename.endswith(('.docx', '.doc')):
        raise HTTPException(status_code=400, detail="Word file must be .docx or .doc")

    return service.create_transformation(
        excel_file=excel_file,
        word_file=word_file,
        data=transformation_data,
    )


@router.get("/transformations", response_model=TransformationList)
async def list_transformations(
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    limit: int = Query(20, ge=1, le=200, description="Number of items per page"),
    date_start: Optional[date] = Query(None, alias="date.start"),
    date_end: Optional[date] = Query(None, alias="date.end"),
    carrier: Optional[List[str]] = Query(None),
    trade_lane: Optional[List[str]] = Query(None),
    status: Optional[List[StatusEnum]] = Query(None),
    service: TransformationsService = Depends(get_transformations_service),
):
    return service.list_transformations(
        cursor=cursor,
        limit=limit,
        date_start=date_start,
        date_end=date_end,
        carrier=carrier,
        trade_lane=trade_lane,
        status=status,
    )


@router.get("/transformations/{id}/status-details-in-progress", response_model=StatusDetails)
async def get_status_details(
    id: str,
    service: TransformationsService = Depends(get_transformations_service),
):
    return service.get_status_details(id)


@router.get("/trade-lanes", response_model=List[str])
async def get_trade_lanes(
    service: TransformationsService = Depends(get_transformations_service),
):
    return service.get_trade_lanes()
