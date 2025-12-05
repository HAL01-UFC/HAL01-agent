from langchain_ollama import OllamaEmbeddings
from langchain_core.tools import tool
import chromadb

emb = OllamaEmbeddings(model="qwen3-embedding:0.6b")

client = chromadb.PersistentClient(path="data/chroma")

collection = client.get_collection("ppcs_chunks")

@tool("retrieve_ppcs", return_direct=False)
def retrieve_ppcs_tool(query: str, top_k: int = 5):
    """
    MANDATORY: Use this tool for ANY question regarding the Computer Science Course (PPC), its objectives, curriculum, subjects, or rules.
    Retrieves relevant text segments from the official Pedagogical Course Project document.
    You must rely on this retrieval tool instead of your internal knowledge.
    """
    try:
        query_vector = emb.embed_query(query)

        result = collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
        )
    except Exception as e:
        return [{"error": str(e)}]

    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]

    results = []
    if documents:
        for doc, meta in zip(documents, metadatas):
            results.append({
                "document": doc,
                "metadata": meta
            })

    return results
