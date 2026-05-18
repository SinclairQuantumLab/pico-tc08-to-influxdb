# Developed from TC-08 SINGLE MODE EXAMPLE (../picosdk-python-wrappers-master/usbtc08Examples/tc08SingleModeExample.py)
# Use streaming mode instead [see the Programmer's guide (usb-tc08-thermocouple-data-logger-programmers-guide) and
# TC-08 STREAMING MODE EXAMPLE modified by JH (../picosdk-python-wrappers-master/usbtc08Examples/tc08SingleModeExample.py)]

import ctypes
from picosdk.usbtc08 import usbtc08 as tc08
from picosdk.functions import assert_pico2000_ok

from time import sleep
from datetime import datetime
import traceback

from pathlib import Path
import sys

import tomllib
from typing import Any

# >>>>> app configuration >>>>>
if len(sys.argv) > 2:
    raise SystemExit("Usage: uv run main.py [settings.toml]")
settings_path = sys.argv[1] if len(sys.argv) == 2 else "./settings.toml"

with open(settings_path, "rb") as f:
    SETTINGS: dict[str, Any] = tomllib.load(f)

SN = str(SETTINGS["sn"])
period = float(SETTINGS["period_s"])  # in second
measurement = str(SETTINGS.get("measurement", "TC08logger"))
channels: dict[int, str] = {
    int(channel): name for channel, name in SETTINGS["channels"].items()
}
enable_logging = bool(SETTINGS.get("enable_logging", True))
dirname_log = str(SETTINGS.get("dirname_log", "./logs/"))  # folder to save log files
fname_log_meas = str(SETTINGS.get("fname_log_meas", "temp.log"))
fname_log_err = str(SETTINGS.get("fname_log_err", "error.log"))
# <<< load & parse config files <<<

log_dir = Path(dirname_log)
path_log_meas = log_dir / fname_log_meas
path_log_err = log_dir / fname_log_err
if enable_logging:
    log_dir.mkdir(exist_ok=True, parents=True)

print(f"TC-08 logger SN = {SN}")
print(f"Settings file = {settings_path}")
print(f"Measurement period = {period} s.")
print(f"Active channels = {list(channels.keys())}.")
print(f"File logging = {'enabled' if enable_logging else 'disabled'}.")
if enable_logging:
    print(f"Measurement log = {path_log_meas}")
    print(f"Error log = {path_log_err}")
print()

# <<<<< app configuration <<<<<

# >>> load IMAQ config >>>
with open("imaq_config/auth.toml", "rb") as f:
    AUTH = tomllib.load(f)
# <<< load IMAQ config <<<

# >>> InfluxDB configuration >>>
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
INFLUXDB_CLIENT = influxdb_client.InfluxDBClient(**AUTH["influxdb"])
INFLUXDB_WRITE_API = INFLUXDB_CLIENT.write_api(write_options=SYNCHRONOUS)
INFLUXDB_ORG = AUTH["influxdb"]["org"]; INFLUXDB_BUCKET = AUTH["influxdb"]["bucket"]
print(f"InfluxDB client initialized for org='{INFLUXDB_ORG}', bucket='{INFLUXDB_BUCKET}'.")
print()
# <<< InfluxDB configuration <<<


