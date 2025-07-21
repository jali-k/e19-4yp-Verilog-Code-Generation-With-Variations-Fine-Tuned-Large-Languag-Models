#!/usr/bin/env python3
"""
Code generation using RAG pipeline for Verilog transformations
"""

import logging
import os
import json
from datetime import datetime
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

        # Create output directory for saving context data
        self.output_dir = os.path.join("generated", "context_data")
        os.makedirs(self.output_dir, exist_ok=True)

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
        """Generate a transformation script based on user request with focused approach"""
        self.logger.info(f"Generating transformation for: {user_request}")

        try:
            # Get search results from vector store
            search_results = self._get_search_results(user_request)

            # Identify the best matching xform
            best_xform = self._identify_best_xform(search_results, user_request)

            # Filter and organize context
            focused_context = self._create_focused_context(
                search_results, best_xform, user_request
            )

            # Save context data for inspection
            context_file = self._save_context_data(
                user_request, search_results, focused_context
            )

            # Generate code using focused prompt
            generated_code = self._generate_with_focused_prompt(
                user_request, focused_context
            )

            # Create filename from request
            filename = self._create_filename(user_request)

            response = {
                "success": True,
                "code": generated_code,
                "filename": filename,
                "user_request": user_request,
                "best_xform": best_xform,
                "context_file": context_file,
                "search_results_count": len(search_results),
            }

            self.logger.info(f"Generated transformation script: {filename}")
            return response

        except Exception as e:
            self.logger.error(f"Error generating transformation: {e}")
            return {"success": False, "error": str(e), "user_request": user_request}

    def _get_search_results(self, user_request: str) -> List[Document]:
        """Get search results from vector store"""
        if hasattr(self.vector_store_manager, "search_similar"):
            # For dual vector store
            return self.vector_store_manager.search_similar(user_request, k=10)
        else:
            # For single vector store
            retriever = self.vector_store_manager.get_retriever()
            return retriever.get_relevant_documents(user_request)

    def _identify_best_xform(
        self, search_results: List[Document], user_request: str
    ) -> str:
        """Identify the best matching xform file from search results"""
        xform_files = []

        for doc in search_results:
            if hasattr(doc, "metadata") and "source" in doc.metadata:
                source = doc.metadata["source"]
                if "xform_" in source and source.endswith(".py"):
                    # Extract just the filename
                    filename = os.path.basename(source)
                    xform_files.append(filename)

        if not xform_files:
            return "No specific xform identified"

        # Return the first (highest scored) xform file
        best_xform = xform_files[0]
        self.logger.info(f"Best matching xform identified: {best_xform}")
        return best_xform

    def _create_focused_context(
        self, search_results: List[Document], best_xform: str, user_request: str
    ) -> Dict[str, Any]:
        """Create focused context prioritizing the best xform and relevant docs"""
        context = {
            "primary_xform": None,
            "supporting_docs": [],
            "other_xforms": [],
            "user_request": user_request,
            "best_xform_file": best_xform,
        }

        for doc in search_results:
            content = doc.page_content
            source = doc.metadata.get("source", "") if hasattr(doc, "metadata") else ""

            # Categorize the document
            if best_xform in source:
                context["primary_xform"] = {
                    "content": content,
                    "source": source,
                    "type": "primary_xform",
                }
            elif any(
                doc_type in source.lower()
                for doc_type in ["pattern", "framework", "ast", "guide"]
            ):
                context["supporting_docs"].append(
                    {"content": content, "source": source, "type": "documentation"}
                )
            elif "xform_" in source and source.endswith(".py"):
                context["other_xforms"].append(
                    {
                        "content": content[:500] + "...",  # Truncate other xforms
                        "source": source,
                        "type": "supporting_xform",
                    }
                )

        return context

    def _save_context_data(
        self,
        user_request: str,
        search_results: List[Document],
        focused_context: Dict[str, Any],
    ) -> str:
        """Save all context data for inspection"""
        timestamp = datetime.now().strftime("%H%M%S")

        # Create safe filename from request
        safe_request = "".join(
            c if c.isalnum() or c in " -_" else "" for c in user_request
        )
        safe_request = "_".join(safe_request.split())[:50]

        context_filename = f"context_{timestamp}_{safe_request}.json"
        context_path = os.path.join(self.output_dir, context_filename)

        # Prepare data for saving
        save_data = {
            "timestamp": datetime.now().isoformat(),
            "user_request": user_request,
            "search_results_count": len(search_results),
            "raw_search_results": [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata if hasattr(doc, "metadata") else {},
                    "source": (
                        doc.metadata.get("source", "unknown")
                        if hasattr(doc, "metadata")
                        else "unknown"
                    ),
                }
                for doc in search_results
            ],
            "focused_context": focused_context,
        }

        with open(context_path, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Context data saved to: {context_path}")
        return context_path

    def _generate_with_focused_prompt(
        self, user_request: str, focused_context: Dict[str, Any]
    ) -> str:
        """Generate code using focused prompt with prioritized context"""

        # Build focused prompt
        prompt_parts = []

        # Start with the primary xform
        if focused_context["primary_xform"]:
            prompt_parts.append("=== PRIMARY REFERENCE XFORM (HIGHEST PRIORITY) ===")
            prompt_parts.append(f"File: {focused_context['primary_xform']['source']}")
            prompt_parts.append(focused_context["primary_xform"]["content"])
            prompt_parts.append("")

        # Add supporting documentation
        if focused_context["supporting_docs"]:
            prompt_parts.append("=== SUPPORTING DOCUMENTATION ===")
            for doc in focused_context["supporting_docs"][:2]:  # Limit to 2 docs
                prompt_parts.append(f"Source: {doc['source']}")
                prompt_parts.append(doc["content"][:800] + "...")  # Truncate long docs
                prompt_parts.append("")

        # Add other xforms as secondary reference
        if focused_context["other_xforms"]:
            prompt_parts.append("=== SECONDARY REFERENCE XFORMS ===")
            for xform in focused_context["other_xforms"][:2]:  # Limit to 2 xforms
                prompt_parts.append(f"File: {xform['source']}")
                prompt_parts.append(xform["content"])
                prompt_parts.append("")

        context_text = "\n".join(prompt_parts)

        # Create focused prompt template
        template = """You are an expert at generating Python scripts for Verilog code transformations using PyVerilog.

{context}

USER REQUEST: {question}

CRITICAL INSTRUCTIONS:
1. FOCUS PRIMARILY on the "PRIMARY REFERENCE XFORM" above - this is your main template
2. The PRIMARY XFORM is the best match for the user's request - follow its pattern closely
3. Use supporting documentation for understanding PyVerilog concepts
4. Secondary xforms are for additional reference only - don't mix their functionality

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
- Create a visitor class for AST analysis (follow PRIMARY XFORM pattern)
- Implement transformation function using regex (adapt PRIMARY XFORM logic)
- Include complete main() function with argument parsing
- Add proper error handling throughout

Generate ONLY the Python script code, no explanations. Focus on the specific transformation requested."""

        # Use LLM directly instead of QA chain for more control
        llm = self.llm_manager.get_llm()
        prompt = template.format(context=context_text, question=user_request)

        result = llm.invoke(prompt)
        return result

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
