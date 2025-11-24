from typing import List, Optional
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import uuid
import json

from app.models.transformations import Transformation
from app.schemas.transformations import TransformationInput, StatusEnum


class TransformationsService:
    def __init__(self, db: Session = None):
        self.db = db

    def create_transformation(self, excel_file, word_file, data: TransformationInput):
        """Create a new transformation and save it to the database"""
        # Generate unique ID
        transformation_id = str(uuid.uuid4())

        # Create new transformation model
        transformation = Transformation(
            id=transformation_id,
            created_at=datetime.utcnow(),
            status=StatusEnum.SENT_TO_DMP.value,
            carrier=data.carrier,
            trade_lane=data.trade_lane,
            xlsx_name=excel_file.filename,
            docx_name=word_file.filename,
            progress=0,
            message="Transformation créée avec succès"
        )

        # Store transformation data as JSON
        transformation.set_transformation_data(data.model_dump())

        # Initialize status details
        transformation.set_status_details({
            "UPLOAD_COMPLETE": True,
            "PROCESSING": False,
            "REVIEW": False,
            "READY_TO_PUBLISH": False
        })

        # Save to database
        self.db.add(transformation)
        self.db.commit()
        self.db.refresh(transformation)

        # Return response in expected format
        return {
            "items": [transformation.to_dict()],
            "next_cursor": None
        }

    def list_transformations(
        self,
        cursor: Optional[str],
        limit: int,
        date_start: Optional[date],
        date_end: Optional[date],
        carrier: Optional[List[str]],
        trade_lane: Optional[List[str]],
        status: Optional[List[str]],
    ):
        """List transformations with filtering and pagination"""
        query = self.db.query(Transformation)

        # Apply filters
        filters = []

        if date_start:
            filters.append(Transformation.created_at >= datetime.combine(date_start, datetime.min.time()))

        if date_end:
            filters.append(Transformation.created_at <= datetime.combine(date_end, datetime.max.time()))

        if carrier:
            filters.append(Transformation.carrier.in_(carrier))

        if trade_lane:
            filters.append(Transformation.trade_lane.in_(trade_lane))

        if status:
            filters.append(Transformation.status.in_(status))

        if filters:
            query = query.filter(and_(*filters))

        # Handle cursor-based pagination
        if cursor:
            # Cursor is the created_at timestamp of the last item from previous page
            try:
                cursor_time = datetime.fromisoformat(cursor)
                query = query.filter(Transformation.created_at < cursor_time)
            except (ValueError, TypeError):
                pass

        # Order by created_at descending (newest first)
        query = query.order_by(Transformation.created_at.desc())

        # Fetch limit + 1 to determine if there's a next page
        transformations = query.limit(limit + 1).all()

        # Determine next cursor
        next_cursor = None
        if len(transformations) > limit:
            # There are more items, use the last item's timestamp as cursor
            next_cursor = transformations[limit - 1].created_at.isoformat()
            transformations = transformations[:limit]

        # Convert to response format
        items = [t.to_dict() for t in transformations]

        return {
            "items": items,
            "next_cursor": next_cursor
        }

    def get_status_details(self, id: str):
        """Get detailed status for a transformation"""
        transformation = self.db.query(Transformation).filter(Transformation.id == id).first()

        if not transformation:
            return {
                "UPLOAD_COMPLETE": False,
                "PROCESSING": False,
                "REVIEW": False,
                "READY_TO_PUBLISH": False
            }

        return transformation.get_status_details()
