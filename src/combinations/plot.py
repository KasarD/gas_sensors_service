import io
import base64
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


def pca_print(transformed: np.ndarray, y: np.ndarray, ax=None):
    if not ax:
        _, ax = plt.subplots(figsize=(15, 7))
    ax.scatter(transformed[:, 0], transformed[:, 1])


def to_base64(fig: Figure) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="jpg")
    buf.seek(0)
    data = base64.b64encode(buf.read()).decode()
    return data


def max_min_spread(results: list[dict]) -> Figure:
    # How worst-best spread changes according to count of materials in group?

    df_result = pd.DataFrame(results)
    df_result["count"] = df_result.sensors.apply(lambda tpl: len(tpl))
    materials_cnt = []  # materials on chip
    min_max_delta = []  # spread between min & max
    min_cnt, max_cnt = df_result["count"].min(), df_result["count"].max()
    for cnt in range(min_cnt, max_cnt):
        df = df_result[df_result["count"] == cnt]
        materials_cnt.append(cnt)
        min_max_delta.append(df["median"].max() - df["median"].min())

    fig, ax = plt.subplots(figsize=(15, 7))
    ax.bar(materials_cnt, min_max_delta)
    ax.set_xticks(range(3, 18))
    ax.set_title("Max-min spread depends on combination size")
    ax.set_ylabel("Max-min spread (after PCA transform)")
    ax.set_xlabel("Combination size (count of materials)")
    ax.grid()
    return fig
