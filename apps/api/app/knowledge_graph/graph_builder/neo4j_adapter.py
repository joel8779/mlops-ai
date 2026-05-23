"""Neo4j-compatible graph abstraction with an in-memory implementation for local/test use."""

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GraphRelationship:
    source: str
    target: str
    relationship_type: str
    properties: dict[str, Any]


class KnowledgeGraphAdapter:
    def __init__(self) -> None:
        self._edges: dict[str, list[GraphRelationship]] = defaultdict(list)

    async def upsert_relationship(self, source: str, target: str, relationship_type: str, **properties: Any) -> None:
        relationship = GraphRelationship(source=source, target=target, relationship_type=relationship_type, properties=properties)
        self._edges[source].append(relationship)

    async def neighbors(self, node: str, relationship_type: str | None = None) -> list[GraphRelationship]:
        edges = self._edges.get(node, [])
        if relationship_type:
            return [edge for edge in edges if edge.relationship_type == relationship_type]
        return list(edges)

    async def traverse(self, start: str, depth: int = 2) -> list[GraphRelationship]:
        seen = {start}
        queue = deque([(start, 0)])
        relationships: list[GraphRelationship] = []
        while queue:
            node, level = queue.popleft()
            if level >= depth:
                continue
            for edge in self._edges.get(node, []):
                relationships.append(edge)
                if edge.target not in seen:
                    seen.add(edge.target)
                    queue.append((edge.target, level + 1))
        return relationships
