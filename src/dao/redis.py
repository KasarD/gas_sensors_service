import redis
import pickle
import uuid
import logging

from typing import Any
from dataclasses import dataclass
from src.settings import RedisConfig


logger = logging.getLogger("custom")


@dataclass
class JobDescription:
    job_uuid: str
    data: Any
    config: Any

    def to_dict(self) -> dict:
        return {"data": self.data, "config": self.config}


class RedisDAO:
    create_key = "%s_data"
    progress_key = "%s_progress"
    result_key = "%s_result"

    def __init__(self, config: RedisConfig):
        self.config = config
        self._client = None

    @property
    def client(self) -> redis.Redis:
        if not self._client:
            self._client = redis.Redis(
                self.config.host, self.config.port, self.config.db
            )
        return self._client

    def create_job(self, data: Any, config: Any) -> str:
        job_uuid = uuid.uuid4().hex
        key = self.create_key % job_uuid
        desc = JobDescription(job_uuid, data, config)
        value = pickle.dumps(desc.to_dict())
        self.client.set(key, value)
        logger.debug("job key %s has been set", key)
        return job_uuid

    def get_job(self, job_uuid: str) -> JobDescription:
        value_bytes = self.client.get(self.create_key % job_uuid)
        dct = pickle.loads(value_bytes)
        logger.debug("job %s data has been loaded", job_uuid)
        return JobDescription(job_uuid, **dct)

    def set_job_results(self, job_uuid: str, value: Any):
        value_bytes = pickle.dumps(value)
        self.client.expire(self.create_key % job_uuid, 5 * 60)
        self.client.expire(self.progress_key % job_uuid, 5 * 60)
        self.client.set(self.result_key % job_uuid, value_bytes, ex=5 * 60)
        logger.debug("result for job %s has been set", job_uuid)

    def get_job_results(self, job_uuid: str) -> Any:
        value_bytes = self.client.get(self.result_key % job_uuid)
        logger.debug("result for job %s has been extracted", job_uuid)
        if not value_bytes:
            return None
        return pickle.loads(value_bytes)

    def update_job_progress(self, job_uuid: str, value: float):
        key = f"{job_uuid}_progress"
        self.client.set(key, value)
        logger.debug("progress for job %s has been updated by %s", job_uuid, value)

    def get_job_progress(self, job_uuid: str) -> float:
        key = f"{job_uuid}_progress"
        logger.debug("progress for job %s has been loaded", job_uuid)
        return float(self.client.get(key))

    def shutdown(self):
        if self._client:
            self._client.close()
