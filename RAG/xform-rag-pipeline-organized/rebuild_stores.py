#!/usr/bin/env python3
"""
Force rebuild dual vector stores with complete xform files
"""

from xform_rag.config import RAGConfig
from xform_rag.dual_vector_store import DualVectorStoreManager
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def rebuild_dual_stores():
    """Force rebuild of dual vector stores"""
    config = RAGConfig()

    print("🔄 Creating dual vector store manager...")
    manager = DualVectorStoreManager(config)

    print("🔧 Force creating dual vector stores...")
    success = manager.create_dual_vector_stores()

    if success:
        print("✅ Dual vector stores created successfully!")

        # Test search
        print("\n🔍 Testing search functionality...")
        results = manager.search_similar("module name", k=3)
        print(f"Found {len(results)} results")

        for i, doc in enumerate(results):
            print(
                f"{i+1}. {doc.metadata.get('source', 'unknown')} ({len(doc.page_content)} chars)"
            )
            print(f"   Content preview: {doc.page_content[:100]}...")

    else:
        print("❌ Failed to create dual vector stores")


if __name__ == "__main__":
    rebuild_dual_stores()
