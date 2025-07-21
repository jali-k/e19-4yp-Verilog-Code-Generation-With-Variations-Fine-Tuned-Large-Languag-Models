#!/usr/bin/env python3
"""
Simple configuration for the organized Xform RAG Pipeline
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class RAGConfig:
    """Simple configuration for the RAG pipeline"""

    # Directories
    xform_examples_dir: Path = Path("./xform_examples")
    documentation_dir: Path = Path("./documentation")
    vector_store_dir: Path = Path("./vector_store")
    output_dir: Path = Path("./generated")

    # Model settings
    model_type: str = "ollama"  # "ollama" or "ec2"
    model_name: str = "qwen2.5-coder:1.5b"
    ec2_endpoint: Optional[str] = None

    # Embedding settings - CodeBERT for code understanding
    embedding_model: str = "microsoft/codebert-base"
    use_hybrid_embeddings: bool = True  # Use hybrid embeddings for better doc retrieval

    # Text splitting settings - optimized for code
    chunk_size: int = 1500  # Smaller chunks for better precision
    chunk_overlap: int = 150  # 10% overlap

    # Retrieval settings
    retrieval_k: int = 3  # Fewer, more relevant results

    # LLM settings
    temperature: float = 0.1  # Very deterministic for code generation
    max_tokens: int = 2048

    def __post_init__(self):
        """Convert string paths to Path objects"""
        for field_name in [
            "xform_examples_dir",
            "documentation_dir",
            "vector_store_dir",
            "output_dir",
        ]:
            value = getattr(self, field_name)
            if isinstance(value, str):
                setattr(self, field_name, Path(value))

    def validate(self):
        """Validate configuration"""
        if not self.xform_examples_dir.exists():
            raise ValueError(
                f"Xform examples directory not found: {self.xform_examples_dir}"
            )

        if not self.documentation_dir.exists():
            print(
                f"Warning: Documentation directory not found: {self.documentation_dir}"
            )

        # Create output directories if they don't exist
        self.vector_store_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
