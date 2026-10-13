// Research helper: open a URL in a headless Chromium-family browser, scroll, and save the rendered text
// (including shadow DOM and same-origin iframes), a form-field inventory, console lines and a screenshot.
// Usage: node tools/page-dump.mjs <browserBinary> <url> <outPrefix> [waitMs]
import { spawn } from 'node:child_process';
import { writeFileSync, mkdtempSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';

const [browser, url, outPrefix, waitMsArg] = process.argv.slice(2);
if (!browser || !url || !outPrefix) {
  console.error('usage: node tools/page-dump.mjs <browserBinary> <url> <outPrefix> [waitMs]');
  process.exit(1);
}
const waitMs = Number(waitMsArg || 7000);
const port = 9300 + Math.floor(Math.random() * 500);
const profile = mkdtempSync(path.join(tmpdir(), 'page-dump-profile-'));
const proc = spawn(browser, [
  '--headless=new', `--remote-debugging-port=${port}`, '--use-mock-keychain', '--password-store=basic',
  `--user-data-dir=${profile}`, '--no-first-run', '--no-default-browser-check', '--disable-gpu',
  '--window-size=1280,2400', 'about:blank',
], { stdio: 'ignore' });
const killer = setTimeout(() => { proc.kill('SIGKILL'); console.error('timeout'); process.exit(2); }, 90000);
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
const consoleLines = [];
ws.onmessage = (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
  if (m.method === 'Runtime.consoleAPICalled') consoleLines.push(m.params.args.map((a) => a.value ?? a.description ?? '').join(' '));
  if (m.method === 'Runtime.exceptionThrown') consoleLines.push('EXC ' + (m.params.exceptionDetails.text || ''));
};
const send = (method, params = {}) => new Promise((res) => { const i = ++id; pending.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
await send('Page.enable');
await send('Runtime.enable');
await send('Page.navigate', { url });
await sleep(waitMs);
const evalText = async (expression) => {
  const r = await send('Runtime.evaluate', { expression, returnByValue: true });
  return r.result?.result?.value ?? '';
};
for (let i = 0; i < 6; i++) {
  await evalText(`window.scrollTo(0, document.body.scrollHeight * ${(i + 1) / 6})`);
  await sleep(1200);
}
await evalText('window.scrollTo(0, 0)');
await sleep(800);
const text = await evalText('document.body ? document.body.innerText : ""');
const deep = await evalText(`(() => {
  const out = [];
  const walk = (root) => {
    if (!root) return;
    const all = root.querySelectorAll ? root.querySelectorAll('*') : [];
    for (const el of all) {
      if (el.shadowRoot) { out.push(el.shadowRoot.textContent || ''); walk(el.shadowRoot); }
      if (el.tagName === 'IFRAME') { try { const d = el.contentDocument; if (d && d.body) { out.push(d.body.innerText || ''); walk(d); } } catch (e) {} }
    }
  };
  walk(document);
  return out.join('\\n');
})()`);
const forms = await evalText(`Array.from(document.querySelectorAll('input,select,textarea,button,label,[role=radio],[role=checkbox]')).map(e => [e.tagName, e.type||'', e.name||e.id||'', e.placeholder||'', ((e.innerText||e.value||'')+'').replace(/\\s+/g,' ').slice(0,120)].join(' | ')).join('\\n')`);
const title = await evalText('document.title');
writeFileSync(`${outPrefix}.txt`, `TITLE: ${title}\nURL: ${url}\n\n${text}`);
writeFileSync(`${outPrefix}.deep.txt`, deep);
writeFileSync(`${outPrefix}.form.txt`, forms);
writeFileSync(`${outPrefix}.console.txt`, consoleLines.join('\n'));
try {
  const shot = await send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
  if (shot.result?.data) writeFileSync(`${outPrefix}.png`, Buffer.from(shot.result.data, 'base64'));
  else console.error('screenshot unavailable:', JSON.stringify(shot).slice(0, 200));
} catch (err) {
  console.error('screenshot failed:', err.message);
}
console.log(`saved ${outPrefix}.txt (${text.length} chars), .deep.txt (${deep.length} chars), .form.txt, .png; title="${title}"`);
ws.close();
proc.kill('SIGKILL');
process.exit(0);
