# standard packages
from typing import Union, List, Dict, Tuple, Any


# local packages
from stil.stil_signal import StilSignal
from stil.stil_signal_group import StilSignalGroup
from stil.stil_waveform import StilCompare, StilForce, StilTimingInCondition, StilTimingOutCondition, StilWaveform
from stil.stil_waveform_table import StilWaveformTable


class StilTestVector():
    def __init__(self, tester_cycle: int, waveform_table: StilWaveformTable) -> None:
        if tester_cycle<0:
            raise ValueError("Tester cycle cannot be negative")
        self._tester_cycle: int = tester_cycle
        self._waveform_table: StilWaveformTable = waveform_table
        self._test_vector: Dict[int, List[Tuple[StilSignal, Union[StilForce, StilCompare]]]] = {}


    @property
    def tester_cycle(self) -> int:
        return self._tester_cycle


    @property
    def waveform_table(self) -> StilWaveformTable:
        return self._waveform_table


    @property
    def test_vector(self) -> Dict[int, List[Tuple[StilSignal, Union[StilForce, StilCompare]]]]:
        return self._test_vector


    def add_input_event(self, signal_group: StilSignalGroup, value_list: List[StilTimingInCondition]) -> None:
        for signal, value in zip(signal_group.signal_list, value_list):
            waveform: StilWaveform[StilTimingInCondition, StilForce] = self.get_waveform_from_signal(signal=signal)
            for timing_condition in waveform.timing_condition_list:
                if timing_condition == value:
                    for timestamp, waveform_value_list in waveform.timestamp_dict.items():
                        if len(waveform_value_list) > 1:
                            for waveform_value in waveform_value_list:
                                if (timing_condition == StilTimingInCondition.UNKNOWN and waveform_value == StilForce.NONE) or \
                                   (timing_condition == StilTimingInCondition.ZERO and waveform_value == StilForce.DOWN) or \
                                   (timing_condition == StilTimingInCondition.ONE and waveform_value == StilForce.UP):
                                    if self.test_vector.get(timestamp) is None:
                                        self.test_vector[timestamp] = [(signal, waveform_value)]
                                    else:
                                        self.test_vector[timestamp].append((signal, waveform_value))
                        else:
                            if self.test_vector.get(timestamp) is None:
                                self.test_vector[timestamp] = [(signal, waveform_value_list[0])]
                            else:
                                self.test_vector[timestamp].append((signal, waveform_value_list[0]))


    def add_output_event(self, signal_group: StilSignalGroup, value_list: List[StilTimingOutCondition]) -> None:
        for signal, value in zip(signal_group.signal_list, value_list):
            waveform: StilWaveform[StilTimingOutCondition, StilCompare] = self.get_waveform_from_signal(signal=signal)
            for timing_condition in waveform.timing_condition_list:
                if timing_condition == value:
                    for timestamp, waveform_value_list in waveform.timestamp_dict.items():
                        if len(waveform_value_list) > 1:
                            for waveform_value in waveform_value_list:
                                if (timing_condition.value == waveform_value.value):
                                    if self.test_vector.get(timestamp) is None:
                                        self.test_vector[timestamp] = [(signal, waveform_value)]
                                    else:
                                        self.test_vector[timestamp].append((signal, waveform_value))
                        else:
                            if self.test_vector.get(timestamp) is None:
                                self.test_vector[timestamp] = [(signal, waveform_value_list[0])]
                            else:
                                self.test_vector[timestamp].append((signal, waveform_value_list[0]))


    def get_waveform_from_signal(self, signal: StilSignal) -> StilWaveform[Any, Any]:
        for signal_group_name, waveform in self.waveform_table.waveform_dict.items():
            if signal in waveform.signal_group.signal_list:
                return self.waveform_table.waveform_dict[signal_group_name]
        raise ValueError(f"Could not find matching waveform for signal '{signal.name}'")


    def sort(self) -> None:
        self._test_vector = dict(sorted(self.test_vector.items()))


    def get_test_vector_str(self, indent_level: int=0) -> str:
        indent_str="\t" * indent_level
        test_vector_str: str = ""
        test_vector_str+=f"{indent_str}{type(self).__qualname__}:\n"
        test_vector_str+=f"{indent_str}\ttester_cycle: '{self.tester_cycle}':\n"

        test_vector_str+=f"{indent_str}\t\ttest vector: \n"        
        for timestamp, signal_value_tuple_list in self.test_vector.items():
            for (signal, value) in signal_value_tuple_list:
                test_vector_str+=f"{indent_str}\t\t\t'{timestamp}': '{signal.name}'='{value}'\n"
        
        test_vector_str=test_vector_str.removesuffix("\n")
        return test_vector_str
