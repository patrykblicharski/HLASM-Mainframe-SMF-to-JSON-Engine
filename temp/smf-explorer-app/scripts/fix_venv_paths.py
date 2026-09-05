#!/usr/bin/env python3
"""Rewrites hardcoded paths in a relocated .venv (Windows and POSIX)."""
from __future__ import annotations

import sys
from pathlib import Path


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
                # No python.exe in home — replace only the target venv path.
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


def main() -> int:
    # Script lives in <app>/scripts/ — .venv is at <app>/.venv
    app_dir = Path(__file__).resolve().parent.parent
    venv_dir = (app_dir / ".venv").resolve()
    if not venv_dir.is_dir():
        print(f"Missing directory {venv_dir}", file=sys.stderr)
        return 1

    prefix = Path(sys.prefix).resolve()
    if prefix != venv_dir:
        print(
            f"Run this script with the interpreter from .venv "
            f"(sys.prefix={prefix}, expected={venv_dir})",
            file=sys.stderr,
        )
        return 1

    # Windows venv uses Scripts/, POSIX — bin/. Pick what exists
    # (do not rely only on sys.platform — venv may have been created on another OS).
    if (venv_dir / "Scripts").is_dir():
        scripts = venv_dir / "Scripts"
    else:
        scripts = venv_dir / "bin"
    _rewrite_activate_bat(scripts / "activate.bat", venv_dir)
    _rewrite_activate_ps1(scripts / "Activate.ps1", venv_dir)
    _rewrite_pyvenv_cfg(venv_dir / "pyvenv.cfg", venv_dir)
    print(f"Updated .venv paths -> {venv_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
