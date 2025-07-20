#!/usr/bin/env python3
"""
LLM management for different backends (Ollama, EC2)
"""

import logging
from typing import Optional, List, Any
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun

try:
    from langchain_ollama import OllamaLLM as Ollama
except ImportError:
    try:
        from langchain_community.llms import Ollama
    except ImportError:
        from langchain.llms import Ollama

from .config import RAGConfig


class LLMManager:
    """Simple LLM management for the RAG pipeline"""

    def __init__(self, config: RAGConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._llm = None

    def get_llm(self) -> LLM:
        """Get the configured LLM instance"""
        if self._llm is None:
            self._llm = self._create_llm()
        return self._llm

    def _create_llm(self) -> LLM:
        """Create LLM based on configuration"""
        self.logger.info(
            f"Creating {self.config.model_type} LLM: {self.config.model_name}"
        )

        if self.config.model_type == "ollama":
            return Ollama(
                model=self.config.model_name,
                temperature=self.config.temperature,
                num_predict=self.config.max_tokens,
            )
        elif self.config.model_type == "ec2":
            if not self.config.ec2_endpoint:
                raise ValueError("EC2 endpoint not configured")
            # Placeholder for EC2 LLM implementation
            raise NotImplementedError("EC2 LLM not implemented in this simple version")
        else:
            raise ValueError(f"Unsupported model type: {self.config.model_type}")

    def test_connection(self) -> bool:
        """Test if the LLM is accessible"""
        try:
            llm = self.get_llm()
            response = llm.invoke("test")
            self.logger.info("LLM connection test successful")
            return True
        except Exception as e:
            self.logger.error(f"LLM connection test failed: {e}")
            return False
