# standard packages
from typing import Optional, List


#local packages
from stil_signal import StilSignal, StilSignalType


class StilSignalGroup():
    def __init__(self, name: str, signal_type: Optional[StilSignalType]=None) -> None:
        self._name: str = name
        self._signal_list: List[StilSignal] = []
        self._signal_type: Optional[StilSignalType] = signal_type


    @property
    def name(self) -> str:
        return self._name


    @property
    def signal_type(self) -> StilSignalType:
        if self._signal_type is None:
            raise AttributeError("Property 'signal_type' is not initialized")
        return self._signal_type


    @property
    def signal_list(self) -> List[StilSignal]:
        return self._signal_list
    
    
    def add_signal_from_list(self, signal_list: List[StilSignal]) -> None:
        for signal in signal_list:
            self.add_signal(signal)


    def add_signal(self, signal: StilSignal) -> None:
        if signal in self.signal_list:
            raise ValueError(f"Signal '{signal.name}' already in group '{[signal.name for signal in self.signal_list]}'")
        if self._signal_type is None:
            self._signal_type = signal.signal_type
        if signal.signal_type != self.signal_type:
            raise ValueError(f"Cannot add signals of conflicting type '{self.signal_type}' to signal group associated with signal type '{self.signal_type}'")
        self.signal_list.append(signal)


    def get_signal_from_name(self, signal_name: str) -> StilSignal:
        for signal in self.signal_list:
            if signal.name == signal_name:
                return signal
        raise ValueError(f"Signal with name '{signal_name}' not in signal group '{[signal.name for signal in self.signal_list]}'")


    def is_in_group(self, signal_name: str) -> bool:
        return signal_name in [signal.name for signal in self.signal_list]


    def remove_signal(self, signal: StilSignal) -> None:
        if signal in self.signal_list:
            self._signal_list.remove(signal)
      

    def remove_signal_from_name(self, signal_name: str) -> None:
        for signal in self.signal_list:
            if signal.name == signal_name:
                self._signal_list.remove(signal)


    def empty(self) -> None:
        for signal in self.signal_list:
            self._signal_list.remove(signal)


    def get_signal_group_str(self, indent_level: int=0) -> str:
        indent_str="\t" * indent_level
        signal_group_str: str = ""
        signal_group_str+=f"{indent_str}{type(self).__qualname__}:\n"
        signal_group_str+=f"{indent_str}\tname: '{self.name}'\n"
        signal_group_str+=f"{indent_str}\tsignal type: '{self.signal_type}'\n"
        
        signal_group_str+=f"{indent_str}\tsignal list: \n"
        for signal in self.signal_list:
            signal_group_str+=f"{indent_str}\t\tsignal: '{signal.name}'\n"
        
        signal_group_str=signal_group_str.removesuffix("\n")
        return signal_group_str
