@echo off
setlocal EnableExtensions EnableDelayedExpansion
rem =============================================================================
rem  Universal Windows launcher (venv, deps, run). Edit CONFIG section below.
rem  Args: start.bat | start.bat --reinstall | start.bat -r
rem  Missing Python: [1] embed ZIP (RUNTIME_DIR_REL) or [2] python.org installer.
rem  Build embed: python start_tools.py build-runtime --version X.Y.Z --arch amd64
rem  Reuse elsewhere: copy start.bat + start_tools.py and set CONFIG variables.
rem  (start_en.bat calls this file.)
rem =============================================================================

set "REINSTALL=0"
call :ParseArgs %*
if errorlevel 2 exit /b 0
if errorlevel 1 exit /b 1


rem =============================================================================
rem PROJECT CONFIGURATION  — edit these variables only
rem =============================================================================

rem Name shown in logs / console header
set "APP_NAME=SMF Explorer"

rem Entry script relative to this .bat directory (run after activate)
set "APP_ENTRY=main.py"

rem URL hint shown at start (text only; does not open a browser)
set "APP_URL_HINT=http://localhost:8080"

rem Exact base Python version (X.Y.Z)
set "REQUIRED_PY=3.11.0"

rem pip requirements (relative path)
set "REQ_REL=requirements.txt"

rem Optional local wheel. Empty = skip. Missing file = warning.
set "WHEEL_REL=vendor\smfexplorer-1.1.13-py3-none-any.whl"

rem Single Python helper next to this .bat (find / check / fix / build-runtime)
set "HELPER_REL=start_tools.py"

rem Folder for ZIP / extracted portable Python
set "RUNTIME_DIR_REL=runtime"

rem 1 = show Minimal runtime option in the menu; 0 = download installer only
set "ENABLE_MINIMAL_RUNTIME=1"

rem Short note under the menu (why this Python version)
set "PYTHON_PIN_NOTE=smfexplorer needs Python 3.9-3.11; this launcher pins REQUIRED_PY."

rem Splash: 1 = cls + logo + pause at start; 0 = off
set "ENABLE_SPLASH=1"
set "SPLASH_SECONDS=2"

rem Startup log
set "LOG_DIR_REL=logs"
set "LOG_FILE_NAME=start_latest.log"


rem =============================================================================
rem DERIVED PATHS  — do not edit (computed from configuration)
rem =============================================================================

cd /d "%~dp0"
set "APP_DIR=%CD%"

set "VENV_DIR=%APP_DIR%\.venv"
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"
set "VENV_ACTIVATE=%VENV_DIR%\Scripts\activate.bat"

set "REQ_FILE=%APP_DIR%\%REQ_REL%"
set "HELPER=%APP_DIR%\%HELPER_REL%"

rem Wheel: empty WHEEL_REL => no path
set "WHEEL_FILE="
if defined WHEEL_REL if not "%WHEEL_REL%"=="" set "WHEEL_FILE=%APP_DIR%\%WHEEL_REL%"

rem major.minor from REQUIRED_PY (e.g. 3.11.0 -> 3 / 11) — quick checks in .bat
for /f "tokens=1,2 delims=." %%A in ("%REQUIRED_PY%") do (
    set "REQ_MAJOR=%%A"
    set "REQ_MINOR=%%B"
)

set "RUNTIME_ROOT=%APP_DIR%\%RUNTIME_DIR_REL%"
set "RUNTIME_ARCH=amd64"
set "PY_DOWNLOAD_URL=https://www.python.org/ftp/python/%REQUIRED_PY%/python-%REQUIRED_PY%-amd64.exe"
if /i "%PROCESSOR_ARCHITECTURE%"=="x86" if not defined PROCESSOR_ARCHITEW6432 (
    set "RUNTIME_ARCH=win32"
    set "PY_DOWNLOAD_URL=https://www.python.org/ftp/python/%REQUIRED_PY%/python-%REQUIRED_PY%.exe"
)
set "RUNTIME_DIR=%RUNTIME_ROOT%\python-%REQUIRED_PY%"
set "RUNTIME_ZIP=%RUNTIME_ROOT%\python-%REQUIRED_PY%-windows-%RUNTIME_ARCH%-minimal-runtime.zip"
set "RUNTIME_PY=%RUNTIME_DIR%\python.exe"

