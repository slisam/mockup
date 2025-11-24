from datetime import datetime
from typing import Dict, Any
from dataclasses import dataclass
import json
from pydantic import Field
from app.schemas.transformations import StatusEnum, FileNames

@dataclass
class TransformationHistoryModel:
    __tablename__ = "transformation_history"
    id: str
    created_at: datetime
    status: StatusEnum
    carrier: str
    trade_lane: str
    file_names: FileNames