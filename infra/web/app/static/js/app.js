/* Theme + Chart.js helpers for SMF Analytics */
window.SMFTheme = {
  key: "smf-theme",
  ids: [
    "classic", "phosphor", "carbon", "harbor", "obsidian", "ledger", "frost",
    "purity-dark", "dabang", "electric", "violet-finance", "glass-neon",
    "tiesen", "logistic-one", "business", "corporate", "cupcake", "halloween",
    "claude-blu-2", "blue-smlb", "albl-v2",
  ],
  current() {
    const t = document.documentElement.getAttribute("data-theme");
    return this.ids.includes(t) ? t : "blue-smlb";
  },
  apply(id) {
    if (!this.ids.includes(id)) id = "blue-smlb";
    document.documentElement.setAttribute("data-theme", id);
    try { localStorage.setItem(this.key, id); } catch (e) {}
    this._syncPicker(id);
    if (window.SMFCharts) SMFCharts.applyTheme();
  },
  _syncPicker(id) {
    const sel = document.getElementById("smf-theme-select");
    if (sel && sel.value !== id) sel.value = id;
    document.querySelectorAll(".theme-swatch").forEach((btn) => {
      const on = btn.getAttribute("data-theme-id") === id;
      btn.setAttribute("aria-checked", on ? "true" : "false");
    });
  },
  init() {
    this._syncPicker(this.current());
    const picker = document.getElementById("smf-theme-picker");
    if (!picker) return;
    const sel = document.getElementById("smf-theme-select");
    if (sel) {
      sel.addEventListener("change", () => this.apply(sel.value));
    }
    picker.addEventListener("click", (ev) => {
      const btn = ev.target.closest(".theme-swatch");
      if (!btn) return;
      this.apply(btn.getAttribute("data-theme-id"));
    });
  },
};

