#!/usr/bin/env python3
"""
Document processing with code-aware chunking for Verilog transformations
"""

import logging
from typing import List
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.schema import Document

from .config import RAGConfig


class DocumentProcessor:
    """Process xform files and documentation with intelligent chunking"""

    def __init__(self, config: RAGConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.text_splitter = self._create_code_splitter()

    def _create_code_splitter(self) -> RecursiveCharacterTextSplitter:
        """Create a text splitter optimized for Python code"""
        return RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            separators=[
                "\n\nclass ",  # Class definitions
                "\n\ndef ",  # Function definitions
                "\n\n#!/usr/bin/env python3",  # Script headers
                '\n\n"""',  # Docstring blocks
                "\n\n# ",  # Major comment sections
                "\n\n",  # Double newlines
                "\n",  # Single newlines
                " ",  # Spaces
            ],
            keep_separator=True,  # Keep separators for context
        )

    def load_all_documents(self) -> List[Document]:
        """Load and process all xform files and documentation"""
        self.logger.info("Loading all documents for the RAG pipeline")

        documents = []

        # Load xform example files
        xform_docs = self._load_xform_files()
        documents.extend(xform_docs)

        # Load documentation files
        doc_files = self._load_documentation_files()
        documents.extend(doc_files)

        # Split all documents into chunks
        split_docs = self.text_splitter.split_documents(documents)

        # Add chunk metadata
        for i, doc in enumerate(split_docs):
            doc.metadata["chunk_id"] = i
            doc.metadata["chunk_type"] = self._classify_chunk(doc.page_content)

        self.logger.info(
            f"Created {len(split_docs)} chunks from {len(documents)} documents"
        )
        return split_docs

    def _load_xform_files(self) -> List[Document]:
        """Load all xform Python files"""
        self.logger.info(f"Loading xform files from {self.config.xform_examples_dir}")

        documents = []
        python_files = list(self.config.xform_examples_dir.glob("*.py"))

        for file_path in python_files:
            try:
                loader = TextLoader(str(file_path), encoding="utf-8")
                file_docs = loader.load()

                # Enhance metadata
                for doc in file_docs:
                    doc.metadata.update(
                        {
                            "source_type": "xform_example",
                            "filename": file_path.name,
                            "category": self._classify_xform_file(file_path.name),
                        }
                    )

                documents.extend(file_docs)
                self.logger.info(f"Loaded xform file: {file_path.name}")

            except Exception as e:
                self.logger.error(f"Error loading {file_path}: {e}")

        return documents

    def _load_documentation_files(self) -> List[Document]:
        """Load documentation files"""
        self.logger.info(f"Loading documentation from {self.config.documentation_dir}")

        documents = []

        if not self.config.documentation_dir.exists():
            self.logger.warning("Documentation directory not found")
            return documents

        # Load markdown and text files
        doc_patterns = ["*.md", "*.txt"]

        for pattern in doc_patterns:
            for file_path in self.config.documentation_dir.glob(pattern):
                try:
                    loader = TextLoader(str(file_path), encoding="utf-8")
                    file_docs = loader.load()

                    # Enhance metadata
                    for doc in file_docs:
                        doc.metadata.update(
                            {
                                "source_type": "documentation",
                                "filename": file_path.name,
                                "doc_category": self._classify_doc_file(file_path.name),
                            }
                        )

                    documents.extend(file_docs)
                    self.logger.info(f"Loaded documentation: {file_path.name}")

                except Exception as e:
                    self.logger.error(f"Error loading {file_path}: {e}")

        return documents

    def _classify_xform_file(self, filename: str) -> str:
        """Classify xform file by type"""
        if "framework" in filename:
            return "framework"
        elif "registry" in filename:
            return "registry"
        elif "signal" in filename or "wire" in filename or "reg" in filename:
            return "signal_transformation"
        elif "module" in filename:
            return "module_transformation"
        elif "port" in filename:
            return "port_transformation"
        else:
            return "general_transformation"

    def _classify_doc_file(self, filename: str) -> str:
        """Classify documentation file by type"""
        if "ast" in filename.lower():
            return "ast_reference"
        elif "parser" in filename.lower():
            return "parser_guide"
        elif "pattern" in filename.lower():
            return "patterns"
        elif "setup" in filename.lower():
            return "setup_guide"
        else:
            return "general_documentation"

    def _classify_chunk(self, content: str) -> str:
        """Classify a chunk by its content"""
        content_lower = content.lower()

        if "class " in content_lower and "def " in content_lower:
            return "class_definition"
        elif "def " in content_lower:
            return "function_definition"
        elif "import " in content_lower:
            return "imports"
        elif '"""' in content or "'''" in content:
            return "documentation"
        elif "#" in content and len(content.split("\n")) < 5:
            return "comments"
        else:
            return "code_block"

    def get_stats(self) -> dict:
        """Get processing statistics"""
        xform_files = len(list(self.config.xform_examples_dir.glob("*.py")))
        doc_files = len(list(self.config.documentation_dir.glob("*.md"))) + len(
            list(self.config.documentation_dir.glob("*.txt"))
        )

        return {
            "xform_files": xform_files,
            "documentation_files": doc_files,
            "total_source_files": xform_files + doc_files,
        }
