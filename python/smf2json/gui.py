"""Tkinter GUI for SMF dump conversion."""

from __future__ import annotations

import csv
import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Any, Dict, List, Optional

from . import __version__
from .engine import convert_dump, field_descriptions_for_rows, ordered_columns
from .reader import read_dump


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


class SmfApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"SMF2JSON Desktop  v{__version__}")
        self.geometry("1200x760")
        self.minsize(900, 560)

        self.rows: List[Dict[str, Any]] = []
        self.columns: List[str] = []
        self.descriptions: Dict[str, str] = {}
        self.dump_path: Optional[Path] = None
        self._hover_col: Optional[str] = None

        self._build_menu()
        self._build_toolbar()
        self._build_body()
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self, textvariable=self.status_var, anchor=tk.W, padding=4).pack(
            side=tk.BOTTOM, fill=tk.X
        )

        self.tooltip = ToolTip(self.tree)
        self.tree.bind("<Motion>", self._on_tree_motion)
        self.tree.bind("<Leave>", self._on_tree_leave)
        self.log(f"INFO: SMF2JSON Desktop {__version__} ready — open an SMF dump to begin")

    def _build_menu(self) -> None:
        menubar = tk.Menu(self)
        file_m = tk.Menu(menubar, tearoff=0)
        file_m.add_command(label="Open SMF dump…", command=self.open_dump, accelerator="Ctrl+O")
        file_m.add_separator()
        file_m.add_command(label="Export JSON…", command=self.export_json, accelerator="Ctrl+J")
        file_m.add_command(label="Export CSV…", command=self.export_csv, accelerator="Ctrl+E")
        file_m.add_separator()
        file_m.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=file_m)

        view_m = tk.Menu(menubar, tearoff=0)
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
        ttk.Button(bar, text="Open SMF…", command=self.open_dump).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar, text="Export JSON", command=self.export_json).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar, text="Export CSV", command=self.export_csv).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar, text="Clear log", command=self.clear_log).pack(side=tk.LEFT, padx=2)
        self.path_var = tk.StringVar(value="(no file loaded)")
        ttk.Label(bar, textvariable=self.path_var).pack(side=tk.LEFT, padx=12)

        desc_bar = ttk.Frame(self, padding=(8, 0, 8, 4))
        desc_bar.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(desc_bar, text="Field:").pack(side=tk.LEFT)
        self.desc_var = tk.StringVar(value="(hover a column header or cell for description)")
        ttk.Label(desc_bar, textvariable=self.desc_var, wraplength=1000).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=6
        )

    def _build_body(self) -> None:
        paned = ttk.Panedwindow(self, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        table_frame = ttk.LabelFrame(
            paned, text="Records (hover column for description)", padding=4
        )
        paned.add(table_frame, weight=3)
        self.tree = ttk.Treeview(table_frame, show="headings", height=18)
        ysb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        xsb = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        ysb.grid(row=0, column=1, sticky="ns")
        xsb.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

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
        self.update_idletasks()

    def clear_log(self) -> None:
        self.debug.delete("1.0", tk.END)
        self.log("INFO: debug log cleared")

    def open_dump(self) -> None:
        path = filedialog.askopenfilename(
            parent=self,
            title="Open SMF dump",
            filetypes=[("SMF dumps", "*.smf *.SMF *.bin *.dump"), ("All files", "*.*")],
            initialdir=str(self.dump_path.parent) if self.dump_path else str(Path.cwd()),
        )
        if path:
            self._load_path(Path(path))

    def _load_path(self, path: Path) -> None:
        self.clear_log()
        self.dump_path = path
        self.path_var.set(str(path))
        self.status_var.set("Reading…")
        try:
            records = read_dump(str(path), log=self.log)
            self.rows = convert_dump(records, log=self.log)
            self.columns = ordered_columns(self.rows)
            self.descriptions = field_descriptions_for_rows(self.rows)
            self._populate_table()
            self.status_var.set(f"Loaded {len(self.rows)} mapped records from {path.name}")
        except Exception as exc:  # noqa: BLE001
            self.log(f"ERROR: {exc}")
            messagebox.showerror("Load failed", str(exc), parent=self)
            self.status_var.set("Error")

    def _populate_table(self) -> None:
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = self.columns
        for col in self.columns:
            self.tree.heading(col, text=col)
            width = max(90, min(180, len(col) * 9 + 24))
            self.tree.column(col, width=width, stretch=False, anchor=tk.W)
        for i, row in enumerate(self.rows):
            values = [row.get(c, "") for c in self.columns]
            self.tree.insert("", tk.END, iid=str(i), values=values)
        if not self.rows:
            self.log("WARN: no mapped records (supported types: 30, 80, 89)")

    def _column_at(self, event: tk.Event) -> Optional[str]:  # type: ignore[type-arg]
        region = self.tree.identify_region(event.x, event.y)
        col_id = self.tree.identify_column(event.x)
        if region not in ("heading", "cell", "tree") or not col_id:
            return None
        try:
            idx = int(col_id.replace("#", "")) - 1
        except ValueError:
            return None
        if idx < 0 or idx >= len(self.columns):
            return None
        return self.columns[idx]

    def _on_tree_motion(self, event: tk.Event) -> None:  # type: ignore[type-arg]
        key = self._column_at(event)
        if not key:
            self._on_tree_leave(event)
            return
        desc = self.descriptions.get(key, "")
        tip = f"{key}\n{desc}" if desc else key
        self.desc_var.set(f"{key} — {desc}" if desc else key)
        self._hover_col = key
        self.tooltip.show(tip, event.x_root + 14, event.y_root + 18)

    def _on_tree_leave(self, _event: tk.Event) -> None:  # type: ignore[type-arg]
        self.tooltip.hide()
        self._hover_col = None
        self.desc_var.set("(hover a column header or cell for description)")

    def _default_export_dir(self) -> str:
        if self.dump_path:
            return str(self.dump_path.parent)
        return str(Path.cwd())

    def write_json(self, path: Path) -> None:
        with path.open("w", encoding="utf-8") as f:
            json.dump(self.rows, f, indent=2, ensure_ascii=False)
        self.log(f"INFO: wrote JSON {path} ({len(self.rows)} objects)")
        self.status_var.set(f"Exported JSON → {path}")

    def write_csv(self, path: Path) -> None:
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.columns, extrasaction="ignore")
            writer.writeheader()
            for row in self.rows:
                writer.writerow({c: row.get(c, "") for c in self.columns})
        self.log(f"INFO: wrote CSV {path} ({len(self.rows)} rows)")
        self.status_var.set(f"Exported CSV → {path}")

    def export_json(self) -> None:
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
        if not self.rows:
            messagebox.showinfo("Export", "No data to export — open a dump first.", parent=self)
            return
        initial = (self.dump_path.stem + ".csv") if self.dump_path else "smf.csv"
        path = filedialog.asksaveasfilename(
            parent=self,
            title="Export CSV",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialdir=self._default_export_dir(),
            initialfile=initial,
        )
        if path:
            self.write_csv(Path(path))

    def _about(self) -> None:
        messagebox.showinfo(
            "About",
            "SMF2JSON Desktop\n\n"
            "Python port of the HLASM table-driven SMF converter.\n"
            "Supports SMF types 30, 80, 89 from VB/VBS binary dumps.\n"
            "Hover a column header or cell for the field description.",
            parent=self,
        )


def run_app(initial_file: Optional[str] = None) -> None:
    app = SmfApp()
    if initial_file:
        app.after(100, lambda: app._load_path(Path(initial_file)))
    app.mainloop()
