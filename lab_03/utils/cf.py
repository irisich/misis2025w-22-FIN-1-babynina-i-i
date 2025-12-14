from collections import defaultdict
from typing import Dict, Iterable, List
from .schemas import Rating, Recommendation
from .similarity import pearson_similarity

ItemUserMatrix = Dict[str, Dict[int, float]]


def build_item_user_matrix(ratings: Iterable[Rating]) -> ItemUserMatrix:
    matrix: ItemUserMatrix = {}
    for rating in ratings:
        matrix.setdefault(rating.item_id, {})[rating.user_id] = float(rating.score)
    return matrix


def build_similarity_matrix(matrix: ItemUserMatrix) -> Dict[str, Dict[str, float]]:
    items = list(matrix.keys())
    similarity: Dict[str, Dict[str, float]] = {item: {} for item in items}
    for i, item in enumerate(items):
        for j in range(i + 1, len(items)):
            other = items[j]
            sim = pearson_similarity(matrix[item], matrix[other])
            similarity[item][other] = sim
            similarity[other][item] = sim
    return similarity


def recommend_items_for_user(
    user_id: int,
    matrix: ItemUserMatrix,
    similarity_matrix: Dict[str, Dict[str, float]],
    k_neighbors: int = 20,
    top_n: int = 10,
) -> List[Recommendation]:
    """Item-based CF with Pearson similarity."""
    user_ratings = {item: users[user_id] for item, users in matrix.items() if user_id in users}
    if not user_ratings:
        return []

    scores: Dict[str, float] = defaultdict(float)
    weights: Dict[str, float] = defaultdict(float)

    for item, rating in user_ratings.items():
        neighbors = similarity_matrix.get(item, {})
        for other, sim in sorted(neighbors.items(), key=lambda x: x[1], reverse=True)[:k_neighbors]:
            if user_id in matrix.get(other, {}):
                continue
            if sim <= 0:
                continue
            scores[other] += sim * rating
            weights[other] += abs(sim)

    recs: List[Recommendation] = []
    for item, score in scores.items():
        weight = weights[item]
        if weight == 0:
            continue
        recs.append(Recommendation(item_id=item, score=score / weight))

    recs.sort(key=lambda r: r.score, reverse=True)
    return recs[:top_n]
