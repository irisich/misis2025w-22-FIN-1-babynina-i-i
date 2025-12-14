import math
from typing import Dict


def pearson_similarity(vec_a: Dict[int, float], vec_b: Dict[int, float]) -> float:
    """Compute Pearson correlation between two item rating vectors."""
    common_users = set(vec_a) & set(vec_b)
    n = len(common_users)
    if n < 2:
        return 0.0

    mean_a = sum(vec_a[u] for u in common_users) / n
    mean_b = sum(vec_b[u] for u in common_users) / n

    num = sum((vec_a[u] - mean_a) * (vec_b[u] - mean_b) for u in common_users)
    den_a = math.sqrt(sum((vec_a[u] - mean_a) ** 2 for u in common_users))
    den_b = math.sqrt(sum((vec_b[u] - mean_b) ** 2 for u in common_users))
    if den_a == 0 or den_b == 0:
        return 0.0
    return num / (den_a * den_b)
