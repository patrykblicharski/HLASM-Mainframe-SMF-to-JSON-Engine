import { chromium } from 'playwright-core';
import fs from 'fs';
import path from 'path';

const BASE = 'https://www.ibm.com/docs/en/SSLTBW_3.2.0/com.ibm.zos.v3r2.ieag200/';
const ROOT = BASE + 'rec42.htm';
const OUT = process.argv[2] || '/tmp/ibm-smf/smf42-classic';
fs.mkdirSync(OUT, { recursive: true });

function absUrl(href, current) {
  try { return new URL(href, current).href; } catch { return null; }
}
function fileOf(url) {
  try { return new URL(url).pathname.split('/').pop(); } catch { return ''; }
}
function inPackage(url) {
  return url.includes('/com.ibm.zos.v3r2.ieag200/');
}

const browser = await chromium.launch({
  executablePath: '/usr/local/bin/google-chrome',
  headless: true,
  args: ['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu'],
});
const page = await browser.newPage({
  userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  viewport: { width: 1400, height: 1200 },
});
page.setDefaultTimeout(90000);

const queue = [ROOT];
const seen = new Set();
const pages = [];

while (queue.length) {
  const url = queue.shift();
  const file = fileOf(url);
  if (!file || seen.has(file)) continue;
  seen.add(file);
  console.error(`FETCH [${seen.size}] ${file}`);
  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 90000 });
    await page.waitForSelector('h1, .ibmdocs-topic-content, .nested0, article', { timeout: 60000 });
    await page.waitForTimeout(2500);
  } catch (e) {
    console.error('ERR', file, e.message);
    continue;
  }

  const data = await page.evaluate(() => {
    const main =
      document.querySelector('.ibmdocs-topic-content') ||
      document.querySelector('.text-content') ||
      document.querySelector('article') ||
      document.querySelector('[role="main"]');
    const title = document.querySelector('h1')?.innerText?.trim() || document.title;
    const text = main?.innerText || '';
    const links = [...document.querySelectorAll('a')].map(a => ({
      href: a.getAttribute('href') || '',
      text: (a.textContent || '').replace(/\s+/g, ' ').trim(),
    }));
    const tables = [...(main?.querySelectorAll('table') || [])].map(table => {
      const norm = (s) => (s || '').replace(/\s+/g, ' ').trim();
      return {
        caption: norm(table.querySelector('caption')?.innerText || ''),
        rows: [...table.querySelectorAll('tr')].map(tr =>
          [...tr.querySelectorAll('th,td')].map(c => norm(c.innerText))
        ),
      };
    });
    return { title, text, links, tables, finalUrl: location.href };
  });

  const fieldTables = [];
  for (const t of data.tables) {
    const rows = t.rows || [];
    if (!rows.length) continue;
    const header = rows[0] || [];
    const looks = header.some(h => /offset|name|length|format|description/i.test(h));
    const fields = [];
    for (const cells of rows.slice(looks ? 1 : 0)) {
      if (cells.length < 5) continue;
      let offDec, offHex, name, length, format, desc;
      if (cells.length >= 6) {
        [offDec, offHex, name, length, format] = cells;
        desc = cells.slice(5).join(' ');
      } else {
        offDec = cells[0]; offHex = ''; name = cells[1]; length = cells[2]; format = cells[3]; desc = cells.slice(4).join(' ');
      }
      const nameTok = (name || '').split(/\s+/)[0];
      if (!nameTok || /^name$/i.test(nameTok) || /^(bit|meaning|offsets?)$/i.test(nameTok)) continue;
      // Prefer SMF/IBM field-looking names but keep others in section tables
      fields.push({
        offset_dec: String(offDec || ''),
        offset_hex: String(offHex || ''),
        name: nameTok,
        name_raw: name,
        length: String(length || ''),
        format: String(format || ''),
        description: desc || '',
      });
    }
    if (fields.length) fieldTables.push({ caption: t.caption, headers: header, fields });
  }

  const childLinks = [];
  for (const l of data.links) {
    const abs = absUrl(l.href, url);
    if (!abs || !inPackage(abs)) continue;
    const f = fileOf(abs);
    if (!f || !/\.htm(l)?$/i.test(f) || seen.has(f)) continue;
    // stay in type 42 neighborhood: rec42, subtype, mapping, environment, smf42, r42
    if (!/(rec42|subtype|mapping|environment|smf42|r42sub|iea3g2_)/i.test(f + l.text)) continue;
    // exclude other record types loosely
    if (/rec(?!42)\d+\.htm/i.test(f)) continue;
    if (!queue.includes(abs) && !seen.has(f)) {
      queue.push(abs);
      childLinks.push({ file: f, text: l.text, href: abs });
    }
  }

  const rec = {
    file,
    url: data.finalUrl || url,
    title: data.title,
    text_excerpt: data.text.slice(0, 2000),
    n_raw_tables: data.tables.length,
    field_tables: fieldTables,
    children: childLinks,
  };
  pages.push(rec);
  const safe = file.replace(/[^\w.\-]+/g, '_');
  fs.writeFileSync(path.join(OUT, safe + '.json'), JSON.stringify(rec, null, 2));
  console.error(`  title=${data.title.slice(0,70)} tables=${fieldTables.length} fields=${fieldTables.reduce((a,t)=>a+t.fields.length,0)} queue=${queue.length}`);
}

const summary = {
  source: ROOT,
  scraped_at: new Date().toISOString(),
  pages: pages.length,
  total_fields: pages.reduce((a,p)=>a+p.field_tables.reduce((b,t)=>b+t.fields.length,0),0),
  pages_with_fields: pages.filter(p => p.field_tables.some(t => t.fields.length)).map(p => ({
    file: p.file,
    title: p.title,
    fields: p.field_tables.reduce((b,t)=>b+t.fields.length,0),
  })),
  all: pages.map(p => ({
    file: p.file,
    title: p.title,
    fields: p.field_tables.reduce((b,t)=>b+t.fields.length,0),
  })),
};
fs.writeFileSync(path.join(OUT, '_summary.json'), JSON.stringify(summary, null, 2));
fs.writeFileSync(path.join(OUT, '_all_pages.json'), JSON.stringify(pages, null, 2));
console.log(JSON.stringify(summary, null, 2));
await browser.close();
