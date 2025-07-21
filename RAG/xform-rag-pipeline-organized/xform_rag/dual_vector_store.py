"""Dual Vector Store Manager with separate stores for documentation and code"""

import logging
import gc
import time
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Optional

from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain_core.retrievers import BaseRetriever

from .config import RAGConfig
from .hybrid_embeddings import HybridEmbeddings
from .document_processor import DocumentProcessor


def get_logger(name):
    """Simple logger helper"""
    return logging.getLogger(name)


class DualRetriever(BaseRetriever):
    """Custom retriever for dual vector store manager"""

    def __init__(self, dual_manager):
        super().__init__()
        self._dual_manager = dual_manager

    def _get_relevant_documents(
        self, query: str, *, run_manager=None
    ) -> List[Document]:
        return self._dual_manager.search_similar(query)


class SentenceTransformerEmbeddings:
    """Wrapper for SentenceTransformers to work with Chroma"""

    def __init__(self, model):
        self.model = model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents"""
        embeddings = self.model.encode(texts)
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        """Embed a query string"""
        embedding = self.model.encode([text])
        return embedding[0].tolist()


class DualVectorStoreManager:
    """Manages separate vector stores for documentation and code"""

    def __init__(self, config: RAGConfig):
        self.config = config
        self.logger = get_logger(__name__)

        # Initialize embeddings
        self.code_embeddings = HybridEmbeddings()  # CodeBERT for code

        # SentenceTransformers for documentation
        try:
            from sentence_transformers import SentenceTransformer

            doc_model = SentenceTransformer("all-MiniLM-L6-v2")
            self.doc_embeddings = SentenceTransformerEmbeddings(doc_model)
            self.logger.info("Initialized SentenceTransformers for documentation")
        except ImportError:
            self.logger.warning(
                "SentenceTransformers not available, using hybrid embeddings for docs"
            )
            self.doc_embeddings = HybridEmbeddings()

        self.document_processor = DocumentProcessor(config)
        self.code_vector_store = None
        self.doc_vector_store = None

        # Find or create timestamped stores
        self.find_or_create_stores()

    def find_or_create_stores(self):
        """Find existing dual stores or create new ones"""
        base_path = Path(self.config.vector_store_dir)

        # Look for existing timestamped stores
        code_pattern = "code_store_*"
        doc_pattern = "doc_store_*"

        code_dirs = sorted(base_path.glob(code_pattern), reverse=True)
        doc_dirs = sorted(base_path.glob(doc_pattern), reverse=True)

        if code_dirs and doc_dirs and len(code_dirs) > 0 and len(doc_dirs) > 0:
            # Use most recent stores if they exist and have the same timestamp
            latest_code = code_dirs[0]
            latest_doc = doc_dirs[0]

            code_timestamp = latest_code.name.split("_")[-1]
            doc_timestamp = latest_doc.name.split("_")[-1]

            if code_timestamp == doc_timestamp:
                self.code_store_path = str(latest_code)
                self.doc_store_path = str(latest_doc)
                self.logger.info(
                    f"Found existing dual stores with timestamp: {code_timestamp}"
                )
                return

        # Create new timestamped stores
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.code_store_path = str(base_path / f"code_store_{timestamp}")
        self.doc_store_path = str(base_path / f"doc_store_{timestamp}")
        self.logger.info(f"Creating new dual stores with timestamp: {timestamp}")

    def get_code_vector_store(self):
        """Get or create the code vector store"""
        if self.code_vector_store is not None:
            return self.code_vector_store

        self.code_vector_store = Chroma(
            persist_directory=self.code_store_path,
            embedding_function=self.code_embeddings,
        )
        return self.code_vector_store

    def get_doc_vector_store(self):
        """Get or create the documentation vector store"""
        if self.doc_vector_store is not None:
            return self.doc_vector_store

        self.doc_vector_store = Chroma(
            persist_directory=self.doc_store_path,
            embedding_function=self.doc_embeddings,
        )
        return self.doc_vector_store

    def create_dual_vector_stores(self) -> bool:
        """Create separate vector stores for documentation and code"""
        try:
            # Load all documents
            documents = self.document_processor.load_all_documents()
            if not documents:
                raise ValueError("No documents found to create vector stores")

            # Separate documents by type
            doc_documents = []
            code_documents = []

            for doc in documents:
                if self._is_documentation(doc):
                    doc_documents.append(doc)
                else:
                    code_documents.append(doc)

            self.logger.info(
                f"Separating {len(documents)} documents: {len(doc_documents)} docs, {len(code_documents)} code"
            )

            # Clean up existing stores
            self._cleanup_existing_stores()

            # Create documentation vector store
            if doc_documents:
                self.logger.info(
                    f"Creating documentation vector store with {len(doc_documents)} documents"
                )
                doc_store = Chroma.from_documents(
                    documents=doc_documents,
                    embedding=self.doc_embeddings,
                    persist_directory=self.doc_store_path,
                )
                doc_store.persist()
                self.doc_vector_store = doc_store

            # Create code vector store
            if code_documents:
                self.logger.info(
                    f"Creating code vector store with {len(code_documents)} documents"
                )
                code_store = Chroma.from_documents(
                    documents=code_documents,
                    embedding=self.code_embeddings,
                    persist_directory=self.code_store_path,
                )
                code_store.persist()
                self.code_vector_store = code_store

            self.logger.info("Successfully created dual vector stores")
            return True

        except Exception as e:
            self.logger.error(f"Failed to create dual vector stores: {e}")
            return False

    def _cleanup_existing_stores(self):
        """Clean up existing vector stores"""
        for store in [self.code_vector_store, self.doc_vector_store]:
            if store is not None:
                try:
                    del store
                except:
                    pass

        self.code_vector_store = None
        self.doc_vector_store = None
        gc.collect()
        time.sleep(0.5)

    def search_similar(self, query: str, k: int = None) -> List[Document]:
        """Search both stores and combine results with boosting for exact matches"""
        if k is None:
            k = self.config.retrieval_k

        # Split k between documentation and code
        doc_k = max(1, k // 2)  # At least 1 for docs
        code_k = k - doc_k

        results = []

        # Search documentation store
        try:
            doc_store = self.get_doc_vector_store()
            doc_results = doc_store.similarity_search(query, k=doc_k)
            results.extend(doc_results)
            self.logger.info(f"Found {len(doc_results)} documentation results")
        except Exception as e:
            self.logger.warning(f"Documentation search failed: {e}")

        # Search code store with enhanced matching using multiple strategies
        try:
            code_store = self.get_code_vector_store()

            # Strategy 1: Similarity search with original query
            similarity_results = code_store.similarity_search(query, k=30)

            # Strategy 2: Keyword-based search for exact filename matches
            keyword_results = self._get_exact_filename_matches(query, code_store)

            # Combine and deduplicate results
            all_results = similarity_results + keyword_results
            seen_sources = set()
            unique_results = []
            for doc in all_results:
                source = doc.metadata.get("source", "")
                if source not in seen_sources:
                    unique_results.append(doc)
                    seen_sources.add(source)

            # Apply boosting for exact matches
            boosted_results = self._boost_exact_matches(query, unique_results)
            results.extend(boosted_results[:code_k])

            self.logger.info(
                f"Found {len(boosted_results[:code_k])} code results (similarity: {len(similarity_results)}, keyword: {len(keyword_results)})"
            )
        except Exception as e:
            self.logger.warning(f"Code search failed: {e}")

        self.logger.info(
            f"Dual-store search returned {len(results)} total results for: {query[:50]}..."
        )
        return results[:k]

    def _boost_exact_matches(
        self, query: str, results: List[Document]
    ) -> List[Document]:
        """Boost documents that have exact filename matches for transformation queries"""
        if not results:
            return results

        # Create query-to-filename mappings for transformations
        query_lower = query.lower()
        filename_mappings = {
            "module name": ["xform_module_name", "module_name"],
            "signal width": ["xform_change_signal_width", "signal_width"],
            "reg to wire": ["xform_reg_to_wire", "reg_to_wire"],
            "wire to reg": ["xform_wire_to_reg", "wire_to_reg"],
            "enable signal": ["xform_add_enable_signal", "enable_signal"],
            "reset condition": ["xform_change_reset_condition", "reset_condition"],
            "port rename": ["xform_rename_port", "rename_port"],
            "port name": ["xform_rename_port", "rename_port"],
        }

        # Find matching transformation terms
        boost_terms = []
        for phrase, terms in filename_mappings.items():
            if phrase in query_lower:
                boost_terms.extend(terms)

        # Score each document
        scored_docs = []
        for doc in results:
            score = 0.0
            source = doc.metadata.get("source", "").lower()
            filename = (
                source.split("/")[-1] if "/" in source else source.split("\\")[-1]
            )

            # Very high boost for exact filename matches
            for term in boost_terms:
                if term in filename:
                    score += 1000.0  # Extremely high score for exact matches
                    self.logger.info(f"EXACT MATCH BOOST: {filename} matches {term}")

            # High boost for partial filename matches
            query_words = query_lower.split()
            for word in query_words:
                if len(word) > 3 and word in filename:  # Skip short words
                    score += 100.0

            # Content-based scoring (much lower priority)
            content = doc.page_content.lower()
            for word in query_words:
                if len(word) > 3 and word in content:
                    score += 5.0

            scored_docs.append((score, doc))

        # Sort by score (descending) and return documents
        scored_docs.sort(key=lambda x: x[0], reverse=True)

        # Log top matches for debugging
        if scored_docs:
            top_matches = [
                (score, doc.metadata.get("source", "unknown")[-40:])
                for score, doc in scored_docs[:5]
            ]
            self.logger.info(f"Top boosted code matches for '{query}': {top_matches}")

        return [doc for score, doc in scored_docs]

    def _get_exact_filename_matches(self, query: str, vector_store) -> List[Document]:
        """Get documents that match exact filename patterns for transformations"""
        query_lower = query.lower()

        # Map queries to specific filename patterns
        filename_patterns = {
            "module name": ["xform_module_name"],
            "signal width": ["xform_change_signal_width"],
            "reg to wire": ["xform_reg_to_wire"],
            "wire to reg": ["xform_wire_to_reg"],
            "enable signal": ["xform_add_enable_signal"],
            "reset condition": ["xform_change_reset_condition"],
            "port rename": ["xform_rename_port"],
            "port name": ["xform_rename_port"],
        }

        # Find matching patterns
        target_patterns = []
        for phrase, patterns in filename_patterns.items():
            if phrase in query_lower:
                target_patterns.extend(patterns)

        if not target_patterns:
            return []

        # Get all documents and filter by filename
        try:
            all_docs = vector_store.similarity_search("", k=300)  # Get all docs
            matching_docs = []

            for doc in all_docs:
                source = doc.metadata.get("source", "").lower()
                filename = (
                    source.split("/")[-1] if "/" in source else source.split("\\")[-1]
                )

                for pattern in target_patterns:
                    if pattern in filename:
                        matching_docs.append(doc)
                        self.logger.info(
                            f"Exact filename match: {filename} for pattern '{pattern}'"
                        )
                        break

            return matching_docs

        except Exception as e:
            self.logger.warning(f"Exact filename search failed: {e}")
            return []

    def _is_documentation(self, doc: Document) -> bool:
        """Check if document is documentation"""
        source = doc.metadata.get("source", "").lower()
        return any(
            doc_type in source
            for doc_type in ["documentation", ".md", "pyverilog_docs", "patterns"]
        )

    def get_retriever(self):
        """Get a retriever that searches both stores"""
        return DualRetriever(self)
