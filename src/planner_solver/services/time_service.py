from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from planner_solver.config.models import TimeConfig

class InternalTime(ABC):
    """
    Interface to define the time in my internal implementation
    """

    @abstractmethod
    def to_datetime(self) -> datetime:
        pass
    @abstractmethod
    def __str__(self) -> str:
        pass

    # region operations
    @abstractmethod
    def __sub__(self, other: 'InternalTime') -> timedelta:
        pass
    # endregion operations

class ContinuousTime(InternalTime):
    """
    this implementation simply wraps a datetime
    """
    def __init__(self, value: datetime):
        self.__value = value

    def to_datetime(self) -> datetime:
        return self.__value
    
    def __str__(self) -> str:
        return self.__value.strftime('%Y-%m-%d %H:%M:%S')

    def __sub__(self, other: InternalTime) -> timedelta:
        return self.__value - other.to_datetime()

class DiscreteTime(InternalTime):
    """
    this implementation wraps an integer.
    Beware! without the time config, this has no sense
    """
    def __init__(self, value: int, config: TimeConfig):
        self.__value = value
        self.__config = config
    
    @staticmethod
    def from_datetime(date: datetime, config: TimeConfig) -> 'DiscreteTime':
        epoch_datetime = config.get_epoch_datetime()
        seconds_diff = (date - epoch_datetime).total_seconds()

        delta_diff = config.round_to_int(seconds_diff / config.delta_time)

        return DiscreteTime(
            config=config,
            value=delta_diff
        )
    
    def to_datetime(self) -> datetime:
        epoch = self.__config.get_epoch_datetime()
        delta_seconds = self.__config.delta_time * self.__value

        return epoch + timedelta(seconds=delta_seconds)
    
    def __str__(self) -> str:
        return self.to_datetime().strftime('%Y-%m-%d %H:%M:%S')
    
    def __sub__(self, other: InternalTime) -> timedelta:
        """
        beware! maybe I will need to optimize this later
        """
        return self.to_datetime() - other.to_datetime()

class TimeService:
    """
    A singleton service to create the InternalTime objects
    """
    def __init__(self, config: TimeConfig):
        self.__config = config
        pass

    def convert(self, date: datetime) -> InternalTime:
        if self.__config.type == 'discrete':
            return DiscreteTime.from_datetime(date=date, config=self.__config)
        if self.__config.type == 'continuous':
            return ContinuousTime(date)
        raise Exception("unrecognized %s, type must either be 'discrete' or 'continuous'" % (self.__config.type))
