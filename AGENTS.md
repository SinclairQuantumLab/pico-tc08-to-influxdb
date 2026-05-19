# AGENTS.md

## Key Points

- This repo is now `pico-tc08-to-influxdb`, not `pico-tc08-influxdb`.
- Use `uv` for the Python environment. Do not reintroduce conda/miniforge setup instructions.
- The native PicoSDK C libraries must be installed on the OS before hardware access works. The PyPI `picosdk` package is only the Python wrapper.
- Be very conservative with `README.md`: preserve user-written details, notes, comments, wording, and section shape unless the user explicitly asks to remove or rewrite them.
- For patterns copied from other SinclairQuantumLab `*-to-influxdb` repos, match the exact block style, headings, comments, and line breaks as closely as possible.
- Local runtime configuration lives in `settings.toml`; shared InfluxDB credentials live in `imaq_config/auth.toml`. Do not commit real credentials.
- `main.py` defaults to `./settings.toml` when no config path is passed. It does not prompt through stdin anymore.

## Project Purpose

This app reads temperatures from a PicoLog TC-08 thermocouple logger and writes them to the Sinclair group InfluxDB bucket. It is intended for lab use, with per-session TC-08 channel names and logging options stored outside `main.py`.

Primary runtime files:

- `main.py`: TC-08 read loop, local logging, and InfluxDB upload.
- `settings.toml`: local, ignored app/session configuration.
- `settings.toml.template`: tracked template for `settings.toml`.
- `imaq_config/auth.toml`: local, ignored credentials/config from the private `imaq_config` repo.
- `query_device_sn.py`: utility to print connected TC-08 batch/serial numbers.
- `Startup.ps1` and `Startup.lnk`: Windows startup path.
- `Startup_bash`, `Startup_ubuntu.bak`, and `Startup_ubuntu.desktop.bak`: Linux/Ubuntu startup path.

## Repo And Git State

- GitHub remote should be:

  ```text
  https://github.com/SinclairQuantumLab/pico-tc08-to-influxdb.git
  ```

- The repo was renamed from `pico-tc08-influxdb`; update any old references if they reappear.
- Recent work moved the project to `uv`, externalized session settings, added the `imaq_config` dependency, renamed Windows startup files, and added the serial-number query utility.
- `settings.toml` and `imaq_config/` are ignored and should stay local.

## User Preferences And Workflow

- The user wants visible, minimal changes. Avoid broad README rewrites or cleanup that was not asked for.
- If a change removes information, call that out clearly before or while doing it.
- When the user edits files, treat those edits as authoritative. Do not revert or overwrite them unless explicitly asked.
- The user prefers direct implementation once the intent is clear, but wants careful preservation of repo-specific details.
- The user was unhappy when installation details were oversimplified. Keep PicoSDK notes, warnings, and practical installation comments unless asked otherwise.

## Environment And Dependencies

- Python environment is managed by `uv`.
- `pyproject.toml`, `uv.lock`, and `.python-version` define the Python project.
- Use:

  ```bash
  uv sync
  ```

  to create/update `.venv`.

- Run scripts through `uv run`, for example:

  ```bash
  uv run picotest.py
  uv run query_device_sn.py
  uv run main.py
  uv run main.py settings_AC161_246.toml
  ```

- Hardware access requires the PicoSDK C libraries to be installed separately. If the wrapper is installed but the native library is not visible, errors such as `picosdk.errors.CannotFindPicoSDKError: PicoSDK (usbtc08) not found, check PATH` can occur.

## Configuration Model

`main.py` loads configuration like this:

- zero arguments: loads `./settings.toml`
- one argument: loads that TOML file
- more than one argument: exits with usage

Important config keys:

- `sn`: TC-08 serial/batch string used as the InfluxDB `Logger SN` tag.
- `period_s`: measurement period in seconds.
- `measurement`: InfluxDB measurement name.
- `enable_logging`: whether local log files are written.
- `dirname_log`, `fname_log_meas`, `fname_log_err`: local logging paths.
- `[channels]`: TOML table mapping TC-08 channel number to InfluxDB channel name.

The channel table intentionally uses channel numbers as keys and names as values, for example:

```toml
[channels]
1 = "Ch1"
2 = "Ch2"
```

In Python this becomes:

```python
channels: dict[int, str] = {
    int(channel): name for channel, name in SETTINGS["channels"].items()
}
```

Do not reintroduce the old `assignments` list or `assignments_legacy`.

## InfluxDB Pattern

The InfluxDB configuration in `main.py` follows the style used in other SinclairQuantumLab `*-to-influxdb` repos. Keep the heading/comment block structure intact:

```python
# >>> InfluxDB configuration >>>
...
# <<< InfluxDB configuration <<<
```

Credentials are loaded from:

```python
with open("imaq_config/auth.toml", "rb") as f:
    AUTH = tomllib.load(f)
```

Do not hard-code InfluxDB tokens, URLs, orgs, or buckets in `main.py`.

## Device Serial Number Utility

`query_device_sn.py` opens every available TC-08, prints its batch/serial string, and closes all handles.

It uses `usb_tc08_get_unit_info2(..., line=4)`, corresponding to `USBTC08LINE_BATCH_AND_SERIAL` in the Pico TC-08 programmer guide.

Use it during setup before editing `settings.toml`:

```bash
uv run query_device_sn.py
```

Known successful output during this thread:

```text
TC-08 #1: A0194/559
```

`main.py` currently does not verify the connected device against `sn`; it only uses `sn` as an InfluxDB tag. A future improvement could query the connected serial in `main.py` and fail or warn if it differs from `settings.toml`.

## Startup Scripts

Windows:

- Current tracked names are `Startup.ps1` and `Startup.lnk`.
- Old names `run_TC08logger.ps1.bak` and `Startup_windows.lnk` were retired.
- `Startup.ps1` changes to its own directory, checks `.venv\Scripts\python.exe`, then runs `main.py`.
- Any arguments passed to `Startup.ps1` are forwarded to `main.py`, so a config file can be passed through the shortcut.

Linux:

- Current tracked names remain `Startup_bash`, `Startup_ubuntu.bak`, and `Startup_ubuntu.desktop.bak`.
- The Linux section of `README.md` may still reflect the original Ubuntu startup flow. Be careful if changing it; the user has not asked to rename the Linux files yet.

## README Notes

The README has been actively edited by the user. Handle it with care.

Important README behavior to preserve:

- PicoSDK installation is first in setup because native libraries are required before hardware use.
- The PicoSDK install notes include practical OS-specific details and should not be compressed away.
- `uv sync` is the installation command for the Python project.
- Setup includes cloning private `imaq_config` into `imaq_config/`.
- Setup includes copying `settings.toml.template` to `settings.toml`.
- Setup includes running `query_device_sn.py` before setting `sn`.
- Windows startup instructions should not mention the old `%CD%` / `Start in` screenshot flow.

## Verification Commands

Common low-risk checks:

```bash
uv run python -m py_compile main.py
uv run python -m py_compile query_device_sn.py
git diff --check
```

Hardware checks require a connected TC-08 and installed PicoSDK C libraries:

```bash
uv run picotest.py
uv run query_device_sn.py
```

`main.py` will write to InfluxDB, so be deliberate when running it.

## Known Follow-Ups

- Consider adding serial-number verification in `main.py` using the helper logic from `query_device_sn.py`.
- Consider whether `settings copy.toml` should stay tracked; it currently mirrors the template, but real local settings should normally remain untracked.
- Consider whether `windows-lnk-setting.jpg` is still needed after the Windows startup README cleanup.
