// Drive one demo call through the harness page in headless Chrome and log its events.
// Usage: NODE_PATH=<npx cache> node scripts/demo-call/run_call.js <access_token> <log.json>
const puppeteer = require('puppeteer-core');
const fs = require('fs');
(async () => {
  const [token, out] = process.argv.slice(2);
  const lines = JSON.parse(fs.readFileSync('scripts/demo-call/lines.json', 'utf8'));
  const cfg = { token, lines: Object.fromEntries(Object.keys(lines).map(k => [k, '/scripts/demo-call/lines/' + k + '.wav'])), order: ['job', 'scope', 'when', 'name', 'phone', 'close'] };
  const browser = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: 'new',
    args: ['--no-sandbox', '--autoplay-policy=no-user-gesture-required', '--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream'] });
  const page = await browser.newPage();
  const events = [];
  page.on('console', (msg) => { const t = msg.text(); if (t.startsWith('HARNESS ')) { try { events.push(JSON.parse(t.slice(8))); } catch (e) { events.push({ raw: t }); } console.log(t); } });
  page.on('pageerror', (e) => console.log('PAGEERROR', e.message));
  await page.evaluateOnNewDocument((c) => { window.CALL_CONFIG = c; }, cfg);
  await page.goto('http://127.0.0.1:8765/scripts/demo-call/harness.html', { waitUntil: 'load' });
  const start = Date.now();
  while (Date.now() - start < 125000) {
    const done = await page.evaluate(() => window.__done === true).catch(() => false);
    if (done) break;
    await new Promise(r => setTimeout(r, 1000));
  }
  await new Promise(r => setTimeout(r, 1500));
  fs.writeFileSync(out, JSON.stringify(events, null, 1));
  console.log('events written', events.length);
  await browser.close();
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