rem start_tools.py reads this as version fallback
set "SMF_REQUIRED_PY=%REQUIRED_PY%"

rem UTF-8 (ASCII logo), ANSI, navy background, optional splash
chcp 65001 >nul
call :InitAnsi
call :ApplyConsoleTheme
call :ShowSplash

if not exist "%APP_DIR%\%LOG_DIR_REL%" mkdir "%APP_DIR%\%LOG_DIR_REL%"
set "APP_LOG=%APP_DIR%\%LOG_DIR_REL%\%LOG_FILE_NAME%"
echo ==== %APP_NAME% start %DATE% %TIME% ==== > "!APP_LOG!"

call :ValidateConfig
if errorlevel 1 goto :Finish

call :RunApp
set "APP_EXIT=!ERRORLEVEL!"
if not defined APP_EXIT set "APP_EXIT=1"

:Finish
if not defined APP_EXIT set "APP_EXIT=1"
echo.
if "!APP_EXIT!"=="0" (
    call :EchoOk "Press any key to close this window..."
) else (
    call :EchoErr "Error code=!APP_EXIT!. Press any key to close this window..."
)
echo Log: !APP_LOG!
pause >nul
exit /b !APP_EXIT!


rem =============================================================================
rem CONFIG VALIDATION
rem =============================================================================

:ValidateConfig
if "%APP_NAME%"=="" (
    call :EchoErr "[ERROR] Set APP_NAME in the CONFIGURATION section."
    exit /b 1
)
if "%APP_ENTRY%"=="" (
    call :EchoErr "[ERROR] Set APP_ENTRY in the CONFIGURATION section."
    exit /b 1
)
if "%REQUIRED_PY%"=="" (
    call :EchoErr "[ERROR] Set REQUIRED_PY=X.Y.Z in the CONFIGURATION section."
    exit /b 1
)
if "%REQ_MAJOR%"=="" (
    call :EchoErr "[ERROR] REQUIRED_PY must be X.Y.Z (e.g. 3.11.0)."
    exit /b 1
)
if not exist "%REQ_FILE%" (
    call :EchoErr "[ERROR] Missing requirements file: %REQ_FILE%"
    exit /b 1
)
if not exist "%HELPER%" (
    call :EchoErr "[ERROR] Missing helper: %HELPER%"
    call :EchoInfo "Copy start_tools.py next to start.bat."
    exit /b 1
)
if not exist "%APP_DIR%\%APP_ENTRY%" (
    call :EchoErr "[ERROR] Missing entry script: %APP_DIR%\%APP_ENTRY%"
    exit /b 1
)
exit /b 0


rem =============================================================================
rem MAIN SEQUENCE
rem =============================================================================

:RunApp
echo.
call :EchoInfo "=== %APP_NAME% ==="
call :EchoInfo "Directory: %APP_DIR%"
call :EchoInfo "Python:    %REQUIRED_PY%   entry: %APP_ENTRY%"
if "!REINSTALL!"=="1" call :EchoInfo "Mode:     --reinstall  (recreate .venv)"
echo.

if "!REINSTALL!"=="1" (
    call :EchoInfo "[.venv] --reinstall: removing existing environment and recreating..."
    call :RecreateVenv
    if errorlevel 1 exit /b 1
) else if exist "%VENV_PY%" (
    call :CheckVenvPaths
    if errorlevel 1 (
        call :EchoErr "[.venv] Invalid paths - attempting repair..."
        call :TryFixVenvPaths
        if errorlevel 1 (
            call :EchoErr "[.venv] Repair failed - recreating .venv..."
            call :RecreateVenv
            if errorlevel 1 exit /b 1
        ) else (
            call :CheckVenvPaths
            if errorlevel 1 (
                call :EchoErr "[.venv] Paths still invalid after repair - recreating .venv..."
                call :RecreateVenv
                if errorlevel 1 exit /b 1
            ) else (
                call :EchoOk "[.venv] Paths repaired."
            )
        )
    ) else (
        call :EchoOk "[.venv] Paths OK - using existing environment."
    )
) else (
    call :EchoInfo "[.venv] No environment - creating a new .venv..."
    call :CreateVenv
    if errorlevel 1 exit /b 1
    call :InstallRequirements
    if errorlevel 1 exit /b 1
)

