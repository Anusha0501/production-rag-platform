import os
from pathlib import Path
from uuid import uuid4
import chromadb
from langsmith import traceable
from pypdf import PdfReader
from app.core.config import get_settings


class RagService:
    def __init__(self):
        settings = get_settings()
        self.client = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)

    def _collection_name(self, user_id: int) -> str:
        return f"user_{user_id}_documents"

    def ingest_pdf(self, user_id: int, source_path: str) -> tuple[str, int]:
        reader = PdfReader(source_path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        chunks = [text[i : i + 1200] for i in range(0, len(text), 1000) if text[i : i + 1200].strip()]
        collection = self.client.get_or_create_collection(self._collection_name(user_id))
        ids = [str(uuid4()) for _ in chunks]
        collection.add(ids=ids, documents=chunks, metadatas=[{"source": Path(source_path).name} for _ in chunks])
        return collection.name, len(chunks)

    @traceable(name="rag_answer")
    def answer(self, user_id: int, question: str) -> tuple[str, list[str]]:
        collection = self.client.get_or_create_collection(self._collection_name(user_id))
        results = collection.query(query_texts=[question], n_results=4)
        docs = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        context = "\n\n".join(docs)
        if not context:
            return "Upload a PDF first so I can answer using your knowledge base.", []
        answer = (
            "Based on the uploaded documents:\n\n"
            f"{context[:1800]}\n\n"
            f"Question: {question}\n\n"
            "Production note: connect an LLM in RagService.answer for synthesized responses."
        )
        sources = sorted({metadata.get("source", "uploaded PDF") for metadata in metadatas})
        return answer, sources


def persist_upload(filename: str, data: bytes) -> str:
    upload_dir = Path(get_settings().upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid4()}_{os.path.basename(filename)}"
    path = upload_dir / safe_name
    path.write_bytes(data)
    return str(path)
