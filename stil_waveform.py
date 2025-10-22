# standard packages
from enum import Enum
from typing import TypeVar, Generic, List, Dict


# local packages
from stil.stil_signal import StilSignalType
from stil.stil_signal_group import StilSignalGroup


class StilTimingInCondition(Enum):
    ZERO = "0"
    ONE = "1"
    UNKNOWN = "N"


class StilForce(Enum):
    UP = "U"
    DOWN = "D"
    NONE = "N"


class StilCompare(Enum):
    HIGH = "H"
    LOW = "L"
    DONT_CARE = "X"
    HIGH_IMPEDANCE = "T"


class StilTimingOutCondition(Enum):
    HIGH = "H"
    LOW = "L"
    DONT_CARE = "X"
    HIGH_IMPEDANCE = "T"


class StilUnits(Enum):
    MS = "ms"
    US = "us"
    NS = "ns"
    PS = "ps"
    FS = "fs"


TCond = TypeVar("TCond", StilTimingInCondition, StilTimingOutCondition)
TVal = TypeVar("TVal", StilForce, StilCompare)


class StilWaveform(Generic[TCond, TVal]):
    def __init__(
        self,
        signal_group: StilSignalGroup,
        period: int,
        units: StilUnits,
        timing_condition_list: List[TCond]=[],
        timestamp_dict: Dict[int, List[TVal]]={}) -> None:

        self._signal_group: StilSignalGroup = signal_group
        
        self._period = period
        self._units = units

        self._timing_condition_list: List[TCond]=[]
        if len(timing_condition_list)>0:
            self.add_timing_condition_list(timing_condition_list=timing_condition_list)
        
        self._timestamp_dict: Dict[int, List[TVal]] = {}
        if len(timestamp_dict)>0:
            self.add_timestamp_dict(timestamp_dict=timestamp_dict)


    @property
    def signal_group(self) -> StilSignalGroup:
        return self._signal_group

    
    @property
    def period(self) -> int:
        return self._period


    @property
    def units(self) -> StilUnits:
        return self._units

    @property
    def timing_condition_list(self) -> List[TCond]:
        return self._timing_condition_list

    
    @property
    def timestamp_dict(self) -> Dict[int, List[TVal]]:
        return self._timestamp_dict


    def add_timing_condition(self, timing_condition: TCond) -> None:
        if (self.signal_group.signal_type == StilSignalType.INPUT and type(timing_condition) == StilTimingOutCondition) or \
           (self.signal_group.signal_type == StilSignalType.OUTPUT and type(timing_condition) == StilTimingInCondition):
            raise TypeError(f"Cannot associate signal group of type '{self._signal_group.signal_type}' with timestamp condition of type '{type(timing_condition).__qualname__}'")
        if timing_condition not in self.timing_condition_list:
            self.timing_condition_list.append(timing_condition)


    def add_timestamp(self, timestamp_key: int, timestamp_value: TVal) -> None:
        if timestamp_key > self.period:
            raise ValueError(f"Timestamp key '{timestamp_key}{self.units}' cannot be higher than period '{self.period}{self.units}'")
        if (self.signal_group.signal_type == StilSignalType.INPUT and type(timestamp_value) == StilCompare) or \
           (self.signal_group.signal_type == StilSignalType.OUTPUT and type(timestamp_value) == StilForce):
                raise TypeError(f"Cannot associate signal group of type '{self._signal_group.signal_type}' with timing value of type '{type(timestamp_value).__qualname__}'")
        if self.timestamp_dict.get(timestamp_key) is not None:
            self.timestamp_dict[timestamp_key].append(timestamp_value)
        else:
            self.timestamp_dict[timestamp_key] = [timestamp_value]


    def add_timing_condition_list(self, timing_condition_list: List[TCond]) -> None:
        for timing_condition in timing_condition_list:
            self.add_timing_condition(timing_condition=timing_condition)


    def add_timestamp_dict(self, timestamp_dict: Dict[int, List[TVal]]):
        for timestamp_key, timestamp_value_list in timestamp_dict.items():
            for timestamp_value in timestamp_value_list:
                self.add_timestamp(timestamp_key=timestamp_key, timestamp_value=timestamp_value)


    def get_waveform_str(self, indent_level: int=0) -> str:
        indent_str="\t" * indent_level
        waveform_str: str = ""
        waveform_str+=f"{indent_str}{type(self).__qualname__}:\n"
        waveform_str+=f"{indent_str}\tsignal group name: '{self.signal_group.name}'\n"
        waveform_str+=f"{indent_str}\tperiod: '{self.period}{self.units.value}'\n"
        
        waveform_str+=f"{indent_str}\ttiming condition list: \n"
        for timing_condition in self.timing_condition_list:
            waveform_str+=f"{indent_str}\t\ttiming condition: '{timing_condition}'\n"

        waveform_str+=f"{indent_str}\ttimestamp dictionary: \n"
        for timestamp_key, timestamp_value in self.timestamp_dict.items():
            waveform_str+=f"{indent_str}\t\t'{timestamp_key}': '{[value.value for value in timestamp_value]}'\n"
        
        waveform_str=waveform_str.removesuffix("\n")
        return waveform_str
