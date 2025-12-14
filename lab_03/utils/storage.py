from typing import Dict, Iterable, List, Tuple
from .schemas import Rating, Recommendation
from . import cf

class RecommendationStorage:
    # класс для хранения рейтингов и предварительно вычисленных схожестей фильмов в памяти.    def __init__(self) -> None:
    # инициализация пустых атрибутов для матрицы "фильм-пользователь" и матрицы схожести
    def __init__(self) -> None:
        self.item_user: cf.ItemUserMatrix = {}    # матрица, где ключ — ID фильма, а значение — словарь с рейтингами пользователей
        self.similarity: Dict[str, Dict[str, float]] = {}    # матрица схожести между фильмами

    def add_rating(self, rating: Rating) -> None:
        """
        добавляет новый рейтинг в хранилище.
        
        аргументы:
            rating (Rating): объект, содержащий информацию о фильме, пользователе и оценке
        """
        # добавление нового рейтинга в матрицу "фильм-пользователь"
        self.item_user.setdefault(rating.item_id, {})[rating.user_id] = float(rating.score)

    def load_bulk(self, ratings: Iterable[Rating]) -> None:
        """
        загружает несколько рейтингов в хранилище и пересчитывает схожести.
        
        аргументы:
            ratings (Iterable[Rating]): объект с рейтингами, которые нужно добавить.
        """
        # для каждого рейтинга добавляем его в хранилище
        for rating in ratings:
            self.add_rating(rating)
        # пересчитываем матрицу схожести между фильмами после загрузки всех рейтингов
        self.recompute_similarity()

    def recompute_similarity(self) -> None:
        """
        пересчитывает матрицу схожести между фильмами с использованием коллаборативной фильтрации
        """
        # пересчитываем схожесть, используя метод build_similarity_matrix из модуля cf
        self.similarity = cf.build_similarity_matrix(self.item_user) if self.item_user else {}

    def recommend_for_user(self, user_id: int, k_neighbors: int = 20, top_n: int = 10) -> List[Recommendation]:
        """
        рекомендует фильмы пользователю на основе коллаборативной фильтрации с использованием коэффициента Пирсона
        
        аргументы:
            user_id (int): ID пользователя, для которого генерируются рекомендации
            k_neighbors (int): количество ближайших соседей для каждого фильма
            top_n (int): количество фильмов, которые нужно вернуть в списке рекомендаций

        возвращает:
            List[Recommendation]: список рекомендаций для пользователя
        """
        # если схожесть еще не была вычислена, пересчитываем её
        if not self.similarity:
            self.recompute_similarity()

        # если схожесть не была вычислена, возвращаем пустой список
        if not self.similarity:
            return []
        
        # вызываем функцию из модуля cf для получения рекомендаций для пользователя
        return cf.recommend_items_for_user(
            user_id=user_id,
            matrix=self.item_user,
            similarity_matrix=self.similarity,
            k_neighbors=k_neighbors,
            top_n=top_n,
        )

    def similar_items(self, item_id: str, top_n: int = 10) -> List[Tuple[str, float]]:
        """
        возвращает топ-N самых похожих фильмов для заданного фильма, используя предварительно вычисленную матрицу сходства.

        аргументы:
            item_id (str): ID фильма, для которого ищем похожие фильмы.
            top_n (int): количество фильмов, которые нужно вернуть.

        возвращает:
            List[Tuple[str, float]]: список фильмов, похожих на заданный, с их коэффициентом сходства.
        """
        # получаем схожесть с другими фильмами для данного фильма
        sims: Dict[str, float] = self.similarity.get(item_id, {})
        
        # если нет схожести для данного фильма, возвращаем пустой список
        if not sims:
            return []
        
        # сортируем фильмы по коэффициенту сходства и возвращаем топ-N
        sorted_items: List[Tuple[str, float]] = sorted(sims.items(), key=lambda x: x[1], reverse=True)
        return sorted_items[:top_n]

# глобальный объект для хранения рекомендаций
rating_storage = RecommendationStorage()

# функции-обертки для работы с хранилищем рекомендаций
def add_rating(rating: Rating) -> None:
    """
    добавляет рейтинг в глобальное хранилище
    
    аргументы:
        rating (Rating): объект рейтинга, который добавляется в хранилище
    """
    rating_storage.add_rating(rating)


def load_base_ratings(ratings: Iterable[Rating]) -> None:
    """
    загружает несколько рейтингов в хранилище и пересчитывает матрицу сходства
    
    аргументы:
        ratings (Iterable[Rating]): объект с рейтингами, которые загружаются в хранилище
    """
    rating_storage.load_bulk(ratings)


def recommend_for_user(user_id: int, k_neighbors: int = 20, top_n: int = 10) -> List[Recommendation]:
    """
    получает рекомендации для пользователя на основе коллаборативной фильтрации
    
    аргументы:
        user_id (int): ID пользователя, для которого генерируются рекомендации
        k_neighbors (int): количество ближайших соседей для фильмов
        top_n (int): количество рекомендаций, которые нужно вернуть

    возвращает:
        List[Recommendation]: список рекомендованных фильмов для пользователя
    """
    return rating_storage.recommend_for_user(user_id, k_neighbors=k_neighbors, top_n=top_n)


def similar_items(item_id: str, top_n: int = 10) -> List[Tuple[str, float]]:
    """
    возвращает похожие фильмы для заданного фильма
    
    аргументы:
        item_id (str): ID фильма, для которого ищем похожие фильмы
        top_n (int): количество похожих фильмов, которое нужно вернуть

    возвращает:
        List[Tuple[str, float]]: список похожих фильмов с коэффициентами сходства
    """
    return rating_storage.similar_items(item_id=item_id, top_n=top_n)
