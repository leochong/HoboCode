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
hobo --version
hobo --help
```

## Troubleshooting

If `hobo` is not recognized after installation, your Python Scripts directory may not be in PATH. Add it:

```powershell
# PowerShell
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$env:LOCALAPPDATA\Packages\PythonSoftwareFoundation.Python.3.*\LocalCache\local-packages\Python*\Scripts", "User")
```

Then restart your terminal.