window.SMFCharts = {
  colors: [],
  _css(name, fallback) {
    const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    return v || fallback;
  },
  _readPalette() {
    this.colors = [
      this._css("--chart-1", "#4ecf5c"),
      this._css("--chart-2", "#b8d44a"),
      this._css("--chart-3", "#d4a03c"),
      this._css("--chart-4", "#6ecf9a"),
      this._css("--chart-5", "#e85d5d"),
      this._css("--chart-6", "#8fbf6a"),
      this._css("--chart-7", "#e8c547"),
      this._css("--chart-8", "#5a9e6a"),
    ];
  },
  applyTheme() {
    this._readPalette();
    this.darkDefaults();
    if (!window.Chart || typeof Chart.getChart !== "function") return;
    const label = this._labelColor();
    const tick = this._tickColor();
    const line = this._css("--line", "#2a3a2c");
    const fontFam = this._fontFamily();
    document.querySelectorAll("canvas").forEach((canvas) => {
      const chart = Chart.getChart(canvas);
      if (!chart) return;
      chart.options.color = label;
      chart.options.font = chart.options.font || {};
      chart.options.font.family = fontFam;
      chart.options.font.size = 14;
      if (!chart.options.plugins) chart.options.plugins = {};
      if (!chart.options.plugins.legend) chart.options.plugins.legend = {};
      chart.options.plugins.legend.labels = Object.assign({}, chart.options.plugins.legend.labels || {}, {
        color: label,
        font: { family: fontFam, size: 14, weight: "600" },
        boxWidth: 14,
        boxHeight: 14,
        padding: 14,
      });
      if (chart.options.scales) {
        Object.values(chart.options.scales).forEach((scale) => {
          if (!scale) return;
          scale.ticks = Object.assign({}, scale.ticks || {}, {
            color: tick,
            font: { family: fontFam, size: 13, weight: "500" },
          });
          if (scale.grid) scale.grid.color = line;
          if (scale.border) scale.border.color = line;
          if (scale.title) {
            scale.title.color = label;
            scale.title.font = { family: fontFam, size: 13, weight: "600" };
          }
        });
      }
      if (chart.data && Array.isArray(chart.data.datasets)) {
        chart.data.datasets.forEach((ds, i) => {
          const c = this.colors[i % this.colors.length];
          if (ds.backgroundColor && !Array.isArray(ds.backgroundColor)) {
            ds.backgroundColor = c;
          } else if (Array.isArray(ds.backgroundColor)) {
            ds.backgroundColor = this.colors.slice();
          }
          if (ds.borderColor && !Array.isArray(ds.borderColor)) ds.borderColor = c;
        });
      }
      chart.update("none");
    });
  },
  _fontFamily() {
    return this._css("--font-table", this._css("--font", "Inter, system-ui, sans-serif"));
  },
  _labelColor() {
    return this._css("--text", "#f4f7fb");
  },
  _tickColor() {
    // Brighter than muted so axis/legend stay readable on dark skins
    return this._css("--accent-2", this._css("--muted", "#aeb9cc"));
  },
  darkDefaults() {
    if (!window.Chart) return;
    this._readPalette();
    const label = this._labelColor();
    const tick = this._tickColor();
    const fontFam = this._fontFamily();
    Chart.defaults.color = label;
    Chart.defaults.borderColor = this._css("--line", "#2a3a2c");
    Chart.defaults.font.family = fontFam;
    Chart.defaults.font.size = 14;
    Chart.defaults.font.weight = "500";
    Chart.defaults.plugins = Chart.defaults.plugins || {};
    Chart.defaults.plugins.legend = Chart.defaults.plugins.legend || {};
    Chart.defaults.plugins.legend.labels = {
      color: label,
      font: { family: fontFam, size: 14, weight: "600" },
      boxWidth: 14,
      boxHeight: 14,
      padding: 14,
      usePointStyle: false,
    };
    Chart.defaults.plugins.tooltip = Chart.defaults.plugins.tooltip || {};
    Chart.defaults.plugins.tooltip.titleFont = { family: fontFam, size: 14, weight: "650" };
    Chart.defaults.plugins.tooltip.bodyFont = { family: fontFam, size: 13 };
    Chart.defaults.plugins.tooltip.padding = 10;
    // Chart.js v3/v4 scale defaults
    const tickFont = { family: fontFam, size: 13, weight: "500" };
    ["category", "linear", "time", "timeseries", "logarithmic"].forEach((id) => {
      Chart.defaults.scales = Chart.defaults.scales || {};
      Chart.defaults.scales[id] = Chart.defaults.scales[id] || {};
      Chart.defaults.scales[id].ticks = Object.assign({}, Chart.defaults.scales[id].ticks || {}, {
        color: tick,
        font: tickFont,
      });
    });
  },
  _legendOpts() {
    return {
      position: "bottom",
      labels: {
        color: this._labelColor(),
        font: { family: this._fontFamily(), size: 14, weight: "600" },
        boxWidth: 14,
        boxHeight: 14,
        padding: 14,
      },
    };
  },
  _scaleTickOpts() {
    return {
      color: this._tickColor(),
      font: { family: this._fontFamily(), size: 13, weight: "500" },
    };
  },
  _el(canvasId) {
    const el = document.getElementById(canvasId);
    if (!el) return null;
    if (!window.Chart) {
      el.replaceWith(Object.assign(document.createElement("div"), {
        className: "empty",
        textContent: "Chart.js failed to load.",
      }));
      return null;
    }
    return el;
  },
  _empty(canvasId, msg) {
    const el = document.getElementById(canvasId);
    if (!el) return;
    const wrap = el.parentElement;
    el.remove();
    const div = document.createElement("div");
    div.className = "empty";
    div.textContent = msg || "No chart data in this time window.";
    (wrap || document.body).appendChild(div);
  },
  applyHourRange(startLabel) {
    const start = String(startLabel || "").trim();
    if (!start) return;
    const endDate = new Date(start.replace(" ", "T"));
    if (Number.isNaN(endDate.getTime())) return;
    endDate.setHours(endDate.getHours() + 1);
    const pad = (n) => String(n).padStart(2, "0");
    const end =
      endDate.getFullYear() +
      "-" +
      pad(endDate.getMonth() + 1) +
      "-" +
      pad(endDate.getDate()) +
      " " +
      pad(endDate.getHours()) +
      ":00:00";
    const u = new URL(window.location.href);
    u.searchParams.set("hour_from", start.length === 16 ? start + ":00" : start);
    u.searchParams.set("hour_to", end);
    window.location.href = u.toString();
  },
  _mergeBrush(options, labels, enabled) {
    if (!enabled) return options;
    const prev = options.onClick;
    options.onClick = (evt, elements, chart) => {
      if (typeof prev === "function") prev(evt, elements, chart);
      if (!elements.length) return;
      const i = elements[0].index;
      this.applyHourRange(labels[i]);
    };
    options.plugins = options.plugins || {};
    const tip = options.plugins.tooltip || {};
    tip.callbacks = tip.callbacks || {};
    const oldFooter = tip.callbacks.footer;
    tip.callbacks.footer = (items) => {
      const base = typeof oldFooter === "function" ? oldFooter(items) : "";
      return (base ? base + "\n" : "") + "Click to filter this hour";
    };
    options.plugins.tooltip = tip;
    return options;
  },
  stackedBar(canvasId, labels, datasets, extraOptions) {
    const el = this._el(canvasId);
    if (!el) return;
    if (!labels.length || !datasets.length) {
      this._empty(canvasId);
      return;
    }
    const extra = extraOptions || {};
    const hourBrush = !!extra.hourBrush;
    const options = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: this._legendOpts() },
      scales: {
        x: { stacked: true, ticks: Object.assign({ maxRotation: 0, autoSkip: true, maxTicksLimit: 12 }, this._scaleTickOpts()) },
        y: { stacked: true, beginAtZero: true, ticks: this._scaleTickOpts() },
      },
    };
    Object.keys(extra).forEach((k) => {
      if (k !== "hourBrush") options[k] = extra[k];
    });
    this._mergeBrush(options, labels, hourBrush);
    new Chart(el, {
      type: "bar",
      data: { labels, datasets },
      options,
    });
  },
  line(canvasId, labels, datasets, extraOptions) {
    const el = this._el(canvasId);
    if (!el) return;
    if (!labels.length || !datasets.length) {
      this._empty(canvasId);
      return;
    }
    const extra = extraOptions || {};
    const hourBrush = !!extra.hourBrush;
    const options = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: this._legendOpts() },
      scales: {
        x: { ticks: this._scaleTickOpts() },
        y: { beginAtZero: true, ticks: this._scaleTickOpts() },
      },
      elements: { line: { tension: 0.25, borderWidth: 2 }, point: { radius: 2, hitRadius: 8 } },
    };
    Object.keys(extra).forEach((k) => {
      if (k !== "hourBrush") options[k] = extra[k];
    });
    this._mergeBrush(options, labels, hourBrush);
    new Chart(el, {
      type: "line",
      data: { labels, datasets },
      options,
    });
  },
  doughnut(canvasId, labels, values) {
    const el = this._el(canvasId);
    if (!el) return;
    const nums = (values || []).map((v) => Number(v) || 0);
    if (!labels.length || !nums.some((n) => n > 0)) {
      this._empty(canvasId);
      return;
    }
    new Chart(el, {
      type: "doughnut",
      data: {
        labels,
        datasets: [{
          data: nums,
          backgroundColor: this.colors,
          borderWidth: 0,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: Object.assign(this._legendOpts(), { position: "right" }) },
        cutout: "62%",
      },
    });
  },
  groupSeries(rows, timeKey, seriesKey, valueKey) {
    const labels = [];
    const series = {};
    const seen = new Set();
    (rows || []).forEach((r) => {
      const t = String(r[timeKey] ?? "");
      if (!seen.has(t)) { seen.add(t); labels.push(t); }
      const s = String(r[seriesKey] ?? "value");
      if (!series[s]) series[s] = {};
      series[s][t] = Number(r[valueKey] ?? 0) || 0;
    });
    const datasets = Object.keys(series).map((name, i) => ({
      label: name,
      data: labels.map((t) => series[name][t] || 0),
      backgroundColor: this.colors[i % this.colors.length],
      borderColor: this.colors[i % this.colors.length],
      borderWidth: 0,
      fill: false,
    }));
    return {
      labels: labels.map((t) => t.replace("T", " ").slice(0, 16)),
      datasets,
    };
  },
};

