#!/usr/bin/env python3
"""CLI helpers for start.bat (Python discovery, venv repair, embedded runtime)."""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
DEFAULT_PY = "3.11.0"


# ---------------------------------------------------------------------------
# shared
# ---------------------------------------------------------------------------

def _parse_xyz(raw: str) -> tuple[int, int, int]:
    parts = raw.strip().split(".")
    if len(parts) != 3:
        raise ValueError(f"expected X.Y.Z, got: {raw!r}")
    return int(parts[0]), int(parts[1]), int(parts[2])


def _parse_xy(raw: str) -> tuple[int, int]:
    parts = raw.strip().split(".")
    if len(parts) < 2:
        raise ValueError(f"expected X.Y[.Z], got: {raw!r}")
    return int(parts[0]), int(parts[1])


def _resolve_version_raw(cli: str | None) -> str:
    if cli and cli.strip():
        return cli.strip()
    env = os.environ.get("SMF_REQUIRED_PY", "").strip()
    return env or DEFAULT_PY


def _norm(p: Path) -> str:
    return os.path.normcase(str(p.resolve()))


def _venv_paths() -> tuple[Path, Path, Path, Path]:
    """venv_dir, scripts_dir, python_exe, activate_bat."""
    venv_dir = (APP_DIR / ".venv").resolve()
    scripts = venv_dir / "Scripts" if (venv_dir / "Scripts").is_dir() else venv_dir / "bin"
    py_exe = scripts / "python.exe" if (scripts / "python.exe").is_file() else scripts / "python"
    return venv_dir, scripts, py_exe, scripts / "activate.bat"


# ---------------------------------------------------------------------------
# find-python
# ---------------------------------------------------------------------------