echo.
rem Avoid parentheses in message text - prevents "was unexpected at this time" in cmd
if defined APP_URL_HINT if not "%APP_URL_HINT%"=="" (
    call :EchoOk "[START] Activating .venv and launching - %APP_URL_HINT%"
) else (
    call :EchoOk "[START] Activating .venv and launching the application"
)

call "%VENV_ACTIVATE%"
if errorlevel 1 (
    call :EchoErr "[ERROR] Failed to activate .venv"
    exit /b 1
)

python "%APP_ENTRY%"
set "RUN_EXIT=!ERRORLEVEL!"
echo.
if "!RUN_EXIT!"=="0" (
    call :EchoOk "[STOP] Application exited with code=!RUN_EXIT!"
) else (
    call :EchoErr "[STOP] Application exited with code=!RUN_EXIT!"
)
exit /b !RUN_EXIT!


rem =============================================================================
rem CLI ARGUMENTS
rem =============================================================================

:ParseArgs
if "%~1"=="" exit /b 0
if /i "%~1"=="--reinstall" (
    set "REINSTALL=1"
    shift
    goto :ParseArgs
)
if /i "%~1"=="/reinstall" (
    set "REINSTALL=1"
    shift
    goto :ParseArgs
)
if /i "%~1"=="-r" (
    set "REINSTALL=1"
    shift
    goto :ParseArgs
)
if /i "%~1"=="--help" goto :ShowHelp
if /i "%~1"=="-h" goto :ShowHelp
if /i "%~1"=="/?" goto :ShowHelp
echo [ERROR] Unknown argument: %~1
echo Usage: %~nx0   or   %~nx0 --reinstall   or   %~nx0 --help
exit /b 1

:ShowHelp
echo.
echo %~nx0  - universal Windows launcher
echo.
echo Usage:
echo   %~nx0
echo   %~nx0 --reinstall
echo   %~nx0 -r
echo.
echo Options:
echo   --reinstall, -r, /reinstall
echo       Delete the .venv folder, recreate it, then start the application.
echo   --help, -h, /?
echo       Show this help and exit.
echo.
exit /b 2


rem =============================================================================
rem ANSI / theme / splash / log
rem =============================================================================

:InitAnsi
set "ESC="
for /f %%A in ('powershell -NoProfile -Command "[char]27"') do set "ESC=%%A"
if defined ESC (set "COLOR_LINES=1") else (set "COLOR_LINES=0")
exit /b 0


:ApplyConsoleTheme
rem Navy background + bright text (cmd color: 1=blue, F=white). No echo — no blank lines.
color 1F >nul
exit /b 0


:ShowSplash
if not "%ENABLE_SPLASH%"=="1" exit /b 0
if not defined SPLASH_SECONDS set "SPLASH_SECONDS=2"
cls
call :ApplyConsoleTheme
call :ShowSplashLogo
timeout /t %SPLASH_SECONDS% /nobreak >nul
cls
call :ApplyConsoleTheme
exit /b 0


