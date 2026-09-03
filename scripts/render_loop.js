// Render a deterministic animation page to frames, then encode with prep_loop.sh.
// The page must expose window.setT(ms) that positions its animation at time ms.
// Usage: NODE_PATH=<npx cache> node scripts/render_loop.js <url> <out-dir> <seconds> [fps] [width] [height]
const puppeteer = require('puppeteer-core');
const fs = require('fs');
(async () => {
  const [url, out, seconds, fps = 24, width = 1400, height = 933, at] = process.argv.slice(2);
  fs.mkdirSync(out, { recursive: true });
  const browser = await puppeteer.launch({ executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless: 'new', args: ['--no-sandbox', '--font-render-hinting=none'] });
  const page = await browser.newPage();
  await page.setViewport({ width: Number(width), height: Number(height), deviceScaleFactor: 1 });
  await page.goto(url, { waitUntil: 'networkidle0' });
  await page.evaluate(() => document.fonts.ready);
  if (at !== undefined) {  // one frame at a given ms, for checking a page
    await page.evaluate((ms) => window.setT(ms), Number(at));
    await page.screenshot({ path: `${out}/at-${at}.png` }); console.log('frame at', at); await browser.close(); return;
  }
  const n = Math.round(Number(seconds) * Number(fps));
  for (let i = 0; i < n; i++) {
    await page.evaluate((ms) => window.setT(ms), Math.round(i * 1000 / Number(fps)));
    await page.screenshot({ path: `${out}/f${String(i).padStart(4, '0')}.png` });
  }
  console.log(`${n} frames to ${out}`);
  await browser.close();
})().catch(e => { console.error('ERR', e.message); process.exit(1); });
