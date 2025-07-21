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
from .pattern_library import PatternLibrary
from .progressive_retrieval import ProgressiveRetrievalManager


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

        # Initialize pattern-guided components
        self.pattern_library = PatternLibrary()
        self.progressive_retrieval = ProgressiveRetrievalManager(
            self.vector_store_manager, self.pattern_library
        )

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
        """Create an enhanced prompt for transformation generation with pattern extraction"""

        template = """You are an expert at generating Python scripts for Verilog code transformations using PyVerilog.

TRANSFORMATION STRATEGY:
{transformation_strategy}

REFERENCE EXAMPLES:
{context}

USER REQUEST: {question}

APPROACH:
1. ANALYZE the transformation strategy above to understand the pattern
2. ADAPT the pattern to the specific requirements in the user request
3. USE the reference examples as templates for implementation details
4. APPLY the transformation logic to handle the specific case requested

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

CRITICAL: Focus on adapting the transformation strategy to the user's specific request, even if the exact keywords differ from the examples.

Generate ONLY the Python script code, no explanations."""

        return PromptTemplate(
            template=template,
            input_variables=["context", "question", "transformation_strategy"],
        )

    def generate_xform(self, user_request: str) -> Dict[str, Any]:
        """Generate transformation script using Pattern-Guided Progressive Retrieval"""
        self.logger.info(f"Generating transformation for: {user_request}")

        try:
            # Use progressive retrieval for enhanced context
            enhanced_context = self.progressive_retrieval.progressive_retrieve(
                user_request
            )

            # Generate code using pattern-guided approach
            generated_code = self._generate_with_pattern_guidance(
                user_request, enhanced_context
            )

            # Save enhanced context for inspection
            context_file = self._save_enhanced_context_data(
                user_request, enhanced_context
            )

            # Create filename from request
            filename = self._create_filename(user_request)

            response = {
                "success": True,
                "code": generated_code,
                "filename": filename,
                "user_request": user_request,
                "best_xform": enhanced_context["best_xform"],
                "transformation_type": enhanced_context["transformation_type"],
                "context_file": context_file,
                "enhancement_stage": enhanced_context["enhancement_stage"],
                "total_examples": enhanced_context["total_examples"],
            }

            self.logger.info(f"Generated transformation script: {filename}")
            return response

        except Exception as e:
            self.logger.error(f"Error generating transformation: {e}")
            return {"success": False, "error": str(e), "user_request": user_request}

    def _generate_with_pattern_guidance(
        self, user_request: str, enhanced_context: Dict[str, Any]
    ) -> str:
        """Generate code using pattern-guided approach with quality focus"""

        # Create pattern-guided prompt
        prompt = self._create_pattern_guided_prompt(user_request, enhanced_context)

        # Generate using LLM
        llm = self.llm_manager.get_llm()
        result = llm.invoke(prompt)

        return result

    def _create_pattern_guided_prompt(
        self, user_request: str, enhanced_context: Dict[str, Any]
    ) -> str:
        """Create enhanced prompt with pattern guidance"""

        prompt_parts = []

        # Header with explicit quality requirements
        prompt_parts.append(
            """You are an expert at generating PRODUCTION-QUALITY Python scripts for Verilog transformations using PyVerilog.

CRITICAL QUALITY REQUIREMENTS:
- Generate PRODUCTION-QUALITY code that handles real-world Verilog complexity
- Use flexible constructors with optional parameters and comprehensive state tracking  
- Implement defensive programming with proper null checks and attribute validation
- Apply sophisticated regex patterns with proper escaping and width preservation
- Include comprehensive error handling with specific user feedback
- Follow the exact architectural patterns shown in HIGH-QUALITY examples

"""
        )

        # Add transformation type and quality guidelines
        transformation_type = enhanced_context["transformation_type"]
        quality_guidelines = enhanced_context["quality_guidelines"]

        prompt_parts.append(f"TRANSFORMATION TYPE: {transformation_type.upper()}\n")
        prompt_parts.append("QUALITY GUIDELINES:")
        for aspect, guideline in quality_guidelines.items():
            prompt_parts.append(f"- {guideline}")
        prompt_parts.append("")

        # Add anti-patterns to avoid
        prompt_parts.append("ANTI-PATTERNS TO AVOID:")
        for anti_pattern in enhanced_context["anti_patterns"]:
            prompt_parts.append(f"- {anti_pattern}")
        prompt_parts.append("")

        # Add pattern templates
        relevant_patterns = enhanced_context["relevant_patterns"]
        prompt_parts.append("=== REQUIRED PATTERN TEMPLATES ===")

        for pattern in relevant_patterns:
            # Format pattern with transformation-specific details
            pattern_kwargs = self._get_pattern_kwargs(transformation_type, user_request)
            formatted_pattern = self.pattern_library.format_pattern_for_prompt(
                pattern, **pattern_kwargs
            )
            prompt_parts.append(formatted_pattern)

        # Add primary high-quality example
        if enhanced_context["primary_example"]:
            prompt_parts.append("=== PRIMARY HIGH-QUALITY EXAMPLE ===")
            primary = enhanced_context["primary_example"]
            if hasattr(primary, "metadata") and "source" in primary.metadata:
                prompt_parts.append(f"Source: {primary.metadata['source']}")
            prompt_parts.append(primary.page_content)
            prompt_parts.append("")

        # Add supporting examples
        if enhanced_context["supporting_examples"]:
            prompt_parts.append("=== SUPPORTING EXAMPLES ===")
            for i, example in enumerate(enhanced_context["supporting_examples"][:2]):
                if hasattr(example, "metadata") and "source" in example.metadata:
                    prompt_parts.append(f"Example {i+1}: {example.metadata['source']}")
                prompt_parts.append(example.page_content[:800] + "...")
                prompt_parts.append("")

        # Add the user request
        prompt_parts.append(f"USER REQUEST: {user_request}")
        prompt_parts.append("")

        # Add generation instructions
        prompt_parts.append(
            """GENERATION APPROACH:
1. ANALYZE the user request and identify the specific transformation needed
2. APPLY the required pattern templates above - use them as your structural foundation
3. ADAPT the high-quality examples to match the user's specific requirements
4. ENSURE all quality guidelines are followed and anti-patterns are avoided
5. GENERATE complete, production-ready code that handles edge cases

SCRIPT STRUCTURE (MANDATORY):
- Start with #!/usr/bin/env python3 and proper docstring
- Import ALL necessary modules (sys, os, re, argparse, PyVerilog)
- Create visitor class using DEFENSIVE_AST_VISITOR pattern with flexible constructor
- Implement transformation function using SOPHISTICATED_REGEX pattern
- Include COMPREHENSIVE_ERROR_HANDLING with specific messages
- Add ROBUST_ARGUMENT_PARSER with proper validation
- Return True/False for success/failure in main function

Generate ONLY the complete Python script code, no explanations or comments outside the code."""
        )

        return "\n".join(prompt_parts)

    def _get_pattern_kwargs(
        self, transformation_type: str, user_request: str
    ) -> Dict[str, str]:
        """Get pattern template arguments based on transformation type"""
        request_lower = user_request.lower()

        if transformation_type == "data_type":
            # Detect source and target types
            if "wire" in request_lower and "reg" in request_lower:
                if request_lower.find("wire") < request_lower.find("reg"):
                    source, target = "wire", "reg"
                else:
                    source, target = "reg", "wire"
            elif "wire" in request_lower and "int" in request_lower:
                source, target = "wire", "int"
            elif "reg" in request_lower and "wire" in request_lower:
                source, target = "reg", "wire"
            else:
                source, target = "reg", "wire"  # Default

            return {
                "target": source,
                "NodeType": source.capitalize(),
                "source": source,
                "target": target,
                "type": source,
                "source_type": source,
                "function_name": f"transform_{source}_to_{target}",
                "description": f"Transform {source} variables to {target}",
                "pattern_specific_logic": f"""# Store information about the {source} declaration
                            width = ""
                            if item.width:
                                msb = item.width.msb.value
                                lsb = item.width.lsb.value
                                width = f"[{{msb}}:{{lsb}}] "

                            self.{source}_declarations.append(
                                {{"name": item.name, "width": width}}
                            )
                            self.changes_made.append(
                                f"Changed '{{item.name}}' from '{source}' to '{target}'"
                            )""",
            }
        else:
            # Generic fallback
            return {
                "target": "signal",
                "NodeType": "Signal",
                "source": "signal",
                "target": "modified_signal",
                "type": "signal",
                "source_type": "signal",
                "function_name": "transform_signal",
                "description": "Transform signal",
                "pattern_specific_logic": "# Pattern-specific logic here",
            }

    def _save_enhanced_context_data(
        self, user_request: str, enhanced_context: Dict[str, Any]
    ) -> str:
        """Save enhanced context data for inspection"""
        timestamp = datetime.now().strftime("%H%M%S")

        # Create safe filename
        safe_request = "".join(
            c if c.isalnum() or c in " -_" else "" for c in user_request
        )
        safe_request = "_".join(safe_request.split())[:50]

        context_filename = f"enhanced_context_{timestamp}_{safe_request}.json"
        context_path = os.path.join(self.output_dir, context_filename)

        # Prepare serializable data
        save_data = {
            "timestamp": datetime.now().isoformat(),
            "user_request": user_request,
            "transformation_type": enhanced_context["transformation_type"],
            "best_xform": enhanced_context["best_xform"],
            "enhancement_stage": enhanced_context["enhancement_stage"],
            "total_examples": enhanced_context["total_examples"],
            "quality_guidelines": enhanced_context["quality_guidelines"],
            "anti_patterns": enhanced_context["anti_patterns"],
            "pattern_count": len(enhanced_context["relevant_patterns"]),
            "pattern_names": [p.name for p in enhanced_context["relevant_patterns"]],
            "has_primary_example": enhanced_context["primary_example"] is not None,
            "supporting_examples_count": len(enhanced_context["supporting_examples"]),
            "pattern_examples_count": len(enhanced_context["pattern_examples"]),
        }

        with open(context_path, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Enhanced context saved to: {context_path}")
        return context_path

    def _identify_best_xform(
        self, search_results: List[Document], user_request: str
    ) -> str:
        """Identify the best matching xform file from search results"""
        xform_files = []

        # First, check for complementary transformations
        complement_xform = self._find_complementary_xform(search_results, user_request)
        if complement_xform:
            self.logger.info(f"Found complementary transformation: {complement_xform}")
            return complement_xform

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

    def _find_complementary_xform(
        self, search_results: List[Document], user_request: str
    ) -> str:
        """Find complementary transformation in search results"""

        query_lower = user_request.lower()

        # Define what to look for based on user request
        complementary_mapping = {
            "wire to reg": "reg_to_wire",
            "reg to wire": "wire_to_reg",
            "input to output": "output_to_input",
            "output to input": "input_to_output",
        }

        for request_pattern, target_file_pattern in complementary_mapping.items():
            if request_pattern in query_lower:
                # Look for the complementary xform in search results
                for doc in search_results:
                    if hasattr(doc, "metadata") and "source" in doc.metadata:
                        source = doc.metadata["source"]
                        filename = os.path.basename(source)

                        if (
                            target_file_pattern in filename
                            and "xform_" in filename
                            and filename.endswith(".py")
                        ):
                            return filename

        return None  # No complementary transformation found

    def _extract_transformation_strategy(
        self, search_results: List[Document], user_request: str
    ) -> str:
        """Extract general transformation strategy from retrieved examples"""

        # Analyze user request to understand transformation type
        request_lower = user_request.lower()

        # Common transformation patterns and their strategies
        transformation_patterns = {
            "wire.*reg|reg.*wire": {
                "pattern": "Data Type Transformation",
                "strategy": """
TRANSFORMATION PATTERN: Change Verilog data type declarations
- ANALYZE: Find declarations of one data type (wire/reg/logic/int)
- TRANSFORM: Replace with target data type while preserving signal names and widths
- METHOD: Use regex to match type declarations and substitute type keywords
- PRESERVE: Signal names, bit widths, array dimensions, and initialization values
- EXAMPLE: 'wire [7:0] signal;' becomes 'reg [7:0] signal;'
                """,
            },
            "input.*output|output.*input": {
                "pattern": "Port Direction Transformation",
                "strategy": """
TRANSFORMATION PATTERN: Change module port directions
- ANALYZE: Find port declarations in module headers
- TRANSFORM: Replace input/output keywords while maintaining port structure
- METHOD: Use regex to match port declarations and substitute direction keywords
- PRESERVE: Port names, data types, bit widths, and port ordering
- EXAMPLE: 'input wire [7:0] data' becomes 'output wire [7:0] data'
                """,
            },
            "width|bit": {
                "pattern": "Signal Width Transformation",
                "strategy": """
TRANSFORMATION PATTERN: Modify signal bit widths
- ANALYZE: Find signal declarations with bit width specifications
- TRANSFORM: Replace bit width values while preserving signal structure  
- METHOD: Use regex to match width patterns like [7:0] and substitute values
- PRESERVE: Signal names, data types, and other attributes
- EXAMPLE: 'wire [7:0] signal' becomes 'wire [15:0] signal'
                """,
            },
            "module.*name|name.*module": {
                "pattern": "Module Name Transformation",
                "strategy": """
TRANSFORMATION PATTERN: Change module names
- ANALYZE: Find module declarations and instantiations
- TRANSFORM: Replace module name while updating all references
- METHOD: Use regex to find module declarations and all instantiations
- PRESERVE: Module structure, ports, and internal logic
- EXAMPLE: 'module counter' becomes 'module timer' (with all instances updated)
                """,
            },
        }

        # Find matching pattern
        for pattern_regex, pattern_info in transformation_patterns.items():
            import re

            if re.search(pattern_regex, request_lower):
                self.logger.info(
                    f"Detected transformation pattern: {pattern_info['pattern']}"
                )
                return pattern_info["strategy"]

        # Fallback: extract strategy from best matching example
        return self._extract_strategy_from_examples(search_results, user_request)

    def _extract_strategy_from_examples(
        self, search_results: List[Document], user_request: str
    ) -> str:
        """Extract transformation strategy from best matching examples"""

        # Find the best code example
        best_example = None
        for doc in search_results:
            if hasattr(doc, "metadata") and "source" in doc.metadata:
                source = doc.metadata["source"]
                if "xform_" in source and source.endswith(".py"):
                    best_example = doc.page_content
                    break

        if not best_example:
            return """
GENERAL TRANSFORMATION PATTERN: Modify Verilog code structure
- ANALYZE: Use PyVerilog AST to understand code structure and find target elements
- TRANSFORM: Apply regex-based replacements to modify specific code patterns
- METHOD: Combine AST analysis for accuracy with regex for text manipulation
- PRESERVE: Overall code structure and functionality while making targeted changes
            """

        # Extract key patterns from the example (simplified analysis)
        strategy_lines = []
        lines = best_example.split("\n")

        # Look for comments that explain the transformation
        for line in lines:
            line = line.strip()
            if line.startswith("#") and any(
                keyword in line.lower()
                for keyword in ["transform", "change", "replace", "modify"]
            ):
                strategy_lines.append(line[1:].strip())

        if strategy_lines:
            strategy = "EXTRACTED TRANSFORMATION STRATEGY:\n" + "\n".join(
                f"- {line}" for line in strategy_lines
            )
        else:
            strategy = """
DERIVED TRANSFORMATION PATTERN: Based on retrieved examples
- ANALYZE: Use PyVerilog AST to parse and understand the Verilog code structure
- IDENTIFY: Locate the specific elements that need to be transformed
- TRANSFORM: Apply appropriate modifications using regex pattern matching
- PRESERVE: Code functionality while making the requested structural changes
            """

        return strategy

    def _create_focused_context(
        self, search_results: List[Document], best_xform: str, user_request: str
    ) -> Dict[str, Any]:
        """Create focused context with smart filtering based on match confidence"""
        context = {
            "primary_xform": None,
            "supporting_docs": [],
            "other_xforms": [],
            "user_request": user_request,
            "best_xform_file": best_xform,
            "filtering_strategy": "none",
        }

        # Calculate match confidence and determine filtering strategy
        best_match_score = self._get_best_match_score(search_results, best_xform)
        filtering_strategy = self._determine_filtering_strategy(
            best_match_score, user_request
        )
        context["filtering_strategy"] = filtering_strategy
        context["best_match_score"] = best_match_score

        self.logger.info(
            f"Best match score: {best_match_score}, Filtering strategy: {filtering_strategy}"
        )

        for doc in search_results:
            content = doc.page_content
            source = doc.metadata.get("source", "") if hasattr(doc, "metadata") else ""

            # Categorize the document
            source_filename = os.path.basename(source)
            if best_xform == source_filename:
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
                # Apply smart filtering for other xforms
                if self._should_include_other_xform(
                    doc, filtering_strategy, user_request, best_xform
                ):
                    context["other_xforms"].append(
                        {
                            "content": content[:500] + "...",  # Truncate other xforms
                            "source": source,
                            "type": "supporting_xform",
                        }
                    )

        self.logger.info(
            f"Context: primary={bool(context['primary_xform'])}, docs={len(context['supporting_docs'])}, other_xforms={len(context['other_xforms'])}"
        )
        return context

    def _get_best_match_score(
        self, search_results: List[Document], best_xform: str
    ) -> float:
        """Extract the match score for the best xform from search results"""
        # Extract score based on query patterns and best xform matching

        query_lower = (
            self._last_user_request.lower()
            if hasattr(self, "_last_user_request")
            else ""
        )

        # High confidence exact matches
        exact_match_patterns = {
            "reg to wire": 2200,
            "wire to reg": 2200,
            "module name": 2200,
            "signal width": 2200,
            "rename port": 2100,
            "reset condition": 2100,
            "enable signal": 2100,
        }

        for pattern, score in exact_match_patterns.items():
            if (
                pattern in query_lower
                and pattern.replace(" ", "_") in best_xform.lower()
            ):
                return float(score)

        # Check for complementary transformations (inverse operations)
        complementary_score = self._get_complementary_transformation_score(
            query_lower, best_xform
        )
        if complementary_score > 0:
            return float(complementary_score)

        # Medium confidence partial matches
        partial_match_patterns = {
            "width": 1800,
            "port": 1700,
            "module": 1700,
            "signal": 1600,
            "reg": 1500,
            "wire": 1500,
            "reset": 1500,
        }

        for pattern, score in partial_match_patterns.items():
            if pattern in query_lower and pattern in best_xform.lower():
                return float(score)

        # Default moderate score
        return 1200.0

    def _get_complementary_transformation_score(
        self, query_lower: str, best_xform: str
    ) -> float:
        """Detect complementary transformations and assign high confidence scores"""

        # Define complementary transformation pairs with their patterns
        complementary_pairs = {
            # Wire/Reg type conversions
            ("wire to reg", "wire_to_reg"): ("reg to wire", "reg_to_wire"),
            ("reg to wire", "reg_to_wire"): ("wire to reg", "wire_to_reg"),
            # Other potential complementary pairs
            ("input to output", "input_to_output"): (
                "output to input",
                "output_to_input",
            ),
            ("output to input", "output_to_input"): (
                "input to output",
                "input_to_output",
            ),
        }

        for (query_pattern, query_file_pattern), (
            complement_pattern,
            complement_file_pattern,
        ) in complementary_pairs.items():
            # Check if query matches one pattern and best_xform matches its complement
            if (
                query_pattern in query_lower
                and complement_file_pattern in best_xform.lower()
            ):

                self.logger.info(
                    f"Detected complementary transformation: '{query_pattern}' -> '{complement_file_pattern}' "
                    f"in {best_xform}"
                )
                return 2150.0  # High confidence for complementary transformations

        return 0.0  # No complementary match found

    def _determine_filtering_strategy(
        self, best_match_score: float, user_request: str
    ) -> str:
        """Determine filtering strategy based on match confidence and request complexity"""

        # Check for complex multi-transformation requests
        complex_keywords = [
            "and",
            "also",
            "plus",
            "both",
            "multiple",
            "combine",
            "together",
        ]
        is_complex_request = any(
            keyword in user_request.lower() for keyword in complex_keywords
        )

        if is_complex_request:
            return "full"  # Complex requests need multiple examples

        # Simple requests with high confidence - use pure focus
        if best_match_score > 2000:
            return "pure"  # Only primary xform
        elif best_match_score > 1500:
            return "limited"  # Primary + 1-2 most relevant
        else:
            return "full"  # Primary + multiple examples

    def _should_include_other_xform(
        self, doc: Document, filtering_strategy: str, user_request: str, best_xform: str
    ) -> bool:
        """Determine if an other xform should be included based on filtering strategy"""

        if filtering_strategy == "pure":
            return False  # No other xforms for pure focus

        if filtering_strategy == "full":
            return True  # Include all other xforms

        if filtering_strategy == "limited":
            # Only include highly relevant other xforms
            return self._is_highly_relevant_xform(doc, user_request, best_xform)

        return False

    def _is_highly_relevant_xform(
        self, doc: Document, user_request: str, best_xform: str
    ) -> bool:
        """Check if an xform is highly relevant to the request and primary xform"""
        source = doc.metadata.get("source", "") if hasattr(doc, "metadata") else ""
        filename = os.path.basename(source)

        # Get transformation categories
        primary_category = self._get_xform_category(best_xform)
        other_category = self._get_xform_category(filename)

        # Same category transformations are relevant
        if primary_category == other_category and primary_category != "unknown":
            return True

        # Complementary transformations (e.g., reg_to_wire with wire_to_reg)
        complementary_pairs = [
            ("reg_to_wire", "wire_to_reg"),
            ("module_name", "rename_port"),
        ]

        for pair in complementary_pairs:
            if primary_category in pair and other_category in pair:
                return True

        return False

    def _get_xform_category(self, filename: str) -> str:
        """Categorize xform files by their transformation type"""
        if not filename or not filename.startswith("xform_"):
            return "unknown"

        # Extract category from filename
        if "reg_to_wire" in filename or "wire_to_reg" in filename:
            return "signal_type"
        elif "signal_width" in filename or "width" in filename:
            return "signal_width"
        elif "module_name" in filename:
            return "module_name"
        elif "rename_port" in filename or "port" in filename:
            return "port_management"
        elif "reset" in filename:
            return "reset_logic"
        elif "enable" in filename:
            return "enable_signal"
        elif "inside_op" in filename:
            return "inside_operator"
        elif "mda" in filename:
            return "mda_operations"
        else:
            return "other"

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
        self,
        user_request: str,
        focused_context: Dict[str, Any],
        transformation_strategy: str = "",
    ) -> str:
        """Generate code using focused prompt with prioritized context and transformation strategy"""

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

        # Use LLM directly with enhanced prompt template
        llm = self.llm_manager.get_llm()

        # Get the enhanced prompt template
        prompt_template = self._create_prompt_template()
        prompt = prompt_template.format(
            context=context_text,
            question=user_request,
            transformation_strategy=transformation_strategy,
        )

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
