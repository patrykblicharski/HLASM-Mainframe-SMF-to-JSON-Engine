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
  stackedBar(canvasId, labels, datasets) {
    const el = this._el(canvasId);
    if (!el) return;
    if (!labels.length || !datasets.length) {
      this._empty(canvasId);
      return;
    }
    new Chart(el, {
      type: "bar",
      data: { labels, datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: "bottom" } },
        scales: {
          x: { stacked: true, ticks: { maxRotation: 0, autoSkip: true, maxTicksLimit: 12 } },
          y: { stacked: true, beginAtZero: true },
        },
      },
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
