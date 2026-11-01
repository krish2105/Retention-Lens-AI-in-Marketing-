// Print report.html to submissions/RetentionLens_Project_Report.pdf. Run: NODE_PATH=<dir with playwright> node design/report/print.js <repoRoot>
const path = require('path');
const { chromium } = require('playwright');
(async () => {
  const root = process.argv[2];
  // Installed Google Chrome by default (Playwright's own Chromium download does not work on the owner's Mac); PW_CHANNEL= to override.
  const browser = await chromium.launch({ channel: process.env.PW_CHANNEL ?? 'chrome' });
  const page = await browser.newPage();
  await page.goto('file://' + path.join(root, 'design/report/report.html'), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({
    path: path.join(root, 'submissions/RetentionLens_Project_Report.pdf'), format: 'A4', printBackground: true,
    displayHeaderFooter: true, headerTemplate: '<span></span>',
    footerTemplate: '<div style="width:100%;font-size:8px;color:#4e5470;padding:0 16mm;display:flex;justify-content:space-between;font-family:sans-serif"><span>RetentionLens · MAIB AI 208 · Krishna Mathur</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>',
    margin: { top: '16mm', bottom: '18mm', left: '16mm', right: '16mm' },
  });
  await browser.close();
  console.log('printed PDF');
})();
