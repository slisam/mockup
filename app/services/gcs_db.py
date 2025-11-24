from google.cloud import storage
from typing import BinaryIO
from app.core.config import settings

class GCSService:
	def __init__(self):
		self.client = storage.Client()
		self.bucket_name = getattr(settings, "GCS_BUCKET_NAME", None)
		if not self.bucket_name:
			raise ValueError("GCS bucket name is not configured in settings (GCS_BUCKET_NAME)")
		self.bucket = self.client.bucket(self.bucket_name)

	def upload_file(self, file_data: BinaryIO, destination_blob_name: str, content_type: str) -> str:
		"""Upload a file to GCS and return the public URL"""
		blob = self.bucket.blob(destination_blob_name)
		file_data.seek(0)  # Reset file pointer
		blob.upload_from_file(file_data, content_type=content_type)
		return f"gs://{self.bucket_name}/{destination_blob_name}"

	def delete_file(self, blob_name: str) -> bool:
		"""Delete a file from GCS"""
		try:
			blob = self.bucket.blob(blob_name)
			blob.delete()
			return True
		except Exception as e:
			print(f"Error deleting file {blob_name}: {str(e)}")
			return False

gcs_service = GCSService()