window.SMFRange = {
  KEY: "smf-analytics-range",
  save() {
    const form = document.getElementById("smf-range-form");
    if (!form) return;
    const data = {
      days: form.days?.value || "4",
      date_from: form.date_from?.value || "",
      date_to: form.date_to?.value || "",
      q: form.q?.value || "",
    };
    try {
      localStorage.setItem(this.KEY, JSON.stringify(data));
    } catch (_e) { /* ignore */ }
    const btn = document.getElementById("smf-save-range");
    if (btn) {
      const prev = btn.textContent;
      btn.textContent = "Saved";
      setTimeout(() => { btn.textContent = prev; }, 1200);
    }
  },
  restoreIfEmpty() {
    const form = document.getElementById("smf-range-form");
    if (!form) return;
    const u = new URL(window.location.href);
    if (u.searchParams.has("days") || u.searchParams.has("date_from") || u.searchParams.has("date_to")) {
      return;
    }
    let saved;
    try {
      saved = JSON.parse(localStorage.getItem(this.KEY) || "null");
    } catch (_e) {
      saved = null;
    }
    if (!saved) return;
    if (saved.days && form.days) form.days.value = saved.days;
    if (saved.date_from && form.date_from) form.date_from.value = saved.date_from;
    if (saved.date_to && form.date_to) form.date_to.value = saved.date_to;
    if (saved.q && form.q) form.q.value = saved.q;
  },
};

window.SMFTips = {
  _el: null,
  _hideTimer: 0,

  ensure(host) {
    const parent = host || document.body;
    if (this._el && this._el.parentElement === parent) return this._el;
    if (!this._el) {
      const el = document.createElement("div");
      el.className = "smf-tip";
      el.setAttribute("role", "tooltip");
      el.hidden = true;
      this._el = el;
    }
    // Native <dialog> uses the top layer — tips on document.body stay behind it.
    parent.appendChild(this._el);
    return this._el;
  },

  tipText(node) {
    if (!node) return "";
    return (
      node.getAttribute("data-tip") ||
      node.getAttribute("title") ||
      ""
    ).trim();
  },

  show(anchor, text) {
    const tip = String(text || "").trim();
    if (!tip || !anchor) return;
    if (this._hideTimer) {
      clearTimeout(this._hideTimer);
      this._hideTimer = 0;
    }
    const dlg = anchor.closest && anchor.closest("dialog");
    const host = dlg && dlg.open ? dlg : document.body;
    const el = this.ensure(host);
    el.textContent = tip;
    el.hidden = false;
    const r = anchor.getBoundingClientRect();
    const pad = 10;
    const tw = el.offsetWidth || 220;
    const th = el.offsetHeight || 40;
    let left = r.left + r.width / 2 - tw / 2;
    let top = r.bottom + 8;
    if (left < pad) left = pad;
    if (left + tw > window.innerWidth - pad) left = window.innerWidth - pad - tw;
    if (top + th > window.innerHeight - pad) top = Math.max(pad, r.top - th - 8);
    el.style.left = Math.round(left) + "px";
    el.style.top = Math.round(top) + "px";
  },

  hide() {
    if (!this._el) return;
    this._el.hidden = true;
  },

  hideSoon() {
    if (this._hideTimer) clearTimeout(this._hideTimer);
    this._hideTimer = setTimeout(() => {
      this._hideTimer = 0;
      this.hide();
    }, 60);
  },

  bind(root) {
    const scope = root || document;
    scope.querySelectorAll("[data-tip]").forEach((node) => {
      if (node.dataset.smfTipBound === "1") return;
      node.dataset.smfTipBound = "1";
      if (node.hasAttribute("title") && node.getAttribute("data-tip")) {
        node.removeAttribute("title");
      }
      node.addEventListener("mouseenter", () => this.show(node, this.tipText(node)));
      node.addEventListener("mouseleave", () => this.hideSoon());
      node.addEventListener("focus", () => this.show(node, this.tipText(node)));
      node.addEventListener("blur", () => this.hideSoon());
    });
  },
};

window.SMFModalChrome = {
  sync() {
    const open = !!document.querySelector("dialog[open]");
    document.body.classList.toggle("smf-modal-open", open);
    if (!open && window.SMFTips) SMFTips.hide();
  },
};

