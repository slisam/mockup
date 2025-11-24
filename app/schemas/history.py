from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from app.schemas.transformations import StatusEnum, FileNames

class TransformationHistory(BaseModel):
    id: str
    created_at: datetime = Field(..., description='RFC3339 date-time')
    status: StatusEnum
    carrier: str
    trade_lane: str
    file_names: FileNames