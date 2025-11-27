"""Tests for TransformationsService."""
from datetime import date
from io import BytesIO
import pytest
from fastapi import HTTPException, UploadFile

from app.services.transformations import TransformationsService
from app.schemas.transformations import TransformationInput, DatesItem
from app.models.transformations import Transformation


class TestTransformationsService:
    """Test suite for TransformationsService."""

    def test_service_requires_db_session(self):
        """Test that service raises error without DB session."""
        with pytest.raises(ValueError, match="Database session cannot be None"):
            TransformationsService(db=None)

    def test_create_transformation_success(self, test_db):
        """Test successful transformation creation."""
        service = TransformationsService(db=test_db)

        # Create mock file uploads
        excel_file = UploadFile(
            filename="test.xlsx",
            file=BytesIO(b"excel content")
        )
        word_file = UploadFile(
            filename="test.docx",
            file=BytesIO(b"word content")
        )

        # Create transformation data
        data = TransformationInput(
            carrier="MSC",
            trade_lane="EU-US",
            dates=[
                DatesItem(
                    application_date=date(2024, 1, 1),
                    validity_date=date(2024, 12, 31)
                )
            ]
        )

        result = service.create_transformation(excel_file, word_file, data)

        assert "items" in result
        assert len(result["items"]) == 1
        assert result["items"][0]["carrier"] == "MSC"
        assert result["items"][0]["trade_lane"] == "EU-US"
        assert result["items"][0]["status"] == "IN_PROGRESS"
        assert result["next_cursor"] is None

    def test_list_transformations_empty(self, test_db):
        """Test listing with no transformations."""
        service = TransformationsService(db=test_db)

        result = service.list_transformations(
            cursor=None,
            limit=10,
            date_start=None,
            date_end=None,
            carrier=None,
            trade_lane=None,
            status=None
        )

        assert result["items"] == []
        assert result["next_cursor"] is None

    def test_list_transformations_with_data(self, test_db):
        """Test listing with existing transformations."""
        # Create test data
        t1 = Transformation(
            id="id-1",
            status="IN_PROGRESS",
            carrier="MSC",
            trade_lane="EU-US",
            xlsx_name="test1.xlsx",
            docx_name="test1.docx"
        )
        t2 = Transformation(
            id="id-2",
            status="IN_PROGRESS",
            carrier="CMA",
            trade_lane="US-ASIA",
            xlsx_name="test2.xlsx",
            docx_name="test2.docx"
        )

        test_db.add_all([t1, t2])
        test_db.commit()

        service = TransformationsService(db=test_db)
        result = service.list_transformations(
            cursor=None,
            limit=10,
            date_start=None,
            date_end=None,
            carrier=None,
            trade_lane=None,
            status=None
        )

        assert len(result["items"]) == 2

    def test_list_transformations_with_carrier_filter(self, test_db):
        """Test filtering by carrier."""
        t1 = Transformation(
            id="id-1",
            status="IN_PROGRESS",
            carrier="MSC",
            trade_lane="EU-US",
            xlsx_name="test1.xlsx",
            docx_name="test1.docx"
        )
        t2 = Transformation(
            id="id-2",
            status="IN_PROGRESS",
            carrier="CMA",
            trade_lane="US-ASIA",
            xlsx_name="test2.xlsx",
            docx_name="test2.docx"
        )

        test_db.add_all([t1, t2])
        test_db.commit()

        service = TransformationsService(db=test_db)
        result = service.list_transformations(
            cursor=None,
            limit=10,
            date_start=None,
            date_end=None,
            carrier=["MSC"],
            trade_lane=None,
            status=None
        )

        assert len(result["items"]) == 1
        assert result["items"][0]["carrier"] == "MSC"

    def test_list_transformations_pagination(self, test_db):
        """Test pagination with cursor."""
        # Create multiple transformations
        for i in range(5):
            t = Transformation(
                id=f"id-{i}",
                status="IN_PROGRESS",
                carrier="MSC",
                trade_lane="EU-US",
                xlsx_name=f"test{i}.xlsx",
                docx_name=f"test{i}.docx"
            )
            test_db.add(t)
        test_db.commit()

        service = TransformationsService(db=test_db)

        # First page
        result = service.list_transformations(
            cursor=None,
            limit=2,
            date_start=None,
            date_end=None,
            carrier=None,
            trade_lane=None,
            status=None
        )

        assert len(result["items"]) == 2
        assert result["next_cursor"] is not None

        # Second page using cursor
        result2 = service.list_transformations(
            cursor=result["next_cursor"],
            limit=2,
            date_start=None,
            date_end=None,
            carrier=None,
            trade_lane=None,
            status=None
        )

        assert len(result2["items"]) == 2

    def test_get_status_details_success(self, test_db):
        """Test getting status details for existing transformation."""
        t = Transformation(
            id="test-id",
            status="IN_PROGRESS",
            carrier="MSC",
            trade_lane="EU-US",
            xlsx_name="test.xlsx",
            docx_name="test.docx"
        )
        t.set_status_details({
            "UPLOAD_COMPLETE": True,
            "PROCESSING": False,
            "REVIEW": False,
            "READY_TO_PUBLISH": False
        })

        test_db.add(t)
        test_db.commit()

        service = TransformationsService(db=test_db)
        result = service.get_status_details("test-id")

        assert result["UPLOAD_COMPLETE"] is True
        assert result["PROCESSING"] is False

    def test_get_status_details_not_found(self, test_db):
        """Test getting status for non-existent transformation."""
        service = TransformationsService(db=test_db)

        with pytest.raises(HTTPException) as exc_info:
            service.get_status_details("non-existent-id")

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()
