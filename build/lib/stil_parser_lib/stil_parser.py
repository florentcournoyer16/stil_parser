# standard packages
from io import TextIOWrapper
from typing import Optional, List, Tuple, Match
from re import search, findall


# local packages
from stil_test import StilTest
   

class StilParser():


    @staticmethod
    def gen_tests_from_stil(directory_list: List[str]=[], stil_list: List[str]=[]) -> List[StilTest]:
        stil_test_list: List[StilTest] = []
        stil_file: Optional[TextIOWrapper] = None
        for directory in directory_list:
            for stil in stil_list:
                try:
                    file_path: str = f"{directory}/{stil}.stil"
                    stil_file = open(file_path)
                    stil_test_list.append(StilParser._parse_stil_file(stil_file=stil_file))
                except (FileNotFoundError, NotADirectoryError):
                    continue
            if stil_file is not None:
                stil_file.close()
                stil_file = None
        return stil_test_list


    @staticmethod
    def _parse_stil_file(stil_file: TextIOWrapper) -> StilTest:
        stil_test: StilTest = StilTest()
        line_list: List[str] = stil_file.readlines()
        line_idx: int = 0

        stil_test, line_idx = StilParser._parse_test_name(      stil_test=stil_test, line_list=line_list, line_idx=line_idx )
        stil_test, line_idx = StilParser._parse_signals(        stil_test=stil_test, line_list=line_list, line_idx=line_idx )
        stil_test, line_idx = StilParser._parse_signal_groups(  stil_test=stil_test, line_list=line_list, line_idx=line_idx )
        stil_test, line_idx = StilParser._parse_waveform_table( stil_test=stil_test, line_list=line_list, line_idx=line_idx )
        stil_test, line_idx = StilParser._parse_waveforms(      stil_test=stil_test, line_list=line_list, line_idx=line_idx )
        stil_test, line_idx = StilParser._parse_test_vector(    stil_test=stil_test, line_list=line_list, line_idx=line_idx )

        return stil_test


    @staticmethod
    def _parse_test_name(stil_test: StilTest, line_list: List[str], line_idx: int) -> Tuple[StilTest, int]:
        while "Title " not in line_list[line_idx]:
            line_idx+=1

        test_name: Optional[Match[str]] = search(r'"(.*?)"', line_list[line_idx])
        if test_name is None:
            raise ValueError(f"Could not find the test name in string '{line_list[line_idx]}' at line '{line_idx}'")        
        stil_test.set_name(name=test_name.group(0).strip("\""))

        return stil_test, line_idx


    @staticmethod
    def _parse_signals(stil_test: StilTest, line_list: List[str], line_idx: int) -> Tuple[StilTest, int]:
        while "Signals {" not in line_list[line_idx]:
            line_idx+=1

        line_idx+=1
        while line_list[line_idx].strip() != "}":
            signal_list: List[str] = StilParser._clean_str_list(list_str=line_list[line_idx].strip().split(";"))
            for signal in signal_list:
                signal_name: Optional[Match[str]] = search(r"\"(.*?)\"", signal)
                if signal_name is None:
                    raise ValueError(f"Could not find a signal name in string {signal}")
                signal_type: Optional[Match[str]] = search(r"\b(?:In|Out)\b", signal.replace(signal_name.group(0), ""))
                if signal_type is None:
                    raise ValueError(f"Signal type {signal_type} is not 'In' or 'Out'") 
                stil_test.add_signal(signal_name=signal_name.group(0).strip("\""), signal_type=signal_type.group(0))
            line_idx+=1

        return stil_test, line_idx


    @staticmethod
    def _parse_signal_groups(stil_test: StilTest, line_list: List[str], line_idx: int) -> Tuple[StilTest, int]:
        while "SignalGroups {" not in line_list[line_idx]:
                line_idx+=1

        line_idx+=1
        while line_list[line_idx].strip() != "}":
            signal_group_name: str = line_list[line_idx].strip().split("=")[0].strip()
            signal_list: List[str] = findall(r"\"(.*?)\"", line_list[line_idx])
            if signal_list == []:
                raise ValueError(f"No signal found in 'signal_list'={signal_list} with 'signal_group_name'={signal_group_name}")
            stil_test.add_signal_group(signal_group_name=signal_group_name, signal_list=signal_list)
            line_idx+=1

        return stil_test, line_idx


    @staticmethod
    def _parse_waveform_table(stil_test: StilTest, line_list: List[str], line_idx: int) -> Tuple[StilTest, int]:
        while "Timing RETARGET_timing {" not in line_list[line_idx]:
            line_idx+=1

        line_idx+=1
        while "Period " not in line_list[line_idx]:
            line_idx+=1

        full_str = line_list[line_idx].strip().removeprefix("Period").removesuffix(";").strip().strip("'")
        period_str: Optional[Match[str]] = search(r"\d+", full_str)
        units_str: Optional[Match[str]] = search(r"(?:ms|us|ns|ps|fs)", full_str)
        if period_str is None or units_str is None:
            raise ValueError(f"Could not extract period and/or units from line '{line_list[line_idx]}' at line: '{line_idx}'")
        stil_test.set_waveform_table(period=int(period_str.group(0)), units=units_str.group(0))
        
        return stil_test, line_idx
    
    @staticmethod
    def _parse_waveforms(stil_test: StilTest, line_list: List[str], line_idx: int) -> Tuple[StilTest, int]:
        while "Waveforms  {" not in line_list[line_idx]:
            line_idx+=1

        line_idx+=1
        while line_list[line_idx].strip() != "}":
            current_line: List[str] = StilParser._clean_str_list(line_list[line_idx].strip().split("{"))
            if len(current_line) != 3:
                raise ValueError(f"Could not extract waveform from line '{current_line}'")
            signal_group_name: str = current_line[0]
            timing_condition: str = current_line[1]
            timestamp_list: List[str] = StilParser._clean_str_list(list_str=current_line[2].strip().removesuffix("}}").strip().split(";"))
            for timestamp in timestamp_list:
                timestamp_key_str: Optional[Match[str]] = search(r"'(.*?)'", timestamp)
                if timestamp_key_str is None:
                    raise ValueError(f"Could not extract timmestamp key in line '{line_list[line_idx].strip()}' at line: '{line_idx}'")
                clean_timestamp_key_str: str = timestamp_key_str.group(0).removeprefix("'").removesuffix(f"{stil_test.waveform_table.units.value}'")
                timestamp_key: int = int(clean_timestamp_key_str)
                timestamp_val: Optional[Match[str]] = search(r"[DUN|LHXT](?:/[DUN|LHXT])*", timestamp)
                if timestamp_val is None:
                    raise ValueError(f"Could not extract timestamp value in line '{line_list[line_idx].strip()}' at line: '{line_idx}'")
                
                stil_test.add_waveform(
                    signal_group_name=signal_group_name,
                    timing_condition=timing_condition,
                    timestamp_key=timestamp_key,
                    timestamp_val_list=StilParser._clean_str_list(timestamp_val.group(0).split('/'))
                )
            line_idx+=1

        return stil_test, line_idx


    @staticmethod
    def _parse_test_vector(stil_test: StilTest, line_list: List[str], line_idx: int) -> Tuple[StilTest, int]:
        tester_cycle: int = 0
        
        while line_idx < len(line_list)-1:
            if "TesterCycle:" in line_list[line_idx].strip():
                tester_cycle_match: Optional[Match[str]] = search(r"TesterCycle:(\d)+", line_list[line_idx].strip())
                if tester_cycle_match is None:
                    raise ValueError(f"Could not extract tester cycle in line '{line_list[line_idx].strip()}' at line '{line_idx}'")
                tester_cycle = int(tester_cycle_match.group(0).removeprefix("TesterCycle:"))
            if line_list[line_idx].strip() == "V {":
                line_idx+=1
                while line_list[line_idx].strip() != "}":
                    signal_group_name: str = line_list[line_idx].strip().split("=")[0].strip()
                    signal_value_str: str = line_list[line_idx].strip().split("=")[1].strip().removesuffix(";")
                    if signal_group_name == "":
                        raise ValueError(f"Could not extract signal group name from test vector line '{line_list[line_idx]}' at line '{line_idx}'")
                    if signal_value_str == "":
                        raise ValueError(f"Could not extract signal value from test vector line '{line_list[line_idx]}' at line '{line_idx}'")
                    stil_test.add_test_vector(tester_cycle=tester_cycle, signal_group_name=signal_group_name, value_str=signal_value_str)
                    line_idx+=1
            line_idx+=1

        stil_test.sort()
        return stil_test, line_idx


    @staticmethod
    def _clean_str_list(list_str: List[str]) -> List[str]:
        cleaned_list_str: List[str] = []
        for e in list_str:
            if e not in [None, "", " ", "\n", "\r", "\t"]:
                cleaned_list_str.append(e.strip())
        
        return cleaned_list_str
