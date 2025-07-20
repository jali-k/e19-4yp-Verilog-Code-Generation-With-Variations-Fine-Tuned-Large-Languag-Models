#!/usr/bin/env python3
"""
Configuration management for the Xform RAG Pipeline
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class RAGConfig:
    """Configuration settings for the RAG pipeline"""

    # Directories
    data_dir: Path = Path(".")
    vector_store_dir: Path = Path("./vector_store")
    output_dir: Path = Path("./generated")

    # Model settings - Optimized for lower memory usage
    model_type: str = "ollama"  # "ollama" or "ec2"
    model_name: str = "qwen2.5-coder:1.5b"  # Smaller, faster model
    ec2_endpoint: Optional[str] = None

    # Embedding settings - Consistent with vector store
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"  # 384-dim consistency
    embedding_type: str = "sentence-transformers"  # Match vector store

    # Text splitting settings
    chunk_size: int = 2000
    chunk_overlap: int = 200

    # Retrieval settings
    retrieval_k: int = 5

    # LLM settings - Optimized for consistency and speed
    temperature: float = 0.2  # More deterministic than 0.1, less random than default
    max_tokens: int = 2048  # Reasonable limit for transformation scripts
    timeout: int = 60  # Shorter timeout for faster feedback

    def __post_init__(self):
        """Convert string paths to Path objects"""
        if isinstance(self.data_dir, str):
            self.data_dir = Path(self.data_dir)
        if isinstance(self.vector_store_dir, str):
            self.vector_store_dir = Path(self.vector_store_dir)
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)

    def validate(self):
        """Validate configuration settings"""
        if self.model_type == "ec2" and not self.ec2_endpoint:
            raise ValueError("EC2 endpoint URL required for EC2 model type")

        if self.model_type not in ["ollama", "ec2"]:
            raise ValueError(f"Unsupported model type: {self.model_type}")

        if self.chunk_size <= self.chunk_overlap:
            raise ValueError("chunk_size must be greater than chunk_overlap")

    @classmethod
    def from_dict(cls, config_dict: dict) -> "RAGConfig":
        """Create config from dictionary"""
        return cls(**config_dict)

    def to_dict(self) -> dict:
        """Convert config to dictionary"""
        return {
            "data_dir": str(self.data_dir),
            "vector_store_dir": str(self.vector_store_dir),
            "output_dir": str(self.output_dir),
            "model_type": self.model_type,
            "model_name": self.model_name,
            "ec2_endpoint": self.ec2_endpoint,
            "embedding_model": self.embedding_model,
            "embedding_type": self.embedding_type,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "retrieval_k": self.retrieval_k,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "timeout": self.timeout,
        }
