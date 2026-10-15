// Print a local HTML file to an A4 PDF with a headless Chromium-family browser (Brave or Chrome)
// through the DevTools protocol. No npm dependencies: uses Node's built-in fetch and WebSocket.
// Usage: node tools/html2pdf.mjs <browserBinary> <htmlFileAbsolutePath> <outPdfPath> [pageRanges] [footerTitle]
import { spawn } from 'node:child_process';
import { writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';

const [browser, htmlPath, outPdf, pageRanges, footerTitle] = process.argv.slice(2);
if (!browser || !htmlPath || !outPdf) {
  console.error('usage: node tools/html2pdf.mjs <browserBinary> <htmlFileAbsolutePath> <outPdfPath> [pageRanges] [footerTitle]');
  process.exit(1);
}
const port = 9800 + Math.floor(Math.random() * 500);
const profile = mkdtempSync(path.join(tmpdir(), 'html2pdf-profile-'));
const proc = spawn(browser, [
  '--headless=new', `--remote-debugging-port=${port}`, '--use-mock-keychain', '--password-store=basic',
  `--user-data-dir=${profile}`, '--no-first-run', '--no-default-browser-check', '--disable-gpu', 'about:blank',
], { stdio: 'ignore' });
const killer = setTimeout(() => { proc.kill('SIGKILL'); console.error('timeout'); process.exit(2); }, 120000);
killer.unref();
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function getTargets() {
  for (let i = 0; i < 60; i++) {
    try { const r = await fetch(`http://127.0.0.1:${port}/json`); return await r.json(); } catch { await sleep(250); }
  }
  throw new Error('browser did not start');
}
const targets = await getTargets();
const page = targets.find((t) => t.type === 'page');
const ws = new WebSocket(page.webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
let id = 0;
const pending = new Map();
ws.onmessage = (ev) => { const m = JSON.parse(ev.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } };
const send = (method, params = {}) => new Promise((res) => { const i = ++id; pending.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
await send('Page.enable');
await send('Page.navigate', { url: 'file://' + htmlPath });
await sleep(2500);
const title = footerTitle || path.basename(htmlPath, '.html');
// Page geometry in inches; the defaults are A4 portrait for documents. A slide deck sets
// PDF_PAPER_WIDTH=13.33 PDF_PAPER_HEIGHT=7.5 PDF_MARGIN=0 PDF_FOOTER=off.
const num = (name, fallback) => (process.env[name] ? Number(process.env[name]) : fallback);
const margin = num('PDF_MARGIN', null);
const pdf = await send('Page.printToPDF', {
  printBackground: true,
  preferCSSPageSize: true,
  paperWidth: num('PDF_PAPER_WIDTH', 8.27), paperHeight: num('PDF_PAPER_HEIGHT', 11.69),
  marginTop: margin ?? 0.55, marginBottom: margin ?? 0.55, marginLeft: margin ?? 0.5, marginRight: margin ?? 0.5,
  ...(pageRanges ? { pageRanges } : {}),
  displayHeaderFooter: process.env.PDF_FOOTER !== 'off',
  headerTemplate: '<div></div>',
  footerTemplate: `<div style="font-size:8px; width:100%; text-align:center; color:#555; font-family: Helvetica, Arial, sans-serif;">${title}, page <span class="pageNumber"></span> of <span class="totalPages"></span></div>`,
});
if (!pdf.result || !pdf.result.data) { console.error('printToPDF failed', JSON.stringify(pdf).slice(0, 300)); proc.kill('SIGKILL'); process.exit(3); }
writeFileSync(outPdf, Buffer.from(pdf.result.data, 'base64'));
console.log('wrote', outPdf);
ws.close();
proc.kill('SIGKILL');
process.exit(0);
