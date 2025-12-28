# Installation

## Prerequisites

- Python 3.10+
- pip or pipx
- Terminal emulator

## Install from PyPI (Recommended)

On Windows, use pipx to automatically handle PATH and isolate the installation:

```bash
# Install pipx if you don't have it
pip install pipx
pipx install hobo
```

Or use pip directly (you may need to add Python Scripts to PATH manually):

```bash
pip install hobo
```

## Install from Source

```bash
git clone https://github.com/leochong/HoboCode
cd HoboCode
pip install -e ".[dev]"
```

## Verify Installation

```bash
hobo --help
```

You should see the list of available commands. If `hobo` is not found, see Troubleshooting below.

## Troubleshooting

### "No module named 'hobo_code'" error

If you get `ModuleNotFoundError: No module named 'hobo_code'` after installation:

1. **Force reinstall with pipx:**
   ```bash
   pipx uninstall hobo
   pipx install hobo
   ```

2. **Or force reinstall from source:**
   ```bash
   pipx uninstall hobo
   pipx install -e /path/to/HoboCode --force
   ```

3. **If pipx metadata is corrupted:**
   ```bash
   # Manually remove the venv and reinstall
   rm -rf %LOCALAPPDATA%\pipx\venvs\hobo-code
   pipx install hobo
   ```

### "hobo is not recognized"

Your Python Scripts directory may not be in PATH. Add it:

```powershell
# PowerShell
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$env:LOCALAPPDATA\Packages\PythonSoftwareFoundation.Python.3.*\LocalCache\local-packages\Python*\Scripts", "User")
```

Then restart your terminal.
