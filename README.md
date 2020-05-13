# pyprtg
Scripts for PRTG's Python Script Advanced sensors.

## Installing modules in the PRTG python environment

Download [get-pip](https://bootstrap.pypa.io/get-pip.py) into PRTGs python directory (C:\Program Files (x86)\PRTG Network Monitor\python)

Install pip
```
cd "C:\Program Files (x86)\PRTG Network Monitor\python"
"C:\Program Files (x86)\PRTG Network Monitor\python python.exe" get-pip.py
```
Install python modules, for example
```
C:\Program Files (x86)\PRTG Network Monitor\python>"C:\Program Files (x86)\PRTG
Network Monitor\python\Scripts\pip.exe" install requests
```
Make sure to qualify all python related commands with the full path to be sure that the modules are installed in PRTG's python environmnet and not the sytem's defaut python environment
