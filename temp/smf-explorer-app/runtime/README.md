# Minimal runtime (ZIP) — used by `start.bat`

When the system **does not have** a version matching `REQUIRED_PY` (here `3.11.0`), `start.bat` asks:

1. **Minimal runtime (no need to download py …)** — unpacks the ZIP from here and creates `.venv`
2. **Download full python … environment** — opens the installer from python.org

Configuration: **PROJECT CONFIGURATION** section in `start.bat`.  
Tools: `start_tools.py` (next to `start.bat`).

## ZIP file name

```
runtime/python-<REQUIRED_PY>-windows-amd64-minimal-runtime.zip
```

Example: `python-3.11.0-windows-amd64-minimal-runtime.zip`  
On 32-bit: use `win32` instead of `amd64`.

Inside the ZIP: `python.exe` at the **root** of the archive. After unpacking:

```
runtime/python-3.11.0/python.exe
```

## How to build the ZIP

On **Windows** (so the package includes `pip` + `virtualenv`):

```bat
cd smf-explorer-app
py -3.11 start_tools.py build-runtime --version 3.11.0 --arch amd64
```

On Linux/macOS the script assembles embeddable only (without running `python.exe`) — build the full package on Windows.

## Distribution

Include: `start.bat`, `start_tools.py`, this ZIP, application code, `vendor\*.whl`.