def _version_tuple(exe: Path) -> tuple[int, int, int] | None:
    try:
        proc = subprocess.run(
            [str(exe), "-c", "import sys; print('.'.join(map(str, sys.version_info[:3])))"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    lines = (proc.stdout or "").strip().splitlines()
    if not lines:
        return None
    parts = lines[0].strip().split(".")
    if len(parts) < 3:
        return None
    try:
        return int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError:
        return None


def _candidates_from_py_launcher(required: tuple[int, int, int]) -> list[Path]:
    found: list[Path] = []
    seen: set[str] = set()

    def add(raw: str) -> None:
        p = Path(raw.strip().strip('"'))
        key = os.path.normcase(str(p.resolve() if p.exists() else p))
        if key in seen:
            return
        seen.add(key)
        found.append(p)

    major, minor, micro = required
    for tag in (f"{major}.{minor}.{micro}", f"{major}.{minor}"):
        try:
            proc = subprocess.run(
                ["py", f"-{tag}", "-c", "import sys; print(sys.executable)"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            continue
        if proc.returncode == 0 and proc.stdout.strip():
            add(proc.stdout.strip().splitlines()[0])

    try:
        proc = subprocess.run(
            ["py", "-0p"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        proc = None
    if proc is not None:
        text = (proc.stdout or "") + (proc.stderr or "")
        for match in re.findall(r"(?:[A-Za-z]:\\|\\\\)[^\r\n]*?\.exe", text, flags=re.I):
            add(match)
    return found


def _candidates_from_path() -> list[Path]:
    found: list[Path] = []
    seen: set[str] = set()
    for name in ("python", "python3"):
        try:
            proc = subprocess.run(
                ["where", name] if os.name == "nt" else ["which", "-a", name],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            continue
        if proc.returncode != 0:
            continue
        for line in (proc.stdout or "").splitlines():
            line = line.strip()
            if not line:
                continue
            p = Path(line)
            key = os.path.normcase(str(p.resolve() if p.exists() else p))
            if key in seen:
                continue
            seen.add(key)
            found.append(p)
    return found


def cmd_find_python(version: str | None) -> int:
    try:
        required = _parse_xyz(_resolve_version_raw(version))
    except ValueError as exc:
        print(f"Invalid Python version: {exc}", file=sys.stderr)
        return 2

    ver = f"{required[0]}.{required[1]}.{required[2]}"
    print(f"Looking for Python {ver} ...", file=sys.stderr)

    exe: Path | None = None
    for candidate in _candidates_from_py_launcher(required) + _candidates_from_path():
        if not candidate.exists():
            continue
        if _version_tuple(candidate) == required:
            exe = candidate.resolve()
            break

    if exe is None:
        print(
            f"Python {ver} not found "
            f"(py -{ver}, py -{required[0]}.{required[1]}, py -0p, PATH).",
            file=sys.stderr,
        )
        return 1

    got = _version_tuple(exe)
    if got != required:
        print(f"Rejected {exe}: version_info={got!r}, required={required!r}", file=sys.stderr)
        return 1

    # Single stdout line: VERSION<TAB>PATH (start.bat / for /f)
    print(f"{ver}\t{exe}")
    return 0


# ---------------------------------------------------------------------------
# check-venv
# ---------------------------------------------------------------------------

def cmd_check_venv(version: str | None) -> int:
    try:
        req_mm = _parse_xy(_resolve_version_raw(version))
    except ValueError as exc:
        print(f"Invalid Python version: {exc}", file=sys.stderr)
        return 2

    venv_dir, _scripts, py_exe, activate_bat = _venv_paths()
    cfg_path = venv_dir / "pyvenv.cfg"

    if not py_exe.is_file():
        print(f"Missing interpreter: {py_exe}", file=sys.stderr)
        return 1
    if not cfg_path.is_file():
        print(f"Missing {cfg_path}", file=sys.stderr)
        return 1

    if _norm(Path(sys.prefix)) != _norm(venv_dir):
        print(f"sys.prefix ({sys.prefix}) != .venv ({venv_dir})", file=sys.stderr)
        return 1

    if sys.version_info[:2] != req_mm:
        print(
            f"Interpreter is not Python {req_mm[0]}.{req_mm[1]}.x: {sys.version.split()[0]}",
            file=sys.stderr,
        )
        return 1

    home: str | None = None
    for raw in cfg_path.read_text(encoding="utf-8", errors="surrogateescape").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        if key.strip().lower() == "home":
            home = val.strip().strip('"')
            break
    if not home:
        print("Missing home= entry in pyvenv.cfg", file=sys.stderr)
        return 1

    home_path = Path(home)
    home_ok = any(
        c.is_file()
        for c in (
            home_path / "python.exe",
            home_path / "python",
            home_path / "python3",
            home_path / "bin" / "python.exe",
            home_path / "bin" / "python",
            home_path / "bin" / "python3",
        )
    )
    if not home_ok:
        print(f"Base Python from pyvenv.cfg does not exist: {home}", file=sys.stderr)
        return 1

    if activate_bat.is_file():
        act_venv: str | None = None
        for raw in activate_bat.read_text(encoding="utf-8", errors="surrogateescape").splitlines():
            stripped = raw.strip()
            lower = stripped.lower()
            if lower.startswith("set virtual_env=") or lower.startswith('set "virtual_env='):
                _, _, rhs = stripped.partition("=")
                act_venv = rhs.strip().strip('"').rstrip("\\/")
                break
        if not act_venv:
            print("Missing VIRTUAL_ENV in activate.bat", file=sys.stderr)
            return 1
        expect = str(venv_dir).rstrip("\\/")
        if os.path.normcase(act_venv) != os.path.normcase(expect):
            print(
                "VIRTUAL_ENV in activate.bat != current .venv\n"
                f"  actual:   {act_venv}\n"
                f"  expected: {expect}",
                file=sys.stderr,
            )
            return 1

    return 0


# ---------------------------------------------------------------------------
# fix-venv
# ---------------------------------------------------------------------------

def _rewrite_activate_bat(path: Path, venv_dir: Path) -> None:
    if not path.exists():
        return
    lines: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="surrogateescape").splitlines(keepends=True):
        lower = line.lstrip().lower()
        if lower.startswith("set virtual_env=") or lower.startswith('set "virtual_env='):
            lines.append(f'set "VIRTUAL_ENV={venv_dir}"\n')
        else:
            lines.append(line)
    path.write_text("".join(lines), encoding="utf-8", errors="surrogateescape")


def _rewrite_activate_ps1(path: Path, venv_dir: Path) -> None:
    if not path.exists():
        return
    escaped = str(venv_dir).replace("'", "''")
    lines: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="surrogateescape").splitlines(keepends=True):
        stripped = line.lstrip()
        indent = line[: len(line) - len(stripped)]
        if stripped.startswith("$env:VIRTUAL_ENV =") or stripped.startswith("$env:VIRTUAL_ENV="):
            lines.append(f"{indent}$env:VIRTUAL_ENV = '{escaped}'\n")
        else:
            lines.append(line)
    path.write_text("".join(lines), encoding="utf-8", errors="surrogateescape")


def _rewrite_pyvenv_cfg(path: Path, venv_dir: Path) -> None:
    if not path.exists():
        return
    home: str | None = None
    new_lines: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="surrogateescape").splitlines():
        key = line.split("=", 1)[0].strip().lower()
        if key == "home":
            home = line.split("=", 1)[1].strip()
            new_lines.append(line)
        elif key == "command":
            candidates = []
            if home:
                home_path = Path(home)
                candidates = [
                    home_path / "python.exe",
                    home_path / "python",
                    home_path / "python3",
                    home_path / "bin" / "python.exe",
                    home_path / "bin" / "python",
                    home_path / "bin" / "python3",
                ]
            py = next((c for c in candidates if c.exists()), None)
            if py is not None:
                new_lines.append(f"command = {py} -m venv {venv_dir}")
            else:
                raw = line.split("=", 1)[1].strip() if "=" in line else ""
                marker = " -m venv "
                if marker in raw:
                    left = raw.split(marker, 1)[0]
                    new_lines.append(f"command = {left}{marker}{venv_dir}")
                else:
                    new_lines.append(line)
        else:
            new_lines.append(line)
    path.write_text("\n".join(new_lines) + "\n", encoding="utf-8", errors="surrogateescape")


def cmd_fix_venv() -> int:
    venv_dir, scripts, _py, _act = _venv_paths()
    if not venv_dir.is_dir():
        print(f"Missing directory {venv_dir}", file=sys.stderr)
        return 1

    prefix = Path(sys.prefix).resolve()
    if prefix != venv_dir:
        print(
            f"Run with the .venv interpreter (sys.prefix={prefix}, expected={venv_dir})",
            file=sys.stderr,
        )
        return 1

    _rewrite_activate_bat(scripts / "activate.bat", venv_dir)
    _rewrite_activate_ps1(scripts / "Activate.ps1", venv_dir)
    _rewrite_pyvenv_cfg(venv_dir / "pyvenv.cfg", venv_dir)
    print(f"Updated .venv paths -> {venv_dir}")
    return 0


# ---------------------------------------------------------------------------
# build-runtime
# ---------------------------------------------------------------------------

def _embed_url(version: str, arch: str) -> str:
    return f"https://www.python.org/ftp/python/{version}/python-{version}-embed-{arch}.zip"


def _download(url: str, dest: Path) -> None:
    print(f"Downloading: {url}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=120) as resp:
        data = resp.read()
    dest.write_bytes(data)
    print(f"  -> {dest} ({len(data)} bytes)")


def _enable_site(extract_dir: Path) -> None:
    pth_files = list(extract_dir.glob("python*._pth"))
    if not pth_files:
        raise FileNotFoundError(f"No python*._pth in {extract_dir}")
    pth = pth_files[0]
    out: list[str] = []
    saw_import_site = False
    saw_site_packages = False
    for line in pth.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("#") and "import site" in stripped:
            out.append("import site")
            saw_import_site = True
            continue
        if stripped == "import site":
            out.append("import site")
            saw_import_site = True
            continue
        if stripped in ("Lib\\site-packages", "Lib/site-packages"):
            saw_site_packages = True
        out.append(line)
    if not saw_import_site:
        out.append("import site")
    if not saw_site_packages:
        out.append("Lib\\site-packages")
    pth.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"Enabled site in {pth.name}")


def _embed_subprocess_env() -> dict[str, str]:
    """Strip host/.venv — otherwise get-pip may see smfexplorer from user-site."""
    env = os.environ.copy()
    for key in (
        "VIRTUAL_ENV",
        "PYTHONHOME",
        "PYTHONPATH",
        "PYTHONSTARTUP",
        "PYTHONEXECUTABLE",
        "PYTHONUSERBASE",
        "__PYVENV_LAUNCHER__",
        "PIP_USER",
        "PIP_TARGET",
        "PIP_PREFIX",
    ):
        env.pop(key, None)
    env["PYTHONNOUSERSITE"] = "1"
    return env


def _run_embed(python_exe: Path, args: list[str], *, what: str) -> None:
    """Run embed Python isolated: -E (ignore PYTHON*), -s (no user site), -I."""
    cmd = [str(python_exe), "-E", "-s", "-I", *args]
    print(f"  $ {' '.join(cmd)}")
    proc = subprocess.run(cmd, check=False, env=_embed_subprocess_env())
    if proc.returncode != 0:
        raise RuntimeError(f"{what} exited with code {proc.returncode}")


def _bootstrap_pip_and_virtualenv(python_exe: Path, work: Path) -> None:
    get_pip = work / "get-pip.py"
    _download("https://bootstrap.pypa.io/get-pip.py", get_pip)
    if os.name != "nt":
        print(
            "NOTE: non-Windows — skipping embed python.exe "
            "(full pip/virtualenv bundle: build on Windows)."
        )
        return

    # pip only — no wheel (wheel>=0.45 pulls packaging 24+/26 and breaks smfexplorer pin).
    print("Bootstrap pip (isolated embed, no wheel)...")
    _run_embed(
        python_exe,
        [
            str(get_pip),
            "--no-warn-script-location",
            "--no-wheel",
            "--no-setuptools",
        ],
        what="get-pip.py",
    )

    # Pins compatible with smfexplorer 1.1.13 + virtualenv for .venv from embed.
    print("Installing packaging/setuptools/virtualenv (smfexplorer pins)...")
    _run_embed(
        python_exe,
        [
            "-m",
            "pip",
            "install",
            "--no-warn-script-location",
            "packaging>=22.0,<23.0",
            "setuptools>=70.0.0,<71.0.0",
            "virtualenv>=20.24.0,<21",
        ],
        what="pip install packaging/setuptools/virtualenv",
    )

    print("Verifying pins in runtime...")
    _run_embed(
        python_exe,
        [
            "-c",
            "import packaging, setuptools; "
            "from packaging.version import Version; "
            "pv, sv = Version(packaging.__version__), Version(setuptools.__version__); "
            "assert Version('22') <= pv < Version('23'), packaging.__version__; "
            "assert Version('70') <= sv < Version('71'), setuptools.__version__; "
            "import virtualenv; "
            "print('OK packaging', packaging.__version__, "
            "'setuptools', setuptools.__version__, "
            "'virtualenv', virtualenv.__version__)",
        ],
        what="verify packaging/setuptools pins",
    )


def _zip_dir_contents(source_dir: Path, zip_path: Path) -> None:
    if zip_path.exists():
        zip_path.unlink()
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(source_dir.rglob("*")):
            if path.is_file():
                zf.write(path, arcname=path.relative_to(source_dir).as_posix())
    print(f"Saved: {zip_path} ({zip_path.stat().st_size} bytes)")


def cmd_build_runtime(version: str, arch: str, out_dir: Path) -> int:
    try:
        _parse_xyz(version)
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    if arch not in ("amd64", "win32"):
        print("[ERROR] arch: amd64 or win32", file=sys.stderr)
        return 1

    out_zip = out_dir / f"python-{version}-windows-{arch}-minimal-runtime.zip"
    try:
        with tempfile.TemporaryDirectory(prefix="app_min_runtime_") as tmp:
            tmp_path = Path(tmp)
            embed_zip = tmp_path / "embed.zip"
            extract_dir = tmp_path / "python"
            extract_dir.mkdir()

            _download(_embed_url(version, arch), embed_zip)
            with zipfile.ZipFile(embed_zip, "r") as zf:
                zf.extractall(extract_dir)

            _enable_site(extract_dir)
            python_exe = extract_dir / "python.exe"
            if not python_exe.exists():
                raise FileNotFoundError(f"No python.exe in embeddable bundle: {extract_dir}")

            # Clean site-packages in embed (no host junk)
            (extract_dir / "Lib" / "site-packages").mkdir(parents=True, exist_ok=True)

            (extract_dir / "SMF_MINIMAL_RUNTIME.txt").write_text(
                "\n".join(
                    [
                        "Minimal portable Python runtime for start.bat",
                        f"Python {version} ({arch})",
                        "Source: official Windows embeddable + pip + virtualenv",
                        "Pins: packaging>=22,<23; setuptools>=70,<71 (smfexplorer)",
                        "Build: isolated embed (-E -s -I, PYTHONNOUSERSITE=1)",
                        f"Menu: Minimal runtime (no need to download py {version})",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            _bootstrap_pip_and_virtualenv(python_exe, tmp_path)
            _zip_dir_contents(extract_dir, out_zip)
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    print()
    print("Done. Place the ZIP in runtime/ next to start.bat:")
    print(f"  {out_zip}")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="start_tools.py",
        description="Utilities for the universal start.bat",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_find = sub.add_parser("find-python", help="Find Python X.Y.Z (stdout: ver\\tpath)")
    p_find.add_argument("version", nargs="?", default=None, help="e.g. 3.11.0")

    p_check = sub.add_parser("check-venv", help="Verify .venv paths and version")
    p_check.add_argument("version", nargs="?", default=None, help="e.g. 3.11.0")

    sub.add_parser("fix-venv", help="Fix paths in a relocated .venv")

    p_build = sub.add_parser("build-runtime", help="Build minimal runtime ZIP")
    p_build.add_argument("--version", default=DEFAULT_PY, help="e.g. 3.11.0")
    p_build.add_argument("--arch", default="amd64", choices=("amd64", "win32"))
    p_build.add_argument(
        "--out-dir",
        type=Path,
        default=APP_DIR / "runtime",
        help="destination directory for the ZIP",
    )

    args = parser.parse_args(argv)

    if args.cmd == "find-python":
        return cmd_find_python(args.version)
    if args.cmd == "check-venv":
        return cmd_check_venv(args.version)
    if args.cmd == "fix-venv":
        return cmd_fix_venv()
    if args.cmd == "build-runtime":
        return cmd_build_runtime(args.version, args.arch, args.out_dir.resolve())
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
