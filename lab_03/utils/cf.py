from collections import defaultdict
from typing import Dict, Iterable, List
from .schemas import Rating, Recommendation
from .similarity import pearson_similarity

# Тип для матрицы "фильм-пользователь"
ItemUserMatrix = Dict[str, Dict[int, float]]


def build_item_user_matrix(ratings: Iterable[Rating]) -> ItemUserMatrix:
    """
    строит матрицу "фильм-пользователь", где строки - это фильмы,
    а столбцы - это пользователи с их рейтингами.
    
    аргументы:
        ratings (Iterable[Rating]): список рейтингов, где каждый рейтинг включает
                                     информацию о пользователе, фильме и оценке.
    
    возвращает:
        ItemUserMatrix: матрица, где ключами являются ID фильмов, а значениями — словари,
                        где ключами являются ID пользователей, а значениями — их оценки.
    """
    matrix: ItemUserMatrix = {}
    for rating in ratings:
        # Создаем запись для каждого фильма, если её нет, и добавляем рейтинг пользователя
        matrix.setdefault(rating.item_id, {})[rating.user_id] = float(rating.score)
    return matrix


def build_similarity_matrix(matrix: ItemUserMatrix) -> Dict[str, Dict[str, float]]:
    """
    строит матрицу сходства между фильмами на основе коэффициента Пирсона.
    
    аргументы:
        matrix (ItemUserMatrix): Матрица "фильм-пользователь".
    
    возвращает:
        Dict[str, Dict[str, float]]: Матрица сходства между фильмами.
    """
    items = list(matrix.keys())    # список всех фильмов (ключи из матрицы)
    similarity: Dict[str, Dict[str, float]] = {item: {} for item in items}   # инициализация словаря для сходства
    for i, item in enumerate(items): 
        for j in range(i + 1, len(items)):
            other = items[j]
            # вычисляем сходство между фильмами с использованием коэффициента Пирсона
            sim = pearson_similarity(matrix[item], matrix[other])
            similarity[item][other] = sim      # добавляем симметричное сходство
            similarity[other][item] = sim
    return similarity


def recommend_items_for_user(
    user_id: int,
    matrix: ItemUserMatrix,
    similarity_matrix: Dict[str, Dict[str, float]],
    k_neighbors: int = 20,
    top_n: int = 10,
) -> List[Recommendation]:
    """
    рекомендует фильмы пользователю на основе коллаборативной фильтрации (Item-Based CF)
    с использованием коэффициента Пирсона для определения схожести.
    
    аргументы:
        user_id (int): ID пользователя, для которого строятся рекомендации.
        matrix (ItemUserMatrix): матрица "фильм-пользователь".
        similarity_matrix (Dict[str, Dict[str, float]]): матрица сходства между фильмами.
        k_neighbors (int): количество ближайших соседей для каждого фильма (по умолчанию 20).
        top_n (int): Количество рекомендованных фильмов, которое нужно вернуть (по умолчанию 10).
    
    возвращает:
        List[Recommendation]: список рекомендаций для пользователя.
    """
    # получаем все фильмы, которые оценил пользователь
    user_ratings = {item: users[user_id] for item, users in matrix.items() if user_id in users}
    # если у пользователя нет оценок, возвращаем пустой список
    if not user_ratings:
        return []

    # словари для хранения итоговых оценок и весов фильмов
    scores: Dict[str, float] = defaultdict(float)
    weights: Dict[str, float] = defaultdict(float)

    # для каждого фильма, который оценил пользователь
    for item, rating in user_ratings.items():
        # получаем похожие фильмы
        neighbors = similarity_matrix.get(item, {})
        for other, sim in sorted(neighbors.items(), key=lambda x: x[1], reverse=True)[:k_neighbors]:
            # если пользователь уже оценил фильм, пропускаем его
            if user_id in matrix.get(other, {}):
                continue
            # если схожесть меньше или равна 0, пропускаем этот фильм
            if sim <= 0:
                continue
            # добавляем рейтинг с учетом схожести
            scores[other] += sim * rating
            weights[other] += abs(sim)   # веса для нормализации

    # формируем список рекомендаций, нормализуя оценки по весам
    recs: List[Recommendation] = []
    for item, score in scores.items():
        weight = weights[item]
        if weight == 0:  # если вес равен нулю, пропускаем фильм
            continue
        recs.append(Recommendation(item_id=item, score=score / weight))

    # сортируем рекомендации по убыванию оценок и возвращаем топ 
    recs.sort(key=lambda r: r.score, reverse=True)

    # возвращаем топ рекомендаций
    return recs[:top_n]
