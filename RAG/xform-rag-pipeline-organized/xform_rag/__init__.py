#!/usr/bin/env python3
"""
Organized Xform RAG Pipeline

A simplified RAG pipeline for generating Verilog transformation scripts
using CodeBERT embeddings and focused chunking strategies.
"""

__version__ = "1.0.0"

# Main exports
from .config import RAGConfig
from .pipeline import XformRAGPipeline
from .embeddings import CodeBERTEmbeddings
from .vector_store import VectorStoreManager
from .document_processor import DocumentProcessor
from .code_generator import CodeGenerator
from .llm_manager import LLMManager


# Convenience function
def create_pipeline(
    xform_examples_dir="./xform_examples",
    documentation_dir="./documentation",
    model_name="qwen2.5-coder:1.5b",
    **kwargs
) -> XformRAGPipeline:
    """
    Create a RAG pipeline with simple configuration

    Args:
        xform_examples_dir: Directory containing xform example files
        documentation_dir: Directory containing PyVerilog documentation
        model_name: LLM model name
        **kwargs: Additional configuration options

    Returns:
        Configured XformRAGPipeline instance
    """
    config = RAGConfig(
        xform_examples_dir=xform_examples_dir,
        documentation_dir=documentation_dir,
        model_name=model_name,
        **kwargs
    )

    return XformRAGPipeline(config)
