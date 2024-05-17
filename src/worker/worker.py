"""Worker to handle a long-running jobs"""

import logging
import multiprocessing as mp

from typing import Callable, Any
from src.globals import GLOBALS


logger = logging.getLogger("custom")


def handler(target: Callable, job_uuid: str):
    desc = GLOBALS.redis.get_job(job_uuid)
    target(desc)


class Worker:
    def __init__(self, pool_size: int):
        self.pool = mp.Pool(pool_size)

    def commit_job(self, target: Callable, data: Any, config: Any) -> str:
        job_uuid = GLOBALS.redis.create_job(data, config)
        self.pool.apply_async(handler, (target, job_uuid))
        # handler(target, job_uuid)
        return job_uuid

    def shutdown(self):
        self.pool.close()
        self.pool.join()
