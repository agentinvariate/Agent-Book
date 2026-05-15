"""
SurrealDB Client - Embedded or HTTP.

Supports multiple connection modes:
- mem://         - In-memory, fastest, no persistence
- rocksdb://db   - File-based, persistent
- http://host   - HTTP server (local or cloud)
- https://...   - HTTPS (cloud)

Example:
    # Embedded
    db = UltraDB("mem://")
    await db.connect()
    await db.init_all()
    
    # HTTP
    db = UltraDB("http://localhost:8000")
    await db.connect()

Docs: https://surrealdb.com/docs/build/embedding/by-language/python
"""

import os
# Use surrealdb SDK for embedded, aiohttp for HTTP
import aiohttp



class UltraDB:
    """
    Unified SurrealDB client.
    
    Attributes:
        url: Connection URL (mem://, rocksdb://, http://, https://)
        user: Username for auth
        password: Password for auth
        namespace: Database namespace
        database: Database name
    """
    
    def __init__(self, url: str = None, user: str = None, password: str = None):
        """Initialize UltraDB client.
        
        Args:
            url: Connection URL. Default: mem:// (in-memory)
            user: Username. Default: root
            password: Password. Default: root
        """
        # Modes: mem://, rocksdb://, file://, http://, https://
        self.url = url or os.getenv("SURREALDB_URL", "mem://")
        self.user = user or os.getenv("SURREALDB_USER", "root")
        self.password = password or os.getenv("SURREALDB_PASSWORD", "root")
        self.namespace = os.getenv("SURREALDB_NS", "ultrarag")
        self.database = os.getenv("SURREALDB_DB", "ultrarag")
        
        # Determine mode
        self._embedded = self.url.startswith(("mem://", "rocksdb://", "file://", "surrealkv://"))
        self._db = None  # Embedded client
        self._session = None  # HTTP client
        self._token = None
    
    async def connect(self):
        """Connect to SurrealDB.
        
        Automatically detects embedded vs HTTP mode.
        
        Returns:
            self: Connected UltraDB instance
        """
        if self._embedded:
            # Use SDK (embedded)
            from surrealdb import AsyncSurreal
            self._db = AsyncSurreal(self.url)
            await self._db.connect()
            await self._db.use(self.namespace, self.database)
            if self.url != "mem://":
                await self._db.authenticate(self.user, self.password)
        else:
            # Use HTTP API
            self._session = aiohttp.ClientSession()
            resp = await self._session.post(
                f"{self.url}/signin",
                json={"username": self.user, "password": self.password}
            )
            data = await resp.json()
            self._token = data.get("token")
        
        return self
    
    async def close(self):
        """Close connection and cleanup resources."""
        if self._db:
            await self._db.close()
        elif self._session:
            await self._session.close()
    
    async def use(self, namespace: str, database: str):
        """Select namespace and database.
        
        Args:
            namespace: Namespace name
            database: Database name
        """
        if self._db:
            await self._db.use(namespace, database)
        else:
            self.namespace = namespace
            self.database = database
    
    async def query(self, sql: str, vars: dict = None):
        """Execute SurrealQL query.
        
        Args:
            sql: SurrealQL query string
            vars: Query variables (optional)
            
        Returns:
            Query result as dict/list
        """
        if self._db:
            return await self._db.query(sql, vars or {})
        else:
            headers = {"Authorization": f"Bearer {self._token}"} if self._token else {}
            resp = await self._session.post(
                f"{self.url}/api/{self.namespace}/{self.database}",
                headers=headers,
                json={"query": sql, "vars": vars or {}}
            )
            return await resp.json()
    
    async def create(self, table: str, data: dict):
        """Create a record.
        
        Args:
            table: Table name
            data: Record data as dict
            
        Returns:
            Created record
        """
        return await self.query(f"CREATE {table} CONTENT $data", {"data": data})
    
    async def select(self, table: str):
        """Select all records from table.
        
        Args:
            table: Table name
            
        Returns:
            List of records
        """
        return await self.query(f"SELECT * FROM {table}")
    
    async def update(self, id: str, data: dict):
        """Update a record by ID.
        
        Args:
            id: Record ID
            data: New data
            
        Returns:
            Updated record
        """
        return await self.query(f"UPDATE {id} CONTENT $data", {"data": data})
    
    # ============ Vector (HNSW) ============
    
    async def create_vector_table(self, table: str, dim: int = 768):
        """Create table with HNSW vector index.
        
        Args:
            table: Table name
            dim: Embedding dimension (default: 768)
        """
        await self.query(f"""
            DEFINE TABLE {table} SCHEMAFULL;
            DEFINE FIELD content ON {table} TYPE string;
            DEFINE FIELD embedding ON {table} TYPE floatarray({dim});
            DEFINE FIELD metadata ON {table} TYPE object;
            DEFINE INDEX emb_idx ON {table} FIELDS embedding HNSW DIMENSION {dim} DISTANCE COSINE;
        """)
    
    async def insert_chunk(self, table: str, content: str, embedding: list, metadata: dict = None):
        """Insert chunk with vector embedding.
        
        Args:
            table: Table name
            content: Text content
            embedding: Vector embedding
            metadata: Optional metadata dict
        """
        return await self.create(table, {
            "content": content,
            "embedding": embedding,
            "metadata": metadata or {}
        })
    
    async def search_vectors(self, table: str, query_embedding: list, limit: int = 10):
        """Search by vector similarity.
        
        Args:
            table: Table name
            query_embedding: Query vector
            limit: Number of results
            
        Returns:
            List of similar records
        """
        return await self.query(f"""
            SELECT * FROM {table}
            ORDER BY embedding <-> $embedding
            LIMIT {limit}
        """, {"embedding": query_embedding})
    
    # ============ Graph (Relations) ============
    
    async def create_entity_table(self):
        """Create entity table for knowledge graph."""
        await self.query("""
            DEFINE TABLE entity SCHEMAFULL;
            DEFINE FIELD name ON entity TYPE string;
            DEFINE FIELD type ON entity TYPE string;
            DEFINE FIELD properties ON entity TYPE object;
        """)
    
    async def create_relation_table(self):
        """Create relation edges table."""
        await self.query("""
            DEFINE TABLE relation SCHEMAFULL;
            DEFINE FIELD from ON relation TYPE record(entity);
            DEFINE FIELD to ON relation TYPE record(entity);
            DEFINE FIELD type ON relation TYPE string;
            DEFINE FIELD weight ON relation TYPE float;
        """)
    
    async def create_entity(self, name: str, entity_type: str, properties: dict = None):
        """Create entity node.
        
        Args:
            name: Entity name
            entity_type: Entity type
            properties: Optional properties
        """
        return await self.create("entity", {
            "name": name,
            "type": entity_type,
            "properties": properties or {}
        })
    
    async def create_relation(self, from_id: str, to_id: str, rel_type: str, weight: float = 1.0):
        """Create relation edge.
        
        Args:
            from_id: Source entity ID
            to_id: Target entity ID
            rel_type: Relation type
            weight: Edge weight
        """
        return await self.create("relation", {
            "from": from_id,
            "to": to_id,
            "type": rel_type,
            "weight": weight
        })
    
    async def get_graph(self, entity_id: str, depth: int = 2):
        """Get subgraph around entity.
        
        Args:
            entity_id: Center entity ID
            depth: Search depth
            
        Returns:
            List of relations
        """
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
        """Insert document.
        
        Args:
            title: Document title
            content: Document text
            source: Source URL/path
            metadata: Additional metadata
        """
        return await self.create("document", {
            "title": title,
            "content": content,
            "source": source,
            "metadata": metadata or {}
        })
    
    async def search_fulltext(self, table: str, query: str, limit: int = 10):
        """Full-text search.
        
        Args:
            table: Table name
            query: Search query
            limit: Max results
            
        Returns:
            Matching records
        """
        return await self.query(f"""
            SELECT * FROM {table}
            WHERE content @1@ $query
            LIMIT {limit}
        """, {"query": query})
    
    # ============ Chats ============
    
    async def create_chat_table(self):
        """Create chat history table."""
        await self.query("""
            DEFINE TABLE chat SCHEMAFULL;
            DEFINE FIELD messages ON chat TYPE array;
            DEFINE FIELD context ON chat TYPE object;
        """)
    
    async def create_chat(self):
        """Create new chat session."""
        return await self.create("chat", {"messages": [], "context": {}})
    
    async def add_message(self, chat_id: str, role: str, content: str, sources: list = None):
        """Add message to chat.
        
        Args:
            chat_id: Chat ID
            role: user/assistant
            content: Message content
            sources: Source references
        """
        return await self.update(chat_id, {
            "messages": {"role": role, "content": content, "sources": sources or []}
        })
    
    async def delete_table(self, table: str):
        """Drop a table.
        
        Args:
            table: Table name
        """
        return await self.query(f"REMOVE TABLE {table}")
    
    async def delete_all(self):
        """Delete all records (keep tables)."""
        await self.query("DELETE FROM chunk")
        await self.query("DELETE FROM entity")
        await self.query("DELETE FROM relation")
        await self.query("DELETE FROM document")
        await self.query("DELETE FROM chat")
        return "All records deleted"
    
    async def drop_all(self):
        """Drop all tables (danger!)."""
        await self.query("REMOVE TABLE chunk")
        await self.query("REMOVE TABLE entity")
        await self.query("REMOVE TABLE relation")
        await self.query("REMOVE TABLE document")
        await self.query("REMOVE TABLE chat")
        return "All tables dropped"
    
    async def init_all(self):
        """Initialize all tables."""
        await self.create_vector_table("chunk")
        await self.create_entity_table()
        await self.create_relation_table()
        await self.create_document_table()
        await self.create_chat_table()
        return "Initialized"