def main():
    # Create chandle and status ready for use
    chandle = ctypes.c_int16()
    status = {}  # dict to store status of device oprations; see the usages below

    try:
        # open unit
        print(f"Connecting to a TC-08 logger...")
        status["open_unit"] = tc08.usb_tc08_open_unit()
        assert_pico2000_ok(status["open_unit"])
        chandle = ctypes.c_int16(status["open_unit"])

        if status["open_unit"] != 1:  # 1 means USBTC08_OK in the Pico status codes
            raise Exception(
                f"Error: Could not open device. Error code: {status['open_unit']}\n\tcf. status=0: no (more) available device to connect.")

        print(f"Connected.")
        print()

        # set mains rejection to 60 Hz
        status["set_mains"] = tc08.usb_tc08_set_mains(
            chandle, 1)  # 0: 50 Hz, 1: 60 Hz
        assert_pico2000_ok(status["set_mains"])

        # set up channel
        # therocouples types and int8 equivalent
        # B=66 , E=69 , J=74 , K=75 , N=78 , R=82 , S=83 , T=84 , ' '=32 , X=88
        typeK = ctypes.c_int8(75)
        for channel in channels:
            status["set_channel"] = tc08.usb_tc08_set_channel(
                chandle, channel, typeK)
            assert_pico2000_ok(status["set_channel"])

        # get minimum sampling interval in ms
        status["get_minimum_interval_ms"] = tc08.usb_tc08_get_minimum_interval_ms(
            chandle
        )
        assert_pico2000_ok(status["get_minimum_interval_ms"])

        temp = (ctypes.c_float * 9)()
        overflow = ctypes.c_int16(0)

        # raise Exception() # error test

        # repeat measuring temps and upload to DB server
        while True:
            try:
                # get single temperature reading
                units = tc08.USBTC08_UNITS["USBTC08_UNITS_CENTIGRADE"]
                status["get_single"] = tc08.usb_tc08_get_single(
                    chandle, ctypes.byref(temp), ctypes.byref(overflow), units
                )
                assert_pico2000_ok(status["get_single"])

                # raise Exception() # error test

                # print & log data
                datetimestr = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                measstr = f"{datetimestr}: Cold Junction={temp[0]:.02f}"
                for channel in channels:
                    measstr += f", Ch{channel}={temp[channel]:.2f}"

                print(measstr)

                if enable_logging:
                    with path_log_meas.open("a") as f:
                        f.write(measstr + "\n")

                # upload results to InfluxDB
                # format your data to write to the database server

                records = \
                    [  # cold junction
                        {
                            "measurement": measurement,
                            "tags": {
                                "Logger SN": SN,
                                "Channel": "Cold Junction",
                            },
                            "fields": {"Temp[degC]": temp[0]},
                        }
                    ] + \
                    [  # channel temperatures
                        {
                            "measurement": measurement,
                            "tags": {
                                "Logger SN": SN,
                                "Channel": channel_name,
                            },
                            "fields": {"Temp[degC]": temp[channel]},
                        }
                        for channel, channel_name in channels.items()
                    ]

                # send the data
                INFLUXDB_WRITE_API.write(
                    bucket=INFLUXDB_BUCKET,
                    org=INFLUXDB_ORG,
                    record=records,
                )

            except Exception as ex:
                datetimestr = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                measstr = f"{datetimestr}: Error occured during a measurement."
                if enable_logging:
                    measstr += f" See \"{path_log_err}\"."
                print(measstr)
                if enable_logging:
                    with path_log_meas.open("a") as f:
                        f.write(measstr + "\n")

                exstr = f"{datetimestr}: Error occured during a measurement.\n"
                exstr += "".join(traceback.format_exception(ex))
                if enable_logging:
                    with path_log_err.open("a") as f:
                        f.write(exstr + "\n\n")

            # wait until next period
            sleep(period)

    except Exception as ex:
        datetimestr = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        exstr = f"{datetimestr}: Error occured out of the measurement loop.\n"
        exstr += "".join(traceback.format_exception(ex))
        print(exstr)

        # append error message to log file
        if enable_logging:
            with path_log_err.open("a") as f:
                f.write(exstr + "\n\n")

    finally:
        # close unit
        try:
            status["close_unit"] = tc08.usb_tc08_close_unit(chandle)
            assert_pico2000_ok(status["close_unit"])
        except:
            pass

        try:
            INFLUXDB_CLIENT.close()
        except:
            pass

        # display status returns
        # print(status)
        # print(temp)

        print("Connection to TC-08 Logger closed. Terminating...")


if __name__ == "__main__":
    main()
