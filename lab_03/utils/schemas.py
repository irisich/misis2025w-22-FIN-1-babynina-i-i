from dataclasses import dataclass


@dataclass(frozen=True)   # frozen=True делает класс неизменяемым
class Rating:
    # хранит информацию о том, какой пользователь оценил какой фильм и какую оценку он поставил
    user_id: int
    item_id: str
    score: float


@dataclass
class Recommendation:
    # изменяемая структура данных, которая хранит информацию о фильме и его рейтинге или вероятности быть рекомендованным пользователю
    item_id: str
    score: float
