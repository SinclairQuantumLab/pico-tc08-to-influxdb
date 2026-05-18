# PicoLog TC-08 temperature logging Python app for Josiah Sinclair group use

## Functions

Periodically read temps and upload it to Sr group's InfluxDB

## Requirements

- PicoSDK C libraries for the TC-08
- PicoLog TC-08 thermocouple logger and thermocouples
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) Python project manager
- Access to the target InfluxDB bucket
- Access to the private [`imaq_config`](https://github.com/SinclairQuantumLab/imaq_config) repository used by this app
- TC-08 logger info:
  - Serial number

## Initial setup

1. Install `picosdk`, the SDK for Pico devices, before installing this app.

   Follow the instruction in README of `picosdk-python-wrappers` github repo: <https://github.com/picotech/picosdk-python-wrappers>, depending on the OS. The below is the brief instructuion as of 06/23/2024.

    1. Installing `picosdk` C libraries:
        - Windows:
            1. Download `PicoSDK_64_10.7.26.362.exe` from <https://www.picotech.com/downloads>.
            2. Run the `.exe` file to install `picosdk`.
            3. Close and reopen PowerShell after installing PicoSDK so updated system paths are loaded.
        - Ubuntu: run the below command lines in `bash` terminal:

            ```bash
            sudo bash -c 'wget -O- https://labs.picotech.com/Release.gpg.key | gpg --dearmor > /usr/share/keyrings/picotech-archive-keyring.gpg'
            sudo bash -c 'echo "deb [signed-by=/usr/share/keyrings/picotech-archive-keyring.gpg] https://labs.picotech.com/rc/picoscope7/debian/ picoscope main" >/etc/apt/sources.list.d/picoscope7.list'
            sudo apt update
            sudo apt install libusbtc08
            ```

    (Optional) installing a GUI software named PicoLog <https://www.picotech.com/downloads> for the OS will help checking the connection to and features of TC-08 device.

2. **(IMPORTANT) REBOOT THE COMPUTER AFTER INSTALLING `picosdk`**. The path to the library should be appended into the `PATH` environment variable (e.g., `C:\Program Files\Pico Technology\SDK\lib\` in Windows).

3. Install [`uv`](https://docs.astral.sh/uv/getting-started/installation/) Python project manager if it has not been installed.

4. Open a terminal (e.g., PowerShell for Windows) and go to the location to install this app as like the below example:

    ```powershell
    cd $HOME\Projects\ # for windows.
    ```

    ```bash
    cd ~/Projects/ # for linux
    ```

5. Clone this repo:

    ```bash
    git clone https://github.com/SinclairQuantumLab/pico-tc08-to-influxdb.git
    cd pico-tc08-to-influxdb/
    ```

6. Clone the private `imaq_config` repo into this repo's `imaq_config` folder for InfluxDB info.

    ```bash
    git clone https://github.com/SinclairQuantumLab/imaq_config.git
    ```

    The local folder name should be `imaq_config`, and `imaq_config/auth.toml` should exist before running `main.py`.

7. Run `uv sync` to install this app.

    ```bash
    uv sync
    ```

8. Try running `picotest.py` to check if picosdk successfully read the temperature from the logger.

    ```bash
    uv run picotest.py
    ```

    The output should look like the below example:

    ```powershell
    > uv run .\picotest.py
    Meas#0: Cold Junction=23.909324645996094, Channel 1=22.9122314453125,
    Meas#1: Cold Junction=23.909475326538086, Channel 1=22.86825180053711,
    Meas#2: Cold Junction=23.909475326538086, Channel 1=23.180992126464844,
    {'open_unit': 1, 'set_mains': 1, 'set_channel': 1, 'get_minimum_interval_ms': 200, 'get_single': 1, 'close_unit': 1}
    <__main__.c_float_Array_9 object at 0x000001B1AFA1E760>
    ```

9. Copy `settings.toml.template` to `settings.toml` and configure the measurement for this the TC-08 session.

    ```bash
    cp settings.toml.template settings.toml
    ```

    Query the connected TC-08 device serial number:

    ```bash
    uv run query_device_sn.py
    ```

    Open `settings.toml` and set:

    - `sn`: TC-08 serial number
    - `period_s`: measurement period in seconds
    - `channels`: active TC-08 channels and InfluxDB channel names
    - `enable_logging`: whether to write local log files
    - log file names, if the defaults should be changed

10. Try running `main.py` script to check if the app runs as it should.

    ```bash
    uv run main.py
    ```

    To use a specific configuration file:

    ```bash
    uv run main.py settings_AC161_246.toml
    ```

11. Check if a relevant way to start up the app in the next section works.

## Starting app

### Windows

1. Run `uv sync` once in the project root so `.venv` exists.
2. Run (doubleclick) `.\Startup.lnk` shortcut file. If the `.lnk` file is moved/copied out of the software folder (with `main.py`), change the `Start in` value from `%CD` to the absolute path of the software folder (e.g., `"%USERPROFILE%\PicoLog TC-80 temp logging\TC08logger"`) in the Properties setting below:
3. To use a specific configuration file, add the settings file path after `Startup.ps1` in the shortcut command line.
![image](windows-lnk-setting.jpg)

Tested for Windows 11.

### Linux

Go to *Activity* dashboard and click *TC08logger* icon that is to be made by the following procedure:

1. Run `uv sync` once in the project root so `.venv` exists.
2. Grant excecutable permission to `./Startup_bash` and `./Startup_ubuntu` files by running the below line in a terminal.

```bash
    cd <root folder path>
    chmod +x ./Startup_bash ./Startup_ubuntu
```

1. Copy and rename `./Startup_ubuntu.bak` to `./Startup_ubuntu` and `./Startup_ubuntu.desktop.bak` to `./Startup_ubuntu_<a unique name>.desktop` (e.g., `./Startup_ubuntu_TC08logger.desktop`) in the same folder (i.e., the root folder).
2. Open the `Startup_ubuntu` script file and update the placeholders
    - `DIR_TC08LOGGER="##type here the path to the project folder; see README.md##"`
    - `gnome-terminal --title="##Type here the desired title of the terminal##" -- bash -i -c "$STR_CMD"`
3. Open the `.desktop` file in a text editer and update the placeholders
    - `Name=##Type here the desired name of the icon; see README.md##`
    - `Exec=##Add here the path of the app's root folder see README.md##/Startup_ubuntu`
    - `Icon=##Add here the path of the app's root folder see README.md##/icon.png`
4. Run `sudo desktop-file-install ./Startup_ubuntu_<custom name>.desktop` and see if the icon shows up in *Activity* (the dashboard that pops up when clicking the left bottom Ubuntu icon).
5. Click and see if a terminal pops up with title set in Step 3 and start recording temperatures.
6. In case the `.desktop` file has to be updated & re-installed, remove the installed `.desktop` file in `/etc/share/applications/` folder as a super user by running the below command line. Then, open *Activity* dashboard, and see if the ion has disappeared or disappear in a few seconds. After the ion is removed, install the edited `.desktop` again, following Steps 4 and 5.

```bash
    sudo rm /etc/share/applications/Startup_ubuntu_<custom name>.desktop
```

Tested for Ubuntu 24.04.

## Use

It will start reading temps, print in stdout, and uploading to Grafana's DB periodically.

## Developer's notes


- Files for initial setup are from the SDK example folder (../picosdk-python-wrappers-master/)
  - setup.py, .gitignore files and picosdk/ folder were copied here as-is.
  - README.md was copied as README_SDK.md and a corresponding change was made in setup.py (see top comments as a release note therein)
- main.py is the entry point and contains the TC-08 read loop and InfluxDB upload logic.
- `settings.toml` contains the local TC-08 session configuration and is ignored by git.
- `imaq_config/auth.toml` contains shared InfluxDB credentials and is ignored by git.
- The codes are developed from the TC-08 SINGLE MODE EXAMPLE in the SDK folder (../picosdk-python-wrappers-master/usbtc08Examples/tc08SingleModeExample.py).
- `pyproject.toml`, `uv.lock`, and `.python-version` are used for the current `uv` workflow.