window.SMFPageLoading = {
  _busy: false,
  STEP_KEY: "smf-load-more-step",
  PAGE_SIZES: [50, 100, 250, 500, 1000, 2500, 100000],

  show(title, msg) {
    const el = document.getElementById("smf-page-loading");
    const t = document.getElementById("smf-page-loading-title");
    const m = document.getElementById("smf-page-loading-msg");
    if (t) t.textContent = title || "Loading";
    if (m) m.textContent = msg || "Please wait…";
    if (el) el.hidden = false;
    document.body.classList.add("smf-page-loading-open");
    this._busy = true;
  },

  hide() {
    const el = document.getElementById("smf-page-loading");
    if (el) el.hidden = true;
    document.body.classList.remove("smf-page-loading-open");
    this._busy = false;
  },

  _normalizeStep(raw) {
    const n = parseInt(raw, 10);
    return this.PAGE_SIZES.includes(n) ? n : 50;
  },

  /** Restore Add-N combo on Top table Load more footers. */
  init() {
    let saved = null;
    try {
      saved = this._normalizeStep(sessionStorage.getItem(this.STEP_KEY) || "50");
    } catch (_e) {
      saved = 50;
    }
    document.querySelectorAll("select.load-more-step").forEach((sel) => {
      sel.value = String(saved);
      sel.addEventListener("change", () => {
        const v = this._normalizeStep(sel.value);
        try {
          sessionStorage.setItem(this.STEP_KEY, String(v));
        } catch (_e) { /* ignore */ }
        document.querySelectorAll("select.load-more-step").forEach((other) => {
          other.value = String(v);
        });
      });
    });
  },

  /** Intercept Load more (full page navigation) and show overlay first. */
  follow(anchor, msg) {
    if (!anchor || !anchor.href) return true;
    if (this._busy) return false;

    const wrap = anchor.closest(".load-more");
    const sel = wrap && wrap.querySelector("select.load-more-step");
    let href = anchor.href;
    if (sel) {
      const step = this._normalizeStep(sel.value);
      try {
        sessionStorage.setItem(this.STEP_KEY, String(step));
      } catch (_e) { /* ignore */ }
      const name = anchor.getAttribute("data-name") || "";
      const limit = parseInt(anchor.getAttribute("data-limit") || "0", 10);
      if (name && !Number.isNaN(limit)) {
        const u = new URL(anchor.href, window.location.href);
        u.searchParams.set("limit_" + name, String(limit + step));
        href = u.toString();
      }
    }

    this.show("Loading more", msg || "Fetching additional table rows…");
    // Soft-disable the control to prevent double clicks.
    anchor.classList.add("is-loading");
    anchor.setAttribute("aria-disabled", "true");
    // Navigate after paint so the overlay is visible.
    setTimeout(() => {
      window.location.href = href;
    }, 30);
    return false;
  },
};

window.SMFTables = {
  init() {
    document.querySelectorAll("table.data").forEach((table) => this.makeSortable(table));
    if (window.SMFTips) SMFTips.bind(document);
  },
  cellSortValue(td) {
    if (!td) return "";
    const raw = td.getAttribute("data-sort");
    if (raw !== null && raw !== undefined && String(raw).trim() !== "") return String(raw).trim();
    return (td.textContent || "").replace(/\s+/g, " ").trim();
  },
  compare(a, b) {
    const na = Number(String(a).replace(/,/g, "").replace(/[^0-9.\-eE]/g, ""));
    const nb = Number(String(b).replace(/,/g, "").replace(/[^0-9.\-eE]/g, ""));
    const aNum = String(a).trim() !== "" && !Number.isNaN(na) && /[0-9]/.test(String(a));
    const bNum = String(b).trim() !== "" && !Number.isNaN(nb) && /[0-9]/.test(String(b));
    if (aNum && bNum) return na - nb;
    return String(a).localeCompare(String(b), undefined, { numeric: true, sensitivity: "base" });
  },
  makeSortable(table) {
    const head = table.tHead && table.tHead.rows[0];
    const body = table.tBodies[0];
    if (!head || !body) return;
    Array.from(head.cells).forEach((th, colIdx) => {
      if (!th || th.classList.contains("no-sort")) return;
      if (!(th.textContent || "").trim()) return;
      th.classList.add("sortable");
      // Ensure every sortable header has a tip (catalog or generic fallback).
      if (!th.getAttribute("data-tip")) {
        const key = th.getAttribute("data-sort-key") || (th.textContent || "").trim();
        const tip =
          (window.SMFDetails && SMFDetails._fieldTip(key)) ||
          (window.SMFFullTable && SMFFullTable._fieldTip(key)) ||
          "";
        if (tip) th.setAttribute("data-tip", tip);
      }
      th.addEventListener("click", () => {
        const asc = th.classList.contains("sorted-asc") ? false : true;
        Array.from(head.cells).forEach((c) => c.classList.remove("sorted-asc", "sorted-desc"));
        th.classList.add(asc ? "sorted-asc" : "sorted-desc");
        const rows = Array.from(body.rows);
        rows.sort((ra, rb) => {
          const va = this.cellSortValue(ra.cells[colIdx]);
          const vb = this.cellSortValue(rb.cells[colIdx]);
          const cmp = this.compare(va, vb);
          return asc ? cmp : -cmp;
        });
        rows.forEach((r) => body.appendChild(r));
      });
    });
    if (window.SMFTips) SMFTips.bind(table);
  },
};

document.addEventListener("DOMContentLoaded", () => {
  if (window.SMFTheme) SMFTheme.init();
  SMFCharts.darkDefaults();
  SMFRange.restoreIfEmpty();
  SMFTables.init();
  if (window.SMFPageLoading) SMFPageLoading.init();
  const saveBtn = document.getElementById("smf-save-range");
  if (saveBtn) saveBtn.addEventListener("click", () => SMFRange.save());
  ["smf-details-modal", "smf-full-table-modal"].forEach((id) => {
    const dlg = document.getElementById(id);
    if (!dlg) return;
    dlg.addEventListener("close", () => {
      if (window.SMFModalChrome) SMFModalChrome.sync();
      if (window.SMFTips) SMFTips.hide();
    });
  });
});

