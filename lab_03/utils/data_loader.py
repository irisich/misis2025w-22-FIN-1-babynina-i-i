from typing import Dict, List, Optional, Tuple
from dataset import dataset_preprocessing, normalize_movie, GENRES
from .schemas import Rating

# глобальные переменные для хранения данных о фильмах и рейтингах
_ratings_df = None
_movies_df = None
_display_map: Dict[str, str] = {}
_avg_ratings: Dict[int, float] = {}
_movie_meta: Dict[str, Dict[str, object]] = {}


def load_dataset():
    """
    загружает и кеширует данные о рейтингах и фильмах.

    при первом вызове функции загружает данные, рассчитывает средний рейтинг для каждого фильма,
    создает отображение нормализованных названий фильмов в формат для отображения, 
    а также собирает метаинформацию о фильмах (жанры и средний рейтинг).

    возвращает:
        Tuple[pd.DataFrame, pd.DataFrame]: два датафрейма: _ratings_df (рейтинг пользователей) и _movies_df (фильмы)
    """
    global _ratings_df, _movies_df, _display_map, _avg_ratings, _movie_meta
    if _ratings_df is None or _movies_df is None:
        # загрузка данных с использованием функции dataset_preprocessing
        _ratings_df, _movies_df = dataset_preprocessing()
        
        # рассчитываем средний рейтинг для каждого фильма
        _avg_ratings = _ratings_df.groupby("item_id")["rating"].mean().to_dict()
        
        # инициализация пустых словарей для отображения информации о фильмах
        _display_map = {}
        _movie_meta = {}
        # заполнение отображений для каждого фильма
        for _, row in _movies_df.iterrows():
            normalized_title = row.get("normalized_title")
            if not (isinstance(normalized_title, str) and normalized_title):
                continue
            # формирование строкового отображения названия фильма с годом
            title_no_year = str(row.get("title_no_year", "")).title()
            year = row.get("year", "0000")
            display = f"{title_no_year} ({year})"
            _display_map[normalized_title] = display
            
            # составление списка жанров для каждого фильма
            genres = [g for g in GENRES if row.get(g, 0) == 1]
            
            # получение среднего рейтинга фильма
            avg = float(_avg_ratings.get(row.get("movie_id"), 0.0))
            
            # добавление метаинформации о фильме
            _movie_meta[normalized_title] = {"display": display, "genres": genres, "avg": avg}
    return _ratings_df, _movies_df


def load_movielens_ratings() -> List[Rating]:
    """
    загружает базовые рейтинги из предварительно загруженного датасета MovieLens.

    функция объединяет данные о рейтингах пользователей с фильмами, добавляет нормализованные названия
    и возвращает список объектов Rating для дальнейшей работы.

    возвращает:
        List[Rating]: список объектов Rating с информацией о пользователе, фильме и рейтинге.
    """
    ratings_df, movies_df = load_dataset()   # загружаем данные о фильмах и рейтингах
    # объединяем данные о фильмах и их оценках
    merged = ratings_df.merge(
        movies_df[["movie_id", "normalized_title"]],
        left_on="item_id",
        right_on="movie_id",
        how="left",
    )
    # заполняем нормализованные названия, если они отсутствуют
    merged["normalized_title"] = merged["normalized_title"].fillna(merged["item_id"].astype(str))

    result: List[Rating] = []
    # перебираем объединенные строки и создаем объекты Rating
    for row in merged.itertuples():
        result.append(
            Rating(
                user_id=int(row.user_id),
                item_id=str(row.normalized_title),
                score=float(row.rating),
            )
        )
    return result


def find_movie_by_name(name: str) -> Optional[str]:
    """
    ищет фильм по части названия, используя нестрогое сопоставление (substring matching) после нормализации.

    аргументы:
        name (str): название фильма, которое нужно найти.

    возвращает:
        Optional[str]: нормализованное название фильма, если найдено. В противном случае возвращает None.
    """
    _, movies_df = load_dataset()
    # нормализуем название фильма перед поиском
    needle = normalize_movie(name)
    if not needle:
        return None
     # ищем фильм по нормализованному названию
    for nm in movies_df["normalized_title"]:
        if isinstance(nm, str) and needle in nm:
            return nm
    return None


def display_title(normalized_title: str) -> str:
    """
    форматирует нормализованное название фильма для отображения.

    аргументы:
        normalized_title (str): нормализованное название фильма.

    возвращает:
        str: отформатированное название фильма для отображения.
    """
    if not _display_map:
        load_dataset()    # загружаем данные, если они еще не загружены
    return _display_map.get(normalized_title, normalized_title)


def get_movie_info(normalized_title: str) -> Tuple[str, List[str], float]:
    """
    возвращает отображаемое название фильма, список жанров и средний рейтинг.

    аргументы:
        normalized_title (str): нормализованное название фильма.

    возвращает:
        Tuple[str, List[str], float]: отображаемое название, список жанров и средний рейтинг фильма.
    """
    if not _movie_meta:
        load_dataset()    # загружаем метаинформацию о фильмах
    meta = _movie_meta.get(normalized_title)
    if not meta:
        return normalized_title, [], 0.0
    return str(meta["display"]), list(meta["genres"]), float(meta["avg"])


def format_movie_line(normalized_title: str, rating: Optional[float] = None) -> str:
    """
    форматирует строку фильма с названием, жанрами и рейтингом.

    аргументы:
        normalized_title (str): нормализованное название фильма.
        rating (Optional[float]): рейтинг фильма. если не передан, используется средний рейтинг.

    возвращает:
        str: отформатированная строка фильма.
    """
    display, genres, avg = get_movie_info(normalized_title)
    genres_text = ", ".join(genres) if genres else "жанр не указан"
    score = rating if rating is not None else avg
    return f"{display} — жанры: {genres_text} — рейтинг {score:.2f}"


def list_genres() -> List[str]:
    """
    возвращает список доступных жанров (из MovieLens).

    возвращает:
        List[str]: список жанров.
    """
    return GENRES


def top_movies_by_genre(genre: str, top_n: int = 10) -> List[Tuple[str, float]]:
    """
    возвращает топ фильмов по среднему рейтингу в заданном жанре.

    аргументы:
        genre (str): жанр для поиска.
        top_n (int): количество фильмов, которое нужно вернуть.

    возвращает:
        List[Tuple[str, float]]: список кортежей, где первый элемент — это название фильма, а второй — его рейтинг.
    """
    _, movies_df = load_dataset()
    genre_clean = genre.strip()
    genre_match = None
    # ищем подходящий жанр в списке доступных жанров
    for g in GENRES:
        if g.lower() == genre_clean.lower():
            genre_match = g
            break
    if not genre_match:
        return []    # возвращаем пустой список, если жанр не найден

    # фильтруем фильмы по жанру
    filtered = movies_df[movies_df[genre_match] == 1]
    # добавляем средние рейтинги и сортируем
    filtered = filtered.copy()
    filtered["avg_rating"] = filtered["movie_id"].map(_avg_ratings).fillna(0.0)
    sorted_movies = filtered.sort_values(by="avg_rating", ascending=False)
    # добавляем фильмы в результат
    result: List[Tuple[str, float]] = []
    for row in sorted_movies.itertuples():
        if isinstance(row.normalized_title, str) and row.normalized_title:
            result.append((row.normalized_title, float(row.avg_rating)))
            if len(result) >= top_n:
                break
    return result
