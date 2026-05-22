from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import json

from fincontract.knowledge.models import KnowledgeChunk


class KnowledgeStore:
    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir
        self.index_file = self.root_dir / "knowledge.jsonl"
        self._cache: list[KnowledgeChunk] | None = None
        self._cache_mtime: float | None = None

    def load_all(self) -> list[KnowledgeChunk]:
        if not self.index_file.exists():
            return []

        mtime = self.index_file.stat().st_mtime
        if self._cache is not None and self._cache_mtime == mtime:
            return list(self._cache)

        chunks: list[KnowledgeChunk] = []
        raw = self.index_file.read_text(encoding="utf-8")
        for line in raw.splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            chunks.append(KnowledgeChunk(**data))

        self._cache = list(chunks)
        self._cache_mtime = mtime
        return chunks

    def find_by_doc_id(self, doc_id: str) -> list[KnowledgeChunk]:
        return [chunk for chunk in self.load_all() if chunk.doc_id == doc_id]

    def find_by_doc_and_chunk(self, doc_id: str, chunk_id: str) -> KnowledgeChunk | None:
        for chunk in self.load_all():
            if chunk.doc_id == doc_id and chunk.chunk_id == chunk_id:
                return chunk
        return None

    def upsert_chunks(self, chunks: list[KnowledgeChunk]) -> None:
        self.root_dir.mkdir(parents=True, exist_ok=True)
        existing = self.load_all()
        existing_map = {(c.doc_id, c.chunk_id): c for c in existing}

        for chunk in chunks:
            existing_map[(chunk.doc_id, chunk.chunk_id)] = chunk

        with self.index_file.open("w", encoding="utf-8") as handle:
            for chunk in existing_map.values():
                handle.write(json.dumps(asdict(chunk), ensure_ascii=False) + "\n")

        self._cache = list(existing_map.values())
        self._cache_mtime = self.index_file.stat().st_mtime
