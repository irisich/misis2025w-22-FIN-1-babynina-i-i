from typing import Dict, List, Optional
from dataset import dataset_preprocessing, normalize_movie, GENRES
from .schemas import Rating

_ratings_df = None
_movies_df = None
_display_map: Dict[str, str] = {}
_avg_ratings: Dict[int, float] = {}


def load_dataset():
    """Load and cache ratings/movies dataframes."""
    global _ratings_df, _movies_df, _display_map
    if _ratings_df is None or _movies_df is None:
        _ratings_df, _movies_df = dataset_preprocessing()
        avg = _ratings_df.groupby("item_id")["rating"].mean().to_dict()
        global _avg_ratings
        _avg_ratings = avg
        _display_map = {
            row.normalized_title: f"{row.title_no_year.title()} ({row.year})"
            for row in _movies_df.itertuples()
            if isinstance(row.normalized_title, str) and row.normalized_title
        }
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


def list_genres() -> List[str]:
    """List available genres (from MovieLens)."""
    return GENRES


def top_movies_by_genre(genre: str, top_n: int = 10) -> List[str]:
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
    titles: List[str] = sorted_movies["normalized_title"].tolist()
    return [t for t in titles if isinstance(t, str) and t][:top_n]
