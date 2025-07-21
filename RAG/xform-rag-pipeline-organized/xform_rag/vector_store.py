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

try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma

from .config import RAGConfig
from .embeddings import CodeBERTEmbeddings
from .hybrid_embeddings import HybridEmbeddings
from .document_processor import DocumentProcessor


class VectorStoreManager:
    """Simple vector store management with CodeBERT embeddings"""

    def __init__(self, config: RAGConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Choose embedding strategy
        if config.use_hybrid_embeddings:
            self.logger.info(
                "Using hybrid embeddings (CodeBERT + SentenceTransformers)"
            )
            self.embeddings = HybridEmbeddings()
        else:
            self.logger.info("Using CodeBERT embeddings only")
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
        """Check if vector store exists and has content, prefer most recent timestamped version"""
        # First, try to find the most recent timestamped vector store
        base_dir = self.config.vector_store_dir.parent
        pattern = f"{self.config.vector_store_dir.name}_*"

        timestamped_dirs = []
        for path in base_dir.glob(pattern):
            if path.is_dir() and any(path.iterdir()):
                timestamped_dirs.append(path)

        if timestamped_dirs:
            # Sort by name (timestamp) and use the most recent
            most_recent = sorted(timestamped_dirs)[-1]
            self.logger.info(f"Found timestamped vector store: {most_recent}")
            self.config.vector_store_dir = most_recent
            return True

        # Fallback to original path
        return self.config.vector_store_dir.exists() and any(
            self.config.vector_store_dir.iterdir()
        )

    def search_similar(self, query: str, k: int = None) -> List[Document]:
        """Search for similar documents using dual-track retrieval: documentation + xforms"""
        if k is None:
            k = self.config.retrieval_k

        vector_store = self.get_vector_store()

        # Dual-track approach: get both documentation and xforms separately
        docs_results = self._search_documentation(
            query, k // 2 + 1
        )  # Get ~half for docs
        xform_results = self._search_xforms(query, k // 2 + 1)  # Get ~half for xforms

        # Combine results with documentation first for better context
        combined_results = docs_results + xform_results

        # Limit to requested k
        final_results = combined_results[:k]

        # Log the composition
        doc_count = len([r for r in final_results if self._is_documentation(r)])
        xform_count = len([r for r in final_results if not self._is_documentation(r)])

        self.logger.info(
            f"Dual-track retrieval: {doc_count} docs, {xform_count} xforms"
        )
        self.logger.info(
            f"Found {len(final_results)} similar documents for query: {query[:50]}..."
        )

        return final_results

    def _search_documentation(self, query: str, k: int) -> List[Document]:
        """Search specifically for documentation using keyword filtering + similarity"""
        vector_store = self.get_vector_store()

        # First, get ALL documentation chunks
        all_docs = vector_store.similarity_search("", k=254)  # Get all documents
        doc_chunks = [doc for doc in all_docs if self._is_documentation(doc)]

        if not doc_chunks:
            return []

        # Score documentation chunks based on keyword relevance
        query_lower = query.lower()
        query_terms = query_lower.split()

        scored_docs = []
        for doc in doc_chunks:
            score = self._score_doc_relevance(query_lower, query_terms, doc)
            scored_docs.append((score, doc))

        # Sort by relevance score and return top k
        scored_docs.sort(key=lambda x: x[0], reverse=True)

        # Log for debugging
        if scored_docs:
            self.logger.info(
                f"Top doc scores for '{query}': {[(score, doc.metadata.get('source', '')[-30:]) for score, doc in scored_docs[:3]]}"
            )

        return [doc for score, doc in scored_docs[:k] if score > 0]

    def _score_doc_relevance(
        self, query_lower: str, query_terms: list, doc: Document
    ) -> float:
        """Score documentation relevance based on keyword matching"""
        content_lower = doc.page_content.lower()
        source_lower = doc.metadata.get("source", "").lower()
        score = 0.0

        # High-value keyword mapping for transformation queries
        keyword_boost = {
            "signal": 20,
            "width": 20,
            "transform": 15,
            "pattern": 15,
            "ast": 15,
            "node": 15,
            "pyverilog": 15,
            "visitor": 10,
            "module": 10,
            "wire": 10,
            "reg": 10,
            "port": 10,
            "change": 10,
            "modify": 10,
            "implementation": 10,
        }

        # Score based on query terms
        for term in query_terms:
            if term in content_lower:
                boost = keyword_boost.get(term, 5)
                score += boost

        # Extra scoring for exact phrase matches
        if query_lower in content_lower:
            score += 30

        # Boost documentation about specific transformation patterns
        if "signal width" in query_lower and "signal width" in content_lower:
            score += 50
        if "transformation" in query_lower and "pattern" in content_lower:
            score += 30

        # Source-based scoring
        if "pattern" in source_lower and any(
            term in query_lower for term in ["transform", "pattern", "change"]
        ):
            score += 25
        if "ast" in source_lower and any(
            term in query_lower for term in ["ast", "node", "visitor"]
        ):
            score += 25

        return score

    def _search_xforms(self, query: str, k: int) -> List[Document]:
        """Search specifically for xform examples"""
        vector_store = self.get_vector_store()

        # Search with original query (good for code)
        search_results = vector_store.similarity_search(query, k=k * 3)

        # Filter to only xforms and apply boosting
        xform_results = []
        for doc in search_results:
            if not self._is_documentation(doc):  # Xforms and other code
                xform_results.append(doc)
                if len(xform_results) >= k:
                    break

        # Apply existing boost logic for exact matches
        boosted_xforms = self._boost_exact_matches(query, xform_results)

        return boosted_xforms[:k]

    def _expand_query_for_docs(self, query: str) -> str:
        """Expand query with code-specific terms that appear in documentation"""
        query_lower = query.lower()

        # Map natural language to code/AST terms that appear in docs
        expansions = {
            "traverse": "visit children node pyverilog ast",
            "ast": "node visitor moduledef wire reg port",
            "find": "visitor visit children traverse",
            "module": "moduledef pyverilog ast node",
            "signal": "wire reg port identifier ast node",
            "pattern": "visitor example transform pyverilog",
            "how to": "example visitor pattern traverse",
            "transformation": "ast node visitor pyverilog moduledef example pattern",
            "transform": "ast node visitor pyverilog example",
            "change": "modify ast node visitor pyverilog",
            "width": "signal wire reg port identifier ast",
            "create": "ast node visitor pyverilog example pattern",
            "implement": "ast node visitor pyverilog example pattern",
        }

        expanded_terms = [query]
        for key, expansion in expansions.items():
            if key in query_lower:
                expanded_terms.append(expansion)

        return " ".join(expanded_terms)

    def _find_exact_keyword_matches(self, query: str, k: int) -> List[Document]:
        """Find documentation that contains exact keyword matches from the query"""
        vector_store = self.get_vector_store()

        # Get all documents in the collection for keyword matching
        all_results = vector_store.similarity_search("", k=k * 5)  # Cast a wide net

        # Extract important keywords from query
        query_words = query.lower().split()
        important_keywords = []

        # Look for important technical terms, class names, etc.
        for word in query_words:
            if len(word) > 3 and word not in [  # Skip short words
                "pattern",
                "implementation",
                "how",
                "the",
                "and",
                "for",
                "with",
            ]:
                important_keywords.append(word)

        matched_docs = []
        for doc in all_results:
            if self._is_documentation(doc):  # Only consider documentation
                content_lower = doc.page_content.lower()
                # Check if any important keywords appear in the content
                for keyword in important_keywords:
                    if keyword in content_lower:
                        matched_docs.append(doc)
                        self.logger.debug(
                            f"Found exact match for '{keyword}' in {doc.metadata.get('source', 'unknown')}"
                        )
                        break  # Avoid duplicates

        return matched_docs[:3]  # Limit to top 3 keyword matches

    def _is_documentation(self, doc: Document) -> bool:
        """Check if document is documentation"""
        source = doc.metadata.get("source", "").lower()
        return any(
            doc_type in source
            for doc_type in ["documentation", "pyverilog", "patterns", ".md"]
        )

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
            self.logger.debug(f"Top matches for '{query}': {top_scores}")

            # Also log if we found any module_name related files
            module_name_files = [
                doc
                for score, doc in scored_docs
                if "module_name" in doc.metadata.get("source", "").lower()
            ]
            if module_name_files:
                self.logger.debug(
                    f"Found module_name files: {[doc.metadata.get('source', '') for doc in module_name_files]}"
                )
            else:
                self.logger.debug("No module_name files found in results")

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
