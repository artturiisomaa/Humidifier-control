# Humidifier control
The program controls a humidifier (on/off) based on the room's humidity level.

## Overview
This program controls a Shelly plug S Gen3 using HTTP requests based on 
humidity measurements from a RuuviTag Bluetooth sensor. The humidifier is 
connected to the smart plug and is turned on or off depending on the measured 
humidity.

The program reads only a single humidity measurement from a RuuviTag sensor and 
controls a plug accordingly. To run it periodically, you can schedule the 
script using cron or another task scheduler.

The program was originally developed as part of my bachelor's thesis, but it 
has been updated since.

## How to use
### Install dependencies (On Linux):
Install the required dependencies using 'pip'. It is recommended to do this 
inside a virtual environment:
```bash
# Update package list
sudo apt update

# Install Python and Python virtual environment
sudo apt install python3
sudo apt install python3-venv

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install requests
pip install ruuvitag_sensor
```

## Create configuration file
The program requires a configuration file named "Conf_file.txt" in the project 
directory. The file should contain the following information on separate lines:

1. The IP address of the smart plug.
2. The MAC address of the RuuviTag sensor.

Example file (replace the example IP and MAC with your actual device values):
```bash
192.168.X.Y
AA:BB:CC:DD:EE:FF
```

Make sure the file exists before running the program.

### Running the program periodically (On Linux):
This example runs the program every minute with the help of cron:
```bash
# Run the program every minute (adjust the path as needed)
* * * * * cd /path/to/project && /path/to/project/venv/bin/python control.py
```

## License
MIT License - See the LICENSE file for details.

### Third-party libraries
The program uses the following third-party libraries, which retain their own 
licenses:
- [requests](https://github.com/psf/requests) (Apache 2.0)
- [ruuvitag_sensor](https://github.com/ttu/ruuvitag-sensor) (MIT)
