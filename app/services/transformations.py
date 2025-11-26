from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, UploadFile
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.transformations import Transformation
from app.schemas.transformations import TransformationInput, StatusEnum


class TransformationsService:
    def __init__(self, db: Session):
        if db is None:
            raise ValueError("Database session cannot be None")
        self.db = db

    def create_transformation(
        self,
        excel_file: UploadFile,
        word_file: UploadFile,
        data: TransformationInput
    ) -> Dict[str, Any]:
        try:
            now = datetime.now(timezone.utc)
            timestamp = now.strftime("%Y%m%d%H%M%S%f")
            transformation_id = f"{data.carrier}_{data.trade_lane}_{timestamp}"

            transformation = Transformation(
                id=transformation_id,
                created_at=now,
                status=StatusEnum.SENT_TO_DMP.value,
                carrier=data.carrier,
                trade_lane=data.trade_lane,
                xlsx_name=excel_file.filename,
                docx_name=word_file.filename,
                progress=0,
                message="Transformation créée avec succès"
            )

            transformation.set_transformation_data(data.model_dump())
            transformation.set_status_details({
                "UPLOAD_COMPLETE": True,
                "PROCESSING": False,
                "REVIEW": False,
                "READY_TO_PUBLISH": False
            })

            self.db.add(transformation)
            self.db.commit()
            self.db.refresh(transformation)

            return {
                "items": [transformation.to_dict()],
                "next_cursor": None
            }
        except SQLAlchemyError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Database error while creating transformation: {str(e)}"
            )

    def list_transformations(
        self,
        cursor: Optional[str] = None,
        limit: int = 20,
        date_start: Optional[date] = None,
        date_end: Optional[date] = None,
        carrier: Optional[List[str]] = None,
        trade_lane: Optional[List[str]] = None,
        status: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        try:
            query = self.db.query(Transformation)

            filters = []

            if date_start:
                start_datetime = datetime.combine(date_start, datetime.min.time())
                filters.append(Transformation.created_at >= start_datetime)

            if date_end:
                end_datetime = datetime.combine(date_end, datetime.max.time())
                filters.append(Transformation.created_at <= end_datetime)

            if carrier:
                filters.append(Transformation.carrier.in_(carrier))

            if trade_lane:
                filters.append(Transformation.trade_lane.in_(trade_lane))

            if status:
                filters.append(Transformation.status.in_(status))

            if filters:
                query = query.filter(and_(*filters))

            if cursor:
                try:
                    cursor_time = datetime.fromisoformat(cursor)
                    query = query.filter(Transformation.created_at < cursor_time)
                except (ValueError, TypeError):
                    pass

            query = query.order_by(Transformation.created_at.desc())
            transformations = query.limit(limit + 1).all()

            next_cursor = None
            if len(transformations) > limit:
                next_cursor = transformations[limit - 1].created_at.isoformat()
                transformations = transformations[:limit]

            return {
                "items": [t.to_dict() for t in transformations],
                "next_cursor": next_cursor
            }
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database error while listing transformations: {str(e)}"
            )

    def get_status_details(self, transformation_id: str) -> Dict[str, bool]:
        try:
            transformation = self.db.query(Transformation).filter(
                Transformation.id == transformation_id
            ).first()

            if not transformation:
                raise HTTPException(
                    status_code=404,
                    detail=f"Transformation {transformation_id} not found"
                )

            return transformation.get_status_details()
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database error while fetching status details: {str(e)}"
            )

    def get_trade_lanes(self) -> List[str]:
        try:
            trade_lanes = self.db.query(Transformation.trade_lane).distinct().all()
            return [tl[0] for tl in trade_lanes]
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database error while fetching trade lanes: {str(e)}"
            )
