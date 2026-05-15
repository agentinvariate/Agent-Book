#!/usr/bin/env python3
"""
FastAPI Backend - REST API + WebSocket
Docs: https://fastapi.tiangolo.com
"""

import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import core modules
from core.db import UltraDB
from core.llm import LLMOrchestrator, Embedder
from core.retrieval import Retriever, Reranker
from core.etl import ETL


# ============ Models ============

class QueryRequest(BaseModel):
    query: str
    chat_id: str = None


class ChatMessage(BaseModel):
    role: str
    content: str
    sources: list = None


class IndexRequest(BaseModel):
    path: str
    recursive: bool = False


# ============ App ============

class UltraRAGApp:
    """Main application."""
    
    def __init__(self):
        self.db = None
        self.llm = None
        self.embedder = None
        self.retriever = None
        self.reranker = None
        self.etl = None
        self._chats = {}  # In-memory chat sessions
    
    async def init(self):
        """Initialize all components."""
        # Database
        self.db = UltraDB()
        await self.db.connect()
        await self.db.init_all()
        
        # LLM
        self.llm = LLMOrchestrator()
        await self.llm.init()
        
        # Embedder
        self.embedder = Embedder()
        await self.embedder.init()
        
        # Retrieval
        self.retriever = Retriever(self.db)
        self.reranker = Reranker()
        
        # ETL
        self.etl = ETL(self.embedder)
        
        return self


# Global app
app_state = UltraRAGApp()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown."""
    await app_state.init()
    print("✅ UltraRAG initialized")
    yield
    await app_state.db.close()


# ============ API ============

app = FastAPI(title="Ultimate RAG API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "provider": app_state.llm.provider}


@app.get("/")
async def root():
    return {"name": "Ultimate RAG", "version": "0.1.0"}


# Index document
@app.post("/index")
async def index(req: IndexRequest):
    result = await app_state.etl.index(req.path, app_state.db)
    return result


# Query
@app.post("/query")
async def query(req: QueryRequest):
    # 1. Embed query
    query_emb = await app_state.embedder.embed(req.query)
    
    # 2. Retrieve (dual-level)
    results = await app_state.retriever.retrieve(req.query, query_emb)
    
    # 3. Build context
    context = "\n\n".join([r.get("content", "") for r in results["fused"]])
    sources = [r.get("id") for r in results["fused"]]
    
    # 4. Generate response
    response = await app_state.llm.chat(req.query, context, sources)
    
    return {
        "response": response,
        "sources": sources,
        "context": context[:500]
    }


# Chat with WebSocket
@app.websocket("/ws/chat")
async def chat_ws(websocket: WebSocket):
    """WebSocket chat for real-time streaming."""
    await websocket.accept()
    
    chat_id = None
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            message = data.get("message", "")
            
            # Create chat if needed
            if not chat_id:
                chat = await app_state.db.create_chat()
                chat_id = chat.get("id")
            
            # Query + LLM
            query_emb = await app_state.embedder.embed(message)
            results = await app_state.retriever.retrieve(message, query_emb)
            context = "\n\n".join([r.get("content", "") for r in results["fused"]])
            
            # Stream response
            response = ""
            async for word in app_state.llm.stream(message, context):
                await websocket.send_json({"type": "chunk", "content": word})
                response += word + " "
            
            # Save message
            await app_state.db.add_message(chat_id, "user", message, results["fused"])
            await app_state.db.add_message(chat_id, "assistant", response, results["fused"])
            
            await websocket.send_json({"type": "done", "response": response})
    
    except WebSocketDisconnect:
        print("Client disconnected")


# Graph endpoints
@app.get("/graph")
async def get_graph(entity_id: str = None, depth: int = 2):
    """Get knowledge graph."""
    if entity_id:
        return await app_state.db.get_graph(entity_id, depth)
    
    # Get all entities
    return await app_state.db.query("SELECT * FROM entity LIMIT 50")


@app.get("/entities")
async def list_entities(limit: int = 50):
    """List all entities."""
    return await app_state.db.query(f"SELECT * FROM entity LIMIT {limit}")


@app.post("/entity")
async def create_entity(name: str, entity_type: str, properties: dict = None):
    """Create entity."""
    return await app_state.db.create_entity(name, entity_type, properties)


# Document endpoints
@app.get("/documents")
async def list_documents(limit: int = 20):
    """List documents."""
    return await app_state.db.query(f"SELECT * FROM document LIMIT {limit}")


# ============ Run ============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)