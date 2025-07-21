#!/usr/bin/env python3
"""
Progressive Retrieval Manager for Pattern-Guided RAG
Implements multi-stage retrieval with pattern-focused context enhancement
"""

import logging
from typing import Dict, List, Any, Tuple
from langchain.schema import Document

from .pattern_library import PatternLibrary, CodePattern


class ProgressiveRetrievalManager:
    """Manages multi-stage progressive retrieval for enhanced code generation"""

    def __init__(self, vector_store_manager, pattern_library: PatternLibrary):
        self.vector_store_manager = vector_store_manager
        self.pattern_library = pattern_library
        self.logger = logging.getLogger(__name__)

    def progressive_retrieve(self, user_request: str) -> Dict[str, Any]:
        """
        Perform progressive retrieval in multiple stages:
        1. General approach retrieval
        2. Pattern-specific retrieval
        3. Quality-focused enhancement
        """

        # Stage 1: General Approach Retrieval
        general_results = self._stage1_general_approach(user_request)

        # Stage 2: Pattern-Specific Retrieval
        pattern_results = self._stage2_pattern_specific(user_request, general_results)

        # Stage 3: Quality Enhancement
        enhanced_context = self._stage3_quality_enhancement(
            user_request, general_results, pattern_results
        )

        return enhanced_context

    def _stage1_general_approach(self, user_request: str) -> Dict[str, Any]:
        """Stage 1: Retrieve general transformation approach"""
        self.logger.info("Stage 1: General approach retrieval")

        # Get basic search results
        if hasattr(self.vector_store_manager, "search_similar"):
            search_results = self.vector_store_manager.search_similar(user_request, k=8)
        else:
            retriever = self.vector_store_manager.get_retriever()
            search_results = retriever.get_relevant_documents(user_request)[:8]

        # Identify best matching transformation
        best_xform = self._identify_best_xform(search_results, user_request)
        transformation_type = self._classify_transformation_type(user_request)

        return {
            "search_results": search_results,
            "best_xform": best_xform,
            "transformation_type": transformation_type,
            "stage": "general_approach",
        }

    def _stage2_pattern_specific(
        self, user_request: str, general_results: Dict
    ) -> Dict[str, Any]:
        """Stage 2: Retrieve pattern-specific examples"""
        self.logger.info("Stage 2: Pattern-specific retrieval")

        transformation_type = general_results["transformation_type"]

        # Get patterns for this transformation type
        relevant_patterns = self.pattern_library.get_patterns_for_transformation_type(
            transformation_type
        )

        # Construct pattern-focused queries
        pattern_queries = self._create_pattern_queries(user_request, relevant_patterns)

        # Retrieve examples for each pattern
        pattern_results = {}
        for pattern_name, query in pattern_queries.items():
            if hasattr(self.vector_store_manager, "search_similar"):
                results = self.vector_store_manager.search_similar(query, k=3)
            else:
                retriever = self.vector_store_manager.get_retriever()
                results = retriever.get_relevant_documents(query)[:3]
            pattern_results[pattern_name] = results

        return {
            "relevant_patterns": relevant_patterns,
            "pattern_queries": pattern_queries,
            "pattern_results": pattern_results,
            "stage": "pattern_specific",
        }

    def _stage3_quality_enhancement(
        self, user_request: str, general_results: Dict, pattern_results: Dict
    ) -> Dict[str, Any]:
        """Stage 3: Quality-focused context enhancement"""
        self.logger.info("Stage 3: Quality enhancement")

        # Get quality guidelines
        quality_guidelines = self.pattern_library.get_quality_guidelines()
        anti_patterns = self.pattern_library.extract_anti_patterns()

        # Filter and prioritize high-quality examples
        high_quality_examples = self._filter_high_quality_examples(
            general_results["search_results"], pattern_results["pattern_results"]
        )

        # Create structured context
        enhanced_context = {
            # Core information
            "user_request": user_request,
            "transformation_type": general_results["transformation_type"],
            "best_xform": general_results["best_xform"],
            # Pattern guidance
            "relevant_patterns": pattern_results["relevant_patterns"],
            "quality_guidelines": quality_guidelines,
            "anti_patterns": anti_patterns,
            # Prioritized examples
            "primary_example": high_quality_examples.get("primary"),
            "supporting_examples": high_quality_examples.get("supporting", []),
            "pattern_examples": high_quality_examples.get("pattern_specific", {}),
            # Context metadata
            "total_examples": len(general_results["search_results"]),
            "enhancement_stage": "quality_focused",
        }

        return enhanced_context

    def _create_pattern_queries(
        self, user_request: str, patterns: List[CodePattern]
    ) -> Dict[str, str]:
        """Create specific queries for pattern retrieval"""
        base_request = user_request.lower()
        pattern_queries = {}

        for pattern in patterns:
            if pattern.category == "constructor":
                query = f"{base_request} constructor __init__ target_variable optional parameter"
            elif pattern.category == "ast_analysis":
                query = f"{base_request} AST visitor hasattr isinstance Node defensive programming"
            elif pattern.category == "width_handling":
                query = f"{base_request} width msb lsb value signal bit range"
            elif pattern.category == "text_transformation":
                query = f"{base_request} regex re.sub re.escape pattern replacement"
            elif pattern.category == "error_handling":
                query = f"{base_request} try except error handling traceback"
            elif pattern.category == "cli_interface":
                query = f"{base_request} argparse main function command line"
            else:
                query = f"{base_request} {pattern.name} {pattern.category}"

            pattern_queries[pattern.name] = query

        return pattern_queries

    def _filter_high_quality_examples(
        self,
        general_results: List[Document],
        pattern_results: Dict[str, List[Document]],
    ) -> Dict[str, Any]:
        """Filter and prioritize high-quality examples"""

        high_quality = {"supporting": [], "pattern_specific": {}}

        # Find primary example (highest quality)
        primary_example = None
        for doc in general_results:
            if self._is_high_quality_example(doc):
                primary_example = doc
                break

        if not primary_example and general_results:
            primary_example = general_results[0]  # Fallback

        high_quality["primary"] = primary_example

        # Filter supporting examples
        for doc in general_results[1:4]:  # Take next 3 as supporting
            if self._is_high_quality_example(doc):
                high_quality["supporting"].append(doc)

        # Filter pattern-specific examples
        for pattern_name, docs in pattern_results.items():
            filtered_docs = [doc for doc in docs if self._is_high_quality_example(doc)]
            if filtered_docs:
                high_quality["pattern_specific"][pattern_name] = filtered_docs[
                    0
                ]  # Best one

        return high_quality

    def _is_high_quality_example(self, doc: Document) -> bool:
        """Determine if an example is high quality"""
        content = doc.page_content.lower()

        # Quality indicators
        quality_indicators = [
            "target_variable",  # Flexible constructor
            "hasattr",  # Defensive programming
            "re.escape",  # Proper regex
            "changes_made",  # State tracking
            "try:",  # Error handling
            "argparse",  # Proper CLI
        ]

        # Anti-pattern indicators
        anti_patterns = ["simple_list = []", "basic_visitor", "direct_replace"]

        quality_score = sum(
            1 for indicator in quality_indicators if indicator in content
        )
        anti_score = sum(1 for anti in anti_patterns if anti in content)

        return quality_score >= 3 and anti_score == 0

    def _identify_best_xform(
        self, search_results: List[Document], user_request: str
    ) -> str:
        """Identify best matching transformation file"""
        xform_files = []

        # Check for complementary transformations first
        complement_xform = self._find_complementary_xform(search_results, user_request)
        if complement_xform:
            return complement_xform

        # Find xform files in results
        for doc in search_results:
            if hasattr(doc, "metadata") and "source" in doc.metadata:
                source = doc.metadata["source"]
                if "xform_" in source and source.endswith(".py"):
                    filename = (
                        source.split("/")[-1]
                        if "/" in source
                        else source.split("\\")[-1]
                    )
                    xform_files.append(filename)

        return xform_files[0] if xform_files else "No specific xform identified"

    def _find_complementary_xform(
        self, search_results: List[Document], user_request: str
    ) -> str:
        """Find complementary transformation"""
        query_lower = user_request.lower()

        complementary_mapping = {
            "wire to reg": "reg_to_wire",
            "wire to int": "reg_to_wire",  # Similar pattern
            "reg to wire": "wire_to_reg",
            "input to output": "output_to_input",
            "output to input": "input_to_output",
        }

        for request_pattern, target_pattern in complementary_mapping.items():
            if request_pattern in query_lower:
                for doc in search_results:
                    if hasattr(doc, "metadata") and "source" in doc.metadata:
                        source = doc.metadata["source"]
                        filename = (
                            source.split("/")[-1]
                            if "/" in source
                            else source.split("\\")[-1]
                        )

                        if target_pattern in filename and "xform_" in filename:
                            return filename

        return None

    def _classify_transformation_type(self, user_request: str) -> str:
        """Classify the type of transformation requested"""
        request_lower = user_request.lower()

        if any(pattern in request_lower for pattern in ["wire", "reg", "logic", "int"]):
            return "data_type"
        elif any(pattern in request_lower for pattern in ["input", "output", "inout"]):
            return "port_direction"
        elif any(pattern in request_lower for pattern in ["width", "bit", "size"]):
            return "width"
        elif any(pattern in request_lower for pattern in ["module", "name"]):
            return "module_name"
        else:
            return "general"
