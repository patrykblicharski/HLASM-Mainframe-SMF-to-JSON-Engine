"""Shared byte-progress helpers for CLI (stderr bar) and the GUI."""

from __future__ import annotations

import sys
from typing import Optional, TextIO

CONVERT_BATCH = 250
PROGRESS_EVERY_BYTES = 256 * 1024
BAR_WIDTH = 28


def fmt_elapsed(seconds: float) -> str:
    if seconds < 0:
        seconds = 0.0
    if seconds < 1:
        return f"{seconds * 1000:.0f} ms"
    if seconds < 60:
        return f"{seconds:.2f} s"
    minutes, sec = divmod(seconds, 60)
    if minutes < 60:
        return f"{int(minutes)}m {sec:04.1f}s"
    hours, minutes = divmod(int(minutes), 60)
    return f"{hours}h {minutes}m {sec:04.1f}s"


def format_timing(records_s: float, dump_s: float) -> str:
    return f"records {fmt_elapsed(records_s)} — dump {fmt_elapsed(dump_s)}"


def fmt_bytes(n: int) -> str:
    if n >= 1024 * 1024:
        return f"{n / (1024 * 1024):.1f} MB"
    if n >= 1024:
        return f"{n / 1024:.0f} KB"
    return f"{n} B"


def format_bar(pos: int, total: int, seen: int, mapped: int, label: str = "") -> str:
    pct = min(100.0, pos * 100.0 / total) if total else 0.0
    filled = int(BAR_WIDTH * pct / 100.0) if total else 0
    bar = "#" * filled + "-" * (BAR_WIDTH - filled)
    prefix = f"{label} " if label else ""
    return (
        f"{prefix}[{bar}] {pct:5.1f}%  {mapped:,} mapped / {seen:,} rec  "
        f"{fmt_bytes(pos)} / {fmt_bytes(total)}"
    )


class CliProgress:
    """Determinate file-byte bar on stderr. Uses \\r when the stream is a TTY."""

    def __init__(
        self,
        enabled: bool = True,
        stream: Optional[TextIO] = None,
        label: str = "",
        tty: Optional[bool] = None,
    ):
        self.stream = stream or sys.stderr
        self.enabled = enabled
        self.label = label
        self.tty = self.stream.isatty() if tty is None else tty
        self.pos = 0
        self.total = 0
        self.seen = 0
        self.mapped = 0
        self._last_sent = 0
        self._last_len = 0

    def update(self, pos: int, total: int, seen: int, mapped: int, *, force: bool = False) -> None:
        self.pos = pos
        self.total = total
        self.seen = seen
        self.mapped = mapped
        if not self.enabled:
            return
        if not force and pos - self._last_sent < PROGRESS_EVERY_BYTES and not (total and pos >= total):
            return
        self._last_sent = pos
        self._emit(format_bar(pos, total, seen, mapped, self.label))

    def close(self) -> None:
        if not self.enabled:
            return
        self._emit(format_bar(self.pos, self.total, self.seen, self.mapped, self.label), final=True)

    def _emit(self, line: str, final: bool = False) -> None:
        try:
            if self.tty:
                pad = " " * max(0, self._last_len - len(line))
                self.stream.write("\r" + line + pad)
                self._last_len = len(line)
                if final:
                    self.stream.write("\n")
            else:
                self.stream.write(line + "\n")
            self.stream.flush()
        except OSError:
            self.enabled = False
