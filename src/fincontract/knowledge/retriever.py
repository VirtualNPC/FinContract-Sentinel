from __future__ import annotations

from fincontract.knowledge.store import KnowledgeStore


class KnowledgeRetriever:
    def __init__(self, store: KnowledgeStore) -> None:
        self.store = store

    def lookup(self, basis_refs: list[str]) -> list[dict]:
        results: list[dict] = []
        for ref in basis_refs:
            doc_id, chunk_id = self._parse_ref(ref)
            if chunk_id:
                chunk = self.store.find_by_doc_and_chunk(doc_id, chunk_id)
                if chunk:
                    results.append(self._to_basis(chunk))
                continue

            chunks = self.store.find_by_doc_id(doc_id)
            if chunks:
                results.append(self._to_basis(chunks[0]))
        return results

    def _parse_ref(self, ref: str) -> tuple[str, str | None]:
        if "#" in ref:
            doc_id, chunk_id = ref.split("#", 1)
            return doc_id, chunk_id
        return ref, None

    @staticmethod
    def _to_basis(chunk) -> dict:
        return {
            "doc_id": chunk.doc_id,
            "title": chunk.title,
            "version": chunk.version,
            "effective_date": chunk.effective_date,
            "source": chunk.source,
            "chunk_id": chunk.chunk_id,
            "excerpt": chunk.text,
        }
