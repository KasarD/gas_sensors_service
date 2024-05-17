import numpy as np
import pandas as pd

from itertools import combinations
from typing import List, Tuple
from sklearn.decomposition import PCA

from src.settings import CONFIG


def _euclidean(a: np.ndarray, b: np.ndarray) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def pca_transform(
    df_data: pd.DataFrame, materials: List[int]
) -> Tuple[np.ndarray, np.ndarray]:
    """Transform data from N space to 2 space"""
    pca = PCA(2)
    df = pca.fit_transform(df_data[materials])
    return df, df_data.Material.reset_index(drop=True)


def pca_estimate(arr: np.ndarray, y: pd.Series = None, only: str = None) -> float:
    """Here we can calculate mean euclidean data (below)"""
    _dist = []
    result = {}

    if only:
        one = y[y == only].index[0]
        a = arr[one]
        others = y[y != only].index

        for b in arr[others]:
            _dist.append(_euclidean(a, b))
    else:
        analytes = CONFIG.services.combinations.analytes
        idx_analytes = np.array(range(len(analytes)))
        arr = np.insert(arr, 2, idx_analytes, axis=1)
        for a, b in combinations(arr, 2):
            d = _euclidean(a[:2], b[:2])
            _dist.append(d)  # save to calculate mean and median
            result[f"{a[2].astype(int)} {b[2].astype(int)}"] = (
                d  # save to calculate distribution statistic across all combs in group
            )
    return {
        "median": np.median(_dist),
        "mean": np.mean(_dist),
        **result,
    }