window.SMFDetails = {
  _state: {
    sources: [],
    si: 0,
    ri: 0,
    days: "4",
    date_from: "",
    date_to: "",
    hour_from: "",
    hour_to: "",
    tables: "",
    filters: {},
    limit: 100,
    offset: 0,
  },

  _fieldTip(name) {
    const meta = window.SMFFieldMeta || {};
    const raw = String(name || "").trim();
    const key = raw.toLowerCase();
    if (!key) return "";
    return (
      meta[key] ||
      meta[key.replace(/ /g, "_")] ||
      meta[key.replace(/_/g, " ")] ||
      raw + " — SMF column"
    );
  },

  _windowLabel() {
    const s = this._state;
    const parts = [];
    if (s.date_from || s.date_to) {
      parts.push((s.date_from || "…") + " → " + (s.date_to || "…"));
    } else {
      parts.push("last " + (s.days || "4") + "d");
    }
    if (s.hour_from || s.hour_to) {
      parts.push("hour " + (s.hour_from || "…") + (s.hour_to ? " → " + s.hour_to : ""));
    }
    return parts.join(" · ");
  },

  open(btn) {
    const dlg = document.getElementById("smf-details-modal");
    const body = document.getElementById("smf-details-body");
    const title = document.getElementById("smf-details-title");
    const sub = document.getElementById("smf-details-sub");
    if (!dlg || !body) return;

    let filters = {};
    try {
      // Prefer getAttribute (decodes &quot;); dataset can be unreliable for JSON blobs.
      const raw = btn.getAttribute("data-filters") || btn.dataset.filters || "{}";
      filters = JSON.parse(raw) || {};
    } catch (_e) {
      filters = {};
    }
    // Drop empty filter values so we never over-constrain (e.g. blank sid).
    Object.keys(filters).forEach((k) => {
      if (filters[k] === null || filters[k] === undefined || String(filters[k]).trim() === "") {
        delete filters[k];
      }
    });
    const page = new URL(window.location.href);
    const tables = btn.getAttribute("data-tables") || "";
    const days =
      btn.getAttribute("data-days") ||
      page.searchParams.get("days") ||
      "4";
    this._state.tables = tables;
    this._state.days = days;
    this._state.date_from =
      btn.getAttribute("data-date-from") || page.searchParams.get("date_from") || "";
    this._state.date_to =
      btn.getAttribute("data-date-to") || page.searchParams.get("date_to") || "";
    this._state.hour_from =
      btn.getAttribute("data-hour-from") || page.searchParams.get("hour_from") || "";
    this._state.hour_to =
      btn.getAttribute("data-hour-to") || page.searchParams.get("hour_to") || "";
    this._state.filters = filters;
    this._state.limit = 100;
    this._state.offset = 0;
    this._state.si = 0;
    this._state.ri = 0;

    title.textContent = "Full details";
    sub.textContent = tables + " · loading…";
    body.innerHTML = '<div class="empty">Loading all SMF fields for matching rows…</div>';
    dlg.showModal();
    if (window.SMFModalChrome) SMFModalChrome.sync();
    this._load();
  },

  _load() {
    const body = document.getElementById("smf-details-body");
    const sub = document.getElementById("smf-details-sub");
    const params = new URLSearchParams({
      tables: this._state.tables,
      days: this._state.days,
      limit: String(this._state.limit),
      offset: String(this._state.offset),
    });
    ["date_from", "date_to", "hour_from", "hour_to"].forEach((k) => {
      const v = this._state[k];
      if (v) params.set(k, v);
    });
    Object.entries(this._state.filters || {}).forEach(([k, v]) => {
      if (v !== null && v !== undefined && String(v) !== "") params.set(k, String(v));
    });

    fetch("/api/details?" + params.toString())
      .then((r) => r.json())
      .then((data) => {
        if (data.error) {
          body.innerHTML = '<div class="error">' + this._esc(data.error) + "</div>";
          return;
        }
        this._state.sources = data.sources || [];
        this._state.limit = data.limit || this._state.limit;
        this._state.offset = data.offset || 0;
        this._state.days = data.days != null ? String(data.days) : this._state.days;
        this._state.date_from = data.date_from || this._state.date_from;
        this._state.date_to = data.date_to || this._state.date_to;
        this._state.hour_from = data.hour_from || this._state.hour_from;
        this._state.hour_to = data.hour_to || this._state.hour_to;
        this._state.appliedFilters = data.filters || {};
        const filt = Object.entries(this._state.appliedFilters)
          .map(([k, v]) => k + "=" + v)
          .join(", ");
        if (sub) sub.textContent = (filt || "no filters") + " · " + this._windowLabel();
        this._render();
      })
      .catch((err) => {
        if (body) body.innerHTML = '<div class="error">' + this._esc(String(err)) + "</div>";
      });
  },

  close() {
    const dlg = document.getElementById("smf-details-modal");
    if (dlg && dlg.open) dlg.close();
    if (window.SMFModalChrome) SMFModalChrome.sync();
  },

  _esc(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  },

  _isMatchKey(k) {
    const filters = this._state.appliedFilters || {};
    if (Object.prototype.hasOwnProperty.call(filters, k)) return true;
    // UI may send volser while the row shows volser_1 / volume_serial
    if (k === "volser_1" || k === "volume_serial") {
      return Object.prototype.hasOwnProperty.call(filters, "volser") ||
        Object.prototype.hasOwnProperty.call(filters, k);
    }
    return false;
  },

  setSource(i) {
    this._state.si = i;
    this._state.ri = 0;
    this._render();
  },

  setRow(delta) {
    const src = this._state.sources[this._state.si];
    if (!src || !src.rows || !src.rows.length) return;
    const n = src.rows.length;
    const next = this._state.ri + delta;
    if (next >= 0 && next < n) {
      this._state.ri = next;
      this._render();
      return;
    }
    const matched = Number(src.matched) || 0;
    const lim = this._state.limit;
    const off = this._state.offset;
    if (delta > 0 && off + n < matched) {
      this._state.offset = off + lim;
      this._state.ri = 0;
      this._load();
    } else if (delta < 0 && off > 0) {
      this._state.offset = Math.max(0, off - lim);
      this._state.ri = 0;
      this._load();
    }
  },

  _render() {
    const body = document.getElementById("smf-details-body");
    const title = document.getElementById("smf-details-title");
    if (!body) return;
    const sources = this._state.sources || [];
    if (!sources.length) {
      body.innerHTML = '<div class="empty">No matching rows.</div>';
      return;
    }

    const tabs = sources
      .map((s, i) => {
        const active = i === this._state.si ? " active" : "";
        const label = s.table + " · " + (s.matched || 0) + " match";
        return (
          '<button type="button" class="details-tab' +
          active +
          '" onclick="SMFDetails.setSource(' +
          i +
          ')">' +
          this._esc(label) +
          "</button>"
        );
      })
      .join("");

    const src = sources[this._state.si] || sources[0];
    if (src.error) {
      body.innerHTML =
        '<div class="details-tabs">' + tabs + '</div><div class="error">' + this._esc(src.error) + "</div>";
      return;
    }
    if (!src.rows || !src.rows.length) {
      body.innerHTML =
        '<div class="details-tabs">' +
        tabs +
        '</div><div class="empty">No rows in ' +
        this._esc(src.table) +
        " for these filters.</div>";
      return;
    }

    const matched = Number(src.matched) || src.rows.length;
    const absIndex = this._state.offset + this._state.ri + 1;
    const row = src.rows[this._state.ri] || src.rows[0];
    if (title) title.textContent = src.table + " · matching row " + absIndex + " / " + matched;

    const matchKeys = [];
    const filled = [];
    const empty = [];
    Object.keys(row).forEach((k) => {
      if (this._isMatchKey(k)) {
        matchKeys.push(k);
        return;
      }
      const v = row[k];
      const blank = v === null || v === undefined || String(v).trim() === "";
      (blank ? empty : filled).push(k);
    });

    const grid = (keys, cls) =>
      keys
        .map((k) => {
          const v = row[k];
          const shown = v === null || v === undefined || String(v).trim() === "" ? "—" : String(v);
          const tip = this._fieldTip(k);
          return (
            '<div class="details-field ' +
            cls +
            '"><dt' +
            (tip ? ' data-tip="' + this._esc(tip) + '"' : "") +
            ">" +
            this._esc(k) +
            '</dt><dd class="mono">' +
            this._esc(shown) +
            "</dd></div>"
          );
        })
        .join("");

    const nav =
      matched > 1
        ? '<div class="details-nav">' +
          '<button type="button" class="btn" onclick="SMFDetails.setRow(-1)">← Prev</button>' +
          "<span>Matching row <strong>" +
          absIndex +
          "</strong> of <strong>" +
          matched +
          "</strong> — all columns from " +
          this._esc(src.table) +
          "</span>" +
          '<button type="button" class="btn" onclick="SMFDetails.setRow(1)">Next →</button>' +
          "</div>"
        : '<p class="muted" style="margin:.5rem 0">1 matching row in ' +
          this._esc(src.table) +
          " — showing every column.</p>";

    const matchSection = matchKeys.length
      ? '<div class="details-section"><h3>Match fields (' +
        matchKeys.length +
        ')</h3><dl class="details-grid">' +
        grid(matchKeys, "is-match") +
        "</dl></div>"
      : "";

    body.innerHTML =
      '<div class="details-tabs">' +
      tabs +
      "</div>" +
      nav +
      matchSection +
      '<div class="details-section"><h3>Filled fields (' +
      filled.length +
      ')</h3><dl class="details-grid">' +
      grid(filled, "") +
      '</dl></div><div class="details-section"><h3>Empty fields (' +
      empty.length +
      ')</h3><dl class="details-grid muted-grid">' +
      grid(empty, "is-empty") +
      "</dl></div>";
    if (window.SMFTips) SMFTips.bind(body);
  },
};

