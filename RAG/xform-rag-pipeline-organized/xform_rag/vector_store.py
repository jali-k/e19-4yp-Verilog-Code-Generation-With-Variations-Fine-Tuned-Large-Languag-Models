#!/usr/bin/env python3
"""
Vector store management using CodeBERT embeddings and Chroma
"""

import logging
import shutil
import time
import gc
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

            # Properly close any existing vector store
            if self.vector_store is not None:
                self.logger.info("Closing existing vector store connection")
                try:
                    # Try to cleanup existing connection
                    del self.vector_store
                    gc.collect()  # Force garbage collection
                    time.sleep(0.5)  # Give time for cleanup
                except:
                    pass
                self.vector_store = None

            # For Windows, use a timestamped directory name to avoid file locking
            import datetime

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            vector_store_path = (
                self.config.vector_store_dir.parent / f"vector_store_{timestamp}"
            )

            # Update config to use new path
            old_path = self.config.vector_store_dir
            self.config.vector_store_dir = vector_store_path

            # Remove old directory later if possible
            if old_path.exists():
                try:
                    shutil.rmtree(old_path)
                    self.logger.info("Successfully removed old vector store")
                except:
                    self.logger.warning(
                        f"Could not remove old vector store at {old_path}, continuing with new location"
                    )

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
                try:
                    self.vector_store = Chroma(
                        persist_directory=str(self.config.vector_store_dir),
                        embedding_function=self.embeddings,
                    )
                except Exception as e:
                    self.logger.warning(f"Failed to load existing vector store: {e}")
                    self.logger.info("Creating new vector store instead")
                    if not self.create_vector_store():
                        raise RuntimeError("Failed to create vector store")
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
        """Search for similar documents with exact filename matching boost"""
        if k is None:
            k = self.config.retrieval_k

        vector_store = self.get_vector_store()

        # Get more results initially for post-processing (increase for better coverage)
        search_k = min(k * 5, 30)  # Get 5x more results to re-rank
        results = vector_store.similarity_search(query, k=search_k)

        self.logger.debug(f"Initial similarity search returned {len(results)} results")

        # Apply filename-based boosting
        boosted_results = self._boost_exact_matches(query, results)

        # Return top k after boosting
        final_results = boosted_results[:k]

        self.logger.info(
            f"Found {len(final_results)} similar documents for query: {query[:50]}..."
        )
        return final_results

    def _boost_exact_matches(
        self, query: str, results: List[Document]
    ) -> List[Document]:
        """Boost documents that have exact filename matches or keyword matches"""
        if not results:
            return results

        # Normalize query for matching
        query_lower = query.lower()
        query_words = query_lower.split()

        # Create enhanced query terms for natural language queries
        enhanced_terms = set(query_words)

        # Map common phrases to specific terms
        phrase_mappings = {
            "module name": ["module_name", "xform_module_name"],
            "signal width": ["signal_width", "xform_change_signal_width"],
            "reg to wire": ["reg_to_wire", "xform_reg_to_wire"],
            "wire to reg": ["wire_to_reg", "xform_wire_to_reg"],
            "enable signal": ["enable_signal", "xform_add_enable_signal"],
            "reset condition": ["reset_condition", "xform_change_reset_condition"],
            "port rename": ["rename_port", "xform_rename_port"],
        }

        # Add enhanced terms based on phrase mappings
        for phrase, terms in phrase_mappings.items():
            if phrase in query_lower:
                enhanced_terms.update(terms)

        # Create scoring for each document
        scored_docs = []

        for doc in results:
            score = 0.0
            source = doc.metadata.get("source", "").lower()
            filename = (
                source.split("/")[-1] if "/" in source else source.split("\\")[-1]
            )

            # Check all enhanced terms
            all_terms = list(enhanced_terms)

            # Exact filename match (highest priority)
            for term in all_terms:
                if term in filename:
                    if term.startswith("xform_"):
                        score += 100.0  # Perfect xform file match
                    else:
                        score += 75.0  # Good keyword match

            # Content-based keyword matching
            content = doc.page_content.lower()

            # Check for exact phrase in content
            if query_lower in content:
                score += 25.0

            # Check for individual terms in content
            for term in all_terms:
                if term in content:
                    score += 5.0

            # Special boost for transformation-specific terms
            if any(
                term in content for term in ["module", "transform", "xform", "def "]
            ):
                score += 10.0

            scored_docs.append((score, doc))

        # Sort by score (descending) and return documents
        scored_docs.sort(key=lambda x: x[0], reverse=True)

        # Log top scores for debugging
        if scored_docs:
            top_scores = [
                (score, doc.metadata.get("source", "unknown")[-30:])
                for score, doc in scored_docs[:5]
            ]  # Show top 5
            self.logger.info(f"DEBUG: Top matches for '{query}': {top_scores}")

            # Also log if we found any module_name related files
            module_name_files = [
                doc
                for score, doc in scored_docs
                if "module_name" in doc.metadata.get("source", "").lower()
            ]
            if module_name_files:
                self.logger.info(
                    f"DEBUG: Found module_name files: {[doc.metadata.get('source', '') for doc in module_name_files]}"
                )
            else:
                self.logger.info("DEBUG: No module_name files found in results")

        return [doc for score, doc in scored_docs]

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

    def _remove_vector_store_with_retry(self, max_retries: int = 5):
        """Remove vector store directory with retry for Windows file locking issues"""
        for attempt in range(max_retries):
            try:
                shutil.rmtree(self.config.vector_store_dir)
                self.logger.info("Successfully removed existing vector store")
                return
            except PermissionError as e:
                if attempt < max_retries - 1:
                    self.logger.warning(
                        f"Attempt {attempt + 1} failed to remove vector store: {e}"
                    )
                    self.logger.info("Waiting before retry...")
                    time.sleep(1.0 * (attempt + 1))  # Exponential backoff
                    gc.collect()  # Force garbage collection
                else:
                    self.logger.error(
                        f"Failed to remove vector store after {max_retries} attempts"
                    )
                    raise
            except Exception as e:
                self.logger.error(f"Unexpected error removing vector store: {e}")
                raise

    def cleanup_old_vector_stores(self):
        """Clean up old timestamped vector store directories"""
        parent_dir = self.config.vector_store_dir.parent
        pattern = "vector_store_*"

        for old_dir in parent_dir.glob(pattern):
            if old_dir != self.config.vector_store_dir:
                try:
                    shutil.rmtree(old_dir)
                    self.logger.info(f"Cleaned up old vector store: {old_dir.name}")
                except:
                    self.logger.warning(
                        f"Could not clean up old vector store: {old_dir.name}"
                    )
                    pass
