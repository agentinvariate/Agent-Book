"""
SurrealDB Client - HTTP API (No SDK, Env Variables)
"""

import os
import aiohttp


class UltraDB:
    """Unified SurrealDB client via HTTP API."""
    
    def __init__(self, url: str = None, user: str = None, password: str = None):
        # All configurable via env vars
        self.url = url or os.getenv("SURREALDB_URL", "http://localhost:8000")
        self.user = user or os.getenv("SURREALDB_USER", "root")
        self.password = password or os.getenv("SURREALDB_PASSWORD", "root")
        self.namespace = os.getenv("SURREALDB_NS", "ultrarag")
        self.database = os.getenv("SURREALDB_DB", "ultrarag")
        self._session = None
        self._token = None
    
    async def connect(self):
        """Connect via HTTP."""
        self._session = aiohttp.ClientSession()
        resp = await self._session.post(
            f"{self.url}/signin",
            json={"username": self.user, "password": self.password}
        )
        data = await resp.json()
        self._token = data.get("token")
        return self
    
    async def close(self):
        if self._session:
            await self._session.close()
    
    async def use(self, namespace: str, database: str):
        """Select namespace/db."""
        self.namespace = namespace
        self.database = database
    
    async def query(self, sql: str, vars: dict = None):
        """Execute SQL query."""
        headers = {"Authorization": f"Bearer {self._token}"} if self._token else {}
        resp = await self._session.post(
            f"{self.url}/api/{self.namespace}/{self.database}",
            headers=headers,
            json={"query": sql, "vars": vars or {}}
        )
        return await resp.json()
    
    async def create(self, table: str, data: dict):
        """Create record."""
        return await self.query(f"CREATE {table} CONTENT $data", {"data": data})
    
    async def select(self, table: str):
        """Select all records."""
        return await self.query(f"SELECT * FROM {table}")
    
    async def update(self, id: str, data: dict):
        """Update record."""
        return await self.query(f"UPDATE {id} CONTENT $data", {"data": data})
    
    # ============ Vector (HNSW) ============
    
    async def create_vector_table(self, table: str, dim: int = 768):
        """Create table with HNSW index."""
        await self.query(f"""
            DEFINE TABLE {table} SCHEMAFULL;
            DEFINE FIELD content ON {table} TYPE string;
            DEFINE FIELD embedding ON {table} TYPE floatarray({dim});
            DEFINE FIELD metadata ON {table} TYPE object;
            DEFINE INDEX emb_idx ON {table} FIELDS embedding HNSW DIMENSION {dim} DISTANCE COSINE;
        """)
    
    async def insert_chunk(self, table: str, content: str, embedding: list, metadata: dict = None):
        """Insert chunk with vector."""
        return await self.create(table, {
            "content": content,
            "embedding": embedding,
            "metadata": metadata or {}
        })
    
    async def search_vectors(self, table: str, query_embedding: list, limit: int = 10):
        """Vector search."""
        return await self.query(f"""
            SELECT * FROM {table}
            ORDER BY embedding <-> $embedding
            LIMIT {limit}
        """, {"embedding": query_embedding})
    
    # ============ Graph (Relations) ============
    
    async def create_entity_table(self):
        """Create entity table."""
        await self.query("""
            DEFINE TABLE entity SCHEMAFULL;
            DEFINE FIELD name ON entity TYPE string;
            DEFINE FIELD type ON entity TYPE string;
            DEFINE FIELD properties ON entity TYPE object;
        """)
    
    async def create_relation_table(self):
        """Create relation table."""
        await self.query("""
            DEFINE TABLE relation SCHEMAFULL;
            DEFINE FIELD from ON relation TYPE record(entity);
            DEFINE FIELD to ON relation TYPE record(entity);
            DEFINE FIELD type ON relation TYPE string;
            DEFINE FIELD weight ON relation TYPE float;
        """)
    
    async def create_entity(self, name: str, entity_type: str, properties: dict = None):
        """Create entity."""
        return await self.create("entity", {
            "name": name,
            "type": entity_type,
            "properties": properties or {}
        })
    
    async def create_relation(self, from_id: str, to_id: str, rel_type: str, weight: float = 1.0):
        """Create relation."""
        return await self.create("relation", {
            "from": from_id,
            "to": to_id,
            "type": rel_type,
            "weight": weight
        })
    
    async def get_graph(self, entity_id: str, depth: int = 2):
        """Get subgraph."""
        return await self.query(f"""
            SELECT * FROM relation
            WHERE from = $entity_id OR to = $entity_id
        """, {"entity_id": entity_id})
    
    # ============ Documents ============
    
    async def create_document_table(self):
        """Create document table."""
        await self.query("""
            DEFINE TABLE document SCHEMAFULL;
            DEFINE FIELD title ON document TYPE string;
            DEFINE FIELD content ON document TYPE string;
            DEFINE FIELD source ON document TYPE string;
            DEFINE FIELD metadata ON document TYPE object;
        """)
    
    async def insert_document(self, title: str, content: str, source: str = None, metadata: dict = None):
        """Insert document."""
        return await self.create("document", {
            "title": title,
            "content": content,
            "source": source,
            "metadata": metadata or {}
        })
    
    async def search_fulltext(self, table: str, query: str, limit: int = 10):
        """Full-text search."""
        return await self.query(f"""
            SELECT * FROM {table}
            WHERE content @1@ $query
            LIMIT {limit}
        """, {"query": query})
    
    # ============ Chats ============
    
    async def create_chat_table(self):
        """Create chat table."""
        await self.query("""
            DEFINE TABLE chat SCHEMAFULL;
            DEFINE FIELD messages ON chat TYPE array;
            DEFINE FIELD context ON chat TYPE object;
        """)
    
    async def create_chat(self):
        """Create new chat."""
        return await self.create("chat", {"messages": [], "context": {}})
    
    async def add_message(self, chat_id: str, role: str, content: str, sources: list = None):
        """Add message."""
        return await self.update(chat_id, {
            "messages": {"role": role, "content": content, "sources": sources or []}
        })
    
    # ============ Init ============
    
    async def init_all(self):
        """Initialize all tables."""
        await self.create_vector_table("chunk")
        await self.create_entity_table()
        await self.create_relation_table()
        await self.create_document_table()
        await self.create_chat_table()
        return "Initialized"