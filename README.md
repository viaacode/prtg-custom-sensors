# PRTG Custom Sensors
A collection of custom sensors developped for the [PRTG monitoring
system](https://www.paessler.com/manuals/prtg/custom_sensors).

## Custom Sensors in python

With PRTG release 25.x.110, Python Script Advanced sensors are no longer
supported. The source files for these sensors live in the `python`
directory.

The are replaced by the [Script V2
sensor](https://www.paessler.com/manuals/prtg/script_v2_sensor). They live in
the `scripts` directory. To run Python scripts as script V2 sensor, Python 3
must be installed for the Windows user account that the probe runs under.

Required modules are installed ingy `pip install` in that environment.
