import requests
import asyncio
from ruuvitag_sensor.ruuvi import RuuviTagSensor
import datetime


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

                plug_on = get_plug_status(plug_ip)
                status = "on" if plug_on else "off"
                save_system_status_to_file(status, humidity)

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
    
def save_system_status_to_file(status, humidity):
    """
    Saves the plug status and humidity with a timestamp to the file.
    
    :param status: str, current on/off status of the Shelly plug.
    :param humidity: float, the measured relative humidity.
    """
    
    current_time = datetime.datetime.now()
    data_file_name = "Data.txt"
    try:
        data_file = open(data_file_name, mode='a')
        data_file.write(f"{current_time}: Shelly plug is {status}, "
                        f"and the humidity is {humidity} % RH.\n")
        data_file.close()
    except OSError:
        print(f"Error: writing to the file '{data_file_name}' failed!")
        return


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
