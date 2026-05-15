"""
LLM Orchestrator - Multiple providers
Docs: https://python.langchain.com/docs/integrations/llms/
"""

import os
from typing import Optional


class LLMOrchestrator:
    """Unified LLM integration with multiple providers."""
    
    PROVIDERS = ["openai", "anthropic", "ollama", "gemini", "azure"]
    
    def __init__(self, provider: str = None):
        self.provider = provider or os.getenv("LLM_PROVIDER", "ollama")
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.base_url = os.getenv("LLM_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("LLM_MODEL", "llama3.2")
        self._client = None
    
    async def init(self):
        """Initialize LLM client."""
        if self.provider == "openai":
            from langchain_openai import ChatOpenAI
            self._client = ChatOpenAI(
                model=self.model,
                api_key=self.api_key,
                temperature=0.1
            )
        elif self.provider == "anthropic":
            from langchain_anthropic import ChatAnthropic
            self._client = ChatAnthropic(
                model=self.model,
                anthropic_api_key=self.api_key,
                temperature=0.1
            )
        elif self.provider == "ollama":
            from langchain_ollama import ChatOllama
            self._client = ChatOllama(
                model=self.model,
                base_url=self.base_url,
                temperature=0.1
            )
        
        return self
    
    async def chat(self, message: str, context: str = None, sources: list = None) -> str:
        """Simple chat response."""
        
        # Build prompt with context
        prompt = message
        if context:
            prompt = f"""Context:
{context}

Sources: {sources}

Question: {message}

Answer based on the context above."""
        
        if self._client:
            from langchain_core.messages import HumanMessage
            response = await self._client.ainvoke([HumanMessage(content=prompt)])
            return response.content
        
        # Fallback: return message with context
        return f"[{self.provider}] {message}\n\nContext: {context[:200]}..."
    
    async def stream(self, message: str, context: str = None):
        """Streaming response (generator)."""
        response = await self.chat(message, context)
        for word in response.split():
            yield word + " "


class Embedder:
    """Embedding generation."""
    
    def __init__(self, provider: str = None):
        self.provider = provider or os.getenv("EMBED_PROVIDER", "ollama")
        self.model = os.getenv("EMBED_MODEL", "nomic-embed-text")
        self._client = None
    
    async def init(self):
        """Initialize embedder."""
        if self.provider == "ollama":
            from langchain_ollama import OllamaEmbeddings
            self._client = OllamaEmbeddings(model=self.model)
        elif self.provider == "openai":
            from langchain_openai import OpenAIEmbeddings
            self._client = OpenAIEmbeddings(model="text-embedding-3-small")
        
        return self
    
    async def embed(self, text: str) -> list:
        """Generate embedding for text."""
        if self._client:
            return await self._client.aembed_query(text)
        
        # Fallback: return dummy vector
        import hashlib
        h = int(hashlib.md5(text.encode()).hexdigest(), 16)
        return [(h % 1000) / 1000.0] * 768
    
    async def embed_batch(self, texts: list) -> list:
        """Generate embeddings for multiple texts."""
        if self._client:
            return await self._client.aembed_documents(texts)
        
        return [await self.embed(t) for t in texts]