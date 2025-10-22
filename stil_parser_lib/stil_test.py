# standard packages
from typing import Optional, Dict, List, Union


# local packages
from stil_signal import StilSignal, StilSignalType
from stil_signal_group import StilSignalGroup
from stil_waveform import StilTimingInCondition, StilTimingOutCondition, StilForce, StilCompare, StilUnits, StilWaveform
from stil_waveform_table import StilWaveformTable
from stil_test_vector import StilTestVector


class StilTest():
    def __init__(self) -> None:
        self._name: Optional[str] = None
        self._signal_dict: Dict[str, StilSignal] = {}
        self._signal_group_dict: Dict[str, StilSignalGroup] = {}
        self._waveform_table: Optional[StilWaveformTable] = None
        self._test_vector_dict: Dict[int, StilTestVector] = {}
 

    @property
    def name(self) -> str:
        if self._name is None:
            raise AttributeError("Property 'test_name' is not initialized")
        return self._name


    @property
    def signal_dict(self) -> Dict[str, StilSignal]:
        return self._signal_dict


    @property
    def signal_group_dict(self) -> Dict[str, StilSignalGroup]:
        return self._signal_group_dict


    @property
    def waveform_table(self) -> StilWaveformTable:
        if self._waveform_table is None:
            raise AttributeError("Property 'waveform_table' is not initialized")
        return self._waveform_table


    @property
    def test_vector_dict(self) -> Dict[int, StilTestVector]:
        return self._test_vector_dict


    def set_name(self, name: str) -> None:
        if self._name is not None:
            raise AttributeError(f"Stil test already has a name: '{self.name}'")
        self._name = name


    def add_signal(self, signal_name: str, signal_type: str) -> None:
        if signal_name in self.signal_dict:
            raise AttributeError(f"Signal '{signal_name}' already in '{list(self.signal_dict.keys())}'")
        stil_signal_type: StilSignalType = StilSignalType(signal_type)
        self.signal_dict[signal_name] = StilSignal(name=signal_name, signal_type=stil_signal_type)


    def add_signal_group(self, signal_group_name: str, signal_list: List[str]) -> None:
        if signal_group_name in self.signal_group_dict:
            raise AttributeError(f"Signal group '{signal_group_name}' already in '{list(self.signal_group_dict.keys())}'")

        self._signal_group_dict[signal_group_name] = StilSignalGroup(name=signal_group_name)
        for signal_name in signal_list:
            self.signal_group_dict[signal_group_name].add_signal(signal=self.signal_dict[signal_name])


    def set_waveform_table(self, period: int, units: str) -> None:
        if self._waveform_table is not None:
            raise AttributeError(f"Waveform table is already defined '{self.waveform_table.get_waveform_table_str}'")
        stil_units: StilUnits = StilUnits(units)
        self._waveform_table = StilWaveformTable(period=period, units=stil_units)


    def add_waveform(self, signal_group_name: str, timing_condition: str, timestamp_key: int, timestamp_val_list: List[str]) -> None:
        if self.signal_group_dict[signal_group_name].signal_type == StilSignalType.INPUT:
            self._add_input_waveform(
                signal_group_name=signal_group_name,
                timing_condition=timing_condition,
                timestamp_key=timestamp_key,
                timestamp_val_list=timestamp_val_list
            )
 
        elif self.signal_group_dict[signal_group_name].signal_type == StilSignalType.OUTPUT:
            self._add_ouput_waveform(
                signal_group_name=signal_group_name,
                timing_condition=timing_condition,
                timestamp_key=timestamp_key,
                timestamp_val_list=timestamp_val_list
            )
        else:
            raise TypeError(f"Type of signal for signal group '{self._signal_group_dict[signal_group_name].name}' is unknown: '{self._signal_group_dict[signal_group_name].signal_type}'")        


    def _add_input_waveform(self, signal_group_name: str, timing_condition: str, timestamp_key: int, timestamp_val_list: List[str]) -> StilWaveform[StilTimingInCondition, StilForce]:
        stil_waveform: Union[StilWaveform[StilTimingInCondition, StilForce], None] = self.waveform_table.get_waveform_from_signal_group_name(signal_group_name=signal_group_name)
        if stil_waveform is None:
            stil_waveform = StilWaveform[StilTimingInCondition, StilForce](
                signal_group=self._signal_group_dict[signal_group_name],
                period=self.waveform_table.period,
                units=self.waveform_table.units
            )
            self.waveform_table.add_waveform(waveform=stil_waveform)
        for i in range(len(timing_condition)):
            stil_waveform.add_timing_condition(
                timing_condition=StilTimingInCondition(timing_condition[i])
            )
        for timestamp_val in timestamp_val_list:
            stil_waveform.add_timestamp(
                timestamp_key=timestamp_key,
                timestamp_value=StilForce(timestamp_val)
            )
        return stil_waveform


    def _add_ouput_waveform(self, signal_group_name: str, timing_condition: str, timestamp_key: int, timestamp_val_list: List[str]) -> StilWaveform[StilTimingOutCondition, StilCompare]:
        stil_waveform: Union[StilWaveform[StilTimingOutCondition, StilCompare], None] = self.waveform_table.get_waveform_from_signal_group_name(signal_group_name=signal_group_name)
        if stil_waveform is None:
            stil_waveform = StilWaveform[StilTimingOutCondition, StilCompare](
                signal_group=self._signal_group_dict[signal_group_name],
                period=self.waveform_table.period,
                units=self.waveform_table.units
            )
            self.waveform_table.add_waveform(waveform=stil_waveform)
        for i in range(len(timing_condition)):
            stil_waveform.add_timing_condition(
                timing_condition=StilTimingOutCondition(timing_condition[i])
            )
        for timestamp_val in timestamp_val_list:
            stil_waveform.add_timestamp(
                timestamp_key=timestamp_key,
                timestamp_value=StilCompare(timestamp_val)
            )
        return stil_waveform


    def add_test_vector(self, tester_cycle: int, signal_group_name: str, value_str: str) -> None:
        if self.signal_group_dict[signal_group_name].signal_type == StilSignalType.INPUT:
            self._add_input_test_vector(tester_cycle=tester_cycle, signal_group_name=signal_group_name, value_str=value_str)
        elif self.signal_group_dict[signal_group_name].signal_type == StilSignalType.OUTPUT:
            self._add_output_test_vector(tester_cycle=tester_cycle, signal_group_name=signal_group_name, value_str=value_str)
        else:
            raise TypeError(f"Type of signal for signal group '{self.signal_group_dict[signal_group_name].name}' is unknown: '{self.signal_group_dict[signal_group_name].signal_type}'")        


    def _add_input_test_vector(self, tester_cycle: int, signal_group_name: str, value_str: str) -> None:
        stil_value_list: List[StilTimingInCondition] = []
        for i in range(len(value_str)):
            stil_value_list.append(StilTimingInCondition(value_str[i]))
        
        stil_test_vector: Optional[StilTestVector] = self.test_vector_dict.get(tester_cycle)
        if stil_test_vector is None:
            self.test_vector_dict[tester_cycle] = StilTestVector(
                tester_cycle=tester_cycle,
                waveform_table=self.waveform_table   
            )
        self.test_vector_dict[tester_cycle].add_input_event(
            signal_group=self.signal_group_dict[signal_group_name],
            value_list=stil_value_list
        )
        
        
    def _add_output_test_vector(self, tester_cycle: int, signal_group_name: str, value_str: str) -> None:
        stil_value_list: List[StilTimingOutCondition] = []
        for i in range(len(value_str)):
            stil_value_list.append(StilTimingOutCondition(value_str[i]))

        stil_test_vector: Optional[StilTestVector] = self.test_vector_dict.get(tester_cycle)
        if stil_test_vector is None:
            stil_test_vector = StilTestVector(
                tester_cycle=tester_cycle,
                waveform_table=self.waveform_table   
            )
        stil_test_vector.add_output_event(
            signal_group=self.signal_group_dict[signal_group_name],
            value_list=stil_value_list
        )


    def sort(self) -> None:
        self._test_vector_dict = dict(sorted(self.test_vector_dict.items()))
        for test_vector in self.test_vector_dict.values():
            test_vector.sort()

    
    def get_test_str(self) -> str:
        test_str: str = ""
        test_str+=f"{type(self).__qualname__}:\n"
        test_str+=f"\tname: '{self.name}'\n"
        
        test_str+=f"\tsignal dict:\n"
        for signal in self.signal_dict.values():
            test_str+=f"{signal.get_signal_str(indent_level=2)}\n"
        
        test_str+=f"\tsignal group dict:\n"
        for signal_group in self.signal_group_dict.values():
            test_str+=f"{signal_group.get_signal_group_str(indent_level=2)}\n"
            
        test_str+=f"\twaveform table:\n"
        test_str+=f"{self.waveform_table.get_waveform_table_str(indent_level=2)}\n"
        
        test_str+=f"\ttest vector dict:\n"
        for test_vector in self.test_vector_dict.values():
            test_str+=f"{test_vector.get_test_vector_str(indent_level=2)}\n"
        
        test_str=test_str.removesuffix("\n")
        return test_str
