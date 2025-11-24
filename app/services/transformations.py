
from typing import List, Optional
from datetime import date


class TransformationsService:
    def create_transformation(self, excel_file, word_file, data: str):
        # TODO: logique métier / stockage / validation
        return {
            "items": [],  
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
        # TODO: logique de pagination/filtre
        return {
            "items": [],
            "next_cursor": None
        }

    def get_status_details(self, id: str):
        # TODO: logique de statut détaillé
        return {
            "id": id,
            "status": "IN_PROGRESS",
            "progress": 50,
            "message": "Traitement en cours"
        }
