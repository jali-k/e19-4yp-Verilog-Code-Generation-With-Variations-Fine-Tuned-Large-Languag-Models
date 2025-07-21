#!/usr/bin/env python3
"""
Main RAG pipeline for Verilog transformation generation
"""

import logging
from typing import Dict, Any, List
from pathlib import Path

from .config import RAGConfig
from .vector_store import VectorStoreManager
from .dual_vector_store import DualVectorStoreManager
from .code_generator import CodeGenerator
from .document_processor import DocumentProcessor


class XformRAGPipeline:
    """Simple, focused RAG pipeline for Verilog transformation generation"""

    def __init__(self, config: RAGConfig = None, use_dual_stores: bool = True):
        """Initialize the RAG pipeline"""
        self.config = config or RAGConfig()
        self.config.validate()
        self.use_dual_stores = use_dual_stores

        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Xform RAG Pipeline")

        # Initialize components - choose vector store strategy
        if use_dual_stores:
            self.vector_store_manager = DualVectorStoreManager(self.config)
            self.logger.info("Using dual vector stores (separate for docs and code)")
        else:
            self.vector_store_manager = VectorStoreManager(self.config)
            self.logger.info("Using single hybrid vector store")

        self.code_generator = CodeGenerator(self.config)
        self.document_processor = DocumentProcessor(self.config)

        self.logger.info("Xform RAG Pipeline initialized successfully")

    def setup_vector_store(self) -> bool:
        """Setup the vector store with existing documents"""
        self.logger.info("Setting up vector store...")
        if self.use_dual_stores:
            return self.vector_store_manager.create_dual_vector_stores()
        else:
            return self.vector_store_manager.create_vector_store()

    def generate_transformation(self, user_request: str) -> Dict[str, Any]:
        """Generate a transformation script based on user request"""
        self.logger.info(f"Processing request: {user_request}")

        # Ensure vector store is ready
        try:
            self.vector_store_manager.get_vector_store()
        except Exception as e:
            return {
                "success": False,
                "error": f"Vector store not ready: {e}",
                "suggestion": "Run setup_vector_store() first",
            }

        # Generate the transformation
        return self.code_generator.generate_xform(user_request)

    def save_generated_code(self, result: Dict[str, Any]) -> bool:
        """Save generated transformation code to file"""
        if not result.get("success", False):
            self.logger.error("Cannot save failed generation result")
            return False

        try:
            code = result.get("code", "")
            filename = result.get("filename", "generated_xform.py")

            output_path = self.config.output_dir / filename

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(code)

            self.logger.info(f"Saved generated code to: {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error saving generated code: {e}")
            return False

    def search_examples(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar transformation examples"""
        try:
            results = self.vector_store_manager.search_similar(query, k)

            examples = []
            for doc in results:
                examples.append(
                    {
                        "content": (
                            doc.page_content[:500] + "..."
                            if len(doc.page_content) > 500
                            else doc.page_content
                        ),
                        "metadata": doc.metadata,
                        "source": doc.metadata.get("filename", "unknown"),
                    }
                )

            return examples

        except Exception as e:
            self.logger.error(f"Error searching examples: {e}")
            return []

    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        try:
            doc_stats = self.document_processor.get_stats()
            vector_stats = self.vector_store_manager.get_stats()

            return {
                "document_processor": doc_stats,
                "vector_store": vector_stats,
                "config": {
                    "embedding_model": self.config.embedding_model,
                    "chunk_size": self.config.chunk_size,
                    "retrieval_k": self.config.retrieval_k,
                },
            }

        except Exception as e:
            self.logger.error(f"Error getting system stats: {e}")
            return {"error": str(e)}

    def test_system(self) -> Dict[str, bool]:
        """Test all system components"""
        self.logger.info("Testing system components...")

        results = {}

        # Test document processor
        try:
            stats = self.document_processor.get_stats()
            results["document_processor"] = stats["total_source_files"] > 0
        except Exception as e:
            self.logger.error(f"Document processor test failed: {e}")
            results["document_processor"] = False

        # Test vector store
        try:
            vector_store = self.vector_store_manager.get_vector_store()
            results["vector_store"] = vector_store is not None
        except Exception as e:
            self.logger.error(f"Vector store test failed: {e}")
            results["vector_store"] = False

        # Test LLM
        try:
            llm_test = self.code_generator.llm_manager.test_connection()
            results["llm"] = llm_test
        except Exception as e:
            self.logger.error(f"LLM test failed: {e}")
            results["llm"] = False

        # Test code generation with simple request
        try:
            test_result = self.generate_transformation("test transformation")
            results["code_generation"] = test_result.get("success", False)
        except Exception as e:
            self.logger.error(f"Code generation test failed: {e}")
            results["code_generation"] = False

        return results
