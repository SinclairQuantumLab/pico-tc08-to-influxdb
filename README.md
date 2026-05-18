# PicoLog TC-08 temperature logging Python app for Josiah Siclair group use

## Functions

Periodically read temps and upload it to Sr group's InfluxDB

## Initial setup

1. Install Miniforge (prefered; <https://github.com/conda-forge/miniforge>) or Miniconda (<https://docs.conda.io/projects/miniconda/en/latest/>).
2. Open VSCode, open this folder in VSCode, and create conda environment in VSCode
    - Command Palette (Ctrl+Shift+P) -> Python: Create Environment... -> Conda
    - **For Windows**, Go to Command Palette (Ctrl+Shift+P) -> Preferences: Open User Settings (JSON) and add the following item in the opened `setting.json` file, to avoid PowerShell from blocking `$PROFILE` `.ps1` file from running (corresponding to `.bashrc` file for `bash`) and thus preventing conda environment from being activated:

        ```JSON
        "terminal.integrated.profiles.windows": {
            "PowerShell": {
                "source": "PowerShell",
                "icon": "terminal-powershell",
                "args": ["-ExecutionPolicy", "Bypass"],
            }
        },
        "terminal.integrated.defaultProfile.windows": "PowerShell",
        ```

3. Open `runtest.py` and press `F5` key to let PowerShell terminal opened in VSCode and the conda environment are activated.
4. Install `picosdk`, the SDK for Pico devices, and the Python wrapper, following the instruction in README of `picosdk-python-wrappers` github repo: <https://github.com/picotech/picosdk-python-wrappers>, depending on the OS. The below is the brief instructuion as of 06/23/2024.
    1. Installing `picosdk`:
        - Windows:
            1. Download `PicoSDK_64_10.7.26.362.exe` from <https://www.picotech.com/downloads>.
            2. Run the `.exe` file to install `picosdk'
        - Ubuntu: run the below command lines in `bash` terminal:

            ```bash
            sudo bash -c 'wget -O- https://labs.picotech.com/Release.gpg.key | gpg --dearmor > /usr/share/keyrings/picotech-archive-keyring.gpg'
            sudo bash -c 'echo "deb [signed-by=/usr/share/keyrings/picotech-archive-keyring.gpg] https://labs.picotech.com/rc/picoscope7/debian/ picoscope main" >/etc/apt/sources.list.d/picoscope7.list'
            sudo apt update
            sudo apt install libusbtc08
            ```

    2. Installing python wapper package
        1. Download the `picosdk-python-wrappers` github repo to a folder.

            ```bash
            cd <folder path>
            git clone https://github.com/picotech/picosdk-python-wrappers.git
            ```

            Install GIT (<https://git-scm.com/>) if it has not bean istalled!
        2. Activate the conda environment for Sr3 TC08 logging software.

            ```bash
            conda activate <path to Sr3 TC08 repo folder>/.conda
            ```

        3. Install the Python package in the conda env.

            ```bash
            cd picosdk-python-wrappers
            ```

            - Windows:

                ```powershell
                pip install .
                ```

            - Linux:

                ```bash
                pip install . --user
                ```

                to install for the current user only, or

                ```bash
                sudo pip install .
                ```

        4. Run `conda list` and check if the `picosdk` package is successfully installed (over pypi).
    (Optional) installing a GUI software named PicoLog <https://www.picotech.com/downloads> for the OS will help checking the connection to and features of TC-08 device.
5. Run `conda install -r requirements` in the terminal to install required Python packages.
    - If Raspberry Pi 3B+ is used, do not use any Conda distributions and instead do everything in `venv` with system's `python`.
    - The 64-bit ARM architecture (aach64) for Raspberry Pi 4B is not supported by Pico Technology (as of 2023/10/22; see <https://www.picotech.com/support/viewtopic.php?t=42162>)
6. Try running `picotest.py` script by pressing `F5` key to check if picosdk successfully read the temperature from the logger.
7. Run `mamba install influxdb-client` in miniforge (or `python -m pip install influxdb-client` for other conda).
8. Open `main.py` and setup `assingment` dict variable to assign `Location` (description of where the temp is being measured) and `Channel` (TC-08 logger's channel #) of temp measurements. Set measurement period to `period` variable with the unit of second.
9. Try running `main.py` script by pressing `F5` key to check if the app runs as it should.
10. Check if a relevant way to start up the app in the next section works.

## Starting app

### Windows

1. Copy and rename `./run_TC08logger.ps1.bak` to `./run_TC08logger.ps1`
2. Open the `./run_TC08logger.ps1` script file and update the placeholder:
    - `$host.ui.RawUI.WindowTitle = "##Type here the desired title of the consol; see README.md##"`
3. Run (doubleclick) `.\Startup_windows.lnk` shortcut file. If the `.lnk` file is moved/copied out of the software folder (with `main.py`), change the `Start in` value from `%CD` to the absolute path of the software folder (e.g., `"%USERPROFILE%\PicoLog TC-80 temp logging\TC08logger"`) in the Properties setting below:
![image](windows-lnk-setting.jpg)

Tested for Windows 11.

### Linux

Go to *Activity* dashboard and click *TC08logger* icon that is to be made by the following procedure:

1. Grant excecutable permission to `./Startup_bash` and `./Startup_ubuntu` files by running the below line in a terminal.

```bash
    cd <root folder path>
    chmod +x ./Startup_bash ./Startup_ubuntu
```

2. Copy and rename `./Startup_ubuntu.bak` to `./Startup_ubuntu` and `./Startup_ubuntu.desktop.bak` to `./Startup_ubuntu_<a unique name>.desktop` (e.g., `./Startup_ubuntu_TC08logger.desktop`) in the same folder (i.e., the root folder).
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

## Autostart setting at OS startup

### Windows

Modify the `.\Startup_windows.lnk` following [this section](#windows).
Copy the `.lnk` file to `%USERPROFILE%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`.

Tested for Windows 11.

### Linux

Using *Startup Applications Properties* GUI application.
Refer to <https://help.ubuntu.com/stable/ubuntu-help/startup-applications.html.en>.

1. Open gnome-session-properties GUI by one of the following ways:
    - Open *Activity* dashboard and search for *Startup Applications Properties*
    - Press Alt+F2 and run `gnome-session-properties`
2. Click *Add* button and populate the blanks as follows:
    - Name: TC08logger
    - Command: ##type the absolute path to the (renamed) copy of `Startup_ubuntu` script file## (e.g.,/home/korra/Startup_ubuntu_TC08logger)
    - Comment: Pico Logger TC-08 read & upload to Grafana's Influx DB
    ![image](ubuntu-startup-application-setting.png)
3. Click *Save* button.

Tested for Ubuntu 24.04.

## Use

It will start reading temps, print in stdout, and uploading to Grafana's DB periodically.

## Developer's notes

- Files for initial setup are from the SDK example folder (../picosdk-python-wrappers-master/)
  - setup.py, .gitignore files and picosdk/ folder were copied here as-is.
  - README.md was copied as README_SDK.md and a corresponding change was made in setup.py (see top comments as a release note therein)
- main.py is the entry point and contain all the essential codes.
- The codes are developed from the TC-08 SINGLE MODE EXAMPLE in the SDK folder (../picosdk-python-wrappers-master/usbtc08Examples/tc08SingleModeExample.py).
