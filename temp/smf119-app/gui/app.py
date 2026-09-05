"""Tkinter UI for offline SMF Type 119 dump exploration."""
from __future__ import annotations

import csv
import json
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from parser.catalog import field_catalog_rows, subtype_catalog_rows
from parser.decode import (
    decode_record,
    dump_record_json,
    export_record_flat_rows,
    section_table_rows,
    summary_row,
)
from parser.dump_index import DumpIndex, read_record_bytes, scan_dump
from parser.registry import coverage_for
from parser.views import columns_for, default_visible_keys


class Smf119App(ttk.Frame):
    def __init__(self, master: tk.Tk):
        super().__init__(master, padding=8)
        self.master = master
        self.pack(fill=tk.BOTH, expand=True)
        self.index: DumpIndex | None = None
        self._current_subtype: int | None = None
        self._record_refs = []
        self._decoded_cache: dict[int, object] = {}
        self._current_sections = []
        self._current_decoded = None
        self._current_offset: int | None = None
        self._use_labels = tk.BooleanVar(value=True)
        self._show_empty = tk.BooleanVar(value=False)
        self._detail_cols: list[str] = []
        self._detail_rows: list[list[str]] = []
        self._build()

    def _build(self) -> None:
        top = ttk.Frame(self)
        top.pack(fill=tk.X, pady=(0, 8))

        self.path_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.path_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6)
        )
        ttk.Button(top, text="Browse…", command=self._browse).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(top, text="Scan dump", command=self._start_scan).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(top, text="Export list CSV", command=self._export_list_csv).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(top, text="Export record JSON", command=self._export_record_json).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(top, text="Export record CSV", command=self._export_record_csv).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(top, text="Field catalog…", command=self._show_catalog).pack(side=tk.LEFT)

        opts = ttk.Frame(self)
        opts.pack(fill=tk.X, pady=(0, 4))
        ttk.Checkbutton(
            opts,
            text="Labels (vs IBM names)",
            variable=self._use_labels,
            command=self._refresh_section_detail,
        ).pack(side=tk.LEFT, padx=(0, 12))
        ttk.Checkbutton(
            opts,
            text="Show empty sections",
            variable=self._show_empty,
            command=self._reload_sections_tree,
        ).pack(side=tk.LEFT)

        self.status_var = tk.StringVar(
            value="Open an IFASMFDP binary dump containing SMF 119, then Scan."
        )
        ttk.Label(self, textvariable=self.status_var).pack(fill=tk.X, pady=(0, 6))

        self.progress = ttk.Progressbar(self, mode="determinate")
        self.progress.pack(fill=tk.X, pady=(0, 8))

        paned = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(paned, padding=(0, 0, 6, 0))
        mid = ttk.Frame(paned, padding=(0, 0, 6, 0))
        right = ttk.Frame(paned)
        paned.add(left, weight=1)
        paned.add(mid, weight=2)
        paned.add(right, weight=3)

        ttk.Label(left, text="SMF 119 subtypes in dump").pack(anchor=tk.W)
        self.subtype_tree = ttk.Treeview(
            left, columns=("subtype", "count", "coverage", "title"), show="headings", height=24
        )
        for c, w in (("subtype", 60), ("count", 50), ("coverage", 70), ("title", 180)):
            self.subtype_tree.heading(c, text=c)
            self.subtype_tree.column(c, width=w, anchor=tk.W)
        self.subtype_tree.pack(fill=tk.BOTH, expand=True)
        self.subtype_tree.bind("<<TreeviewSelect>>", self._on_select_subtype)

        ttk.Label(mid, text="Records (summary)").pack(anchor=tk.W)
        self.rec_tree = ttk.Treeview(mid, columns=("offset",), show="headings", height=24)
        self.rec_tree.pack(fill=tk.BOTH, expand=True)
        self.rec_tree.bind("<<TreeviewSelect>>", self._on_select_record)

        self.summary_var = tk.StringVar(value="")
        ttk.Label(right, textvariable=self.summary_var, wraplength=640, justify=tk.LEFT).pack(
            anchor=tk.W, pady=(0, 4)
        )
        ttk.Label(right, text="Decoded sections").pack(anchor=tk.W)
        right_split = ttk.Panedwindow(right, orient=tk.VERTICAL)
        right_split.pack(fill=tk.BOTH, expand=True)

        sec_frame = ttk.Frame(right_split)
        detail_frame = ttk.Frame(right_split)
        right_split.add(sec_frame, weight=1)
        right_split.add(detail_frame, weight=2)

        self.sec_tree = ttk.Treeview(
            sec_frame,
            columns=("idx", "name", "num", "len", "eye"),
            show="headings",
            height=10,
        )
        for c, w in (("idx", 40), ("name", 140), ("num", 40), ("len", 50), ("eye", 50)):
            self.sec_tree.heading(c, text=c)
            self.sec_tree.column(c, width=w, anchor=tk.W)
        self.sec_tree.pack(fill=tk.BOTH, expand=True)
        self.sec_tree.bind("<<TreeviewSelect>>", self._on_select_section)

        detail_btns = ttk.Frame(detail_frame)
        detail_btns.pack(fill=tk.X, pady=(0, 4))
        ttk.Label(detail_btns, text="Section fields").pack(side=tk.LEFT)
        ttk.Button(detail_btns, text="Export section CSV…", command=self._export_section_csv).pack(
            side=tk.RIGHT
        )

        self.detail = ttk.Treeview(detail_frame, show="headings", height=14)
        self.detail.pack(fill=tk.BOTH, expand=True)

        default = Path(__file__).resolve().parents[2] / "IZYP.SMFT000.EXPLORER.bin"
        if default.exists():
            self.path_var.set(str(default))

    def _browse(self) -> None:
        path = filedialog.askopenfilename(
            title="SMF dump",
            filetypes=[("Binary dumps", "*.bin;*.smf;*.dump;*"), ("All", "*.*")],
        )
        if path:
            self.path_var.set(path)

    def _start_scan(self) -> None:
        path = self.path_var.get().strip()
        if not path:
            messagebox.showwarning("Scan", "Choose a dump file first.")
            return
        if not Path(path).exists():
            messagebox.showerror("Scan", f"File not found:\n{path}")
            return
        self.status_var.set("Scanning for SMF 119…")
        self.progress["value"] = 0

        def work() -> None:
            def progress(cur: int, total: int) -> None:
                self.after(0, lambda: self._set_progress(cur, total))

            try:
                index = scan_dump(path, progress=progress)
            except Exception as exc:  # noqa: BLE001
                self.after(0, lambda: messagebox.showerror("Scan failed", str(exc)))
                return
            self.after(0, lambda: self._apply_index(index))

        threading.Thread(target=work, daemon=True).start()

    def _set_progress(self, cur: int, total: int) -> None:
        self.progress["maximum"] = max(total, 1)
        self.progress["value"] = cur

    def _apply_index(self, index: DumpIndex) -> None:
        self.index = index
        self._decoded_cache.clear()
        self.subtype_tree.delete(*self.subtype_tree.get_children())
        self.rec_tree.delete(*self.rec_tree.get_children())
        self.sec_tree.delete(*self.sec_tree.get_children())
        self._clear_detail()
        self.summary_var.set("")
        for row in index.discovery_rows():
            st = row["subtype"]
            self.subtype_tree.insert(
                "",
                tk.END,
                iid=str(st),
                values=(st, row["count"], coverage_for(st), row["title"]),
            )
        self.status_var.set(
            f"Found {len(index.records)} SMF 119 record(s) in {index.path.name} "
            f"({index.size:,} bytes)."
        )

    def _configure_record_columns(self, subtype: int) -> None:
        cols = [c for c in columns_for(subtype) if c.key in default_visible_keys(subtype)]
        names = [c.key for c in cols]
        self.rec_tree["columns"] = names
        for c in cols:
            self.rec_tree.heading(c.key, text=c.label)
            self.rec_tree.column(c.key, width=c.width, anchor=tk.W)
        self._visible_cols = cols

    def _on_select_subtype(self, _evt=None) -> None:
        sel = self.subtype_tree.selection()
        if not sel or not self.index:
            return
        subtype = int(sel[0])
        self._current_subtype = subtype
        self._record_refs = self.index.records_for(subtype)
        self._configure_record_columns(subtype)
        self.rec_tree.delete(*self.rec_tree.get_children())
        self.sec_tree.delete(*self.sec_tree.get_children())
        self._clear_detail()
        self.summary_var.set("")
        note = ""
        if coverage_for(subtype) == "external":
            note = " (layout not in ezasmf — Ident + raw preview)"
        self.status_var.set(
            f"Decoding {len(self._record_refs)} subtype {subtype} record(s)…{note}"
        )
        threading.Thread(target=self._load_records, args=(subtype,), daemon=True).start()

    def _load_records(self, subtype: int) -> None:
        assert self.index is not None
        rows = []
        for ref in self._record_refs:
            try:
                blob = read_record_bytes(self.index.path, ref)
                decoded = decode_record(blob)
                self._decoded_cache[ref.offset] = decoded
                rows.append((ref.offset, summary_row(decoded, file_offset=ref.offset)))
            except Exception:  # noqa: BLE001
                continue
        self.after(0, lambda: self._fill_records(subtype, rows))

    def _fill_records(self, subtype: int, rows: list) -> None:
        if self._current_subtype != subtype:
            return
        self.rec_tree.delete(*self.rec_tree.get_children())
        for offset, row in rows:
            values = [row.get(c.key, "") for c in self._visible_cols]
            self.rec_tree.insert("", tk.END, iid=str(offset), values=values)
        self.status_var.set(f"Subtype {subtype}: {len(rows)} record(s) ready.")

    def _on_select_record(self, _evt=None) -> None:
        sel = self.rec_tree.selection()
        if not sel:
            return
        offset = int(sel[0])
        self._current_offset = offset
        decoded = self._decoded_cache.get(offset)
        if decoded is None and self.index:
            refs = [r for r in self._record_refs if r.offset == offset]
            if refs:
                blob = read_record_bytes(self.index.path, refs[0])
                decoded = decode_record(blob)
                self._decoded_cache[offset] = decoded
        if decoded is None:
            return
        self._current_decoded = decoded
        self._current_sections = decoded.sections
        summary = summary_row(decoded, file_offset=offset)
        parts = []
        for c in columns_for(decoded.subtype):
            if not c.default:
                continue
            val = summary.get(c.key, "")
            if val not in ("", None):
                parts.append(f"{c.label}={val}")
        note = ""
        if coverage_for(decoded.subtype) == "external":
            note = "  [layout not in ezasmf]"
        self.summary_var.set(" | ".join(parts) + note)
        self._reload_sections_tree()

    def _reload_sections_tree(self) -> None:
        self.sec_tree.delete(*self.sec_tree.get_children())
        self._clear_detail()
        show_empty = self._show_empty.get()
        for sec in self._current_sections:
            trip = sec.triplet
            if not show_empty and trip.number == 0 and trip.index != 0:
                continue
            name = sec.info.key if sec.info else f"triplet[{trip.index}]"
            eye = ""
            if sec.entries:
                eye_val = sec.entries[0].get("_eye")
                if eye_val:
                    eye = str(eye_val)
            self.sec_tree.insert(
                "",
                tk.END,
                iid=str(trip.index),
                values=(trip.index, name, trip.number, trip.length, eye),
            )
        children = self.sec_tree.get_children()
        if children:
            self.sec_tree.selection_set(children[0])
            self._on_select_section()

    def _on_select_section(self, _evt=None) -> None:
        self._refresh_section_detail()

    def _refresh_section_detail(self) -> None:
        sel = self.sec_tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        section = next((s for s in self._current_sections if s.triplet.index == idx), None)
        if section is None:
            return
        cols, rows, _ibm = section_table_rows(section, use_labels=self._use_labels.get())
        self._detail_cols = cols
        self._detail_rows = rows
        self.detail.delete(*self.detail.get_children())
        self.detail["columns"] = cols
        for c in cols:
            self.detail.heading(c, text=c)
            self.detail.column(c, width=max(80, min(200, 10 * len(c) + 40)), anchor=tk.W)
        for row in rows:
            self.detail.insert("", tk.END, values=row)

    def _clear_detail(self) -> None:
        self.detail.delete(*self.detail.get_children())
        self.detail["columns"] = ()
        self._detail_cols = []
        self._detail_rows = []

    def _export_section_csv(self) -> None:
        if not self._detail_cols or not self._detail_rows:
            messagebox.showinfo("Export", "Select a section with decoded fields first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
        )
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(self._detail_cols)
            writer.writerows(self._detail_rows)
        self.status_var.set(f"Exported {len(self._detail_rows)} row(s) to {path}")

    def _export_list_csv(self) -> None:
        if self._current_subtype is None or not self.index:
            messagebox.showinfo("Export", "Select a subtype first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path:
            return
        cols = columns_for(self._current_subtype)
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow([c.key for c in cols])
            for ref in self._record_refs:
                decoded = self._decoded_cache.get(ref.offset)
                if decoded is None:
                    blob = read_record_bytes(self.index.path, ref)
                    decoded = decode_record(blob)
                    self._decoded_cache[ref.offset] = decoded
                row = summary_row(decoded, file_offset=ref.offset)
                writer.writerow([row.get(c.key, "") for c in cols])
        self.status_var.set(f"Wrote list CSV {path}")

    def _export_record_json(self) -> None:
        if not self._current_decoded or self._current_offset is None:
            messagebox.showinfo("Export", "Select a record first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not path:
            return
        Path(path).write_text(
            dump_record_json(self._current_decoded, file_offset=self._current_offset),
            encoding="utf-8",
        )
        self.status_var.set(f"Wrote {path}")

    def _export_record_csv(self) -> None:
        if not self._current_decoded or self._current_offset is None:
            messagebox.showinfo("Export", "Select a record first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if not path:
            return
        rows = export_record_flat_rows(self._current_decoded, file_offset=self._current_offset)
        if not rows:
            messagebox.showinfo("Export", "No mapped fields to export for this record.")
            return
        # Union of keys across rows
        keys: list[str] = []
        seen = set()
        for row in rows:
            for k in row:
                if k not in seen:
                    seen.add(k)
                    keys.append(k)
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        self.status_var.set(f"Wrote {path}")

    def _show_catalog(self) -> None:
        win = tk.Toplevel(self)
        win.title("SMF 119 field catalog")
        win.geometry("980x560")
        nb = ttk.Notebook(win)
        nb.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        fields_frame = ttk.Frame(nb)
        subtypes_frame = ttk.Frame(nb)
        nb.add(fields_frame, text="Fields")
        nb.add(subtypes_frame, text="Subtypes")

        fcols = ("section", "field", "offset", "size", "kind", "description")
        ftree = ttk.Treeview(fields_frame, columns=fcols, show="headings")
        for c, w in (
            ("section", 160),
            ("field", 200),
            ("offset", 60),
            ("size", 50),
            ("kind", 80),
            ("description", 300),
        ):
            ftree.heading(c, text=c)
            ftree.column(c, width=w, anchor=tk.W)
        ftree.pack(fill=tk.BOTH, expand=True)
        for row in field_catalog_rows():
            ftree.insert(
                "",
                tk.END,
                values=(
                    row["section"],
                    row["field"],
                    row["offset"],
                    row["size"],
                    row["kind"],
                    row["description"],
                ),
            )

        scols = ("subtype", "title", "coverage", "fields", "sections")
        stree = ttk.Treeview(subtypes_frame, columns=scols, show="headings")
        for c, w in (
            ("subtype", 70),
            ("title", 260),
            ("coverage", 90),
            ("fields", 70),
            ("sections", 70),
        ):
            stree.heading(c, text=c)
            stree.column(c, width=w, anchor=tk.W)
        stree.pack(fill=tk.BOTH, expand=True)
        for row in subtype_catalog_rows():
            stree.insert(
                "",
                tk.END,
                values=(
                    row["subtype"],
                    row["title"],
                    row["coverage"],
                    row.get("mapped_fields", ""),
                    row.get("mapped_sections", ""),
                ),
            )


def run() -> None:
    root = tk.Tk()
    root.title("SMF Type 119 Offline Explorer")
    root.geometry("1380x820")
    root.minsize(1000, 640)
    Smf119App(root)
    root.mainloop()
