import os
import pickle
from typing import Any
from src.settings import FilesConfig


class FilesDAO:
    def __init__(self, config: FilesConfig):
        self.config = config

    def load_job_results(self, job_uuid: str) -> Any:
        with open(os.path.join(self.config.dump_folder, job_uuid), "rb") as fp:
            result = pickle.load(fp)
        return result

    def dump_job_results(self, job_uuid: str, result: Any):
        with open(os.path.join(self.config.dump_folder, job_uuid), "wb") as fp:
            pickle.dump(result, fp)
