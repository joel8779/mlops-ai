from uuid import uuid4

from app.knowledge_graph.taxonomy.taxonomy_service import TaxonomyService
from app.ml.recommendation.collaborative_filtering import CollaborativeFilteringRecommender, Interaction
from app.ml.recommendation.similarity_network import CandidateNode, CandidateSimilarityNetwork


def test_taxonomy_expands_skills_and_infers_roles():
    enriched = TaxonomyService().enrich_candidate_skills(["py", "k8s", "mlops"])

    assert "python" in enriched["canonical_skills"]
    assert "kubernetes" in enriched["canonical_skills"]
    assert "mlops engineer" in enriched["role_matches"]


def test_similarity_network_links_related_candidates():
    left = CandidateNode(candidate_id=uuid4(), skills={"python", "fastapi", "postgresql"})
    right = CandidateNode(candidate_id=uuid4(), skills={"python", "fastapi", "redis"})

    edges = CandidateSimilarityNetwork().build_edges([left, right], threshold=0.2)

    assert edges[left.candidate_id][0][0] == right.candidate_id


def test_collaborative_filtering_recommends_unseen_candidates():
    recruiter = uuid4()
    similar_recruiter = uuid4()
    shared_candidate = uuid4()
    unseen_candidate = uuid4()

    recommendations = CollaborativeFilteringRecommender().recommend(
        [
            Interaction(recruiter, shared_candidate, 1.0),
            Interaction(similar_recruiter, shared_candidate, 1.0),
            Interaction(similar_recruiter, unseen_candidate, 0.8),
        ],
        recruiter,
    )

    assert recommendations[0][0] == unseen_candidate
