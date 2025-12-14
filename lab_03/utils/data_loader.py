from typing import Dict, List, Optional, Tuple
from dataset import dataset_preprocessing, normalize_movie, GENRES
from .schemas import Rating

_ratings_df = None
_movies_df = None
_display_map: Dict[str, str] = {}
_avg_ratings: Dict[int, float] = {}
_movie_meta: Dict[str, Dict[str, object]] = {}


def load_dataset():
    """Load and cache ratings/movies dataframes."""
    global _ratings_df, _movies_df, _display_map, _avg_ratings, _movie_meta
    if _ratings_df is None or _movies_df is None:
        _ratings_df, _movies_df = dataset_preprocessing()
        _avg_ratings = _ratings_df.groupby("item_id")["rating"].mean().to_dict()
        _display_map = {}
        _movie_meta = {}
        for _, row in _movies_df.iterrows():
            normalized_title = row.get("normalized_title")
            if not (isinstance(normalized_title, str) and normalized_title):
                continue
            title_no_year = str(row.get("title_no_year", "")).title()
            year = row.get("year", "0000")
            display = f"{title_no_year} ({year})"
            _display_map[normalized_title] = display
            genres = [g for g in GENRES if row.get(g, 0) == 1]
            avg = float(_avg_ratings.get(row.get("movie_id"), 0.0))
            _movie_meta[normalized_title] = {"display": display, "genres": genres, "avg": avg}
    return _ratings_df, _movies_df


def load_movielens_ratings() -> List[Rating]:
    """Load base ratings from the bundled MovieLens subset."""
    ratings_df, movies_df = load_dataset()
    merged = ratings_df.merge(
        movies_df[["movie_id", "normalized_title"]],
        left_on="item_id",
        right_on="movie_id",
        how="left",
    )
    merged["normalized_title"] = merged["normalized_title"].fillna(merged["item_id"].astype(str))

    result: List[Rating] = []
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
    """Find a normalized_title by fuzzy match (substring) after normalization."""
    _, movies_df = load_dataset()
    needle = normalize_movie(name)
    if not needle:
        return None
    for nm in movies_df["normalized_title"]:
        if isinstance(nm, str) and needle in nm:
            return nm
    return None


def display_title(normalized_title: str) -> str:
    """Pretty display for normalized title."""
    if not _display_map:
        load_dataset()
    return _display_map.get(normalized_title, normalized_title)


def get_movie_info(normalized_title: str) -> Tuple[str, List[str], float]:
    """Return display title, genres list, and average rating for the movie."""
    if not _movie_meta:
        load_dataset()
    meta = _movie_meta.get(normalized_title)
    if not meta:
        return normalized_title, [], 0.0
    return str(meta["display"]), list(meta["genres"]), float(meta["avg"])


def format_movie_line(normalized_title: str, rating: Optional[float] = None) -> str:
    """Format movie line with title, genres, and rating."""
    display, genres, avg = get_movie_info(normalized_title)
    genres_text = ", ".join(genres) if genres else "жанр не указан"
    score = rating if rating is not None else avg
    return f"{display} — жанры: {genres_text} — рейтинг {score:.2f}"


def list_genres() -> List[str]:
    """List available genres (from MovieLens)."""
    return GENRES


def top_movies_by_genre(genre: str, top_n: int = 10) -> List[Tuple[str, float]]:
    """Return top movies by average rating within a genre."""
    _, movies_df = load_dataset()
    genre_clean = genre.strip()
    genre_match = None
    for g in GENRES:
        if g.lower() == genre_clean.lower():
            genre_match = g
            break
    if not genre_match:
        return []

    filtered = movies_df[movies_df[genre_match] == 1]
    # Attach average ratings and sort
    filtered = filtered.copy()
    filtered["avg_rating"] = filtered["movie_id"].map(_avg_ratings).fillna(0.0)
    sorted_movies = filtered.sort_values(by="avg_rating", ascending=False)
    result: List[Tuple[str, float]] = []
    for row in sorted_movies.itertuples():
        if isinstance(row.normalized_title, str) and row.normalized_title:
            result.append((row.normalized_title, float(row.avg_rating)))
            if len(result) >= top_n:
                break
    return result
