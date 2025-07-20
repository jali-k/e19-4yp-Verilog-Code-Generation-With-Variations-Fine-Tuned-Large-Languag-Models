#!/usr/bin/env python3
from xform_rag import create_pipeline

pipeline = create_pipeline()
stats = pipeline.get_system_stats()
print(
    f"Vector store documents: {stats.get('vector_store', {}).get('vector_store_documents', 'unknown')}"
)
print(
    f"Available transformations: {len(pipeline.vector_store_manager.list_transformations())}"
)
