"""Console Q key shuts down the NiceGUI server (requires ui.run(reload=False))."""
from __future__ import annotations

import os
import platform
import signal
import sys
import threading
import time

from nicegui import app

_STARTED = False


def enable_console_quit(*, quit_keys: str = "qQ") -> None:
    """Register message and Q listener after ``app.on_startup``."""

    global _STARTED
    if _STARTED:
        return
    _STARTED = True

    def _shutdown() -> None:
        print("\n[Q] Shutting down application...\n", flush=True)
        try:
            app.shutdown()
            return
        except Exception as exc:  # noqa: BLE001 — emergency fallback
            print(f"[console_quit] app.shutdown() failed: {exc}", flush=True)
        sig = getattr(
            signal,
            "CTRL_C_EVENT" if platform.system() == "Windows" else "SIGINT",
        )
        try:
            os.kill(os.getpid(), sig)
        except OSError:
            os._exit(0)

    def _watch_windows() -> None:
        import msvcrt

        while True:
            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                # Arrow / function keys: prefix + second character
                if ch in ("\x00", "\xe0"):
                    if msvcrt.kbhit():
                        msvcrt.getwch()
                    continue
                if ch in quit_keys:
                    _shutdown()
                    return
            time.sleep(0.05)

    def _watch_posix() -> None:
        if not sys.stdin.isatty():
            print(
                "[console_quit] stdin is not a TTY — Q listener disabled "
                "(use Ctrl+C).",
                flush=True,
            )
            return

        import select
        import termios
        import tty

        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            while True:
                ready, _, _ = select.select([sys.stdin], [], [], 0.1)
                if not ready:
                    continue
                ch = sys.stdin.read(1)
                if ch in quit_keys:
                    _shutdown()
                    return
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

    def _watch() -> None:
        # Give NiceGUI time to print "NiceGUI ready on ..." / endpoints.
        time.sleep(0.8)
        print("Press [Q] to quit the application.\n", flush=True)
        try:
            if sys.platform == "win32":
                _watch_windows()
            else:
                _watch_posix()
        except Exception as exc:  # noqa: BLE001
            print(f"[console_quit] Keyboard listener error: {exc}", flush=True)

    @app.on_startup
    def _on_startup() -> None:
        threading.Thread(
            target=_watch,
            name="smf-console-quit",
            daemon=True,
        ).start()
