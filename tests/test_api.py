"""Integration tests for API endpoints."""
from io import BytesIO
import json
import pytest


class TestTransformationsAPI:
    """Test suite for /transformations endpoints."""

    def test_create_transformation_endpoint(self, client, sample_transformation_data):
        """Test POST /transformations endpoint."""
        # Create file-like objects
        excel_file = ("test.xlsx", BytesIO(b"excel content"), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        word_file = ("test.docx", BytesIO(b"word content"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        response = client.post(
            "/transformations",
            files={
                "excel_file": excel_file,
                "word_file": word_file,
            },
            data={"data": json.dumps(sample_transformation_data)}
        )

        assert response.status_code == 201
        data = response.json()

        assert "items" in data
        assert len(data["items"]) == 1
        assert data["items"][0]["carrier"] == "MSC"
        assert data["items"][0]["trade_lane"] == "EU-US"

    def test_create_transformation_invalid_excel_extension(self, client, sample_transformation_data):
        """Test validation of Excel file extension."""
        excel_file = ("test.txt", BytesIO(b"not excel"), "text/plain")
        word_file = ("test.docx", BytesIO(b"word"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        response = client.post(
            "/transformations",
            files={
                "excel_file": excel_file,
                "word_file": word_file,
            },
            data={"data": json.dumps(sample_transformation_data)}
        )

        assert response.status_code == 400
        assert "Excel file must be" in response.json()["detail"]

    def test_create_transformation_invalid_word_extension(self, client, sample_transformation_data):
        """Test validation of Word file extension."""
        excel_file = ("test.xlsx", BytesIO(b"excel"), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        word_file = ("test.txt", BytesIO(b"not word"), "text/plain")

        response = client.post(
            "/transformations",
            files={
                "excel_file": excel_file,
                "word_file": word_file,
            },
            data={"data": json.dumps(sample_transformation_data)}
        )

        assert response.status_code == 400
        assert "Word file must be" in response.json()["detail"]

    def test_create_transformation_invalid_json(self, client):
        """Test validation of JSON data."""
        excel_file = ("test.xlsx", BytesIO(b"excel"), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        word_file = ("test.docx", BytesIO(b"word"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        response = client.post(
            "/transformations",
            files={
                "excel_file": excel_file,
                "word_file": word_file,
            },
            data={"data": "invalid json {"}
        )

        assert response.status_code == 400
        assert "Invalid JSON" in response.json()["detail"]

    def test_list_transformations_empty(self, client):
        """Test listing when no transformations exist."""
        response = client.get("/transformations")

        assert response.status_code == 200
        data = response.json()

        assert data["items"] == []
        assert data["next_cursor"] is None

    def test_list_transformations_with_limit(self, client, sample_transformation_data):
        """Test listing with limit parameter."""
        # Create multiple transformations
        for i in range(3):
            excel_file = (f"test{i}.xlsx", BytesIO(b"excel"), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            word_file = (f"test{i}.docx", BytesIO(b"word"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

            client.post(
                "/transformations",
                files={"excel_file": excel_file, "word_file": word_file},
                data={"data": json.dumps(sample_transformation_data)}
            )

        response = client.get("/transformations?limit=2")

        assert response.status_code == 200
        data = response.json()

        assert len(data["items"]) == 2

    def test_list_transformations_with_carrier_filter(self, client):
        """Test filtering by carrier."""
        # Create transformations with different carriers
        for carrier in ["MSC", "CMA", "MSC"]:
            data = {
                "carrier": carrier,
                "trade_lane": "EU-US",
                "dates": [{"application_date": "2024-01-01", "validity_date": "2024-12-31"}]
            }

            excel_file = ("test.xlsx", BytesIO(b"excel"), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            word_file = ("test.docx", BytesIO(b"word"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

            client.post(
                "/transformations",
                files={"excel_file": excel_file, "word_file": word_file},
                data={"data": json.dumps(data)}
            )

        response = client.get("/transformations?carrier=MSC")

        assert response.status_code == 200
        data = response.json()

        assert len(data["items"]) == 2
        for item in data["items"]:
            assert item["carrier"] == "MSC"

    def test_get_status_details_success(self, client, sample_transformation_data):
        """Test getting status details for existing transformation."""
        # Create transformation
        excel_file = ("test.xlsx", BytesIO(b"excel"), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        word_file = ("test.docx", BytesIO(b"word"), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        create_response = client.post(
            "/transformations",
            files={"excel_file": excel_file, "word_file": word_file},
            data={"data": json.dumps(sample_transformation_data)}
        )

        transformation_id = create_response.json()["items"][0]["id"]

        # Get status details
        response = client.get(f"/transformations/{transformation_id}/status-details-in-progress")

        assert response.status_code == 200
        data = response.json()

        assert "UPLOAD_COMPLETE" in data
        assert "PROCESSING" in data
        assert data["UPLOAD_COMPLETE"] is True

    def test_get_status_details_not_found(self, client):
        """Test getting status for non-existent transformation."""
        response = client.get("/transformations/non-existent-id/status-details-in-progress")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
