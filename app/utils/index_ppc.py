from pathlib import Path
from langchain_ollama import OllamaEmbeddings
import chromadb
import json
from typing import List


def batch_process(data: List, batch_size: int):
    for i in range(0, len(data), batch_size):
        yield data[i : i + batch_size]


def index_chunks(directory_path: str):
    chroma_path = Path("data/chroma")
    chroma = chromadb.PersistentClient(path=str(chroma_path))

    collection = chroma.get_or_create_collection(
        name="ppcs_chunks", metadata={"hnsw:space": "cosine"}
    )

    emb = OllamaEmbeddings(model="qwen3-embedding:0.6b")

    # carrega todos os chunks de todos os arquivos JSON no diretório
    chunks = []
    files = list(Path(directory_path).glob("*.json"))

    print(
        f"Encontrados {len(files)} arquivos JSON em '{directory_path}'. Carregando..."
    )

    for file_path in files:
        content = file_path.read_text(encoding="utf-8")
        file_chunks = json.loads(content)
        chunks.extend(file_chunks)

    if not chunks:
        print("Nenhum chunk encontrado.")
        return

    all_ids = [c["id"] for c in chunks]

    # verifica IDs existentes para evitar reprocessamento
    existing_records = collection.get(ids=all_ids, include=[])
    existing_ids = set(existing_records["ids"])

    chunks_to_process = [c for c in chunks if c["id"] not in existing_ids]

    if not chunks_to_process:
        print("Todos os chunks encontrados já foram indexados.")
        return

    total_chunks = len(chunks_to_process)
    print(
        f"Iniciando indexação de {total_chunks} novos chunks (ignorado {len(existing_ids)} existentes)..."
    )

    batch_size = 1024

    for batch in batch_process(chunks_to_process, batch_size):
        ids = [str(c["id"]) for c in batch]
        texts = [c["text"] for c in batch]
        metas = [{"source": c["source"]} for c in batch]

        vectors = emb.embed_documents(texts)

        collection.add(ids=ids, documents=texts, metadatas=metas, embeddings=vectors)
        print(f"Processados {len(ids)} chunks.")

    print(f"Finalizado. Total na coleção: {collection.count()}")


if __name__ == "__main__":
    index_chunks("data/chunks")
