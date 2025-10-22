# standard packages
from typing import List, Any, Dict, Union


# local packages
from stil_waveform import StilWaveform, StilUnits
from stil_signal_group import StilSignalGroup


class StilWaveformTable():
    def __init__(
        self,
        period: int,
        units: StilUnits,
        waveform_list: List[StilWaveform[Any, Any]]=[]) -> None:

        self._period = period
        self._units = units

        self._waveform_dict: Dict[str, StilWaveform[Any, Any]] = {}
        if len(waveform_list)>0:
            self.add_waveform_list(waveform_list=waveform_list)


    @property
    def period(self) -> int:
        return self._period


    @property
    def units(self) -> StilUnits:
        return self._units


    @property
    def waveform_dict(self) -> Dict[str, StilWaveform[Any, Any]]:
        return self._waveform_dict


    def add_waveform(self, waveform: StilWaveform[Any, Any]) -> None:
        if waveform.period != self.period or waveform.units != self.units:
            raise ValueError(f"Waveform with period '{waveform.period}{waveform.units}' is not compatible with waveform table with period '{self.period}{self.units}'")
        self.waveform_dict[waveform.signal_group.name] = waveform


    def add_waveform_list(self, waveform_list: List[StilWaveform[Any, Any]]) -> None:
        for waveform in waveform_list:
            self.add_waveform(waveform=waveform)


    def get_waveform_from_signal_group(self, signal_group: StilSignalGroup) -> Union[StilWaveform[Any, Any], None]:
        return self.waveform_dict.get(signal_group.name)


    def get_waveform_from_signal_group_name(self, signal_group_name: str) -> Union[StilWaveform[Any, Any], None]:
        return self.waveform_dict.get(signal_group_name)


    def get_waveform_table_str(self, indent_level: int=0) -> str:
        indent_str="\t" * indent_level
        waveform_table_str: str = ""
        waveform_table_str+=f"{indent_str}{type(self).__qualname__}:\n"
        waveform_table_str+=f"{indent_str}\tperiod: '{self.period}{self.units}'\n"

        waveform_table_str+=f"{indent_str}\twaveform dict:\n"
        for waveform in self.waveform_dict.values():
            waveform_table_str+=f"{waveform.get_waveform_str(indent_level=indent_level+2)}\n"
        
        waveform_table_str=waveform_table_str.removesuffix("\n")
        return waveform_table_str
