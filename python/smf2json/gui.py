"""Tkinter GUI for SMF dump conversion."""

from __future__ import annotations

import csv
import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, font as tkfont, messagebox, ttk
from typing import Any, Callable, Dict, List, Optional, Set

from . import __version__
from .column_config import (
    config_path,
    group_label,
    group_rows,
    load_config,
    save_config,
    store_group_selection,
    visible_for_group,
)
from .engine import convert_dump, field_meta, ordered_columns
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
        rows: List[Dict[str, Any]],
    ):
        self.app = app
        self.rty = rty
        self.sty = sty
        self.rows = rows
        self.columns = ordered_columns(rows)
        self.visible = visible_for_group(self.columns, rty, sty, load_config())
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
        self.populate()

    @property
    def label(self) -> str:
        return group_label(self.rty, self.sty, len(self.rows))

    def populate(self) -> None:
        self.tree.delete(*self.tree.get_children())
        shown = self.visible or self.columns
        self.tree["columns"] = shown
        for col in shown:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=self.app._header_width(col), stretch=False, anchor=tk.W)
        for i, row in enumerate(self.rows):
            values = [row.get(c, "") for c in shown]
            self.tree.insert("", tk.END, iid=str(i), values=values)

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
        self.meta: Dict[str, Dict[str, Any]] = field_meta()
        self.dump_path: Optional[Path] = None
        self._heading_font = tkfont.nametofont("TkHeadingFont")

        self._build_menu()
        self._build_toolbar()
        self._build_body()
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self, textvariable=self.status_var, anchor=tk.W, padding=4).pack(
            side=tk.BOTTOM, fill=tk.X
        )
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
        ttk.Button(bar, text="Open SMF…", command=self.open_dump).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar, text="Export JSON", command=self.export_json).pack(side=tk.LEFT, padx=2)
        self._btn_csv = ttk.Button(bar, text="Export CSV", command=self.export_csv)
        self._btn_csv.pack(side=tk.LEFT, padx=2)
        self.columns_btn = ttk.Button(bar, text="Columns…", command=self.open_columns)
        ttk.Button(bar, text="Clear log", command=self.clear_log).pack(side=tk.LEFT, padx=2)
        self.path_var = tk.StringVar(value="(no file loaded)")
        ttk.Label(bar, textvariable=self.path_var).pack(side=tk.LEFT, padx=12)

        desc_bar = ttk.Frame(self, padding=(8, 0, 8, 4))
        desc_bar.pack(side=tk.TOP, fill=tk.X)
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
        self.update_idletasks()

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
        path = filedialog.askopenfilename(
            parent=self,
            title="Open SMF dump",
            filetypes=[("SMF dumps", "*.smf *.SMF *.bin *.dump"), ("All files", "*.*")],
            initialdir=str(self.dump_path.parent) if self.dump_path else str(Path.cwd()),
        )
        if path:
            self._load_path(Path(path))

    def _clear_tabs(self) -> None:
        for pane in self.panes:
            pane.tooltip.hide()
        for child in self.notebook.winfo_children():
            child.destroy()
        self.panes.clear()

    def _load_path(self, path: Path) -> None:
        self.clear_log()
        self.dump_path = path
        self.path_var.set(str(path))
        self.status_var.set("Reading…")
        try:
            records = read_dump(str(path), log=self.log)
            self.rows = convert_dump(records, log=self.log)
            self._rebuild_tabs()
            self._show_columns_button()
            labels = ", ".join(group_label(rty, sty) for (rty, sty), _rows in group_rows(self.rows))
            self.status_var.set(
                f"Loaded {len(self.rows)} mapped records in {len(self.panes)} tab(s) "
                f"({labels or 'none'}) from {path.name}"
            )
        except Exception as exc:  # noqa: BLE001
            self.log(f"ERROR: {exc}")
            messagebox.showerror("Load failed", str(exc), parent=self)
            self.status_var.set("Error")

    def _rebuild_tabs(self) -> None:
        self._clear_tabs()
        groups = group_rows(self.rows)
        if not groups:
            self.log("WARN: no mapped records (supported types: 30, 80, 89, 119-1)")
            return
        for (rty, sty), rows in groups:
            pane = RecordPane(self.notebook, self, rty, sty, rows)
            self.notebook.add(pane.frame, text=pane.label)
            self.panes.append(pane)
            self.log(f"INFO: tab {pane.label}")

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
            "Supports SMF types 30, 80, 89, 119 subtype 1 from VB/VBS binary dumps.\n"
            "Records are grouped into tabs by type / subtype.\n"
            f"Column layout is saved to {config_path()}.",
            parent=self,
        )


def run_app(initial_file: Optional[str] = None) -> None:
    app = SmfApp()
    if initial_file:
        app.after(100, lambda: app._load_path(Path(initial_file)))
    app.mainloop()
