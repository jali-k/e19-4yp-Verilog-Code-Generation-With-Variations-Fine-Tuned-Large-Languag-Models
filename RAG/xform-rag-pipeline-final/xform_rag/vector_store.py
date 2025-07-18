#!/usr/bin/env python3
"""
Vector store management for the Xform RAG Pipeline
Handles Chroma vector database operations
"""

import logging
import shutil
import hashlib
import json
import time
from typing import List, Dict, Any
from langchain.schema import Document

# Import with fallback for different versions
try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
    except ImportError:
        from langchain.embeddings import HuggingFaceEmbeddings

# Additional imports for CodeBERT support
try:
    from transformers import AutoTokenizer, AutoModel
    import torch

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from .config import RAGConfig
from .document_processor import DocumentProcessor


class CodeBERTEmbeddings:
    """Custom CodeBERT embeddings for code-specific similarity"""

    def __init__(self, model_name: str = "microsoft/codebert-base"):
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "transformers and torch are required for CodeBERT embeddings"
            )

        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents"""
        embeddings = []
        for text in texts:
            embedding = self._embed_single(text)
            embeddings.append(embedding.tolist())
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        return self._embed_single(text).tolist()

    def _embed_single(self, text: str) -> torch.Tensor:
        """Generate embedding for a single text"""
        # Tokenize and truncate to model's max length
        inputs = self.tokenizer(
            text, return_tensors="pt", truncation=True, padding=True, max_length=512
        )

        with torch.no_grad():
            outputs = self.model(**inputs)
            # Use [CLS] token embedding
            embeddings = outputs.last_hidden_state[:, 0, :]
            # Normalize for cosine similarity
            embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)

        return embeddings.squeeze()


class VectorStoreManager:
    """Manages the vector store for document retrieval with caching support"""

    def __init__(self, config: RAGConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.embeddings = self._create_embeddings()
        self.vector_store = None
        self.document_processor = DocumentProcessor(config)

        # Initialize caching
        self._query_cache = {}
        self._cache_ttl = 3600  # 1 hour cache TTL
        self._max_cache_size = 1000

    def _create_embeddings(self) -> HuggingFaceEmbeddings:
        """Create embeddings model based on configuration"""
        self.logger.info(
            f"Creating embeddings with model: {self.config.embedding_model} (type: {self.config.embedding_type})"
        )

        if (
            self.config.embedding_type == "codebert"
            or "codebert" in self.config.embedding_model.lower()
        ):
            self.logger.info("Using CodeBERT embeddings for code-specific similarity")
            return CodeBERTEmbeddings(self.config.embedding_model)
        else:
            # Use HuggingFace sentence transformers
            return HuggingFaceEmbeddings(
                model_name=self.config.embedding_model,
                model_kwargs={"device": "cpu"},  # Ensure CPU usage for compatibility
            )

    def get_vector_store(self) -> Chroma:
        """Get or create the vector store"""
        if self.vector_store is None:
            self.vector_store = self._load_or_create_vector_store()
        return self.vector_store

    def _load_or_create_vector_store(self) -> Chroma:
        """Load existing vector store or create new one"""
        if self._vector_store_exists():
            self.logger.info("Loading existing vector store...")
            return self._load_existing_vector_store()
        else:
            self.logger.info("Creating new vector store...")
            return self._create_new_vector_store()

    def _vector_store_exists(self) -> bool:
        """Check if vector store directory exists and has content"""
        return self.config.vector_store_dir.exists() and any(
            self.config.vector_store_dir.iterdir()
        )

    def _load_existing_vector_store(self) -> Chroma:
        """Load existing vector store from disk"""
        try:
            vector_store = Chroma(
                persist_directory=str(self.config.vector_store_dir),
                embedding_function=self.embeddings,
            )

            # Verify the store has documents
            if vector_store._collection.count() == 0:
                self.logger.warning("Vector store is empty, creating new one...")
                return self._create_new_vector_store()

            self.logger.info(
                f"Loaded vector store with {vector_store._collection.count()} documents"
            )
            return vector_store

        except Exception as e:
            self.logger.error(f"Error loading vector store: {e}")
            self.logger.info("Creating new vector store...")
            return self._create_new_vector_store()

    def _create_new_vector_store(self) -> Chroma:
        """Create new vector store from documents"""
        # Load documents
        documents = self.document_processor.load_xform_documents()

        if not documents:
            raise RuntimeError("No documents found to create vector store")

        # Validate documents
        if not self.document_processor.validate_documents(documents):
            raise RuntimeError("Document validation failed")

        # Create vector store
        self.config.vector_store_dir.mkdir(parents=True, exist_ok=True)

        vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=str(self.config.vector_store_dir),
        )

        self.logger.info(f"Created vector store with {len(documents)} documents")
        return vector_store

    def update_vector_store(self) -> bool:
        """Refresh vector store with current documents"""
        self.logger.info("Updating vector store...")

        try:
            # Remove existing store
            if self.config.vector_store_dir.exists():
                shutil.rmtree(self.config.vector_store_dir)

            # Create new store
            self.vector_store = None  # Reset cached instance
            self.vector_store = self._create_new_vector_store()

            self.logger.info("Vector store updated successfully!")
            return True

        except Exception as e:
            self.logger.error(f"Error updating vector store: {e}")
            return False

    def search_similar(self, query: str, k: int = None) -> List[Document]:
        """Search for similar documents with caching"""
        if k is None:
            k = self.config.retrieval_k

        # Check cache first
        cache_key = self._get_cache_key(query, k)
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            self.logger.debug(f"Cache hit for query: {query[:50]}...")
            return cached_result

        # Perform search
        vector_store = self.get_vector_store()
        results = vector_store.similarity_search(query, k=k)

        # Cache the results
        self._add_to_cache(cache_key, results)

        return results

    def _get_cache_key(self, query: str, k: int) -> str:
        """Generate cache key for query"""
        query_hash = hashlib.md5(query.encode()).hexdigest()
        return f"{query_hash}_{k}"

    def _get_from_cache(self, cache_key: str) -> List[Document]:
        """Get results from cache if valid"""
        if cache_key not in self._query_cache:
            return None

        cache_entry = self._query_cache[cache_key]

        # Check if cache entry is still valid
        if time.time() - cache_entry["timestamp"] > self._cache_ttl:
            del self._query_cache[cache_key]
            return None

        return cache_entry["results"]

    def _add_to_cache(self, cache_key: str, results: List[Document]):
        """Add results to cache"""
        # Clean old entries if cache is full
        if len(self._query_cache) >= self._max_cache_size:
            self._cleanup_cache()

        self._query_cache[cache_key] = {"results": results, "timestamp": time.time()}

    def _cleanup_cache(self):
        """Remove old cache entries"""
        current_time = time.time()
        to_remove = []

        for key, entry in self._query_cache.items():
            if current_time - entry["timestamp"] > self._cache_ttl:
                to_remove.append(key)

        for key in to_remove:
            del self._query_cache[key]

        # If still too many entries, remove oldest ones
        if len(self._query_cache) >= self._max_cache_size:
            sorted_entries = sorted(
                self._query_cache.items(), key=lambda x: x[1]["timestamp"]
            )
            to_remove = sorted_entries[: len(sorted_entries) // 2]  # Remove half
            for key, _ in to_remove:
                del self._query_cache[key]

    def clear_cache(self):
        """Clear the query cache"""
        self._query_cache.clear()
        self.logger.info("Query cache cleared")

    def get_retriever(self):
        """Get retriever for use in QA chains"""
        vector_store = self.get_vector_store()
        return vector_store.as_retriever(
            search_type="similarity", search_kwargs={"k": self.config.retrieval_k}
        )

    def list_transformations(self) -> List[str]:
        """List all known transformations from the vector store"""
        try:
            docs = self.search_similar("transformation function class", k=50)
            transformations = set()

            for doc in docs:
                filename = doc.metadata.get("filename", "")
                if (
                    filename
                    and filename.startswith("xform_")
                    and filename.endswith(".py")
                ):
                    transformations.add(filename)

            return sorted(list(transformations))

        except Exception as e:
            self.logger.error(f"Error listing transformations: {e}")
            return []

    def get_stats(self) -> dict:
        """Get vector store statistics"""
        try:
            vector_store = self.get_vector_store()
            doc_count = vector_store._collection.count()

            # Get file stats
            file_stats = self.document_processor.get_file_stats()

            return {
                "vector_store_documents": doc_count,
                "vector_store_directory": str(self.config.vector_store_dir),
                "embedding_model": self.config.embedding_model,
                **file_stats,
            }

        except Exception as e:
            self.logger.error(f"Error getting vector store stats: {e}")
            return {"error": str(e)}
