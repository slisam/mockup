from __future__ import annotations
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db.session import Base
import json
from typing import Optional


class Transformation(Base):
    """SQLAlchemy model for transformations table"""
    __tablename__ = "transformations"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, index=True)
    carrier: Mapped[str] = mapped_column(String, nullable=False, index=True)
    trade_lane: Mapped[str] = mapped_column(String, nullable=False, index=True)

    # File names stored as JSON
    xlsx_name: Mapped[str] = mapped_column(String, nullable=False)
    docx_name: Mapped[str] = mapped_column(String, nullable=False)

    # Store the full transformation input as JSON for reference
    transformation_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Progress tracking fields
    progress: Mapped[Optional[int]] = mapped_column(nullable=True, default=0)
    message: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Status details as JSON
    status_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def to_dict(self):
        """Convert model to dictionary for API response"""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
            "carrier": self.carrier,
            "trade_lane": self.trade_lane,
            "file_names": {
                "xlsx_name": self.xlsx_name,
                "docx_name": self.docx_name
            }
        }

    def get_transformation_data(self):
        """Parse and return transformation data from JSON"""
        if self.transformation_data:
            return json.loads(self.transformation_data)
        return None

    def set_transformation_data(self, data):
        """Store transformation data as JSON"""
        if data:
            self.transformation_data = json.dumps(data, default=str)

    def get_status_details(self):
        """Parse and return status details from JSON"""
        if self.status_details:
            return json.loads(self.status_details)
        return {
            "UPLOAD_COMPLETE": False,
            "PROCESSING": False,
            "REVIEW": False,
            "READY_TO_PUBLISH": False
        }

    def set_status_details(self, details: dict):
        """Store status details as JSON"""
        self.status_details = json.dumps(details)
