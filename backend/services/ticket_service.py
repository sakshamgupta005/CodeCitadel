from __future__ import annotations

import hashlib
import io
import logging
from typing import Any

import pandas as pd

from models.schemas import KnowledgeDocument, clean_metadata
from services.exceptions import InputValidationError


logger = logging.getLogger(__name__)


class TicketService:
    required_columns = {"ticket", "resolution"}

    def parse_csv(self, content: bytes) -> list[KnowledgeDocument]:
        if not content:
            raise InputValidationError("Uploaded CSV is empty.")

        try:
            dataframe = pd.read_csv(io.BytesIO(content))
        except Exception as exc:
            raise InputValidationError(f"Could not parse CSV: {exc}") from exc

        dataframe.columns = [str(column).strip().lower() for column in dataframe.columns]
        missing = self.required_columns.difference(dataframe.columns)
        if missing:
            expected = ", ".join(sorted(self.required_columns))
            raise InputValidationError(f"CSV must include columns: {expected}.")

        documents: list[KnowledgeDocument] = []
        for row_number, row in dataframe.iterrows():
            ticket = self._cell_to_text(row.get("ticket"))
            resolution = self._cell_to_text(row.get("resolution"))
            if not ticket and not resolution:
                continue

            text = f"Support ticket: {ticket}\nResolution: {resolution}"
            document_id = self._document_id(row_number=row_number, ticket=ticket, resolution=resolution)
            documents.append(
                KnowledgeDocument(
                    id=document_id,
                    text=text,
                    metadata=clean_metadata(
                        {
                            "source": "ticket",
                            "type": "support_ticket",
                            "row_number": row_number + 1,
                        }
                    ),
                )
            )

        if not documents:
            raise InputValidationError("CSV did not contain any non-empty support tickets.")

        logger.info("Normalized %s support ticket documents", len(documents))
        return documents

    @staticmethod
    def _cell_to_text(value: Any) -> str:
        if pd.isna(value):
            return ""
        return str(value).strip()

    @staticmethod
    def _document_id(row_number: int, ticket: str, resolution: str) -> str:
        digest = hashlib.sha256(f"{row_number}:{ticket}:{resolution}".encode("utf-8")).hexdigest()
        return f"ticket:{digest[:24]}"
