from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
import hashlib
import json
import re
import time
from typing import Iterable
from urllib.parse import urlparse

import httpx
import pdfplumber
import yaml

from fincontract.knowledge.models import KnowledgeChunk
from fincontract.knowledge.store import KnowledgeStore


@dataclass(frozen=True)
class DocumentSpec:
    doc_id: str
    title: str
    version: str
    effective_date: str
    source: str
    url: str
    format: str
    category: str
    enabled: bool


@dataclass(frozen=True)
class IngestOptions:
    knowledge_dir: Path
    raw_dir: Path
    dry_run: bool
    max_docs: int | None
    rate_limit_seconds: float
    skip_existing: bool
    timeout_seconds: float
    user_agent: str


class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        self._parts.append(data)

    def get_text(self) -> str:
        return "\n".join(self._parts)


def load_documents(path: Path) -> list[DocumentSpec]:
    if not path.exists():
        return []

    raw = path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw) or {}
    items = data.get("documents", [])
    documents: list[DocumentSpec] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        enabled = bool(item.get("enabled", True))
        if not enabled:
            continue
        doc_id = str(item.get("doc_id", "")).strip()
        title = str(item.get("title", "")).strip()
        source = str(item.get("source", "")).strip()
        url = str(item.get("url", "")).strip()
        if not doc_id or not title or not source or not url:
            raise ValueError("document spec requires doc_id, title, source, and url")
        documents.append(
            DocumentSpec(
                doc_id=doc_id,
                title=title,
                version=str(item.get("version", "")).strip(),
                effective_date=str(item.get("effective_date", "")).strip(),
                source=source,
                url=url,
                format=str(item.get("format", "html")).strip().lower(),
                category=str(item.get("category", "")).strip(),
                enabled=enabled,
            )
        )
    return documents


def normalize_text(text: str) -> str:
    cleaned = re.sub(r"\r\n?", "\n", text)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def extract_text_from_html(html: str) -> str:
    parser = _HTMLTextExtractor()
    parser.feed(html)
    return normalize_text(parser.get_text())


def extract_text_from_pdf(path: Path) -> str:
    try:
        with pdfplumber.open(path) as pdf:
            parts = [page.extract_text() or "" for page in pdf.pages]
        return normalize_text("\n".join(parts))
    except Exception:
        return ""


def _split_long_paragraph(paragraph: str, max_chars: int) -> list[str]:
    sentences = re.split(r"(?<=[。！？.!?])\s+", paragraph)
    chunks: list[str] = []
    current: list[str] = []
    for sentence in sentences:
        if not sentence:
            continue
        tentative = (" ".join(current + [sentence])).strip()
        if len(tentative) > max_chars and current:
            chunks.append(" ".join(current).strip())
            current = [sentence]
        else:
            current.append(sentence)
    if current:
        chunks.append(" ".join(current).strip())
    return chunks


def chunk_text(text: str, max_chars: int = 800, min_chars: int = 200) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    buffer: list[str] = []
    for paragraph in paragraphs:
        if len(paragraph) > max_chars:
            for piece in _split_long_paragraph(paragraph, max_chars):
                chunks.append(piece)
            continue
        tentative = "\n\n".join(buffer + [paragraph]).strip()
        if len(tentative) <= max_chars:
            buffer.append(paragraph)
            continue
        if buffer:
            chunks.append("\n\n".join(buffer).strip())
            buffer = [paragraph]
        else:
            chunks.append(paragraph)
    if buffer:
        chunks.append("\n\n".join(buffer).strip())

    merged: list[str] = []
    for chunk in chunks:
        if merged and len(merged[-1]) < min_chars:
            merged[-1] = f"{merged[-1]}\n\n{chunk}".strip()
        else:
            merged.append(chunk)
    return merged


def _guess_extension(url: str, content_type: str | None) -> str:
    if content_type:
        if "pdf" in content_type:
            return ".pdf"
        if "html" in content_type:
            return ".html"
    path = urlparse(url).path
    ext = Path(path).suffix
    return ext if ext else ".bin"


def download_document(
    client: httpx.Client, url: str, dest_dir: Path, skip_existing: bool
) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
    response = client.get(url)
    response.raise_for_status()
    ext = _guess_extension(url, response.headers.get("content-type"))
    target = dest_dir / f"{digest}{ext}"
    if skip_existing and target.exists():
        return target
    target.write_bytes(response.content)
    return target


