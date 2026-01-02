"""
This program controls a smart plug with HTTP requests based on the humidity
measured with a RuuviTag Bluetooth humidity sensor.
"""

# NOTICE: This program includes code from the following libraries:
#   - requests: Apache-2.0 License
#   - ruuvitag_sensor: MIT License


# Apache-2.0 License for requests
#
# Copyright 2019 Kenneth Reitz
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# MIT License for ruuvitag_sensor
#
# Copyright (c) 2016 Tomi Tuhkanen
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import requests
import asyncio
from ruuvitag_sensor.ruuvi import RuuviTagSensor


async def monitor_and_control_humidity(ruuvitag_mac, plug_ip):
    """
    Captures humidity sensor measurement data, gets smart socket status
    information, and controls the smart socket based on measurement data
    and status information.

    :param ruuvitag_mac: str, the MAC address of the RuuviTag sensor.
    :param plug_ip: str, the IP address of the smart plug.
    """

    target_humidity = 37
    humidity_threshold_on = target_humidity - 0.01
    humidity_threshold_off = target_humidity + 0.01
    datas = []
    
    try:
        async with asyncio.timeout(10):
            async for found_data in RuuviTagSensor.get_data_async(ruuvitag_mac):
                humidity = found_data[1]["humidity"]
                plug_on = get_plug_status(plug_ip)
                status = "on" if plug_on else "off"
                print(f"Plug is {status}, and the humidity is {humidity} % RH.")
                datas.append(found_data)

                if humidity > humidity_threshold_off and plug_on:
                    control_plug(plug_ip, turn_on=False)
                elif humidity < humidity_threshold_on and not plug_on:
                    control_plug(plug_ip, turn_on=True)
                else:
                    pass

                if len(datas) > 0:
                    break
    except TimeoutError:
        print("An error occurred while getting the humidity.")


def get_plug_status(ip_address):
    """
    Gets the status of the smart plug.

    :param ip_address: str, the IP addres of the smart plug.
    :return: str, the satus of the plug (on/off).
    """

    url = f"http://{ip_address}/relay/0"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            status = response.json()["ison"]
            return status
        else:
            print("Failed to get status.")
    except:
        print("An error occurred while getting status.")


def control_plug(ip_address, turn_on=True):
    """
    Turns the smart plug on and off.

    :param ip_address: str, the IP address of the smart plug.
    :param turn_on: bool, True to turn the plug on, False to turn it off.
    """

    command = "on" if turn_on else "off"
    url = f"http://{ip_address}/relay/0?turn={command}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Plug turned {command} succesfully.")
        else:
            print(f"Failed to turn {command} the plug.")
    except:
        print(f"An error occurred while turning the plug {command}.")
    

def get_conf_info(conf_file_name):
    """
    Gets the MAC address of the RuuviTag sensor and the IP address of the
    smart plug from the configuration file and saves them to the list.

    :param conf_file_name: str, the name of the configuration file.
    :return: list, contains the IP address and MAC address.
    """

    try:
        conf_file = open(conf_file_name, mode='r')
        conf_info = []
        for file_line in conf_file:
            file_line = file_line.rstrip()
            conf_info.append(file_line)
        conf_file.close()
        return conf_info
    except OSError:
        print(f"Error: opening the file '{conf_file_name}' failed!")
        return []


def main():
    conf_file_name = "Conf_file.txt"
    conf_info = get_conf_info(conf_file_name)

    if not conf_info:
        return
    else:
        plug_ip = conf_info[0]
        ruuvitag_mac = conf_info[1]
        asyncio.run(monitor_and_control_humidity(ruuvitag_mac, plug_ip))


if __name__ == "__main__":
    main()