window.SMFFullTable = {
  PAGE: 50,
  PAGE_SIZES: [50, 100, 250, 500, 1000, 2500, 100000],
  _reqId: 0,
  _abort: null,
  _state: {
    sources: [],
    si: 0,
    days: "4",
    date_from: "",
    date_to: "",
    hour_from: "",
    hour_to: "",
    tables: "",
    filters: {},
    limit: 50,
    pageSize: 50,
    loading: false,
  },

  _fieldTip(name) {
    const meta = window.SMFFieldMeta || {};
    const raw = String(name || "").trim();
    const key = raw.toLowerCase();
    if (!key) return "";
    return (
      meta[key] ||
      meta[key.replace(/ /g, "_")] ||
      meta[key.replace(/_/g, " ")] ||
      raw + " — SMF column"
    );
  },

  _windowLabel() {
    const s = this._state;
    const parts = [];
    if (s.date_from || s.date_to) {
      parts.push((s.date_from || "…") + " → " + (s.date_to || "…"));
    } else {
      parts.push("last " + (s.days || "4") + "d");
    }
    if (s.hour_from || s.hour_to) {
      parts.push("hour " + (s.hour_from || "…") + (s.hour_to ? " → " + s.hour_to : ""));
    }
    return parts.join(" · ");
  },

  _esc(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  },

  _parseFilters(btn) {
    let filters = {};
    try {
      const raw = btn.getAttribute("data-filters") || btn.dataset.filters || "{}";
      filters = JSON.parse(raw) || {};
    } catch (_e) {
      filters = {};
    }
    Object.keys(filters).forEach((k) => {
      if (filters[k] === null || filters[k] === undefined || String(filters[k]).trim() === "") {
        delete filters[k];
      }
    });
    return filters;
  },

  _normalizePageSize(raw) {
    const n = parseInt(raw, 10);
    return this.PAGE_SIZES.includes(n) ? n : this.PAGE;
  },

  setPageSize(raw) {
    this._state.pageSize = this._normalizePageSize(raw);
    this._state.limit = this._state.pageSize;
  },

  _pageSizeSelectHtml() {
    const cur = this._normalizePageSize(this._state.pageSize || this.PAGE);
    this._state.pageSize = cur;
    const opts = this.PAGE_SIZES.map((n) => {
      const label = n >= 1000 ? n.toLocaleString("en-US") : String(n);
      return (
        '<option value="' +
        n +
        '"' +
        (n === cur ? " selected" : "") +
        ">" +
        label +
        "</option>"
      );
    }).join("");
    return (
      '<label class="load-more-size">Add' +
      '<select id="smf-full-table-page-size" aria-label="Rows to add"' +
      ' onchange="SMFFullTable.setPageSize(this.value)">' +
      opts +
      "</select></label>"
    );
  },

  _showLoading(title, msg) {
    const el = document.getElementById("smf-full-table-loading");
    const t = document.getElementById("smf-full-table-loading-title");
    const m = document.getElementById("smf-full-table-loading-msg");
    if (t) t.textContent = title || "Loading";
    if (m) m.textContent = msg || "Fetching SMF rows…";
    if (el) el.hidden = false;
  },

  _hideLoading() {
    const el = document.getElementById("smf-full-table-loading");
    if (el) el.hidden = true;
  },

  open(btn) {
    const dlg = document.getElementById("smf-full-table-modal");
    const body = document.getElementById("smf-full-table-body");
    const title = document.getElementById("smf-full-table-title");
    const sub = document.getElementById("smf-full-table-sub");
    if (!dlg || !body) return;

    const page = new URL(window.location.href);
    const tables = btn.getAttribute("data-tables") || "";
    this._state.tables = tables;
    this._state.days =
      btn.getAttribute("data-days") || page.searchParams.get("days") || "4";
    this._state.date_from =
      btn.getAttribute("data-date-from") || page.searchParams.get("date_from") || "";
    this._state.date_to =
      btn.getAttribute("data-date-to") || page.searchParams.get("date_to") || "";
    this._state.hour_from =
      btn.getAttribute("data-hour-from") || page.searchParams.get("hour_from") || "";
    this._state.hour_to =
      btn.getAttribute("data-hour-to") || page.searchParams.get("hour_to") || "";
    this._state.filters = this._parseFilters(btn);
    // Always start at PAGE rows — do not reuse a previous Load-more pageSize (can be 100000).
    this._state.pageSize = this.PAGE;
    this._state.limit = this.PAGE;
    this._state.si = 0;
    this._state.sources = [];
    this._state.loading = false;
    this._reqId += 1;

    if (title) title.textContent = "Full table";
    if (sub) sub.textContent = tables + " · loading…";
    body.innerHTML = '<div class="empty">Loading full SMF rows for this time window…</div>';
    dlg.showModal();
    if (window.SMFModalChrome) SMFModalChrome.sync();
    this._fetch({ append: false, tables: tables, offset: 0 });
  },

  close() {
    // Invalidate in-flight fetches so late responses cannot re-render after close.
    this._reqId += 1;
    this._state.loading = false;
    if (this._abort) {
      try {
        this._abort.abort();
      } catch (_e) { /* ignore */ }
      this._abort = null;
    }
    this._hideLoading();
    if (window.SMFTips) SMFTips.hide();
    const dlg = document.getElementById("smf-full-table-modal");
    if (dlg && dlg.open) dlg.close();
    if (window.SMFModalChrome) SMFModalChrome.sync();
  },

  setSource(i) {
    this._state.si = i;
    this._render();
  },

  loadMore() {
    const src = this._state.sources[this._state.si];
    if (!src || this._state.loading) return;
    const matched = Number(src.matched) || 0;
    const have = (src.rows || []).length;
    if (have >= matched) return;
    const sel = document.getElementById("smf-full-table-page-size");
    if (sel) this.setPageSize(sel.value);
    this._state.limit = this._state.pageSize;
    this._fetch({ append: true, tables: src.table, offset: have });
  },

  _fetch({ append, tables, offset }) {
    const body = document.getElementById("smf-full-table-body");
    const sub = document.getElementById("smf-full-table-sub");
    const dlg = document.getElementById("smf-full-table-modal");
    const reqId = ++this._reqId;
    this._state.loading = true;
    const batch = this._normalizePageSize(this._state.limit || this._state.pageSize || this.PAGE);
    this._state.limit = batch;
    this._showLoading(
      append ? "Loading more" : "Loading full table",
      append
        ? "Fetching " + batch.toLocaleString("en-US") + " more SMF rows…"
        : "Fetching SMF rows for the selected time window…"
    );

    const params = new URLSearchParams({
      tables: tables,
      days: this._state.days,
      limit: String(batch),
      offset: String(offset),
    });
    ["date_from", "date_to", "hour_from", "hour_to"].forEach((k) => {
      const v = this._state[k];
      if (v) params.set(k, v);
    });
    Object.entries(this._state.filters || {}).forEach(([k, v]) => {
      if (v !== null && v !== undefined && String(v) !== "") params.set(k, String(v));
    });

    if (this._abort) {
      try {
        this._abort.abort();
      } catch (_e) { /* ignore */ }
    }
    this._abort = typeof AbortController !== "undefined" ? new AbortController() : null;
    const t0 = performance.now();
    const url = "/api/full-table?" + params.toString();

    fetch(url, this._abort ? { signal: this._abort.signal } : undefined)
      .then((r) => r.json().then((data) => ({ ok: r.ok, status: r.status, data })))
      .then((payload) => {
        const ms = Math.round(performance.now() - t0);
        if (reqId !== this._reqId) {
          return;
        }
        this._state.loading = false;
        this._hideLoading();
        const data = payload.data || {};
        const sources = data.sources || [];
        const rows0 = sources[0] && sources[0].rows ? sources[0].rows.length : 0;
        const cols0 = sources[0] && sources[0].rows && sources[0].rows[0] ? Object.keys(sources[0].rows[0]).length : 0;
        if (!dlg || !dlg.open) return;
        if (data.error) {
          if (body) body.innerHTML = '<div class="error">' + this._esc(data.error) + "</div>";
          return;
        }
        this._state.days = data.days != null ? String(data.days) : this._state.days;
        this._state.date_from = data.date_from || this._state.date_from;
        this._state.date_to = data.date_to || this._state.date_to;
        this._state.hour_from = data.hour_from || this._state.hour_from;
        this._state.hour_to = data.hour_to || this._state.hour_to;
        this._state.appliedFilters = data.filters || {};

        const incoming = sources;
        if (!append) {
          this._state.sources = incoming.map((s) => ({
            table: s.table,
            matched: s.matched,
            rows: s.rows || [],
            error: s.error || null,
          }));
          this._state.si = 0;
        } else {
          const got = incoming[0];
          const cur = this._state.sources[this._state.si];
          if (got && cur && got.table === cur.table) {
            cur.matched = got.matched;
            cur.error = got.error || null;
            cur.rows = (cur.rows || []).concat(got.rows || []);
          }
        }

        const filt = Object.entries(this._state.appliedFilters || {})
          .map(([k, v]) => k + "=" + v)
          .join(", ");
        if (sub) {
          sub.textContent =
            (filt ? filt + " · " : "time window · ") + this._windowLabel();
        }
        this._render();
      })
      .catch((err) => {
        if (reqId !== this._reqId) return;
        this._state.loading = false;
        this._hideLoading();
        if (err && err.name === "AbortError") return;
        if (!dlg || !dlg.open) return;
        if (body) body.innerHTML = '<div class="error">' + this._esc(String(err)) + "</div>";
      });
  },

  _render() {
    const body = document.getElementById("smf-full-table-body");
    const title = document.getElementById("smf-full-table-title");
    const dlg = document.getElementById("smf-full-table-modal");
    if (!body || !dlg || !dlg.open) return;
    const t0 = performance.now();
    const sources = this._state.sources || [];
    if (!sources.length) {
      body.innerHTML = '<div class="empty">No matching rows.</div>';
      return;
    }

    const tabs = sources
      .map((s, i) => {
        const active = i === this._state.si ? " active" : "";
        const label = s.table + " · " + (s.matched || 0);
        return (
          '<button type="button" class="details-tab' +
          active +
          '" onclick="SMFFullTable.setSource(' +
          i +
          ')">' +
          this._esc(label) +
          "</button>"
        );
      })
      .join("");

    const src = sources[this._state.si] || sources[0];
    if (src.error) {
      body.innerHTML =
        '<div class="details-tabs">' + tabs + '</div><div class="error">' + this._esc(src.error) + "</div>";
      return;
    }
    if (!src.rows || !src.rows.length) {
      body.innerHTML =
        '<div class="details-tabs">' +
        tabs +
        '</div><div class="empty">No rows in ' +
        this._esc(src.table) +
        " for this window.</div>";
      return;
    }

    const matched = Number(src.matched) || src.rows.length;
    const shown = src.rows.length;
    if (title) title.textContent = src.table + " · " + shown + " / " + matched;

    const cols = Object.keys(src.rows[0] || {});
    const head = cols
      .map((c) => {
        const tip = this._fieldTip(c);
        return (
          "<th" +
          (tip ? ' data-tip="' + this._esc(tip) + '"' : "") +
          ' data-sort-key="' +
          this._esc(String(c).toLowerCase()) +
          '">' +
          this._esc(c) +
          "</th>"
        );
      })
      .join("");
    const rowsHtml = src.rows
      .map((row) => {
        const cells = cols
          .map((c) => {
            const v = row[c];
            const blank = v === null || v === undefined || String(v).trim() === "";
            const shownCell = blank ? "—" : String(v);
            return (
              '<td class="mono"' +
              (blank ? ' data-sort=""' : ' data-sort="' + this._esc(shownCell) + '"') +
              ">" +
              this._esc(shownCell) +
              "</td>"
            );
          })
          .join("");
        return "<tr>" + cells + "</tr>";
      })
      .join("");

    const more =
      shown < matched
        ? this._pageSizeSelectHtml() +
          '<button type="button" class="btn btn-load-more" onclick="SMFFullTable.loadMore()"' +
          (this._state.loading ? " disabled" : "") +
          ">Load more</button>" +
          '<span class="muted">Showing ' +
          shown +
          " · " +
          (matched - shown) +
          " more available</span>"
        : '<span class="muted">Showing all ' + shown + " matching rows</span>";

    body.innerHTML =
      '<div class="full-table-panel"><div class="details-tabs">' +
      tabs +
      '</div><div class="full-table-scroll"><table class="data" id="smf-full-table-grid"><thead><tr>' +
      head +
      "</tr></thead><tbody>" +
      rowsHtml +
      '</tbody></table></div><div class="full-table-footer">' +
      more +
      "</div></div>";

    const table = document.getElementById("smf-full-table-grid");
    if (table && window.SMFTables) SMFTables.makeSortable(table);
    else if (table && window.SMFTips) SMFTips.bind(table);
  },
};

document.addEventListener("keydown", (e) => {
  if (e.key !== "Escape") return;
  SMFDetails.close();
  SMFFullTable.close();
});
