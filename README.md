# stil_parser lib

## Installing the library with pip

```shell
pip install git+git@github.com:florentcournoyer16/stil_parser.git
```

## Using the library

### Parsing stil file into a StilTest

```python
from stil_parser import StilParser
from stil_test import StilTest

stil_test: StilTest = StilParser.gen_tests_from_stil(
    directory_list=["<DIRECTORY PATH 1>", "<DIRECTORY PATH 2>"], stil_list=["<FILE_PATH_1>", "<FILE_PATH_2>"]
)[0]
```

### Driving signals from a StilTest

```python
from stil_test import StilTest
from stil_signal import StilSignalType
from stil_waveform import StilForce, StilCompare

current_cycle_timing: int = 0
    for _, test_vector in stil_test.test_vector_dict.items():
        current_cycle_timing = 0
        for in_cycle_timing, signal_value_tuple_list in test_vector.test_vector.items():
            for (stil_signal, stil_value) in signal_value_tuple_list:
                wait_time: int = in_cycle_timing-current_cycle_timing
                if wait_time > 0:
                    await Timer(time=wait_time, units=stil_test.waveform_table.units.value)
                current_cycle_timing = in_cycle_timing
                if stil_signal.signal_type == StilSignalType.INPUT:
                    if stil_value == StilForce.DOWN:
                        self.in_sig_dict[stil_signal.name].value = 0
                    elif stil_value == StilForce.UP:
                        self.in_sig_dict[stil_signal.name].value = 1
                    elif stil_value == StilForce.NONE:
                        pass
                elif stil_signal.signal_type == StilSignalType.OUTPUT:
                    if stil_value == StilCompare.LOW:
                        assert self.out_sig_dict[stil_signal.name].value == 0
                    elif stil_value == StilCompare.HIGH:
                        assert self.out_sig_dict[stil_signal.name].value == 1
                    elif stil_value == StilCompare.DONT_CARE:
                        pass
                    elif stil_value == StilCompare.HIGH_IMPEDANCE:
                        pass

```
