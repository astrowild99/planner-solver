import logging
from typing import Literal, Optional, Type, List
from math import ceil, floor
from datetime import datetime
from pydantic import Field, BaseModel
from pydantic_settings import SettingsConfigDict, YamlConfigSettingsSource
from pydantic_settings_yaml import YamlBaseSettings

class LoggingConfig(YamlBaseSettings):
    """
    To set the logging behavior
    """

    model_config = SettingsConfigDict(
        yaml_file="configs/logging.yaml",
        env_prefix="LOGGING_",
        case_sensitive=False
    )

    level: str

    def get_logger_level(self) -> int:
        if self.level == "DEBUG":
            return logging.DEBUG
        if self.level == "INFO":
            return logging.INFO
        if self.level == "WARNING":
            return logging.WARNING
        if self.level == "ERROR":
            return logging.ERROR
        if self.level == "CRITICAL":
            return logging.CRITICAL
        return logging.NOTSET

class TimeConfig(YamlBaseSettings):
    """
    These are the config that will be present in either a .env or a .yaml config provided to the system

    When timing is continuous, I will keep the standard python way of handling the time, using the epoch of the system

    When timing is discrete instead, I will set a custom epoch, a delta time interval and a rounding strategy
    """

    model_config = SettingsConfigDict(
        yaml_file="configs/time.yaml",
        env_prefix="TIME_",
        case_sensitive=False
    )

    type: Literal['continuous', 'discrete'] = Field()
    # region discrete
    
    delta_time: Optional[int] = Field(default=1) # seconds
    epoch: Optional[str] = Field(default='1970-01-01 00:00:00') # in format 2025-01-01 00:00:00, useful to keep the calculations simpler
    rounding_strategy: Optional[Literal['round', 'floor', 'ceil']] = Field(default='round') 

    def get_epoch_datetime(self) -> datetime:
        return datetime.strptime(self.epoch, '%Y-%m-%d %H:%M:%S')
    
    def round_to_int(self, val: int | float) -> int:
        if self.rounding_strategy == 'round':
            return round(val)
        if self.rounding_strategy == 'ceil':
            return ceil(val)
        if self.rounding_strategy == 'floor':
            return floor(val)
    
    # endregion discrete

class ModuleConfig(YamlBaseSettings):
    """
    module loader service config
    """
    model_config = SettingsConfigDict(
        yaml_file="configs/modules.yaml",
        env_prefix="MODULE_",
        case_sensitive=False
    )

    # module path will be considered from the current working directly if not absolute
    module_paths: List[str] = [] # by default, the base modules will always be loaded.

class RabbitmqConnectionConfig(BaseModel):
    host: str
    port: str | int
    username: str
    password: str

class RabbitmqConfig(YamlBaseSettings):
    """
    rabbitmq service config
    """
    model_config = SettingsConfigDict(
        yaml_file="configs/rabbitmq.yaml",
        env_prefix="RABBITMQ_",
        case_sensitive=False
    )

    connection: RabbitmqConnectionConfig

class MongodbConnectionConfig(BaseModel):
    host: str
    port: str | int
    username: str
    password: str
    database: str

class MongodbConfig(YamlBaseSettings):
    """
    mongodb service config
    """
    model_config = SettingsConfigDict(
        yaml_file="configs/mongodb.yaml",
        env_prefix="MONGODB_",
        case_sensitive=False
    )

    connection: MongodbConnectionConfig