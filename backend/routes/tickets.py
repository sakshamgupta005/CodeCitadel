from __future__ import annotations

import logging

from fastapi import APIRouter, File, UploadFile

from models.schemas import ImportResponse
from services.import_tracker import import_tracker
from services.moss_service import MossService
from services.ticket_service import TicketService


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tickets", tags=["tickets"])

ticket_service = TicketService()
moss_service = MossService()


@router.post("/import", response_model=ImportResponse)
async def import_tickets(file: UploadFile = File(...)) -> ImportResponse:
    import_id = import_tracker.start(
        source="ticket",
        index_name=moss_service.index_name,
        filename=file.filename,
    )
    logger.info("Ticket import started for filename=%s import_id=%s", file.filename, import_id)
    try:
        content = await file.read()
        documents = ticket_service.parse_csv(content)
        indexed_count, job_id = await moss_service.add_documents(documents)
    except Exception as exc:
        import_tracker.fail(import_id, str(exc))
        logger.exception("Ticket import failed for filename=%s import_id=%s", file.filename, import_id)
        raise

    message = f"Imported {indexed_count} support ticket documents."
    import_tracker.complete(
        import_id=import_id,
        documents=documents,
        indexed_count=indexed_count,
        job_id=job_id,
        message=message,
    )
    logger.info("Ticket import completed for filename=%s import_id=%s", file.filename, import_id)
    return ImportResponse(
        imported_count=len(documents),
        indexed_count=indexed_count,
        index_name=moss_service.index_name,
        job_id=job_id,
        import_id=import_id,
        message=message,
    )
