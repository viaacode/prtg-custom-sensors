# PRTG Custom Sensors
A collection of custom sensors developped for the [PRTG monitoring
system](https://www.paessler.com/manuals/prtg/custom_sensors).

## Installing python packages in the PRTG python environment
Custom Sensors written in python might need python packages. In order to make
these packages available for python custom sensors, download
[get-pip](https://bootstrap.pypa.io/get-pip.py) into PRTGs python directory
(C:\Program Files (x86)\PRTG Network Monitor\python) and install pip
```
cd "C:\Program Files (x86)\PRTG Network Monitor\python"
"C:\Program Files (x86)\PRTG Network Monitor\python python.exe" get-pip.py
```
Once `pip` is available, python modules can be installed, for example
```
C:\Program Files (x86)\PRTG Network Monitor\python>"C:\Program Files (x86)\PRTG
Network Monitor\python\Scripts\pip.exe" install requests
```
Make sure to qualify all python related commands with the full path to be sure that the modules are installed in PRTG's python environmnet and not the sytem's defaut python environment
