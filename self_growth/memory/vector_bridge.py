# vector_bridge.py

import chromadb
from chromadb.config import Settings

# Initialize the Chroma client using local persistent storage
client = chromadb.PersistentClient(
    path="./chroma_store"
)

# Reference or create the Raven memory collection
raven_memory = client.get_or_create_collection(name="raven_memory")

def store_thought(text: str, uid: str) -> None:
    """
    Store a thought in vector memory.
    :param text: The content to store
    :param uid: A unique string ID to reference this thought
    """
    try:
        raven_memory.add(documents=[text], ids=[uid])
    except Exception as e:
        print(f"[Vector Store] Error storing thought: {e}")

def search_memory(query: str, n_results: int = 1):
    """
    Query vector memory for a matching thought.
    :param query: The search phrase
    :param n_results: How many top results to return
    :return: Matching document(s) or empty list
    """
    try:
        results = raven_memory.query(
            query_texts=[query],
            n_results=n_results
        )
        return results.get("documents", [])
    except Exception as e:
        print(f"[Vector Store] Error during query: {e}")
        return []