:ShowSplashLogo
rem =============================================================================
rem STARTUP LOGO — paste / edit "echo" lines below (UTF-8, chcp 65001).
rem Clear all lines and leave only "INIT..." or empty echo( if you want none.
rem WARNING: do not use these characters in the art:  ^  |  &  <  >  %  !
rem =============================================================================
echo(
echo ███████╗███╗   ███╗███████╗
echo ██╔════╝████╗ ████║██╔════╝
echo ███████╗██╔████╔██║█████╗
echo ╚════██║██║╚██╔╝██║██╔══╝
echo ███████║██║ ╚═╝ ██║██║
echo ╚══════╝╚═╝     ╚═╝╚═╝
echo(
echo     ███████╗██╗  ██╗██████╗ ██╗      ██████╗ ██████╗ ███████╗██████╗
echo     ██╔════╝╚██╗██╔╝██╔══██╗██║     ██╔═══██╗██╔══██╗██╔════╝██╔══██╗
echo     █████╗   ╚███╔╝ ██████╔╝██║     ██║   ██║██████╔╝█████╗  ██████╔╝
echo     ██╔══╝   ██╔██╗ ██╔═══╝ ██║     ██║   ██║██╔══██╗██╔══╝  ██╔══██╗
echo     ███████╗██╔╝ ██╗██║     ███████╗╚██████╔╝██║  ██║███████╗██║  ██║
echo     ╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
echo(
echo                         INIT...
echo(
exit /b 0


:AppendLog
if defined APP_LOG >>"!APP_LOG!" echo(%~1
exit /b 0


:EchoOk
rem PASS: green background + black text; then restore navy (console log stays colored).
set "MSG=%~1"
call :AppendLog "!MSG!"
if not "!COLOR_LINES!"=="1" (
    echo !MSG!
    call :ApplyConsoleTheme
    exit /b 0
)
echo !ESC![42;30m!MSG!!ESC![K!ESC![0m
call :ApplyConsoleTheme
exit /b 0


:EchoErr
rem FAIL: burgundy background + white text; then restore navy.
set "MSG=%~1"
call :AppendLog "!MSG!"
if not "!COLOR_LINES!"=="1" (
    echo !MSG!
    call :ApplyConsoleTheme
    exit /b 0
)
echo !ESC![48;2;112;28;40m!ESC![97m!MSG!!ESC![K!ESC![0m
call :ApplyConsoleTheme
exit /b 0


:EchoInfo
rem INFO: bright text on navy (matches console theme).
set "MSG=%~1"
call :AppendLog "!MSG!"
if not "!COLOR_LINES!"=="1" (
    echo !MSG!
    exit /b 0
)
echo !ESC![48;2;10;28;72m!ESC![97m!MSG!!ESC![K!ESC![0m
call :ApplyConsoleTheme
exit /b 0


rem =============================================================================
rem .venv
rem =============================================================================

:CheckVenvPaths
if not exist "%VENV_PY%" (
    call :EchoErr "[.venv] Missing interpreter: %VENV_PY%"
    exit /b 1
)
if not exist "%VENV_ACTIVATE%" (
    call :EchoErr "[.venv] Missing activate.bat"
    exit /b 1
)
if not exist "%VENV_DIR%\pyvenv.cfg" (
    call :EchoErr "[.venv] Missing pyvenv.cfg"
    exit /b 1
)

"%VENV_PY%" "%HELPER%" check-venv "%REQUIRED_PY%"
if errorlevel 1 (
    call :EchoErr "[.venv] .venv verification failed."
    exit /b 1
)
call :EchoOk "[.venv] .venv verification OK."
exit /b 0


:TryFixVenvPaths
"%VENV_PY%" -c "import sys; raise SystemExit(0 if sys.version_info[:2]==(!REQ_MAJOR!,!REQ_MINOR!) else 1)" >nul 2>&1
if errorlevel 1 (
    call :EchoErr "[.venv] .venv interpreter broken / wrong line %REQ_MAJOR%.%REQ_MINOR% - cannot repair."
    exit /b 1
)

"%VENV_PY%" "%HELPER%" fix-venv
if errorlevel 1 (
    call :EchoErr "[.venv] %HELPER_REL% fix-venv failed."
    exit /b 1
)
call :EchoOk "[.venv] Path repair finished."
exit /b 0


:RecreateVenv
if exist "%VENV_DIR%" (
    call :EchoInfo "[.venv] Removing old environment..."
    rmdir /s /q "%VENV_DIR%"
    if exist "%VENV_DIR%" (
        call :EchoErr "[ERROR] Cannot remove %VENV_DIR% - close processes using this venv."
        exit /b 1
    )
    call :EchoOk "[.venv] Old environment removed."
)
call :CreateVenv
if errorlevel 1 exit /b 1
call :InstallRequirements
exit /b %ERRORLEVEL%


:CreateVenv
call :FindRequiredPython
if errorlevel 1 exit /b 1

call :EchoInfo "[.venv] Creating: !PY_EXE! -m venv %VENV_DIR%"
"!PY_EXE!" -m venv "%VENV_DIR%"
if errorlevel 1 (
    rem Embeddable / minimal runtime often lacks full ensurepip — fall back to virtualenv.
    call :EchoInfo "[.venv] -m venv failed - trying: -m virtualenv"
    "!PY_EXE!" -m virtualenv "%VENV_DIR%"
    if errorlevel 1 (
        call :EchoErr "[ERROR] Failed to create .venv via venv or virtualenv"
        exit /b 1
    )
)
if not exist "%VENV_PY%" (
    call :EchoErr "[ERROR] After create, missing %VENV_PY%"
    exit /b 1
)
call :EchoOk "[.venv] Created successfully."
exit /b 0


:InstallRequirements
call :EchoInfo "[.venv] Installing requirements..."
"%VENV_PY%" -m pip install --upgrade pip
if errorlevel 1 (
    call :EchoErr "[ERROR] pip upgrade failed"
    exit /b 1
)
call :EchoOk "[.venv] pip upgrade OK."

rem Requirements + wheel in one call so the resolver sees smfexplorer pins
rem (e.g. packaging>=22,<23) together with NiceGUI dependencies.
if defined WHEEL_FILE if not "%WHEEL_FILE%"=="" if exist "%WHEEL_FILE%" (
    call :EchoInfo "[.venv] Installing %REQ_REL% + %WHEEL_REL%..."
    "%VENV_PY%" -m pip install -r "%REQ_FILE%" "%WHEEL_FILE%"
    if errorlevel 1 (
        call :EchoErr "[ERROR] Installing requirements/wheel failed"
        exit /b 1
    )
    call :EchoOk "[.venv] %REQ_REL% and wheel installed."
) else (
    "%VENV_PY%" -m pip install -r "%REQ_FILE%"
    if errorlevel 1 (
        call :EchoErr "[ERROR] Installing %REQ_REL% failed"
        exit /b 1
    )
    call :EchoOk "[.venv] %REQ_REL% installed."
    if defined WHEEL_FILE if not "%WHEEL_FILE%"=="" (
        call :EchoErr "[WARN] Missing %WHEEL_FILE% - skipped wheel install."
    )
)

call :EchoOk "[.venv] Dependencies installed."
exit /b 0


rem =============================================================================
rem PYTHON DETECTION
rem =============================================================================

:FindRequiredPython
set "PY_EXE="
set "FOUND_VER="

where py >nul 2>&1
if not errorlevel 1 (
    call :EchoInfo "[.venv] Installed interpreters via py -0:"
    py -0 2>nul
    echo.
    call :EchoInfo "[.venv] Searching for Python %REQUIRED_PY% among launcher installs..."
    for /f "usebackq tokens=1,* delims=	" %%A in (`py "%HELPER%" find-python "%REQUIRED_PY%"`) do (
        set "FOUND_VER=%%A"
        set "PY_EXE=%%B"
    )
)

if not defined PY_EXE (
    where python >nul 2>&1
    if not errorlevel 1 (
        for /f "usebackq tokens=1,* delims=	" %%A in (`python "%HELPER%" find-python "%REQUIRED_PY%"`) do (
            set "FOUND_VER=%%A"
            set "PY_EXE=%%B"
        )
    )
)
if not defined PY_EXE (
    where python3 >nul 2>&1
    if not errorlevel 1 (
        for /f "usebackq tokens=1,* delims=	" %%A in (`python3 "%HELPER%" find-python "%REQUIRED_PY%"`) do (
            set "FOUND_VER=%%A"
            set "PY_EXE=%%B"
        )
    )
)

if not defined PY_EXE (
    call :OfferPythonChoice
    exit /b !ERRORLEVEL!
)

if /i not "!FOUND_VER!"=="%REQUIRED_PY%" (
    call :EchoErr "[ERROR] Finder returned version !FOUND_VER!, required is %REQUIRED_PY%."
    call :EchoErr "       Rejected path: !PY_EXE!"
    set "PY_EXE="
    set "FOUND_VER="
    call :OfferPythonChoice
    exit /b !ERRORLEVEL!
)

if not exist "!PY_EXE!" (
    call :EchoErr "[ERROR] Detected path does not exist: !PY_EXE!"
    set "PY_EXE="
    call :OfferPythonChoice
    exit /b !ERRORLEVEL!
)

call :ProbePythonVersion "!PY_EXE!"
if /i not "!PROBE_VER!"=="%REQUIRED_PY%" (
    call :EchoErr "[ERROR] Interpreter !PY_EXE! reports version !PROBE_VER!, required %REQUIRED_PY%."
    set "PY_EXE="
    set "FOUND_VER="
    call :OfferPythonChoice
    exit /b !ERRORLEVEL!
)

call :EchoOk "[.venv] Found Python %REQUIRED_PY%: !PY_EXE!"
exit /b 0


:ProbePythonVersion
rem %~1 = python.exe (may contain spaces). Result: PROBE_VER.
rem Do not use for /f + backticks — they split "C:\Program Files\...".
set "PROBE_VER="
set "VER_TMP=%TEMP%\app_pyver_%RANDOM%%RANDOM%.txt"
del "!VER_TMP!" >nul 2>&1
"%~1" -c "import sys; print('.'.join(map(str, sys.version_info[:3])))" > "!VER_TMP!" 2>nul
if exist "!VER_TMP!" (
    set /p PROBE_VER=<"!VER_TMP!"
    del "!VER_TMP!" >nul 2>&1
)
exit /b 0


rem =============================================================================
rem MENU: required Python version missing
rem =============================================================================

:OfferPythonChoice
echo.
call :EchoErr "[ERROR] Python %REQUIRED_PY% was not found on this system."
where py >nul 2>&1
if not errorlevel 1 (
    call :EchoInfo "       Launcher sees py -0:"
    py -0 2>nul
)
echo.
call :EchoErr "Exactly Python %REQUIRED_PY% is required"
if defined PYTHON_PIN_NOTE if not "%PYTHON_PIN_NOTE%"=="" (
    call :EchoInfo "%PYTHON_PIN_NOTE%"
)
echo.
call :EchoInfo "Choose how to prepare the environment:"
echo.

if "%ENABLE_MINIMAL_RUNTIME%"=="1" (
    call :EchoInfo "  [1] Minimal runtime (no need to download py %REQUIRED_PY%)"
    call :EchoInfo "      Extract the ZIP and create .venv without a system install."
    call :EchoInfo "      Package: %RUNTIME_ZIP%"
    echo.
    call :EchoInfo "  [2] Download full python %REQUIRED_PY% environment"
    call :EchoInfo "      Opens the official python.org installer in your browser."
    call :EchoInfo "      After install, run start.bat again."
    echo.
    choice /C 12 /N /M "Choice [1/2]: "
    if errorlevel 2 goto :OfferPythonChoice_Download
    if errorlevel 1 goto :OfferPythonChoice_Minimal
    goto :OfferPythonChoice_Minimal
)

rem ENABLE_MINIMAL_RUNTIME=0 — download only
call :EchoInfo "  [1] Download full python %REQUIRED_PY% environment"
call :EchoInfo "      Opens the official python.org installer in your browser."
echo.
choice /C 1 /N /M "Choice [1]: "
goto :OfferPythonChoice_Download

:OfferPythonChoice_Minimal
echo.
call :EchoOk "[1] Minimal runtime (no need to download py %REQUIRED_PY%)"
call :EnsureMinimalRuntime
if errorlevel 1 exit /b 1
call :EchoOk "[.venv] Using runtime ZIP: !PY_EXE!"
exit /b 0

:OfferPythonChoice_Download
echo.
call :EchoOk "Download full python %REQUIRED_PY% environment"
call :EchoInfo "Installer link:"
call :EchoInfo "  %PY_DOWNLOAD_URL%"
echo.
call :EchoOk "Opening download in your browser..."
call :EchoInfo "After install, run start.bat again"
call :EchoInfo "  recommended: Add python.exe to PATH and the py launcher"
echo.
start "" "%PY_DOWNLOAD_URL%"
exit /b 1


rem =============================================================================
rem MINIMAL RUNTIME (ZIP)
rem =============================================================================

:EnsureMinimalRuntime
if not exist "!RUNTIME_ROOT!" mkdir "!RUNTIME_ROOT!"

if exist "!RUNTIME_PY!" (
    call :EchoInfo "[runtime] Found extracted runtime: !RUNTIME_PY!"
    call :ProbePythonVersion "!RUNTIME_PY!"
    if /i "!PROBE_VER!"=="%REQUIRED_PY%" (
        set "PY_EXE=!RUNTIME_PY!"
        set "FOUND_VER=%REQUIRED_PY%"
        call :EchoOk "[runtime] Version OK: !PROBE_VER!"
        exit /b 0
    )
    call :EchoErr "[runtime] Folder has version !PROBE_VER!, required %REQUIRED_PY% - recreating from ZIP."
    rmdir /s /q "!RUNTIME_DIR!" 2>nul
)

if not exist "!RUNTIME_ZIP!" (
    call :EchoErr "[ERROR] Missing minimal runtime package:"
    call :EchoErr "       !RUNTIME_ZIP!"
    echo.
    call :EchoInfo "Build it on Windows:"
    call :EchoInfo "  python %HELPER_REL% build-runtime --version %REQUIRED_PY% --arch %RUNTIME_ARCH%"
    call :EchoInfo "Or copy a ready ZIP into %RUNTIME_DIR_REL%\ and run again."
    call :EchoInfo "Details: %RUNTIME_DIR_REL%\README.md"
    exit /b 1
)

call :EchoInfo "[runtime] Extracting: !RUNTIME_ZIP!"
if exist "!RUNTIME_DIR!" (
    rmdir /s /q "!RUNTIME_DIR!" 2>nul
)
mkdir "!RUNTIME_DIR!" 2>nul

powershell -NoProfile -Command "Expand-Archive -LiteralPath '!RUNTIME_ZIP!' -DestinationPath '!RUNTIME_DIR!' -Force"
if errorlevel 1 (
    call :EchoErr "[ERROR] Expand-Archive failed"
    exit /b 1
)

rem ZIP with a top-level folder — flatten so python.exe is under RUNTIME_DIR
if not exist "!RUNTIME_PY!" (
    for /d %%D in ("!RUNTIME_DIR!\*") do (
        if exist "%%~fD\python.exe" (
            call :EchoInfo "[runtime] Moving contents from %%~nxD..."
            robocopy "%%~fD" "!RUNTIME_DIR!" /E /MOVE >nul
            if errorlevel 8 (
                call :EchoErr "[ERROR] robocopy failed while flattening ZIP"
                exit /b 1
            )
            if exist "%%~fD" rmdir /s /q "%%~fD" 2>nul
        )
    )
)

if not exist "!RUNTIME_PY!" (
    call :EchoErr "[ERROR] After extract, missing !RUNTIME_PY!"
    call :EchoInfo "In the ZIP, python.exe should be at the archive root."
    exit /b 1
)

call :ProbePythonVersion "!RUNTIME_PY!"
if /i not "!PROBE_VER!"=="%REQUIRED_PY%" (
    call :EchoErr "[ERROR] Runtime from ZIP reports version !PROBE_VER!, required %REQUIRED_PY%."
    exit /b 1
)

set "PY_EXE=!RUNTIME_PY!"
set "FOUND_VER=%REQUIRED_PY%"
call :EchoOk "[runtime] Ready Python %REQUIRED_PY%: !PY_EXE!"
exit /b 0
