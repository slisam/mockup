import json
from datetime import datetime, UTC
from app.core.db.session import get_history_db
from app.schemas.transformations import StatusEnum, FileNames

class HistoryService:
    def __init__(self):
        self.db = get_history_db()

    def log_transformation_event(
        self,
        transformation_id: str,
        status: StatusEnum,
        carrier: str,
        trade_lane: str,
        file_names: FileNames,
        created_at: datetime, 
    ) -> int:
        """Insert one transformation history record and return its auto-incremented id."""
        timestamp = datetime.now(UTC).isoformat()

        query = """
        INSERT INTO transformation_history (transformation_id, status, carrier, trade_lane, timestamp, details, file_names)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            transformation_id,
            status.value,
            carrier,
            trade_lane,
            timestamp,
            json.dumps({}),               
            json.dumps(file_names.dict()),
        )
        history_id = self.db.execute_insert(query, params)
        return history_id
