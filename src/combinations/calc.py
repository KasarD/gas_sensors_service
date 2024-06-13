import io
import logging
import pandas as pd

from itertools import combinations
from src.dao.redis import JobDescription
from src.combinations import features
from src.combinations.entities import CombinationsConfig
from src.settings import CONFIG
from src.globals import GLOBALS


logger = logging.getLogger("custom")


def transform_data(df_data: pd.DataFrame, analytes: list[str]) -> pd.DataFrame:
    """Just transparent df_data"""
    df_data_T = df_data[analytes].T
    df_data_T["Material"] = df_data_T.index
    return df_data_T


def calculate_stats(
    job_uuid: str, df_data_T: pd.DataFrame, min_sensors: int, max_sensors: int
) -> list[dict]:
    result = []
    total = max_sensors - min_sensors + 1
    for idx, count in enumerate(range(min_sensors, max_sensors + 1)):
        GLOBALS.redis.update_job_progress(job_uuid, round(idx / total, 2))
        for sensors in combinations(CONFIG.services.combinations.sensors, count):
            tr, _ = features.pca_transform(df_data_T, list(sensors))
            info = features.pca_estimate(tr)
            result.append(
                {
                    "sensors": sensors,
                    **info,
                }
            )
    GLOBALS.redis.update_job_progress(job_uuid, 1)
    return result


def process(desc: JobDescription):
    """Request handler from Flask router

    Args:
        data (str): a stringify representation of csv data
        config (CombinationsConfig): config to process csv
    """
    data: str = desc.data
    config: CombinationsConfig = desc.config

    df_data = pd.read_csv(io.StringIO(data))
    logger.info("Dataframe shape: %s", df_data.shape)
    df_T = transform_data(df_data, CONFIG.services.combinations.analytes)

    result = calculate_stats(
        desc.job_uuid, df_T, config.min_sensors, config.max_sensors
    )
    GLOBALS.redis.set_job_results(desc.job_uuid, result)
    if CONFIG.creds.dump_results:
        GLOBALS.files.dump_job_results(desc.job_uuid, result)


def get_best_worst_combs(results: list[dict]) -> dict:
    df = pd.DataFrame(results)
    best = df.loc[df["median"].idxmax()]
    worst = df.loc[df["median"].idxmin()]
    return {
        "best": {"sensors": best.sensors, "mean median": round(best["median"], 3)},
        "worst": {"sensors": worst.sensors, "mean median": round(worst["median"], 3)},
    }