def build_chunks(doc: DocumentSpec, text: str) -> list[KnowledgeChunk]:
    chunks = chunk_text(text)
    output: list[KnowledgeChunk] = []
    for index, chunk in enumerate(chunks, start=1):
        output.append(
            KnowledgeChunk(
                doc_id=doc.doc_id,
                title=doc.title,
                version=doc.version,
                effective_date=doc.effective_date,
                source=doc.source,
                chunk_id=f"{index:04d}",
                text=chunk,
            )
        )
    return output


def ingest_documents(documents: Iterable[DocumentSpec], options: IngestOptions) -> int:
    docs = list(documents)
    if options.max_docs is not None:
        docs = docs[: options.max_docs]

    store = KnowledgeStore(options.knowledge_dir)
    headers = {"User-Agent": options.user_agent}
    total_chunks = 0
    with httpx.Client(headers=headers, timeout=options.timeout_seconds) as client:
        for doc in docs:
            raw_dir = options.raw_dir / doc.doc_id
            try:
                raw_path = download_document(client, doc.url, raw_dir, options.skip_existing)
                if doc.format == "pdf" or raw_path.suffix.lower() == ".pdf":
                    text = extract_text_from_pdf(raw_path)
                else:
                    text = extract_text_from_html(raw_path.read_text(encoding="utf-8", errors="ignore"))

                if not text:
                    print(f"[warn] no text extracted: {doc.doc_id}")
                    continue

                chunks = build_chunks(doc, text)
                total_chunks += len(chunks)
                if not options.dry_run:
                    store.upsert_chunks(chunks)
                print(f"[ok] {doc.doc_id} chunks={len(chunks)}")
            except Exception as exc:
                print(f"[error] {doc.doc_id} {exc}")
            time.sleep(options.rate_limit_seconds)
    return total_chunks


def parse_args() -> dict:
    import argparse

    parser = argparse.ArgumentParser(description="Ingest knowledge documents into knowledge.jsonl")
    parser.add_argument(
        "--documents",
        default="data/knowledge/documents.yaml",
        help="Path to documents.yaml",
    )
    parser.add_argument(
        "--knowledge-dir",
        default="data/knowledge",
        help="Knowledge directory containing knowledge.jsonl",
    )
    parser.add_argument(
        "--raw-dir",
        default="data/knowledge/raw",
        help="Directory to store raw downloads",
    )
    parser.add_argument("--dry-run", action="store_true", help="Download and parse without writing")
    parser.add_argument("--max-docs", type=int, default=None, help="Limit number of documents")
    parser.add_argument("--rate-limit", type=float, default=1.0, help="Seconds between requests")
    parser.add_argument("--skip-existing", action="store_true", help="Skip existing raw files")
    parser.add_argument("--timeout", type=float, default=30.0, help="HTTP timeout in seconds")
    parser.add_argument(
        "--user-agent",
        default="FinContractSentinelBot/0.1",
        help="User-Agent header for downloads",
    )
    args = parser.parse_args()
    return {
        "documents": Path(args.documents),
        "knowledge_dir": Path(args.knowledge_dir),
        "raw_dir": Path(args.raw_dir),
        "dry_run": args.dry_run,
        "max_docs": args.max_docs,
        "rate_limit": args.rate_limit,
        "skip_existing": args.skip_existing,
        "timeout": args.timeout,
        "user_agent": args.user_agent,
    }


def main() -> int:
    options_raw = parse_args()
    documents = load_documents(options_raw["documents"])
    if not documents:
        print("[warn] no enabled documents found in documents.yaml")
        return 0

    options = IngestOptions(
        knowledge_dir=options_raw["knowledge_dir"],
        raw_dir=options_raw["raw_dir"],
        dry_run=options_raw["dry_run"],
        max_docs=options_raw["max_docs"],
        rate_limit_seconds=options_raw["rate_limit"],
        skip_existing=options_raw["skip_existing"],
        timeout_seconds=options_raw["timeout"],
        user_agent=options_raw["user_agent"],
    )
    total = ingest_documents(documents, options)
    print(f"[done] total_chunks={total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
