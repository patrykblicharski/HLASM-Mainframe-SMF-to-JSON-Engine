"""Tkinter UI for SMF binary dump discovery and table extract."""
from __future__ import annotations

import csv
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from parser.columns import ColumnSpec, column_specs_for, default_visible_keys
from parser.decode import decode_records
from parser.dump_index import DumpIndex, scan_dump


class ColumnPickerDialog(tk.Toplevel):
    """Checkbox list of columns with documentation descriptions."""

    def __init__(
        self,
        master: tk.Tk,
        columns: list[ColumnSpec],
        visible: set[str],
        on_apply,
    ):
        super().__init__(master)
        self.title("Columns")
        self.transient(master)
        self.grab_set()
        self.geometry("640x520")
        self._columns = columns
        self._on_apply = on_apply
        self._vars: dict[str, tk.BooleanVar] = {}

        ttk.Label(
            self,
            text="Select columns to display. Non-default fields are available in the "
            "decoded data but hidden until enabled.",
            wraplength=600,
        ).pack(anchor=tk.W, padx=10, pady=(10, 6))

        canvas = tk.Canvas(self, highlightthickness=0)
        scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=canvas.yview)
        inner = ttk.Frame(canvas)
        inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=inner, anchor=tk.NW)
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=4)
        scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10), pady=4)

        for col in columns:
            row = ttk.Frame(inner)
            row.pack(fill=tk.X, pady=2, padx=4)
            var = tk.BooleanVar(value=col.key in visible)
            self._vars[col.key] = var
            ttk.Checkbutton(row, variable=var).pack(side=tk.LEFT, anchor=tk.N)
            text = ttk.Frame(row)
            text.pack(side=tk.LEFT, fill=tk.X, expand=True)
            title = ttk.Frame(text)
            title.pack(fill=tk.X)
            ttk.Label(title, text=col.label, font=("", 9, "bold")).pack(side=tk.LEFT)
            badge = "default" if col.default else "non-default"
            ttk.Label(title, text=f"  [{badge}]", foreground="#666").pack(side=tk.LEFT)
            ttk.Label(
                text,
                text=col.description or col.key,
                foreground="#555",
                wraplength=520,
            ).pack(anchor=tk.W)

        btns = ttk.Frame(self)
        btns.pack(fill=tk.X, padx=10, pady=10)

        def select_all() -> None:
            for v in self._vars.values():
                v.set(True)

        def select_defaults() -> None:
            for col in self._columns:
                self._vars[col.key].set(col.default)

        ttk.Button(btns, text="Select all", command=select_all).pack(side=tk.LEFT)
        ttk.Button(btns, text="Defaults only", command=select_defaults).pack(
            side=tk.LEFT, padx=6
        )
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side=tk.RIGHT)
        ttk.Button(btns, text="Apply", command=self._apply).pack(side=tk.RIGHT, padx=6)

    def _apply(self) -> None:
        selected = {k for k, v in self._vars.items() if v.get()}
        if not selected:
            messagebox.showwarning("Columns", "Select at least one column.", parent=self)
            return
        self._on_apply(selected)
        self.destroy()


