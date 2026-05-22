from dataclasses import dataclass


@dataclass(frozen=True)
class KnowledgeChunk:
    doc_id: str
    title: str
    version: str
    effective_date: str
    source: str
    chunk_id: str
    text: str
