from __future__ import annotations

import hashlib
import io
import logging
import re
from datetime import UTC, datetime
from html.parser import HTMLParser

import requests

from models.schemas import KnowledgeDocument, Product, clean_metadata
from services.exceptions import ExternalServiceError, InputValidationError


logger = logging.getLogger(__name__)


class ProductKnowledgeService:
    chunk_size = 3500
    chunk_overlap = 300

    def parse_pdf(self, content: bytes) -> str:
        if not content:
            raise InputValidationError("Uploaded PDF is empty.")
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise InputValidationError("PDF upload requires pypdf. Install backend requirements first.") from exc

        try:
            reader = PdfReader(io.BytesIO(content))
            pages = [page.extract_text() or "" for page in reader.pages]
        except Exception as exc:
            raise InputValidationError(f"Could not parse PDF: {exc}") from exc

        text = "\n\n".join(page.strip() for page in pages if page.strip())
        if not text:
            raise InputValidationError("PDF did not contain extractable text.")
        return text

    def parse_text_file(self, content: bytes) -> str:
        if not content:
            raise InputValidationError("Uploaded text document is empty.")
        text = content.decode("utf-8", errors="replace").strip()
        if not text:
            raise InputValidationError("Uploaded text document did not contain text.")
        return text

    def fetch_url_text(self, url: str) -> str:
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise ExternalServiceError(f"Could not fetch URL: {exc}") from exc

        content_type = response.headers.get("content-type", "")
        body = response.text
        if "html" in content_type.lower() or "<html" in body[:1000].lower():
            text = _html_to_text(body)
        else:
            text = body

        text = _normalize_text(text)
        if not text:
            raise InputValidationError("URL did not contain readable text.")
        return text

    def build_documents(
        self,
        product: Product,
        text: str,
        source_type: str,
        title: str,
        url: str | None = None,
        filename: str | None = None,
    ) -> list[KnowledgeDocument]:
        normalized_text = _normalize_text(text)
        if not normalized_text:
            raise InputValidationError("Document text is empty.")

        source_id = hashlib.sha256(
            f"{product.id}:{source_type}:{title}:{url or filename or ''}:{normalized_text}".encode("utf-8")
        ).hexdigest()[:24]

        chunks = self._chunk_text(normalized_text)
        documents = []
        for index, chunk in enumerate(chunks, start=1):
            document_id = f"product:{product.id}:{source_type}:{source_id}:{index}"
            documents.append(
                KnowledgeDocument(
                    id=document_id,
                    text=(
                        f"Product ID: {product.id}\n"
                        f"Product: {product.name}\n"
                        f"Category: {product.category}\n"
                        f"Document: {title}\n\n"
                        f"{chunk}"
                    ),
                    metadata=clean_metadata(
                        {
                            "source": "product_knowledge",
                            "type": source_type,
                            "product_id": product.id,
                            "product_name": product.name,
                            "product_category": product.category,
                            "title": title,
                            "url": url,
                            "filename": filename,
                            "source_id": source_id,
                            "chunk_index": index,
                            "chunk_count": len(chunks),
                            "created_at": datetime.now(UTC).isoformat(),
                        }
                    ),
                )
            )

        logger.info("Built %s %s knowledge chunks for product=%s", len(documents), source_type, product.id)
        return documents

    def _chunk_text(self, text: str) -> list[str]:
        if len(text) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end >= len(text):
                break
            start = max(end - self.chunk_overlap, start + 1)
        return chunks


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1
        if tag in {"p", "br", "li", "h1", "h2", "h3", "h4", "tr"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._skip_depth > 0:
            self._skip_depth -= 1
        if tag in {"p", "li", "h1", "h2", "h3", "h4", "tr"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0:
            self.parts.append(data)


def _html_to_text(html: str) -> str:
    parser = _TextExtractor()
    parser.feed(html)
    return _normalize_text(" ".join(parser.parts))


def _normalize_text(value: str) -> str:
    lines = [re.sub(r"\s+", " ", line).strip() for line in value.splitlines()]
    return "\n".join(line for line in lines if line).strip()


product_knowledge_service = ProductKnowledgeService()
