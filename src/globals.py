from src.dao.redis import RedisDAO
from src.dao.files import FilesDAO
from src.settings import CONFIG


class Globals:
    def __init__(self):
        self._redis: RedisDAO = None
        self._files: FilesDAO = None

    @property
    def redis(self) -> RedisDAO:
        if not self._redis:
            self._redis = RedisDAO(CONFIG.creds.redis)
        return self._redis

    @property
    def files(self) -> FilesDAO:
        if not self._files:
            self._files = FilesDAO(CONFIG.creds.files)
        return self._files

    def shutdown(self):
        if self._redis:
            self._redis.shutdown()


GLOBALS = Globals()
