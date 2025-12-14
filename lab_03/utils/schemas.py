from dataclasses import dataclass


@dataclass(frozen=True)
class Rating:
    user_id: int
    item_id: str
    score: float


@dataclass
class Recommendation:
    item_id: str
    score: float