class SmfDumpApp(ttk.Frame):
    def __init__(self, master: tk.Tk):
        super().__init__(master, padding=8)
        self.master = master
        self.pack(fill=tk.BOTH, expand=True)
        self.index: DumpIndex | None = None
        self._rows: list[dict] = []
        self._columns: list[ColumnSpec] = []
        self._visible: set[str] = set()
        self._current_type: tuple[int, int] | None = None
        self._sort_key: str | None = None
        self._sort_reverse: bool = False
        self._build()

    def _build(self) -> None:
        top = ttk.Frame(self)
        top.pack(fill=tk.X, pady=(0, 8))

        self.path_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.path_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6)
        )
        ttk.Button(top, text="Browse…", command=self._browse).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(top, text="Scan dump", command=self._start_scan).pack(side=tk.LEFT)

        self.status_var = tk.StringVar(value="Open an IFASMFDP binary dump, then Scan.")
        ttk.Label(self, textvariable=self.status_var).pack(fill=tk.X, pady=(0, 6))

        self.progress = ttk.Progressbar(self, mode="determinate")
        self.progress.pack(fill=tk.X, pady=(0, 8))

        paned = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(paned, padding=(0, 0, 6, 0))
        right = ttk.Frame(paned)
        paned.add(left, weight=1)
        paned.add(right, weight=3)

        ttk.Label(left, text="SMF types in dump (Gatherer set)").pack(anchor=tk.W)
        cols = ("type", "subtype", "count", "title")
        self.tree = ttk.Treeview(left, columns=cols, show="headings", height=24)
        for c, w in (("type", 50), ("subtype", 60), ("count", 60), ("title", 220)):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w, anchor=tk.W)
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_select_type)

        btns = ttk.Frame(right)
        btns.pack(fill=tk.X, pady=(0, 6))
        ttk.Label(btns, text="Decoded records").pack(side=tk.LEFT)
        ttk.Button(btns, text="Export CSV…", command=self._export_csv).pack(side=tk.RIGHT)
        self.columns_btn = ttk.Button(
            btns, text="Columns…", command=self._open_column_picker, state=tk.DISABLED
        )
        self.columns_btn.pack(side=tk.RIGHT, padx=(0, 6))

        table_frame = ttk.Frame(right)
        table_frame.pack(fill=tk.BOTH, expand=True)
        self.table = ttk.Treeview(table_frame, show="headings", height=24)
        yscroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.table.yview)
        xscroll = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.table.xview)
        self.table.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        self.table.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        default = Path(__file__).resolve().parents[1].parent / "IZYP.SMFT000.EXPLORER.bin"
        if default.exists():
            self.path_var.set(str(default))

    def _browse(self) -> None:
        path = filedialog.askopenfilename(
            title="Select SMF dump",
            filetypes=[("Binary dump", "*.bin;*.smf;*.dump;*.*"), ("All files", "*.*")],
        )
        if path:
            self.path_var.set(path)

    def _start_scan(self) -> None:
        path = Path(self.path_var.get().strip())
        if not path.is_file():
            messagebox.showerror("Missing file", f"File not found:\n{path}")
            return
        self.status_var.set(f"Scanning {path.name}…")
        self.progress["value"] = 0
        self.tree.delete(*self.tree.get_children())
        self._clear_table()
        self.columns_btn.configure(state=tk.DISABLED)

        def report(done: int, total: int) -> None:
            pct = int(100 * done / total) if total else 0
            self.master.after(0, lambda: self._set_progress(pct, done, total))

        def work() -> None:
            try:
                index = scan_dump(path, progress=report)
            except Exception as exc:
                self.master.after(0, lambda: self._scan_failed(exc))
                return
            self.master.after(0, lambda: self._scan_done(index))

        threading.Thread(target=work, daemon=True).start()

    def _set_progress(self, pct: int, done: int, total: int) -> None:
        self.progress["value"] = pct
        self.status_var.set(f"Scanning… {done:,} / {total:,} bytes ({pct}%)")

    def _scan_failed(self, exc: Exception) -> None:
        self.status_var.set("Scan failed.")
        messagebox.showerror("Scan failed", str(exc))

    def _scan_done(self, index: DumpIndex) -> None:
        self.index = index
        self.progress["value"] = 100
        for row in index.discovery_rows():
            self.tree.insert(
                "",
                tk.END,
                iid=f"{row['type']}-{row['subtype']}",
                values=(row["type"], row["subtype"], row["count"], row["title"]),
            )
        self.status_var.set(
            f"{index.path.name}: {len(index.records):,} Gatherer records, "
            f"{len(index.discovery_rows())} type/subtype pairs "
            f"({index.size / 1e6:.1f} MB)"
        )

    def _on_select_type(self, _event=None) -> None:
        if not self.index:
            return
        sel = self.tree.selection()
        if not sel:
            return
        typ_s, sty_s = sel[0].split("-", 1)
        smf_type, subtype = int(typ_s), int(sty_s)
        refs = self.index.records_for(smf_type, subtype)
        self.status_var.set(f"Decoding SMF {smf_type}-{subtype} ({len(refs)} records)…")
        self.master.update_idletasks()

        def work() -> None:
            try:
                columns = column_specs_for(smf_type, subtype)
                rows = decode_records(self.index.path, refs, limit=None)
            except Exception as exc:
                self.master.after(0, lambda: messagebox.showerror("Decode failed", str(exc)))
                return
            self.master.after(
                0,
                lambda: self._show_rows(smf_type, subtype, rows, columns),
            )

        threading.Thread(target=work, daemon=True).start()

    def _clear_table(self) -> None:
        self.table.delete(*self.table.get_children())
        self.table["columns"] = ()
        self._rows = []
        self._columns = []
        self._visible = set()
        self._current_type = None
        self._sort_key = None
        self._sort_reverse = False

    def _show_rows(
        self,
        smf_type: int,
        subtype: int,
        rows: list[dict],
        columns: list[ColumnSpec],
    ) -> None:
        self._rows = rows
        self._columns = columns
        self._visible = default_visible_keys(columns)
        self._current_type = (smf_type, subtype)
        self._sort_key = None
        self._sort_reverse = False
        self.columns_btn.configure(state=tk.NORMAL if columns else tk.DISABLED)
        self._render_table()
        self.status_var.set(f"SMF {smf_type}-{subtype}: {len(rows)} rows")

    def _visible_columns(self) -> list[ColumnSpec]:
        cols = [c for c in self._columns if c.key in self._visible]
        return cols or self._columns[:1]

    @staticmethod
    def _sort_value(value):
        if value is None or value == "":
            return (2, "")  # empty last
        if isinstance(value, bool):
            return (0, int(value))
        if isinstance(value, (int, float)):
            return (0, value)
        text = str(value)
        try:
            if text.startswith(("0x", "0X")):
                return (0, int(text, 16))
            if "." in text:
                return (0, float(text))
            return (0, int(text))
        except ValueError:
            return (1, text.casefold())

    def _sorted_rows(self) -> list[dict]:
        if not self._sort_key:
            return self._rows
        key = self._sort_key
        return sorted(
            self._rows,
            key=lambda row: self._sort_value(row.get(key)),
            reverse=self._sort_reverse,
        )

    def _on_heading_click(self, column_key: str) -> None:
        if self._sort_key == column_key:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_key = column_key
            self._sort_reverse = False
        self._render_table()

    def _heading_text(self, col: ColumnSpec) -> str:
        if self._sort_key != col.key:
            return col.label
        arrow = " ▼" if self._sort_reverse else " ▲"
        return f"{col.label}{arrow}"

    def _render_table(self) -> None:
        self.table.delete(*self.table.get_children())
        cols = self._visible_columns()
        if not cols:
            self.table["columns"] = ()
            return
        keys = [c.key for c in cols]
        self.table["columns"] = keys
        rows = self._sorted_rows()

        # Estimate pixel width from character count (Tk default UI font ~7–8 px/char).
        def col_width(col: ColumnSpec) -> int:
            heading = self._heading_text(col)
            max_chars = len(heading)
            for row in rows:
                val = row.get(col.key)
                if val is None:
                    continue
                max_chars = max(max_chars, len(str(val)))
            # Cap very wide columns so one free-text field does not dominate.
            return max(80, min(480, max_chars * 8 + 16))

        for col in cols:
            self.table.heading(
                col.key,
                text=self._heading_text(col),
                command=lambda k=col.key: self._on_heading_click(k),
            )
            self.table.column(col.key, width=col_width(col), anchor=tk.W, stretch=False)
        for row in rows:
            values = ["" if row.get(k) is None else str(row.get(k)) for k in keys]
            self.table.insert("", tk.END, values=values)

    def _open_column_picker(self) -> None:
        if not self._columns:
            return
        ColumnPickerDialog(
            self.master,
            self._columns,
            set(self._visible),
            on_apply=self._apply_columns,
        )

    def _apply_columns(self, visible: set[str]) -> None:
        self._visible = visible
        self._render_table()
        if self._current_type:
            t, s = self._current_type
            shown = len(self._visible_columns())
            self.status_var.set(
                f"SMF {t}-{s}: {len(self._rows)} rows, {shown} columns visible"
            )

    def _export_csv(self) -> None:
        if not self._rows or not self._columns:
            messagebox.showinfo("Nothing to export", "Decode a type/subtype first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            title="Export table",
        )
        if not path:
            return
        cols = self._visible_columns()
        fieldnames = [c.key for c in cols]
        headers = {c.key: c.label for c in cols}
        with open(path, "w", newline="", encoding="utf-8-sig") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
            writer.writerow(headers)
            for row in self._sorted_rows():
                writer.writerow({k: row.get(k) for k in fieldnames})
        self.status_var.set(f"Exported {len(self._rows)} rows → {path}")


def run() -> None:
    root = tk.Tk()
    root.title("SMF Dump Explorer (offline)")
    root.geometry("1200x700")
    try:
        ttk.Style().theme_use("vista")
    except tk.TclError:
        pass
    SmfDumpApp(root)
    root.mainloop()
