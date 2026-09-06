/* Shared Chart.js helpers for SMF Analytics */
window.SMFCharts = {
  colors: ["#3db8a8", "#5b8def", "#9b7bff", "#f0a05a", "#4fc3f7", "#e35d6a", "#4ec98a", "#e6a23c"],
  darkDefaults() {
    if (!window.Chart) return;
    Chart.defaults.color = "#93a0b8";
    Chart.defaults.borderColor = "rgba(36,49,73,.9)";
    Chart.defaults.font.family = "'Segoe UI', system-ui, sans-serif";
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
  stackedBar(canvasId, labels, datasets, extraOptions) {
    const el = this._el(canvasId);
    if (!el) return;
    if (!labels.length || !datasets.length) {
      this._empty(canvasId);
      return;
    }
    const options = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: "bottom" } },
      scales: {
        x: { stacked: true, ticks: { maxRotation: 0, autoSkip: true, maxTicksLimit: 12 } },
        y: { stacked: true, beginAtZero: true },
      },
    };
    if (extraOptions) Object.assign(options, extraOptions);
    new Chart(el, {
      type: "bar",
      data: { labels, datasets },
      options,
    });
  },
  line(canvasId, labels, datasets) {
    const el = this._el(canvasId);
    if (!el) return;
    if (!labels.length || !datasets.length) {
      this._empty(canvasId);
      return;
    }
    new Chart(el, {
      type: "line",
      data: { labels, datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: "bottom" } },
        scales: { y: { beginAtZero: true } },
        elements: { line: { tension: 0.25, borderWidth: 2 }, point: { radius: 0 } },
      },
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
        plugins: { legend: { position: "right" } },
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
      backgroundColor: this.colors[i % this.colors.length] + "cc",
      borderColor: this.colors[i % this.colors.length],
      fill: false,
    }));
    return {
      labels: labels.map((t) => t.replace("T", " ").slice(0, 16)),
      datasets,
    };
  },
};

document.addEventListener("DOMContentLoaded", () => {
  SMFCharts.darkDefaults();
});

window.SMFDetails = {
  _state: { sources: [], si: 0, ri: 0, days: "4", tables: "", filters: {}, limit: 100, offset: 0 },

  open(btn) {
    const dlg = document.getElementById("smf-details-modal");
    const body = document.getElementById("smf-details-body");
    const title = document.getElementById("smf-details-title");
    const sub = document.getElementById("smf-details-sub");
    if (!dlg || !body) return;

    let filters = {};
    try {
      filters = JSON.parse(btn.getAttribute("data-filters") || "{}") || {};
    } catch (_e) {
      filters = {};
    }
    const tables = btn.getAttribute("data-tables") || "";
    const days = btn.getAttribute("data-days") || "4";
    this._state.tables = tables;
    this._state.days = days;
    this._state.filters = filters;
    this._state.limit = 100;
    this._state.offset = 0;
    this._state.si = 0;
    this._state.ri = 0;

    title.textContent = "Full details";
    sub.textContent = tables + " · loading…";
    body.innerHTML = '<div class="empty">Loading all SMF fields for matching rows…</div>';
    dlg.showModal();
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
        this._state.appliedFilters = data.filters || {};
        const filt = Object.entries(this._state.appliedFilters)
          .map(([k, v]) => k + "=" + v)
          .join(", ");
        if (sub) sub.textContent = (filt || "no filters") + " · last " + this._state.days + "d";
        this._render();
      })
      .catch((err) => {
        if (body) body.innerHTML = '<div class="error">' + this._esc(String(err)) + "</div>";
      });
  },

  close() {
    const dlg = document.getElementById("smf-details-modal");
    if (dlg && dlg.open) dlg.close();
  },

  _esc(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
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
    // Page to next/prev chunk of matching rows
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

    const filled = [];
    const empty = [];
    Object.keys(row).forEach((k) => {
      const v = row[k];
      const blank = v === null || v === undefined || String(v).trim() === "";
      (blank ? empty : filled).push(k);
    });

    const grid = (keys, cls) =>
      keys
        .map((k) => {
          const v = row[k];
          const shown = v === null || v === undefined || String(v).trim() === "" ? "—" : String(v);
          return (
            '<div class="details-field ' +
            cls +
            '"><dt>' +
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

    body.innerHTML =
      '<div class="details-tabs">' +
      tabs +
      "</div>" +
      nav +
      '<div class="details-section"><h3>Filled fields (' +
      filled.length +
      ')</h3><dl class="details-grid">' +
      grid(filled, "") +
      '</dl></div><div class="details-section"><h3>Empty fields (' +
      empty.length +
      ')</h3><dl class="details-grid muted-grid">' +
      grid(empty, "is-empty") +
      "</dl></div>";
  },
};

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") SMFDetails.close();
});
