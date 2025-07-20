from typing import Literal, Optional
from math import ceil, floor
from datetime import datetime
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class TimeConfig(BaseSettings):
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