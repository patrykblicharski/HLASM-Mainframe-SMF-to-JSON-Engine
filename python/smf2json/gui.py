"""Tkinter GUI for SMF dump conversion."""

from __future__ import annotations

import csv
import json
import threading
import time
import tkinter as tk
from pathlib import Path
from queue import Empty, SimpleQueue
from tkinter import filedialog, font as tkfont, messagebox, ttk
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from . import __version__
from .column_config import (
    GroupKey,
    config_path,
    group_label,
    load_config,
    row_group,
    save_config,
    store_group_selection,
    visible_for_group,
)
from .engine import convert_record, field_meta, ordered_columns
from .progress import CONVERT_BATCH, PROGRESS_EVERY_BYTES, fmt_bytes, format_timing
from .reader import iter_dump
from .terse import TerseHeader, default_output_path, decompress_file

# Convert / paint this many rows before yielding back to Tk.
LOAD_BATCH = CONVERT_BATCH
UI_BATCHES_PER_TICK = 2
TREE_PAINT_BATCH = 250
TREE_CLEAR_BATCH = 400
PROGRESS_MAX = 1000


class ToolTip:
    """Lightweight tooltip; keeps one window and only rebuilds when text changes."""

    def __init__(self, widget: tk.Widget):
        self.widget = widget
        self.tip: Optional[tk.Toplevel] = None
        self._text = ""

    def show(self, text: str, x: int, y: int) -> None:
        if not text:
            self.hide()
            return
        if self.tip is not None and self._text == text:
            self.tip.wm_geometry(f"+{x}+{y}")
            return
        self.hide()
        self._text = text
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.attributes("-topmost", True)
        self.tip.wm_geometry(f"+{x}+{y}")
        tk.Label(
            self.tip,
            text=text,
            justify=tk.LEFT,
            background="#fff8d6",
            foreground="#1a1a1a",
            relief=tk.SOLID,
            borderwidth=1,
            font=("DejaVu Sans", 9),
            wraplength=420,
            padx=8,
            pady=5,
        ).pack()

    def hide(self) -> None:
        self._text = ""
        if self.tip is not None:
            self.tip.destroy()
            self.tip = None


