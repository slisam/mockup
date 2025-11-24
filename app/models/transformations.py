from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import String, DateTime, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.session import Base


class Transformation(Base):
    """SQLAlchemy model for transformations table."""

    __tablename__ = "transformations"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    status: Mapped[str] = mapped_column(String, nullable=False, index=True)
    carrier: Mapped[str] = mapped_column(String, nullable=False, index=True)
    trade_lane: Mapped[str] = mapped_column(String, nullable=False, index=True)
    xlsx_name: Mapped[str] = mapped_column(String, nullable=False)
    docx_name: Mapped[str] = mapped_column(String, nullable=False)
    transformation_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    progress: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=0)
    message: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for API response."""
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

    def get_transformation_data(self) -> Optional[Dict[str, Any]]:
        """Parse and return transformation data from JSON."""
        if not self.transformation_data:
            return None
        try:
            return json.loads(self.transformation_data)
        except json.JSONDecodeError:
            return None

    def set_transformation_data(self, data: Dict[str, Any]) -> None:
        """Store transformation data as JSON."""
        if data:
            self.transformation_data = json.dumps(data, default=str)

    def get_status_details(self) -> Dict[str, bool]:
        """Parse and return status details from JSON."""
        default_status = {
            "UPLOAD_COMPLETE": False,
            "PROCESSING": False,
            "REVIEW": False,
            "READY_TO_PUBLISH": False
        }

        if not self.status_details:
            return default_status

        try:
            return json.loads(self.status_details)
        except json.JSONDecodeError:
            return default_status

    def set_status_details(self, details: Dict[str, bool]) -> None:
        """Store status details as JSON."""
        self.status_details = json.dumps(details)
