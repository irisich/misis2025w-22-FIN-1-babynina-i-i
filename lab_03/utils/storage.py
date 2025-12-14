from typing import Dict, Iterable, List, Tuple
from .schemas import Rating, Recommendation
from . import cf


class RecommendationStorage:
    """In-memory store for ratings and precomputed similarity."""

    def __init__(self) -> None:
        self.item_user: cf.ItemUserMatrix = {}
        self.similarity: Dict[str, Dict[str, float]] = {}

    def add_rating(self, rating: Rating) -> None:
        self.item_user.setdefault(rating.item_id, {})[rating.user_id] = float(rating.score)

    def load_bulk(self, ratings: Iterable[Rating]) -> None:
        for rating in ratings:
            self.add_rating(rating)
        self.recompute_similarity()

    def recompute_similarity(self) -> None:
        self.similarity = cf.build_similarity_matrix(self.item_user) if self.item_user else {}

    def recommend_for_user(self, user_id: int, k_neighbors: int = 20, top_n: int = 10) -> List[Recommendation]:
        if not self.similarity:
            self.recompute_similarity()
        if not self.similarity:
            return []
        return cf.recommend_items_for_user(
            user_id=user_id,
            matrix=self.item_user,
            similarity_matrix=self.similarity,
            k_neighbors=k_neighbors,
            top_n=top_n,
        )

    def similar_items(self, item_id: str, top_n: int = 10) -> List[str]:
        """
        Return top-N most similar items to the given item_id using precomputed similarity.
        """
        sims: Dict[str, float] = self.similarity.get(item_id, {})
        if not sims:
            return []
        sorted_items: List[Tuple[str, float]] = sorted(sims.items(), key=lambda x: x[1], reverse=True)
        return [item for item, _ in sorted_items[:top_n]]


rating_storage = RecommendationStorage()


def add_rating(rating: Rating) -> None:
    rating_storage.add_rating(rating)


def load_base_ratings(ratings: Iterable[Rating]) -> None:
    rating_storage.load_bulk(ratings)


def recommend_for_user(user_id: int, k_neighbors: int = 20, top_n: int = 10) -> List[Recommendation]:
    return rating_storage.recommend_for_user(user_id, k_neighbors=k_neighbors, top_n=top_n)


def similar_items(item_id: str, top_n: int = 10) -> List[str]:
    return rating_storage.similar_items(item_id=item_id, top_n=top_n)