class ColumnPickerDialog(tk.Toplevel):
    """Checkbox list: source key, friendly name, optional description."""

    def __init__(
        self,
        master: tk.Tk,
        columns: List[str],
        visible: Set[str],
        meta: Dict[str, Dict[str, Any]],
        title: str,
        on_apply: Callable[[List[str]], None],
    ):
        super().__init__(master)
        self.title(f"Columns — {title}")
        self.transient(master)
        self.grab_set()
        self.geometry("720x560")
        self._columns = columns
        self._meta = meta
        self._on_apply = on_apply
        self._vars: Dict[str, tk.BooleanVar] = {}

        ttk.Label(
            self,
            text=(
                "Select columns to display. The source name is shown with its friendly "
                "header label and description (when available). Choices are saved "
                f"for {title}."
            ),
            wraplength=680,
        ).pack(anchor=tk.W, padx=10, pady=(10, 6))

        canvas = tk.Canvas(self, highlightthickness=0)
        scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=canvas.yview)
        inner = ttk.Frame(canvas)
        inner.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        window = canvas.create_window((0, 0), window=inner, anchor=tk.NW)
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=4)
        scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=4)

        def _stretch(_event: tk.Event) -> None:  # type: ignore[type-arg]
            canvas.itemconfigure(window, width=canvas.winfo_width())

        canvas.bind("<Configure>", _stretch)

        def _wheel(event: tk.Event) -> None:  # type: ignore[type-arg]
            delta = int(-event.delta / 120) if event.delta else 0
            if delta:
                canvas.yview_scroll(delta, "units")

        canvas.bind_all("<MouseWheel>", _wheel)
        self.bind("<Destroy>", lambda _e: canvas.unbind_all("<MouseWheel>"))

        for key in columns:
            info = meta.get(key, {})
            label = info.get("label") or key
            description = (info.get("description") or "").strip()
            ibm = (info.get("ibm_name") or "").strip()

            row = ttk.Frame(inner)
            row.pack(fill=tk.X, pady=3, padx=4)
            var = tk.BooleanVar(value=key in visible)
            self._vars[key] = var
            ttk.Checkbutton(row, variable=var).pack(side=tk.LEFT, anchor=tk.N)
            text = ttk.Frame(row)
            text.pack(side=tk.LEFT, fill=tk.X, expand=True)

            title_row = ttk.Frame(text)
            title_row.pack(fill=tk.X)
            ttk.Label(title_row, text=key, font=("", 9, "bold")).pack(side=tk.LEFT)
            if label and label != key:
                ttk.Label(title_row, text=f"  —  {label}").pack(side=tk.LEFT)

            extra = description if description and description != label else ""
            if extra:
                ttk.Label(text, text=extra, foreground="#555", wraplength=620).pack(anchor=tk.W)
            elif ibm:
                ttk.Label(text, text=f"IBM {ibm}", foreground="#777").pack(anchor=tk.W)

        btns = ttk.Frame(self)
        btns.pack(fill=tk.X, padx=10, pady=10)

        def select_all() -> None:
            for var in self._vars.values():
                var.set(True)

        def select_none() -> None:
            for var in self._vars.values():
                var.set(False)

        ttk.Button(btns, text="Select all", command=select_all).pack(side=tk.LEFT)
        ttk.Button(btns, text="Select none", command=select_none).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side=tk.RIGHT)
        ttk.Button(btns, text="Apply", command=self._apply).pack(side=tk.RIGHT, padx=6)

    def _apply(self) -> None:
        selected = [key for key in self._columns if self._vars[key].get()]
        if not selected:
            messagebox.showwarning("Columns", "Select at least one column.", parent=self)
            return
        self._on_apply(selected)
        self.destroy()


