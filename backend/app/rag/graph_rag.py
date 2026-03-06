"""Graph RAG using Neo4j knowledge graph."""
from typing import List, Dict, Any
from neo4j import AsyncGraphDatabase, AsyncDriver

from app.core.config import settings
from app.core.logging import get_logger
from app.models.paper import Entity, Relationship, EntityType, RelationType

logger = get_logger(__name__)


class GraphRAG:
    """Neo4j-based graph RAG system."""

    def __init__(self) -> None:
        """Initialize Neo4j driver."""
        self.driver: AsyncDriver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )

    async def close(self) -> None:
        """Close Neo4j driver."""
        await self.driver.close()

    async def add_entity(self, entity: Entity) -> None:
        """Add entity to graph."""
        async with self.driver.session() as session:
            await session.run(
                """
                MERGE (e:Entity {id: $id})
                SET e.name = $name, e.type = $type, 
                    e.mention_count = $mention_count,
                    e.confidence = $confidence
                """,
                id=entity.id,
                name=entity.name,
                type=entity.type.value,
                mention_count=entity.mention_count,
                confidence=entity.confidence,
            )

    async def add_relationship(self, rel: Relationship) -> None:
        """Add relationship to graph."""
        async with self.driver.session() as session:
            await session.run(
                f"""
                MATCH (source:Entity {{id: $source_id}})
                MATCH (target:Entity {{id: $target_id}})
                MERGE (source)-[r:{rel.type.value}]->(target)
                SET r.confidence = $confidence, r.paper_id = $paper_id
                """,
                source_id=rel.source_id,
                target_id=rel.target_id,
                confidence=rel.confidence,
                paper_id=rel.paper_id,
            )

    async def find_related_entities(
        self, entity_id: str, max_hops: int = 2
    ) -> List[Dict[str, Any]]:
        """Find entities related to given entity."""
        async with self.driver.session() as session:
            result = await session.run(
                """
                MATCH path = (start:Entity {id: $entity_id})-[*1.."""
                + str(max_hops)
                + """]->(related:Entity)
                RETURN DISTINCT related.id as id, related.name as name, 
                       related.type as type, length(path) as distance
                ORDER BY distance, related.mention_count DESC
                LIMIT 50
                """,
                entity_id=entity_id,
            )
            
            records = await result.data()
            return records

    async def query_context(self, entity_names: List[str]) -> str:
        """Build context from graph for given entities."""
        context_parts = []
        
        for name in entity_names[:10]:  # Limit to top 10
            async with self.driver.session() as session:
                result = await session.run(
                    """
                    MATCH (e:Entity {name: $name})-[r]->(related:Entity)
                    RETURN e.name as entity, type(r) as relation, 
                           related.name as related_entity
                    LIMIT 5
                    """,
                    name=name,
                )
                
                records = await result.data()
                for record in records:
                    context_parts.append(
                        f"{record['entity']} {record['relation']} {record['related_entity']}"
                    )
        
        return "\\n".join(context_parts)
