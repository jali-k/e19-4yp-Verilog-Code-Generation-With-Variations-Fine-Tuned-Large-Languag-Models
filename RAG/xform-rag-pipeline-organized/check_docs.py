#!/usr/bin/env python3
"""Check what documentation we actually have"""

from xform_rag.vector_store import VectorStoreManager
from xform_rag.config import RAGConfig


def check_docs():
    config = RAGConfig()
    vs = VectorStoreManager(config)
    vector_store = vs.get_vector_store()

    # Get ALL documents
    all_results = vector_store.similarity_search("", k=254)
    docs = [doc for doc in all_results if vs._is_documentation(doc)]

    print(f"Found {len(docs)} documentation chunks:")
    for i, doc in enumerate(docs):
        source = doc.metadata.get("source", "unknown")
        content_preview = doc.page_content[:100].replace("\n", " ")
        print(f"{i+1}. {source}")
        print(f"   Content: {content_preview}...\n")


if __name__ == "__main__":
    check_docs()
