# standard packages
from enum import Enum


class StilSignalType(Enum):
    INPUT = "In"
    OUTPUT = "Out"


class StilSignal():
    def __init__(self, name: str, signal_type: StilSignalType) -> None:
        self._name: str = name
        self._signal_type: StilSignalType = signal_type


    @property
    def name(self) -> str:
        return self._name


    @property
    def signal_type(self) -> StilSignalType:
        return self._signal_type


    def get_signal_str(self, indent_level: int=0) -> str:
        indent_str="\t" * indent_level
        signal_str: str = ""
        signal_str+=f"{indent_str}{type(self).__qualname__}:\n"
        signal_str+=f"{indent_str}\tname: '{self.name}'\n"
        signal_str+=f"{indent_str}\tsignal type: '{self.signal_type}'"
        return signal_str
