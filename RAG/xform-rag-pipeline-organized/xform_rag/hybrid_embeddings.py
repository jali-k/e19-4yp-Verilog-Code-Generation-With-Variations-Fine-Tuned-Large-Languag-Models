#!/usr/bin/env python3
"""
Hybrid embeddings: CodeBERT for code, sentence-transformers for documentation
"""

import logging
from typing import List
import torch
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer


class HybridEmbeddings:
    """Hybrid embeddings using CodeBERT for code and SentenceTransformers for docs"""

    def __init__(
        self,
        code_model: str = "microsoft/codebert-base",
        text_model: str = "all-MiniLM-L6-v2",
    ):
        self.logger = logging.getLogger(__name__)
        self.code_model_name = code_model
        self.text_model_name = text_model

        try:
            # Load CodeBERT for code
            self.logger.info(f"Loading CodeBERT model: {code_model}")
            self.code_tokenizer = AutoTokenizer.from_pretrained(code_model)
            self.code_model = AutoModel.from_pretrained(code_model)
            self.code_model.eval()

            # Load SentenceTransformers for text/documentation
            self.logger.info(f"Loading text model: {text_model}")
            self.text_model = SentenceTransformer(text_model)

            # Test both models
            test_code = self._embed_code_single("def test(): pass")
            test_text = self._embed_text_single("how to traverse nodes")

            self.logger.info(
                f"Hybrid embeddings loaded - Code dim: {len(test_code)}, Text dim: {len(test_text)}"
            )

        except Exception as e:
            self.logger.error(f"Error loading hybrid models: {e}")
            raise

    def _embed_code_single(self, text: str) -> List[float]:
        """Embed single text using CodeBERT"""
        with torch.no_grad():
            inputs = self.code_tokenizer(
                text, return_tensors="pt", padding=True, truncation=True, max_length=512
            )
            outputs = self.code_model(**inputs)
            embeddings = outputs.last_hidden_state.mean(dim=1)
            return embeddings.squeeze().tolist()

    def _embed_text_single(self, text: str) -> List[float]:
        """Embed single text using SentenceTransformers and pad to match CodeBERT dimension"""
        embedding = self.text_model.encode(text)

        # Pad to match CodeBERT dimension (768) if needed
        if len(embedding) < 768:
            # Pad with zeros
            padded = embedding.tolist() + [0.0] * (768 - len(embedding))
            return padded
        elif len(embedding) > 768:
            # Truncate if longer
            return embedding[:768].tolist()
        else:
            return embedding.tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed documents, choosing model based on content type"""
        embeddings = []
        for text in texts:
            if self._is_code_content(text):
                embedding = self._embed_code_single(text)
            else:
                embedding = self._embed_text_single(text)
            embeddings.append(embedding)
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """Embed query using a hybrid approach for better document matching"""
        # For queries, we want to match both code and documentation content
        # So we'll create a combined embedding that can match both types

        code_embedding = self._embed_code_single(text)
        text_embedding = self._embed_text_single(text)

        # Create a weighted combination - favor text embedding for natural language queries
        # but include some code embedding to match technical documentation
        if self._is_code_content(text):
            # Code-like query - favor code embedding
            weight_code = 0.7
            weight_text = 0.3
        else:
            # Natural language query - favor text embedding but include code for technical docs
            weight_code = 0.4
            weight_text = 0.6

        # Combine embeddings with weights
        combined_embedding = [
            weight_code * code_val + weight_text * text_val
            for code_val, text_val in zip(code_embedding, text_embedding)
        ]

        return combined_embedding

    def _is_code_content(self, text: str) -> bool:
        """Determine if content is code or documentation"""
        code_indicators = [
            "def ",
            "class ",
            "import ",
            "from ",
            "#!/",
            "ast.",
            "visit(",
            "Node",
            "children()",
            "pyverilog",
            "moduledef",
            "wire ",
            "reg ",
        ]

        # Count code indicators
        code_score = sum(
            1 for indicator in code_indicators if indicator.lower() in text.lower()
        )

        # If it has multiple code indicators or is short and has code syntax, treat as code
        return code_score >= 2 or (len(text) < 500 and code_score >= 1)
