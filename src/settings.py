import yaml

from logging.config import dictConfig
from dataclasses import dataclass


@dataclass
class Combinations:
    analytes: list[str]
    sensors: list[int]

    @classmethod
    def from_dict(cls, data: dict) -> "Combinations":
        return cls(data["analytes"], data["sensors"])


@dataclass
class Services:
    combinations: Combinations

    @classmethod
    def from_dict(cls, data: dict) -> "Services":
        comb = Combinations.from_dict(data["combinations"])
        return cls(comb)


@dataclass
class RedisConfig:
    host: str
    port: int
    db: int

    @classmethod
    def from_dict(cls, data: dict) -> "RedisConfig":
        return cls(**data)


@dataclass
class FilesConfig:
    dump_folder: str


@dataclass
class Creds:
    redis: RedisConfig
    files: FilesConfig
    dump_results: bool

    @classmethod
    def from_dict(cls, data: dict) -> "Creds":
        redis = RedisConfig.from_dict(data["redis"])
        files = FilesConfig(data["files_dump_folder"])
        return cls(redis, files, data["dump_results"])


@dataclass
class Config:
    creds: Creds
    services: Services

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        creds = Creds.from_dict(data["creds"])
        services = Services.from_dict(data["services"])
        return cls(creds, services)


with open("./config/config.yaml", encoding="UTF-8") as fp:
    dct = yaml.safe_load(fp)
    CONFIG = Config.from_dict(dct)


with open("./config/logging.yaml", encoding="UTF-8") as fp:
    log = yaml.safe_load(fp)
    dictConfig(log)


__all__ = ["CONFIG"]
