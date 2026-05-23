"""Graph-based candidate recommendations."""

from collections import defaultdict
from uuid import UUID


class CandidateRecommendationGraph:
    def personalized_pagerank(
        self,
        graph: dict[UUID, list[tuple[UUID, float]]],
        seeds: dict[UUID, float],
        iterations: int = 20,
        damping: float = 0.85,
    ) -> list[tuple[UUID, float]]:
        nodes = set(graph) | set(seeds)
        if not nodes:
            return []
        restart_total = sum(seeds.values()) or 1.0
        restart = {node: seeds.get(node, 0.0) / restart_total for node in nodes}
        ranks = restart.copy()
        for _ in range(iterations):
            next_ranks = {node: (1 - damping) * restart.get(node, 0.0) for node in nodes}
            for node, neighbors in graph.items():
                total_weight = sum(weight for _, weight in neighbors) or 1.0
                for neighbor, weight in neighbors:
                    next_ranks[neighbor] = next_ranks.get(neighbor, 0.0) + damping * ranks.get(node, 0.0) * (weight / total_weight)
            ranks = next_ranks
        return sorted(ranks.items(), key=lambda item: item[1], reverse=True)

    def community_candidates(self, graph: dict[UUID, list[tuple[UUID, float]]]) -> dict[int, list[UUID]]:
        communities: dict[int, list[UUID]] = defaultdict(list)
        for node, neighbors in graph.items():
            signature = hash(tuple(sorted(neighbor for neighbor, score in neighbors[:3] if score > 0.5))) % 97
            communities[signature].append(node)
        return dict(communities)
