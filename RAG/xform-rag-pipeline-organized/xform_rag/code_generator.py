#!/usr/bin/env python3
"""
Code generation using RAG pipeline for Verilog transformations
"""

import logging
from typing import Dict, Any, List
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_core.retrievers import BaseRetriever
from langchain.schema import Document

from .config import RAGConfig
from .llm_manager import LLMManager
from .vector_store import VectorStoreManager


class CodeGenerator:
    """Generate Verilog transformation code using RAG"""

    def __init__(self, config: RAGConfig, vector_store_manager=None):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.llm_manager = LLMManager(config)

        # Use provided vector store manager or create default
        if vector_store_manager:
            self.vector_store_manager = vector_store_manager
        else:
            self.vector_store_manager = VectorStoreManager(config)

        self.qa_chain = self._create_qa_chain()

    def _create_qa_chain(self):
        """Create the QA chain with optimized prompt"""
        prompt_template = self._create_prompt_template()

        # Get retriever from vector store manager (works for both types)
        retriever = self.vector_store_manager.get_retriever()

        return RetrievalQA.from_chain_type(
            llm=self.llm_manager.get_llm(),
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt_template},
            return_source_documents=True,
        )

    def _create_prompt_template(self) -> PromptTemplate:
        """Create a focused prompt for Verilog transformation generation"""

        template = """You are an expert at generating Python scripts for Verilog code transformations using PyVerilog.

REFERENCE EXAMPLES:
{context}

USER REQUEST: {question}

REQUIREMENTS:
1. Generate a COMPLETE Python script that transforms Verilog code
2. Use PyVerilog AST for ANALYSIS to understand the code structure
3. Use REGEX for ACTUAL MODIFICATIONS to transform the text
4. Include proper argument parsing with argparse
5. Handle errors gracefully with try/except blocks
6. Return True/False for success/failure in main function

SCRIPT STRUCTURE:
- Start with #!/usr/bin/env python3
- Import necessary modules (sys, os, re, argparse, PyVerilog)
- Create a visitor class for AST analysis
- Implement transformation function using regex
- Include complete main() function with argument parsing
- Add proper error handling throughout

Generate ONLY the Python script code, no explanations."""

        return PromptTemplate(
            template=template, input_variables=["context", "question"]
        )

    def generate_xform(self, user_request: str) -> Dict[str, Any]:
        """Generate a transformation script based on user request"""
        self.logger.info(f"Generating transformation for: {user_request}")

        try:
            # Use the QA chain to generate response
            result = self.qa_chain.invoke({"query": user_request})

            # Extract the generated code
            generated_code = result.get("result", "")
            source_docs = result.get("source_documents", [])

            # Create filename from request
            filename = self._create_filename(user_request)

            response = {
                "success": True,
                "code": generated_code,
                "filename": filename,
                "user_request": user_request,
                "source_documents_count": len(source_docs),
                "source_snippets": [
                    doc.page_content[:200] + "..." for doc in source_docs[:3]
                ],
            }

            self.logger.info(f"Generated transformation script: {filename}")
            return response

        except Exception as e:
            self.logger.error(f"Error generating transformation: {e}")
            return {"success": False, "error": str(e), "user_request": user_request}

    def _create_filename(self, user_request: str) -> str:
        """Create a filename based on the user request"""
        # Simple filename generation
        import re

        # Extract key words and create filename
        words = re.findall(r"\b\w+\b", user_request.lower())
        key_words = [
            w
            for w in words
            if len(w) > 2 and w not in ["the", "and", "for", "with", "from", "into"]
        ]

        if not key_words:
            filename = "generated_xform"
        else:
            filename = "_".join(key_words[:4])  # Use first 4 meaningful words

        return f"xform_{filename}.py"
