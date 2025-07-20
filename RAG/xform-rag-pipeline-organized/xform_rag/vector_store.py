#!/usr/bin/env python3
"""
Vector store management using CodeBERT embeddings and Chroma
"""

import logging
import shutil
from typing import List
from langchain.schema import Document
from langchain_chroma import Chroma

from .config import RAGConfig
from .embeddings import CodeBERTEmbeddings
from .document_processor import DocumentProcessor


class VectorStoreManager:
    """Simple vector store management with CodeBERT embeddings"""

    def __init__(self, config: RAGConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.embeddings = CodeBERTEmbeddings(self.config.embedding_model)
        self.vector_store = None
        self.document_processor = DocumentProcessor(config)

    def create_vector_store(self) -> bool:
        """Create a new vector store from documents"""
        self.logger.info("Creating vector store with CodeBERT embeddings")

        try:
            # Load all documents
            documents = self.document_processor.load_all_documents()

            if not documents:
                raise ValueError("No documents found to create vector store")

            # Remove existing vector store if it exists
            if self.config.vector_store_dir.exists():
                self.logger.info("Removing existing vector store")
                shutil.rmtree(self.config.vector_store_dir)

            # Create new vector store
            self.config.vector_store_dir.mkdir(parents=True, exist_ok=True)

            self.vector_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=str(self.config.vector_store_dir),
            )

            self.logger.info(
                f"Created vector store with {len(documents)} document chunks"
            )
            return True

        except Exception as e:
            self.logger.error(f"Error creating vector store: {e}")
            return False

    def get_vector_store(self) -> Chroma:
        """Get the vector store instance"""
        if self.vector_store is None:
            if self._vector_store_exists():
                self.logger.info("Loading existing vector store")
                self.vector_store = Chroma(
                    persist_directory=str(self.config.vector_store_dir),
                    embedding_function=self.embeddings,
                )
            else:
                self.logger.info("No existing vector store found, creating new one")
                if not self.create_vector_store():
                    raise RuntimeError("Failed to create vector store")

        return self.vector_store

    def _vector_store_exists(self) -> bool:
        """Check if vector store exists and has content"""
        return self.config.vector_store_dir.exists() and any(
            self.config.vector_store_dir.iterdir()
        )

    def search_similar(self, query: str, k: int = None) -> List[Document]:
        """Search for similar documents"""
        if k is None:
            k = self.config.retrieval_k

        vector_store = self.get_vector_store()
        results = vector_store.similarity_search(query, k=k)

        self.logger.info(
            f"Found {len(results)} similar documents for query: {query[:50]}..."
        )
        return results

    def get_retriever(self):
        """Get retriever for QA chains"""
        vector_store = self.get_vector_store()
        return vector_store.as_retriever(
            search_type="similarity", search_kwargs={"k": self.config.retrieval_k}
        )

    def get_stats(self) -> dict:
        """Get vector store statistics"""
        try:
            if self.vector_store is None:
                vector_store = self.get_vector_store()
            else:
                vector_store = self.vector_store

            doc_count = vector_store._collection.count()

            return {
                "total_documents": doc_count,
                "vector_store_path": str(self.config.vector_store_dir),
                "embedding_model": self.config.embedding_model,
            }

        except Exception as e:
            self.logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}
