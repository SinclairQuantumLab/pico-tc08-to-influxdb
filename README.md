# PicoLog TC-08 temperature logging Python app for Josiah Sinclair group use

## Functions

Periodically read temps from PicoLog TC-08 thermocouple loggers and optionally upload them to Sr group's InfluxDB.

This app is intended to be configured per TC-08 unit. In normal use, make one local `settings_*.toml` file for each TC-08 logger, set that file's `sn` to the unit's batch/serial string, and run the app with the matching settings file.

## Requirements

- PicoSDK C libraries for the TC-08
- PicoLog TC-08 thermocouple logger and thermocouples
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) Python project manager
- Access to the target InfluxDB bucket, if `enable_influxdb_upload = true`
- Access to the private [`imaq_config`](https://github.com/SinclairQuantumLab/imaq_config) repository used by this app, if `enable_influxdb_upload = true`
- TC-08 logger info:
  - Batch/serial string, found by running `uv run query_device_sn.py`

## Initial setup

1. Install `picosdk`, the SDK for Pico devices, before installing this app.

   The native PicoSDK C libraries must be installed on the OS before hardware access works. The PyPI `picosdk` package installed by `uv` is only the Python wrapper.

   Follow the instruction in README of `picosdk-python-wrappers` github repo: <https://github.com/picotech/picosdk-python-wrappers>, depending on the OS. The below is the brief instruction as of 06/23/2024.

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

4. Open a terminal (e.g., PowerShell for Windows) and go to the location to install this app as in the examples below:

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

6. If this checkout will upload to InfluxDB, clone the private `imaq_config` repo into this repo's `imaq_config` folder for InfluxDB info.

    ```bash
    git clone https://github.com/SinclairQuantumLab/imaq_config.git
    ```

    The local folder name should be `imaq_config`, and `imaq_config/auth.toml` should exist before running `main.py` with InfluxDB upload enabled.

7. Run `uv sync` to install this app.

    ```bash
    uv sync
    ```

8. Try running `picotest.py` to check if picosdk successfully reads the temperature from the logger.

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

9. Query all TC-08 logger batch/serial strings connected to the computer:

    ```bash
    uv run query_device_sn.py
    ```

    Example output:

    ```text
    TC-08 #1: B0001/035
    TC-08 #2: A0194/559
    ```

    Confirm the SNs with the ones labeled on the rear side of the devices.

10. Create and configure a settings file for the TC-08 session. See the next section.

11. Try running `main.py` with the settings file for one TC-08 unit.

    ```bash
    uv run main.py settings_B0001_035.toml
    ```

    If no settings path is passed, `main.py` uses `./settings.toml`:

    ```bash
    uv run main.py
    ```

12. Check if a relevant way to start up the app in the Starting app section works.

## Creating a settings file

Copy `settings.toml.template` to a local settings file and configure the measurement for the TC-08 session.

For the default settings file used by `uv run main.py` with no arguments:

```bash
cp settings.toml.template settings.toml
```

For a TC-08-specific settings file, use a name that identifies the unit. A useful naming pattern is to replace `/` in the batch/serial string with `_`.

```bash
cp settings.toml.template settings_B0001_035.toml
```

This unit-specific naming is recommended when multiple TC-08 loggers may be used from the same checkout, or when one computer has several startup shortcuts.

Open the new settings file and set:

- `sn`: TC-08 batch/serial string printed by `query_device_sn.py`, for example `B0001/035`
- `period_s`: measurement period in seconds
- `enable_logging`: whether to write local log files
- `enable_influxdb_upload`: whether to upload measurements to InfluxDB
- `measurement`: InfluxDB measurement name, if upload is enabled
- `dirname_log`, `fname_log_meas`, `fname_log_err`: local log folder and file names
- `channels`: active TC-08 channels and their InfluxDB channel names

The channel table maps TC-08 channel numbers to names:

```toml
[channels]
1 = "Heater left"
2 = "Heater right"
3 = "AR test viewport outer rim top"
```

Only channels listed in the settings file are activated. `main.py` also records channel `0` as `Cold Junction`.

When multiple TC-08 units are connected, run one process per unit with the matching settings file:

```bash
uv run main.py settings_B0001_035.toml
uv run main.py settings_A0194_559.toml
```

`main.py` scans the connected TC-08 loggers and selects the logger whose batch/serial string matches `sn`. If that unit is not connected, the app exits with an error listing the connected TC-08 SNs it found.

## Starting app

### Windows

For Windows startup, make one local `.lnk` shortcut per TC-08 unit if more than one logger may be used from the same checkout.

1. Copy and rename `Startup.lnk.template` to a local `.lnk` file, for example `Startup_B0001_035.lnk`.
2. Right-click the `.lnk` file and select **Properties**.
3. Go to the **Shortcut** tab and update the settings as needed.
    - In **Target**, pass the unit-specific settings file to `Startup.ps1`. A working example is:

        ```text
        C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -ExecutionPolicy Bypass -File Startup.ps1 settings_B0001_035.toml
        ```

    - If the `.lnk` file stays in the project folder, **Start in** can be blank.
    - When the `.lnk` file is moved outside the project folder, set **Start in** to the absolute path of this project folder `<PROJECT DIR>`.
    - (Optional) click **Change Icon...** and set it to `<PROJECT DIR>\icon.ico`.
4. Run (double-click) the `.lnk` shortcut file.

`Startup.ps1` changes to its own directory, checks `.venv\Scripts\python.exe`, reads `sn` from the selected settings file, sets the terminal title to `Pico TC-08 logger (SN: XX)`, and forwards all arguments to `main.py`. To adjust the terminal window size, edit `$terminalColumns`, `$terminalRows`, and `$terminalBufferRows` near the top of `Startup.ps1`.

Tested for Windows 11.

### Linux

Go to *Activity* dashboard and click *TC08logger* icon that is to be made by the following procedure. Make one local `.desktop` file per TC-08 unit if more than one logger may be used from the same checkout.

1. Grant executable permission to `./Startup_bash` by running the below line in a terminal.

    ```bash
    cd <root folder path>
    chmod +x ./Startup_bash
    ```

2. Copy and rename `./Startup_ubuntu_pico_tc08.desktop.template` to a `.desktop` file for the TC-08 logger, for example `./Startup_ubuntu_pico_tc08_B0001_035.desktop`, in the same folder.
3. Open the `.desktop` file in a text editor and update every placeholder wrapped in `<...>`.
    - `<SN>`: TC-08 serial number or another short label shown in *Activity*
    - `<PROJECT DIR>`: absolute path to this project folder
    - `settings.toml`: settings file to pass to `Startup_bash`; replace it with the unit-specific settings file, for example `settings_B0001_035.toml`

    Do not leave the `<...>` placeholders in the installed `.desktop` file.

4. Run `sudo desktop-file-install ./Startup_ubuntu_pico_tc08_B0001_035.desktop` and see if the icon shows up in *Activity* (the dashboard that pops up when clicking the left bottom Ubuntu icon).
5. Click and see if a terminal pops up and starts recording temperatures.
6. In case the `.desktop` file has to be updated & re-installed, remove the installed `.desktop` file in `/etc/share/applications/` folder as a super user by running the below command line. Then, open *Activity* dashboard, and see if the icon has disappeared or disappear in a few seconds. After the icon is removed, install the edited `.desktop` again, following Steps 4 and 5.

    ```bash
    sudo rm /etc/share/applications/Startup_ubuntu_pico_tc08_B0001_035.desktop
    ```

`Startup_bash` changes to its own directory, checks `.venv/bin/python`, reads `sn` from the selected settings file, sets the terminal title to `Pico TC-08 logger (SN: XX)`, and forwards all arguments to `main.py`. To adjust the terminal window size, edit `terminal_columns` and `terminal_rows` near the top of `Startup_bash`.

Tested for Ubuntu 24.04.

## Use

To start a logger manually:

```bash
uv run main.py settings_B0001_035.toml
```

It will start reading temps, print in stdout, write local logs if `enable_logging = true`, and upload to Grafana's DB if `enable_influxdb_upload = true`.

## Developer's notes

- `main.py` is the entry point and contains the TC-08 read loop and InfluxDB upload logic.
- If no config path is passed, `main.py` loads `./settings.toml`.
- If a config path is passed, `main.py` loads that file.
- `main.py` opens the connected TC-08 whose batch/serial string matches `sn`.
- `query_device_sn.py` prints the batch/serial strings for all TC-08 loggers connected to the computer.
- `picotest.py` is a lightweight TC-08 hardware smoke test developed from the SDK single-mode example.
- `settings*.toml` files contain local TC-08 session configuration and are ignored by git.
- Generated `*.lnk` and `*.desktop` startup files are local and ignored by git.
- `imaq_config/auth.toml` contains shared InfluxDB credentials and is ignored by git.
- The codes are developed from the TC-08 SINGLE MODE EXAMPLE in the SDK folder (../picosdk-python-wrappers-master/usbtc08Examples/tc08SingleModeExample.py).
- `pyproject.toml`, `uv.lock`, and `.python-version` are used for the current `uv` workflow.