class RecordPane:
    """One type/subtype table inside a notebook tab."""

    def __init__(
        self,
        notebook: ttk.Notebook,
        app: "SmfApp",
        rty: int,
        sty: Optional[int],
    ):
        self.app = app
        self.rty = rty
        self.sty = sty
        self.rows: List[Dict[str, Any]] = []
        self.columns: List[str] = []
        self.visible: List[str] = []
        self._next_iid = 0
        self._paint_token = 0
        self.frame = ttk.Frame(notebook, padding=4)
        self.tree = ttk.Treeview(self.frame, show="headings", height=18)
        ysb = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.tree.yview)
        xsb = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        ysb.grid(row=0, column=1, sticky="ns")
        xsb.grid(row=1, column=0, sticky="ew")
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

        self.tooltip = ToolTip(self.tree)
        self.tree.bind("<Motion>", self._on_motion)
        self.tree.bind("<Leave>", self._on_leave)

    @property
    def label(self) -> str:
        return group_label(self.rty, self.sty, len(self.rows))

    def _shown(self) -> List[str]:
        return self.visible or self.columns

    def _configure_columns(self) -> None:
        shown = self._shown()
        self.tree["columns"] = shown
        for col in shown:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=self.app._header_width(col), stretch=False, anchor=tk.W)

    def _insert_slice(self, start: int, end: int) -> None:
        shown = self._shown()
        for i in range(start, end):
            row = self.rows[i]
            self.tree.insert("", tk.END, iid=str(i), values=[row.get(c, "") for c in shown])
        self._next_iid = end

    def add_rows(self, rows: List[Dict[str, Any]]) -> None:
        if not rows:
            return
        start = len(self.rows)
        self.rows.extend(rows)
        if not self.columns:
            self.columns = ordered_columns(self.rows)
            self.visible = visible_for_group(self.columns, self.rty, self.sty, load_config())
            self._configure_columns()
        self._insert_slice(start, len(self.rows))

    def populate(self) -> None:
        """Rebuild the tree in slices so a column change does not freeze Tk."""
        self._paint_token += 1
        token = self._paint_token
        self._rebuild_tree(token, phase="clear")

    def _rebuild_tree(self, token: int, phase: str = "clear") -> None:
        if token != self._paint_token:
            return
        if phase == "clear":
            kids = self.tree.get_children()
            for iid in kids[:TREE_CLEAR_BATCH]:
                self.tree.delete(iid)
            if self.tree.get_children():
                self.app.after(1, lambda: self._rebuild_tree(token, "clear"))
                return
            self._configure_columns()
            self._next_iid = 0
            self.app.after(1, lambda: self._rebuild_tree(token, "fill"))
            return
        end = min(self._next_iid + TREE_PAINT_BATCH, len(self.rows))
        self._insert_slice(self._next_iid, end)
        if end < len(self.rows):
            self.app.after(1, lambda: self._rebuild_tree(token, "fill"))

    def apply_visible(self, selected: List[str]) -> None:
        self.visible = [key for key in self.columns if key in set(selected)]
        path = save_config(store_group_selection(load_config(), self.rty, self.sty, self.visible))
        self.populate()
        title = group_label(self.rty, self.sty)
        self.app.log(f"INFO: saved {len(self.visible)} visible columns for {title} → {path}")
        self.app.status_var.set(
            f"Showing {len(self.visible)} / {len(self.columns)} columns ({title})"
        )

    def _column_at(self, event: tk.Event) -> Optional[str]:  # type: ignore[type-arg]
        region = self.tree.identify_region(event.x, event.y)
        col_id = self.tree.identify_column(event.x)
        if region not in ("heading", "cell", "tree") or not col_id:
            return None
        try:
            idx = int(col_id.replace("#", "")) - 1
        except ValueError:
            return None
        shown = self.visible or self.columns
        if idx < 0 or idx >= len(shown):
            return None
        return shown[idx]

    def _on_motion(self, event: tk.Event) -> None:  # type: ignore[type-arg]
        key = self._column_at(event)
        if not key:
            self._on_leave(event)
            return
        ibm, desc = self.app._ibm_and_desc(key, self.rty)
        self.app.desc_var.set(" — ".join(p for p in (ibm, desc) if p) or key)
        self.tooltip.show(self.app._field_tip(key, self.rty), event.x_root + 14, event.y_root + 18)

    def _on_leave(self, _event: tk.Event) -> None:  # type: ignore[type-arg]
        self.tooltip.hide()
        self.app.desc_var.set("(hover a column header or cell for IBM name and description)")


class SmfApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"SMF2JSON Desktop  v{__version__}")
        self.geometry("1200x760")
        self.minsize(900, 560)

        self.rows: List[Dict[str, Any]] = []
        self.panes: List[RecordPane] = []
        self._panes_by_key: Dict[GroupKey, RecordPane] = {}
        self.meta: Dict[str, Dict[str, Any]] = field_meta()
        self.dump_path: Optional[Path] = None
        self._heading_font = tkfont.nametofont("TkHeadingFont")
        self._busy = False
        self._load_token = 0
        self._cancel = threading.Event()
        self._queue: Optional[SimpleQueue[Tuple[Any, ...]]] = None
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.status_var = tk.StringVar(value="Ready")
        self._build_menu()
        self._build_toolbar()
        self._build_body()
        ttk.Label(self, textvariable=self.status_var, anchor=tk.W, padding=4).pack(
            side=tk.BOTTOM, fill=tk.X
        )
        self.log(f"INFO: SMF2JSON Desktop {__version__} ready — open an SMF dump to begin")

    def _build_menu(self) -> None:
        menubar = tk.Menu(self)
        file_m = tk.Menu(menubar, tearoff=0)
        file_m.add_command(label="Open SMF dump…", command=self.open_dump, accelerator="Ctrl+O")
        file_m.add_command(label="Terse decompress…", command=self.terse_decompress)
        file_m.add_separator()
        file_m.add_command(label="Export JSON…", command=self.export_json, accelerator="Ctrl+J")
        file_m.add_command(label="Export CSV…", command=self.export_csv, accelerator="Ctrl+E")
        file_m.add_separator()
        file_m.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=file_m)

        view_m = tk.Menu(menubar, tearoff=0)
        view_m.add_command(label="Columns…", command=self.open_columns)
        view_m.add_separator()
        view_m.add_command(label="Clear debug log", command=self.clear_log)
        menubar.add_cascade(label="View", menu=view_m)

        help_m = tk.Menu(menubar, tearoff=0)
        help_m.add_command(label="About", command=self._about)
        menubar.add_cascade(label="Help", menu=help_m)
        self.config(menu=menubar)
        self.bind("<Control-o>", lambda _e: self.open_dump())
        self.bind("<Control-j>", lambda _e: self.export_json())
        self.bind("<Control-e>", lambda _e: self.export_csv())

    def _build_toolbar(self) -> None:
        bar = ttk.Frame(self, padding=6)
        bar.pack(side=tk.TOP, fill=tk.X)
        self._btn_open = ttk.Button(bar, text="Open SMF…", command=self.open_dump)
        self._btn_open.pack(side=tk.LEFT, padx=2)
        self._btn_json = ttk.Button(bar, text="Export JSON", command=self.export_json)
        self._btn_json.pack(side=tk.LEFT, padx=2)
        self._btn_csv = ttk.Button(bar, text="Export CSV", command=self.export_csv)
        self._btn_csv.pack(side=tk.LEFT, padx=2)
        self.columns_btn = ttk.Button(bar, text="Columns…", command=self.open_columns)
        self._btn_cancel = ttk.Button(bar, text="Cancel load", command=self.cancel_load)
        ttk.Button(bar, text="Clear log", command=self.clear_log).pack(side=tk.LEFT, padx=2)
        self.path_var = tk.StringVar(value="(no file loaded)")
        ttk.Label(bar, textvariable=self.path_var).pack(side=tk.LEFT, padx=12)

        desc_bar = ttk.Frame(self, padding=(8, 0, 8, 4))
        self._desc_bar = desc_bar
        desc_bar.pack(side=tk.TOP, fill=tk.X)

        self._load_strip = ttk.Frame(self, padding=(8, 4, 8, 4))
        ttk.Label(self._load_strip, text="Loading:").pack(side=tk.LEFT)
        self.progress = ttk.Progressbar(
            self._load_strip, mode="determinate", maximum=PROGRESS_MAX, length=360
        )
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        self.progress_status = tk.Label(
            self.progress,
            textvariable=self.status_var,
            bd=0,
            padx=6,
            font=("Segoe UI", 8),
        )
        self.progress_status.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        ttk.Label(desc_bar, text="Field:").pack(side=tk.LEFT)
        self.desc_var = tk.StringVar(value="(hover a column header or cell for IBM name and description)")
        ttk.Label(desc_bar, textvariable=self.desc_var, wraplength=1000).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=6
        )

    def _show_columns_button(self) -> None:
        if self.columns_btn.winfo_ismapped():
            return
        self.columns_btn.pack(side=tk.LEFT, padx=2, after=self._btn_csv)

    def _build_body(self) -> None:
        paned = ttk.Panedwindow(self, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        table_frame = ttk.LabelFrame(
            paned, text="Records (one tab per SMF type / subtype)", padding=4
        )
        paned.add(table_frame, weight=3)
        self.notebook = ttk.Notebook(table_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        dbg_frame = ttk.LabelFrame(paned, text="Processing debug", padding=4)
        paned.add(dbg_frame, weight=1)
        self.debug = tk.Text(dbg_frame, height=10, wrap=tk.WORD, font=("DejaVu Sans Mono", 9))
        dbg_scroll = ttk.Scrollbar(dbg_frame, orient=tk.VERTICAL, command=self.debug.yview)
        self.debug.configure(yscrollcommand=dbg_scroll.set)
        self.debug.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        dbg_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def log(self, msg: str) -> None:
        self.debug.insert(tk.END, msg + "\n")
        self.debug.see(tk.END)

    def clear_log(self) -> None:
        self.debug.delete("1.0", tk.END)
        self.log("INFO: debug log cleared")

    def current_pane(self) -> Optional[RecordPane]:
        sel = self.notebook.select()
        if not sel:
            return None
        widget = self.nametowidget(sel)
        for pane in self.panes:
            if str(pane.frame) == str(widget):
                return pane
        return None

    def _on_tab_changed(self, _event: tk.Event | None = None) -> None:  # type: ignore[type-arg]
        pane = self.current_pane()
        if pane is None:
            return
        self.status_var.set(f"{pane.label} — {len(pane.visible or pane.columns)} columns")

    def open_dump(self) -> None:
        if self._busy:
            return
        path = filedialog.askopenfilename(
            parent=self,
            title="Open SMF dump",
            filetypes=[("SMF dumps", "*.smf *.SMF *.bin *.dump"), ("All files", "*.*")],
            initialdir=str(self.dump_path.parent) if self.dump_path else str(Path.cwd()),
        )
        if path:
            self._load_path(Path(path))

    def terse_decompress(self) -> None:
        if self._busy:
            return
        path = filedialog.askopenfilename(
            parent=self,
            title="Terse decompress",
            filetypes=[
                ("TERSE / AMATERSE", "*.trs *.TRS *.pack *.PACK *.spack *.SPACK"),
                ("All files", "*.*"),
            ],
            initialdir=str(self.dump_path.parent) if self.dump_path else str(Path.cwd()),
        )
        if not path:
            return
        src = Path(path)
        dest = default_output_path(src)
        if dest.exists() and not messagebox.askyesno(
            "Terse decompress",
            f"{dest.name} already exists.\nReplace it?",
            parent=self,
        ):
            return
        self.status_var.set(f"Decompressing {src.name}…")
        self.log(f"INFO: unterse {src} → {dest}")
        self._set_busy(True, progress=False)

        def work() -> None:
            try:
                header = decompress_file(src, dest)
                size = dest.stat().st_size
                self.after(0, lambda: self._terse_done(dest, header, size, None))
            except Exception as exc:  # noqa: BLE001
                self.after(0, lambda e=exc: self._terse_done(dest, None, 0, e))

        threading.Thread(target=work, name="smf2json-unterse", daemon=True).start()

    def _terse_done(
        self,
        dest: Path,
        header: Optional[TerseHeader],
        size: int,
        error: Optional[BaseException],
    ) -> None:
        self._set_busy(False, progress=False)
        if error is not None:
            self.log(f"ERROR: unterse failed: {error}")
            messagebox.showerror("Terse decompress", str(error), parent=self)
            self.status_var.set("Terse decompress failed")
            return
        assert header is not None
        recfm = "VB" if header.recfm_v else "FB"
        self.log(
            f"INFO: wrote {dest} ({size:,} bytes) method={header.method} recfm={recfm}"
        )
        self.status_var.set(f"Unpacked {dest.name} ({size:,} bytes)")
        if messagebox.askyesno(
            "Terse decompress",
            f"Wrote {dest.name} ({size:,} bytes, {header.method} {recfm}).\n\n"
            "Load this file now?",
            parent=self,
        ):
            self._load_path(dest)

    def cancel_load(self) -> None:
        if self._busy:
            self._cancel.set()
            self.status_var.set("Cancelling…")

    def _on_close(self) -> None:
        self._cancel.set()
        self.destroy()

    def _set_busy(self, busy: bool, *, progress: bool = True) -> None:
        self._busy = busy
        state = tk.DISABLED if busy else tk.NORMAL
        for widget in (self._btn_open, self._btn_json, self._btn_csv, self.columns_btn):
            widget.configure(state=state)
        if busy:
            if progress:
                if not self._btn_cancel.winfo_ismapped():
                    self._btn_cancel.pack(side=tk.LEFT, padx=2, after=self._btn_csv)
                if not self._load_strip.winfo_ismapped():
                    self._load_strip.pack(side=tk.TOP, fill=tk.X, after=self._desc_bar)
                self.progress["value"] = 0
            self.config(cursor="watch")
        else:
            self._btn_cancel.pack_forget()
            self._load_strip.pack_forget()
            self.config(cursor="")

    def _clear_tabs(self) -> None:
        for pane in self.panes:
            pane.tooltip.hide()
            pane._paint_token += 1
        for child in self.notebook.winfo_children():
            child.destroy()
        self.panes.clear()
        self._panes_by_key.clear()

    def _load_path(self, path: Path) -> None:
        if self._busy:
            self._cancel.set()
        self.clear_log()
        self.dump_path = path
        self.path_var.set(str(path))
        self.rows = []
        self._clear_tabs()
        self.status_var.set("Reading file…")
        self._load_t0 = time.perf_counter()
        self._cancel = threading.Event()
        self._load_token += 1
        token = self._load_token
        queue: SimpleQueue[Tuple[Any, ...]] = SimpleQueue()
        self._queue = queue
        self._set_busy(True)
        self.log(f"INFO: loading {path} in batches of {LOAD_BATCH}")
        thread = threading.Thread(
            target=_load_worker,
            args=(str(path), queue, self._cancel),
            name="smf2json-load",
            daemon=True,
        )
        thread.start()
        self.after(20, lambda: self._poll_load(token))

    def _poll_load(self, token: int) -> None:
        if token != self._load_token or self._queue is None:
            return
        finished = False
        error: Optional[str] = None
        cancelled = False
        records_s = 0.0
        batches = 0
        while True:
            try:
                msg = self._queue.get_nowait()
            except Empty:
                break
            kind = msg[0]
            if kind == "log":
                self.log(str(msg[1]))
            elif kind == "progress":
                self._apply_progress(int(msg[1]), int(msg[2]), int(msg[3]), int(msg[4]))
            elif kind == "batch":
                rows: List[Dict[str, Any]] = msg[1]
                seen = int(msg[2])
                mapped = int(msg[3])
                self._ingest_batch(rows)
                self._apply_progress(int(msg[4]), int(msg[5]), seen, mapped)
                batches += 1
                if batches >= UI_BATCHES_PER_TICK:
                    break
            elif kind == "done":
                seen = int(msg[1])
                mapped = int(msg[2])
                total = int(msg[3])
                records_s = float(msg[4])
                finished = True
                self._apply_progress(total, total, seen, mapped)
                self.log(f"INFO: converted {mapped:,} mapped records from {seen:,} SMF records")
                break
            elif kind == "cancelled":
                cancelled = True
                finished = True
                if len(msg) > 1:
                    records_s = float(msg[1])
                break
            elif kind == "error":
                error = str(msg[1])
                finished = True
                break
        if not finished:
            self.after(20, lambda: self._poll_load(token))
            return
        self._set_busy(False)
        if error:
            self.log(f"ERROR: {error}")
            messagebox.showerror("Load failed", error, parent=self)
            self.status_var.set("Error")
            return
        if not self.panes:
            self.log("WARN: no mapped records (supported types: 30, 80, 89, 119)")
        dump_s = time.perf_counter() - getattr(self, "_load_t0", time.perf_counter())
        timing = format_timing(records_s, dump_s)
        self.log(f"INFO: timing  {timing}")
        labels = ", ".join(pane.label for pane in self.panes)
        prefix = "Cancelled — kept" if cancelled else "Loaded"
        self.status_var.set(
            f"{prefix} {len(self.rows):,} mapped records in {len(self.panes)} tab(s) "
            f"({labels or 'none'})"
            + (f" from {self.dump_path.name}" if self.dump_path else "")
            + f"  —  {timing}"
        )

    def _apply_progress(self, pos: int, total: int, seen: int, mapped: int) -> None:
        if total > 0:
            self.progress["value"] = min(PROGRESS_MAX, int(pos * PROGRESS_MAX / total))
            pct = min(100.0, pos * 100.0 / total)
        else:
            self.progress["value"] = 0
            pct = 0.0
        name = self.dump_path.name if self.dump_path else ""
        self.status_var.set(
            f"Loading {name}  —  {mapped:,} mapped / {seen:,} records  —  "
            f"{fmt_bytes(pos)} / {fmt_bytes(total)}  ({pct:.0f}%)"
        )

    def _ingest_batch(self, rows: List[Dict[str, Any]]) -> None:
        if not rows:
            return
        self.rows.extend(rows)
        buckets: Dict[GroupKey, List[Dict[str, Any]]] = {}
        order: List[GroupKey] = []
        for row in rows:
            key = row_group(row)
            if key is None:
                continue
            if key not in buckets:
                buckets[key] = []
                order.append(key)
            buckets[key].append(row)
        for key in order:
            pane = self._panes_by_key.get(key)
            if pane is None:
                rty, sty = key
                pane = RecordPane(self.notebook, self, rty, sty)
                self._panes_by_key[key] = pane
                self.notebook.add(pane.frame, text=pane.label)
                self.panes.append(pane)
                self._show_columns_button()
                self.log(f"INFO: tab {group_label(rty, sty)}")
            pane.add_rows(buckets[key])
            self.notebook.tab(pane.frame, text=pane.label)

    def _header_width(self, title: str) -> int:
        return max(72, self._heading_font.measure(title) + 28)

    def _ibm_and_desc(self, key: str, rty: Optional[int] = None) -> tuple[str, str]:
        info = self.meta.get(key, {})
        ibm_by = info.get("ibm_by_type") or {}
        desc_by = info.get("desc_by_type") or {}
        if rty is not None and rty in ibm_by:
            return ibm_by[rty] or "", desc_by.get(rty) or info.get("description") or ""
        ibm = info.get("ibm_name") or ""
        desc = info.get("description") or info.get("label") or ""
        return ibm, desc

    def _field_tip(self, key: str, rty: Optional[int] = None) -> str:
        ibm, desc = self._ibm_and_desc(key, rty)
        parts = [p for p in (ibm, desc) if p]
        return "\n".join(parts) if parts else key

    def open_columns(self) -> None:
        if self._busy:
            return
        pane = self.current_pane()
        if pane is None:
            messagebox.showinfo("Columns", "Open an SMF dump first.", parent=self)
            return
        ColumnPickerDialog(
            self,
            pane.columns,
            set(pane.visible or pane.columns),
            self.meta,
            group_label(pane.rty, pane.sty),
            on_apply=pane.apply_visible,
        )

    def _default_export_dir(self) -> str:
        if self.dump_path:
            return str(self.dump_path.parent)
        return str(Path.cwd())

    def write_json(self, path: Path) -> None:
        with path.open("w", encoding="utf-8") as f:
            json.dump(self.rows, f, indent=2, ensure_ascii=False)
        self.log(f"INFO: wrote JSON {path} ({len(self.rows)} objects)")
        self.status_var.set(f"Exported JSON → {path}")

    def write_csv(self, path: Path, pane: Optional[RecordPane] = None) -> None:
        pane = pane or self.current_pane()
        rows = pane.rows if pane else self.rows
        cols = (pane.visible or pane.columns) if pane else ordered_columns(rows)
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            writer.writeheader()
            for row in rows:
                writer.writerow({c: row.get(c, "") for c in cols})
        self.log(f"INFO: wrote CSV {path} ({len(rows)} rows)")
        self.status_var.set(f"Exported CSV → {path}")

    def export_json(self) -> None:
        if self._busy:
            return
        if not self.rows:
            messagebox.showinfo("Export", "No data to export — open a dump first.", parent=self)
            return
        initial = (self.dump_path.stem + ".json") if self.dump_path else "smf.json"
        path = filedialog.asksaveasfilename(
            parent=self,
            title="Export JSON",
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
            initialdir=self._default_export_dir(),
            initialfile=initial,
        )
        if path:
            self.write_json(Path(path))

    def export_csv(self) -> None:
        if self._busy:
            return
        pane = self.current_pane()
        if pane is None and not self.rows:
            messagebox.showinfo("Export", "No data to export — open a dump first.", parent=self)
            return
        stem = self.dump_path.stem if self.dump_path else "smf"
        suffix = ""
        if pane is not None:
            suffix = f"-{pane.rty}" if pane.sty is None else f"-{pane.rty}-{pane.sty}"
        path = filedialog.asksaveasfilename(
            parent=self,
            title="Export CSV (current tab)",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialdir=self._default_export_dir(),
            initialfile=f"{stem}{suffix}.csv",
        )
        if path:
            self.write_csv(Path(path), pane)

    def _about(self) -> None:
        messagebox.showinfo(
            "About",
            "SMF2JSON Desktop\n\n"
            "Python port of the HLASM table-driven SMF converter.\n"
            "Supports SMF types 30, 80, 89, and 119 (TCP/IP subtypes) from VB/VBS binary dumps.\n"
            "Records are grouped into tabs by type / subtype.\n"
            f"Column layout is saved to {config_path()}.",
            parent=self,
        )


def _load_worker(path: str, queue: SimpleQueue, cancel: threading.Event) -> None:
    """Read and convert off the Tk thread; push mapped rows in LOAD_BATCH chunks."""

    def reader_log(msg: str) -> None:
        if msg.startswith(("ERROR", "WARN")) or msg.startswith("INFO: loaded"):
            queue.put(("log", msg))

    try:
        batch: List[Dict[str, Any]] = []
        seen = 0
        mapped = 0
        last_pos = 0
        total = 0
        last_sent = 0
        t_start = time.perf_counter()
        t_records_start: Optional[float] = None

        def on_progress(pos: int, n: int) -> None:
            nonlocal last_pos, total, last_sent
            last_pos = pos
            total = n
            if pos - last_sent >= PROGRESS_EVERY_BYTES or (n and pos >= n):
                last_sent = pos
                queue.put(("progress", pos, n, seen, mapped))

        def _times() -> tuple[float, float]:
            now = time.perf_counter()
            records_s = (now - t_records_start) if t_records_start is not None else 0.0
            return records_s, now - t_start

        for rec in iter_dump(path, log=reader_log, progress=on_progress):
            if t_records_start is None:
                t_records_start = time.perf_counter()
            if cancel.is_set():
                if batch:
                    queue.put(("batch", batch, seen, mapped, last_pos, total))
                rec_s, dump_s = _times()
                queue.put(("cancelled", rec_s, dump_s))
                return
            seen += 1
            obj = convert_record(rec)
            if obj is None:
                continue
            mapped += 1
            batch.append(obj)
            if len(batch) >= LOAD_BATCH:
                queue.put(("batch", batch, seen, mapped, last_pos, total))
                batch = []
        if batch:
            queue.put(("batch", batch, seen, mapped, last_pos, total))
        rec_s, dump_s = _times()
        queue.put(("done", seen, mapped, total, rec_s, dump_s))
    except Exception as exc:  # noqa: BLE001
        queue.put(("error", str(exc)))


def run_app(initial_file: Optional[str] = None) -> None:
    app = SmfApp()
    if initial_file:
        app.after(100, lambda: app._load_path(Path(initial_file)))
    app.mainloop()
