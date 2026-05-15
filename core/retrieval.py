"""
Dual-Level Retrieval - Entity + Semantic
Inspired: https://github.com.com/MiniMaxAI/LightRAG
"""

from .db import UltraDB


class Retriever:
    """Dual-level retrieval combining entity and semantic search."""
    
    def __init__(self, db: UltraDB):
        self.db = db
    
    async def retrieve(self, query: str, query_embedding: list, top_k: int = 10):
        """Dual-level retrieval: low-level (entity) + high-level (semantic)."""
        
        # Level 1: Semantic (vector) search
        semantic_results = await self.db.search_vectors("chunk", query_embedding, limit=top_k)
        
        # Level 2: Entity-based retrieval
        entity_results = await self._get_entity_results(query)
        
        # Level 3: Full-text fallback
        ft_results = await self.db.search_fulltext("chunk", query, limit=top_k)
        
        # Fuse results (Simple ranking)
        fused = self._fuse_results(semantic_results, entity_results, ft_results, top_k)
        
        return {
            "semantic": semantic_results,
            "entity": entity_results,
            "fulltext": ft_results,
            "fused": fused
        }
    
    async def _get_entity_results(self, query: str):
        """Extract entities from query and find related chunks."""
        # Extract keywords as entities
        keywords = query.lower().split()
        
        # Find related entities
        results = []
        for kw in keywords[:5]:
            entities = await self.db.query("""
                SELECT * FROM entity
                WHERE name CONTAINS $kw
                LIMIT 3
            """, {"kw": kw})
            if entities:
                results.extend(entities)
        
        return results
    
    def _fuse_results(self, semantic, entity, fulltext, top_k):
        """Fuse results from all levels (simple rank by count)."""
        seen = {}
        fused = []
        
        for r in semantic:
            id_ = r.get("id")
            if id_ and id_ not in seen:
                seen[id_] = 1
                fused.append({**r, "score": 0.8, "source": "semantic"})
        
        for r in fulltext:
            id_ = r.get("id")
            if id_ and id_ not in seen:
                seen[id_] = 1
                fused.append({**r, "score": 0.6, "source": "fulltext"})
        
        # Sort by score and return top_k
        fused.sort(key=lambda x: x.get("score", 0), reverse=True)
        return fused[:top_k]


class Reranker:
    """Optional reranking for better results."""
    
    def __init__(self):
        self.enabled = True
    
    async def rerank(self, query: str, results: list) -> list:
        """Rerank results (placeholder - integrate BGE reranker)."""
        # Could integrate: BAAI/bge-reranker-v2-m3
        return sorted(results, key=lambda x: x.get("score", 0), reverse=True)