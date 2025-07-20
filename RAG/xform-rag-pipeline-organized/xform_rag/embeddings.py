#!/usr/bin/env python3
"""
CodeBERT embeddings for code-specific similarity in Verilog transformations
"""

import logging
from typing import List
import torch
from transformers import AutoTokenizer, AutoModel


class CodeBERTEmbeddings:
    """CodeBERT embeddings optimized for code understanding"""

    def __init__(self, model_name: str = "microsoft/codebert-base"):
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name

        try:
            self.logger.info(f"Loading CodeBERT model: {model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
            self.model.eval()

            # Test the model
            test_embedding = self._embed_single("def test(): pass")
            self.logger.info(
                f"CodeBERT model loaded successfully, embedding dimension: {len(test_embedding)}"
            )

        except Exception as e:
            raise RuntimeError(f"Failed to load CodeBERT model: {e}")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents"""
        self.logger.info(f"Embedding {len(texts)} documents with CodeBERT")
        embeddings = []

        for i, text in enumerate(texts):
            if i % 10 == 0:
                self.logger.info(f"Processing document {i+1}/{len(texts)}")

            embedding = self._embed_single(text)
            embeddings.append(embedding)

        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        return self._embed_single(text)

    def _embed_single(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            # Handle empty text
            if not text or not text.strip():
                text = "empty"

            # Tokenize with truncation for long code
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512,  # CodeBERT's max length
            )

            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use [CLS] token embedding (first token)
                embeddings = outputs.last_hidden_state[:, 0, :]
                # Normalize for cosine similarity
                embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)

            return embeddings.squeeze().tolist()

        except Exception as e:
            self.logger.error(f"Error generating embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * 768  # CodeBERT dimension
