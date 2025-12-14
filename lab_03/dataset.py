from pathlib import Path
import logging
import re
from typing import Tuple, List
import pandas as pd

logging.basicConfig(level=logging.INFO)
DATA_DIR: Path = Path(__file__).parent / "data"
U_DATA_FILE: Path = DATA_DIR / "u.data"
U_ITEM_FILE: Path = DATA_DIR / "u.item"

GENRES: List[str] = [
    "unknown", "Action", "Adventure", "Animation", "Children's", "Comedy", "Crime",
    "Documentary", "Drama", "Fantasy", "Film-Noir", "Horror", "Musical",
    "Mystery", "Romance", "Sci-Fi", "Thriller", "War", "Western"
]

def normalize_movie(title: str) -> str:
    """
    Нормализует название фильма для поиска.
    - Преобразует строку в нижний регистр.
    - Убирает год выпуска, если он указан в скобках в названии (например, "The Matrix (1999)" станет "the matrix").
    - Убирает лишние пробелы в начале и конце.
    
    Аргументы:
        title (str): исходное название фильма

    Возвращает:
        str: нормализованное название
    """
    if title is None:
        return ""
    s: str = str(title).lower().strip()
    s = re.sub(r"\(\d{4}\)", "", s).strip()
    return s


def dataset_preprocessing() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Загружает u.data и u.item и возвращает DataFrame с рейтингами и фильмами.

    Возвращает:
        Tuple[pd.DataFrame, pd.DataFrame]: (ratings_df, movies_df)
    """
    logging.info("Загрузка оценки пользователей (u.data)")
    ratings_cols: List[str] = ["user_id", "item_id", "rating", "timestamp"]
    ratings: pd.DataFrame = pd.read_csv(U_DATA_FILE, sep="\t", names=ratings_cols, encoding="latin-1")

    logging.info("Загрузка информации о фильмах и жанрах (u.item)")
    movies_raw: pd.DataFrame = pd.read_csv(U_ITEM_FILE, sep="|", header=None, encoding="latin-1", low_memory=False)
    expected_cols = 5 + len(GENRES)
    if movies_raw.shape[1] < expected_cols:
        for i in range(movies_raw.shape[1], expected_cols):
            movies_raw[i] = None

    cols: List[str] = ["movie_id", "title", "release_date", "video_release_date", "imdb_url"] + GENRES
    movies: pd.DataFrame = movies_raw.iloc[:, :len(cols)].copy()
    movies.columns = cols

    movies["title_no_year"] = movies["title"].astype(str).str.replace(r"\(\d{4}\)", "", regex=True).str.strip()
    movies["normalized_title"] = movies["title_no_year"].apply(normalize_movie)
    movies["year"] = movies["release_date"].astype(str).str.extract(r"(\d{4})", expand=False).fillna("0000")

    return ratings, movies


def build_matrix(ratings: pd.DataFrame, movies: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    строит матрицу item-user (строки = normalized_title, колонки = user_id)

    аргументы:
        ratings (pd.DataFrame): таблица с рейтингами
        movies (pd.DataFrame): таблица с фильмами

    возвращает:
        Tuple[pd.DataFrame, List[str]]: (item_feature_matrix, item_names)
    """
    logging.info("Построение (item x user) матрицы...")
    merged: pd.DataFrame = ratings.merge(
        movies[["movie_id", "normalized_title"]],
        left_on="item_id",
        right_on="movie_id",
        how="left"
    )

    item_feature_matrix: pd.DataFrame = merged.pivot_table(
        index="normalized_title",
        columns="user_id",
        values="rating",
        aggfunc="mean",
        fill_value=0
    )

    item_names: List[str] = item_feature_matrix.index.tolist()
    logging.info("Построена матрица: %d items x %d users", *item_feature_matrix.shape)
    return item_feature_matrix, item_names
