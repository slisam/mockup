from __future__ import annotations
from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class StatusEnum(str, Enum):
    SENT_TO_DMP = 'SENT_TO_DMP'
    IN_PROGRESS = 'IN_PROGRESS'
    PENDING_FINAL_REVIEW = 'PENDING_FINAL_REVIEW'
    NEEDING_INPUT = 'NEEDING_INPUT'

class FileNames(BaseModel):
    xlsx_name: str
    docx_name: str

class Transformation(BaseModel):
    id: str
    created_at: datetime = Field(..., description='RFC3339 date-time')
    status: StatusEnum
    carrier: str
    trade_lane: str
    file_names: FileNames

class TransformationList(BaseModel):
    items: List[Transformation]
    next_cursor: Optional[str] = Field(None, description='Cursor for next page (nullable)')

class StatusDetails(BaseModel):
    UPLOAD_COMPLETE: bool
    PROCESSING: bool
    REVIEW: bool
    READY_TO_PUBLISH: bool

class SheetFilter(BaseModel):
    name: str
    column: str
    sheet_name: Optional[str] = None

class SurchargeIncluded(BaseModel):
    surcharge_code: str
    geo_restriction: Optional[str] = None
    validity_date: Optional[date] = None
    expiry_date: Optional[date] = None
    sheet_name: Optional[str] = None

class SurchargeToBeAdded(BaseModel):
    surcharge_code: str
    price: float
    currency: str
    geo_restriction: Optional[str] = None
    validity_date: Optional[date] = None
    expiry_date: Optional[date] = None
    basis: str
    sheet_name: Optional[str] = None

class DatesItem(BaseModel):
    application_date: date
    validity_date: date
    sheets: Optional[List[str]] = None

class SheetsAndFilters(BaseModel):
    sheets_to_exclude: List[str]
    filters: List[SheetFilter]

class TransformationInput(BaseModel): 
    carrier: str
    trade_lane: str
    dates: List[DatesItem]
    sheets_and_filters: Optional[SheetsAndFilters] = None
    surcharges_to_exclude: Optional[List[str]] = None
    surcharges_included: Optional[List[SurchargeIncluded]] = None
    surcharges_to_be_added: Optional[List[SurchargeToBeAdded]] = None

### To do for the remaning classes ####
Transformation.model_rebuild()
TransformationList.model_rebuild()
StatusDetails.model_rebuild()
TransformationInput.model_rebuild()
