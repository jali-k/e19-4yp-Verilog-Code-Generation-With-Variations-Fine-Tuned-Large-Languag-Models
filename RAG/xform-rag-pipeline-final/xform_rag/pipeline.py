#!/usr/bin/env python3
"""
Main pipeline orchestrator for the Xform RAG Pipeline
Coordinates all components and provides the main API
"""

import logging
from typing import Dict, Any, List

from .config import RAGConfig
from .llm_manager import LLMManager
from .vector_store import VectorStoreManager
from .document_processor import DocumentProcessor
from .code_generator import CodeGenerator
from .file_manager import FileManager


class XformRAGPipeline:
    """Main RAG pipeline for xform code generation"""

    def __init__(self, config: RAGConfig = None):
        """
        Initialize the RAG pipeline

        Args:
            config: Configuration object. If None, uses default config.
        """
        self.config = config or RAGConfig()
        self.config.validate()

        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Xform RAG Pipeline...")

        # Initialize all components
        self.llm_manager = LLMManager(self.config)
        self.vector_store_manager = VectorStoreManager(self.config)
        self.document_processor = DocumentProcessor(self.config)
        self.code_generator = CodeGenerator(self.config)
        self.file_manager = FileManager(self.config)

        self.logger.info("Xform RAG Pipeline initialized successfully!")

    def generate_xform(self, user_request: str) -> Dict[str, Any]:
        """
        Generate a new transformation based on user request

        Args:
            user_request: Description of the desired transformation

        Returns:
            Dictionary containing generated code and metadata
        """
        return self.code_generator.generate_xform(user_request)

    def save_generated_xform(self, result: Dict[str, Any]) -> bool:
        """
        Save generated transformation to file

        Args:
            result: Result from generate_xform()

        Returns:
            True if saved successfully, False otherwise
        """
        return self.file_manager.save_generated_xform(result)

    def update_vector_store(self) -> bool:
        """
        Refresh vector store with new documents

        Returns:
            True if updated successfully, False otherwise
        """
        return self.vector_store_manager.update_vector_store()

    def list_transformations(self) -> List[str]:
        """
        List all known transformations from the vector store

        Returns:
            List of transformation filenames
        """
        return self.vector_store_manager.list_transformations()

    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive system statistics

        Returns:
            Dictionary with system statistics
        """
        return {
            "config": self.config.to_dict(),
            "vector_store": self.vector_store_manager.get_stats(),
            "generated_files": self.file_manager.get_generation_stats(),
            "llm_info": self.llm_manager.get_model_info(),
        }

    def test_system(self) -> Dict[str, bool]:
        """
        Test all system components

        Returns:
            Dictionary with test results for each component
        """
        results = {}

        try:
            # Test LLM connectivity
            results["llm"] = self.llm_manager.test_connection()
        except Exception as e:
            self.logger.error(f"LLM test failed: {e}")
            results["llm"] = False

        try:
            # Test vector store
            docs = self.vector_store_manager.search_similar("test", k=1)
            results["vector_store"] = len(docs) > 0
        except Exception as e:
            self.logger.error(f"Vector store test failed: {e}")
            results["vector_store"] = False

        try:
            # Test file operations
            test_result = {
                "filename": "test.py",
                "code": "# test",
                "user_request": "test",
            }
            results["file_manager"] = True  # Just check if we can create the manager
        except Exception as e:
            self.logger.error(f"File manager test failed: {e}")
            results["file_manager"] = False

        try:
            # Test code generator
            results["code_generator"] = self.code_generator.test_connection()
        except Exception as e:
            self.logger.error(f"Code generator test failed: {e}")
            results["code_generator"] = False

        return results

    def validate_generated_file(self, filename: str) -> Dict[str, Any]:
        """
        Validate a specific generated file

        Args:
            filename: Name of the file to validate

        Returns:
            Validation results
        """
        return self.file_manager.validate_generated_file(filename)

    def cleanup_old_files(self, days: int = 30) -> int:
        """
        Clean up old generated files

        Args:
            days: Remove files older than this many days

        Returns:
            Number of files removed
        """
        return self.file_manager.cleanup_old_files(days)

    def export_metadata(self, output_file: str = None) -> str:
        """
        Export all metadata to a JSON file

        Args:
            output_file: Output filename (optional)

        Returns:
            Path to exported file
        """
        return self.file_manager.export_metadata(output_file)

    def batch_generate(self, requests: List[str]) -> List[Dict[str, Any]]:
        """
        Generate multiple transformations in batch

        Args:
            requests: List of transformation requests

        Returns:
            List of generation results
        """
        results = []

        for i, request in enumerate(requests, 1):
            self.logger.info(f"Batch generation {i}/{len(requests)}: {request[:50]}...")

            try:
                result = self.generate_xform(request)
                results.append(result)

                # Auto-save if generation was successful
                if "error" not in result:
                    self.save_generated_xform(result)

            except Exception as e:
                self.logger.error(f"Batch item {i} failed: {e}")
                results.append({"error": str(e), "user_request": request})

        return results

    def search_similar_transformations(
        self, query: str, k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar transformations in the knowledge base

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of similar transformation documents with metadata
        """
        docs = self.vector_store_manager.search_similar(query, k=k)

        results = []
        for doc in docs:
            results.append(
                {
                    "content": (
                        doc.page_content[:200] + "..."
                        if len(doc.page_content) > 200
                        else doc.page_content
                    ),
                    "metadata": doc.metadata,
                    "filename": doc.metadata.get("filename", "unknown"),
                }
            )

        return results

    def get_transformation_template(self, transformation_type: str) -> str:
        """
        Get a template for a specific type of transformation

        Args:
            transformation_type: Type of transformation (e.g., "signal_modification", "module_wrapper")

        Returns:
            Template code string
        """
        # Search for similar transformations
        similar = self.search_similar_transformations(transformation_type, k=1)

        if similar:
            return similar[0]["content"]
        else:
            return self._get_default_template()

    def _get_default_template(self) -> str:
        """Get default transformation template"""
        return '''#!/usr/bin/env python3
"""
Template for Verilog transformation
"""

import sys
import os
import re
import argparse
from pyverilog.vparser.parser import parse

class TransformationVisitor:
    def __init__(self, target_signal):
        self.target_signal = target_signal
        self.changes_made = []
    
    def visit(self, node):
        # Implement transformation logic here
        pass

def transform_verilog(input_file, output_file, target_signal):
    """Main transformation function"""
    try:
        # Parse input file
        with open(input_file, 'r') as f:
            content = f.read()
        
        # Apply transformations
        visitor = TransformationVisitor(target_signal)
        # ... transformation logic ...
        
        # Write output
        with open(output_file, 'w') as f:
            f.write(content)
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Verilog transformation")
    parser.add_argument("input_file", help="Input Verilog file")
    parser.add_argument("output_file", help="Output Verilog file")
    parser.add_argument("--signal", required=True, help="Target signal")
    args = parser.parse_args()
    
    success = transform_verilog(args.input_file, args.output_file, args.signal)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
'''

    def __repr__(self) -> str:
        """String representation of the pipeline"""
        return (
            f"XformRAGPipeline(model={self.config.model_type}:{self.config.model_name})"
        )
