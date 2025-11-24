"""Tests for Transformation model."""
from datetime import datetime, timezone
import json
import pytest

from app.models.transformations import Transformation


class TestTransformationModel:
    """Test suite for Transformation model."""

    def test_create_transformation(self, test_db):
        """Test creating a transformation instance."""
        transformation = Transformation(
            id="test-id-123",
            status="SENT_TO_DMP",
            carrier="MSC",
            trade_lane="EU-US",
            xlsx_name="test.xlsx",
            docx_name="test.docx",
            progress=0,
            message="Test message"
        )

        test_db.add(transformation)
        test_db.commit()

        # Retrieve from DB
        saved = test_db.query(Transformation).filter_by(id="test-id-123").first()

        assert saved is not None
        assert saved.carrier == "MSC"
        assert saved.trade_lane == "EU-US"
        assert saved.progress == 0

    def test_to_dict(self, test_db):
        """Test conversion to dictionary."""
        transformation = Transformation(
            id="test-id-123",
            created_at=datetime.now(timezone.utc),
            status="SENT_TO_DMP",
            carrier="MSC",
            trade_lane="EU-US",
            xlsx_name="test.xlsx",
            docx_name="test.docx"
        )

        result = transformation.to_dict()

        assert result["id"] == "test-id-123"
        assert result["status"] == "SENT_TO_DMP"
        assert result["carrier"] == "MSC"
        assert result["trade_lane"] == "EU-US"
        assert "file_names" in result
        assert result["file_names"]["xlsx_name"] == "test.xlsx"
        assert result["file_names"]["docx_name"] == "test.docx"

    def test_set_and_get_transformation_data(self):
        """Test JSON storage for transformation data."""
        transformation = Transformation(
            id="test-id",
            status="SENT_TO_DMP",
            carrier="MSC",
            trade_lane="EU-US",
            xlsx_name="test.xlsx",
            docx_name="test.docx"
        )

        data = {"carrier": "MSC", "dates": [{"date": "2024-01-01"}]}
        transformation.set_transformation_data(data)

        retrieved = transformation.get_transformation_data()

        assert retrieved == data
        assert retrieved["carrier"] == "MSC"

    def test_get_transformation_data_with_invalid_json(self):
        """Test handling of corrupted JSON."""
        transformation = Transformation(
            id="test-id",
            status="SENT_TO_DMP",
            carrier="MSC",
            trade_lane="EU-US",
            xlsx_name="test.xlsx",
            docx_name="test.docx"
        )

        # Manually set invalid JSON
        transformation.transformation_data = "invalid json {"

        result = transformation.get_transformation_data()

        # Should return None instead of crashing
        assert result is None

    def test_set_and_get_status_details(self):
        """Test status details JSON storage."""
        transformation = Transformation(
            id="test-id",
            status="SENT_TO_DMP",
            carrier="MSC",
            trade_lane="EU-US",
            xlsx_name="test.xlsx",
            docx_name="test.docx"
        )

        status = {
            "UPLOAD_COMPLETE": True,
            "PROCESSING": False,
            "REVIEW": False,
            "READY_TO_PUBLISH": False
        }

        transformation.set_status_details(status)
        retrieved = transformation.get_status_details()

        assert retrieved == status
        assert retrieved["UPLOAD_COMPLETE"] is True

    def test_get_status_details_default(self):
        """Test default status details when none set."""
        transformation = Transformation(
            id="test-id",
            status="SENT_TO_DMP",
            carrier="MSC",
            trade_lane="EU-US",
            xlsx_name="test.xlsx",
            docx_name="test.docx"
        )

        result = transformation.get_status_details()

        assert result["UPLOAD_COMPLETE"] is False
        assert result["PROCESSING"] is False
        assert result["REVIEW"] is False
        assert result["READY_TO_PUBLISH"] is False

    def test_created_at_default(self, test_db):
        """Test that created_at is set automatically."""
        transformation = Transformation(
            id="test-id",
            status="SENT_TO_DMP",
            carrier="MSC",
            trade_lane="EU-US",
            xlsx_name="test.xlsx",
            docx_name="test.docx"
        )

        test_db.add(transformation)
        test_db.commit()
        test_db.refresh(transformation)

        assert transformation.created_at is not None
        assert isinstance(transformation.created_at, datetime)
