#!/usr/bin/env python3
"""Check if xform_module_name.py is in the vector store"""

from xform_rag.dual_vector_store import DualVectorStoreManager
from xform_rag.config import RAGConfig


def check_module_name_docs():
    config = RAGConfig()
    manager = DualVectorStoreManager(config)
    code_store = manager.get_code_vector_store()

    # Get all documents and check for module_name
    all_docs = code_store.similarity_search("", k=300)
    module_name_docs = [
        doc
        for doc in all_docs
        if "module_name" in doc.metadata.get("source", "").lower()
    ]

    print(f"Total code documents: {len(all_docs)}")
    print(f"Module name documents found: {len(module_name_docs)}")

    for doc in module_name_docs:
        source = doc.metadata.get("source", "unknown")
        print(f"Source: {source}")
        content_preview = doc.page_content[:100].replace("\n", " ")
        print(f"Content: {content_preview}...\n")

    # Also search directly for "module name" to see what comes up
    print('\n=== Direct search for "module name" ===')
    direct_results = code_store.similarity_search("module name", k=10)
    for i, doc in enumerate(direct_results):
        source = doc.metadata.get("source", "unknown")
        print(f"{i+1}. {source}")


if __name__ == "__main__":
    check_module_name_docs()
