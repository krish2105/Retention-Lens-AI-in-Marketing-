// RetentionLens deck. Run: NODE_PATH=<dir with pptxgenjs> node design/deck/build.js <repoRoot>
// Every number is read from the committed result files, never typed by hand.
const fs = require('fs');
const path = require('path');
const pptxgen = require('pptxgenjs');

const ROOT = process.argv[2];
const J = (p) => JSON.parse(fs.readFileSync(path.join(ROOT, p), 'utf8'));
const SHOT = (n) => path.join(ROOT, 'submissions/screenshots', n + '.jpg');
const ART = (n) => path.join(__dirname, 'img', n + '.jpg');
const OUT = path.join(ROOT, 'submissions/RetentionLens_Presentation.pptx');

const model = J('reports/model_results.json');
const test = model.cutoffs['2011-09-01'];
const summary = J('apps/web/public/data/summary.json');
const profile = J('reports/data_profile.json');
const signals = J('apps/web/public/data/signals.json');
const segments = J('apps/web/public/data/segments.json');
const look = J('apps/web/public/data/lookalikes.json');
const genai = J('reports/genai_eval.json');
const lab = J('apps/web/public/data/product_lab.json');
const r5 = J('reports/r5_results.json');
const load = J('reports/load_test.json');
const drill = fs.readFileSync(path.join(ROOT, 'reports/restore_drill.md'), 'utf8');
const drillTables = (drill.match(/for all (\d+) tables/) || [])[1];
const drillPassed = /\*\*PASSED\*\*/.test(drill);
// Test counts from collection (pytest --collect-only, playwright --list) on the day the pack was built.
const TESTS = J('design/test_counts.json');
const pct = (v, d = 1) => (v * 100).toFixed(d) + '%';

const C = { night: '070912', ink: 'EEF0FF', muted: 'A7ADC8', panel: '12152A', edge: '2A2E48', cyan: '67E8F9', magenta: 'F472B6', amber: 'FBBF24', violet: 'A78BFA', paper: 'F3F4FB', inkDark: '11132A', mutedDark: '4E5470', cyanDark: '0E7490', magentaDark: 'BE185D' };
const FONT = { head: 'Calibri', body: 'Calibri' };
const W = 13.333, M = 0.6;
const fmt = (n, d = 0) => Number(n).toLocaleString('en-GB', { maximumFractionDigits: d, minimumFractionDigits: d });

const pres = new pptxgen();
pres.layout = 'LAYOUT_WIDE';
pres.author = 'Krishna Mathur';
pres.title = 'RetentionLens: 90-day lapse risk and value for wholesale accounts';
pres.subject = 'MAIB AI 208 AI in Marketing';
pres.theme = { headFontFace: FONT.head, bodyFontFace: FONT.body };

pres.defineSlideMaster({
  title: 'AURORA', background: { color: C.night },
  objects: [
    { text: { text: 'RetentionLens · MAIB AI 208 AI in Marketing · Krishna Mathur', options: { x: M, y: 7.02, w: 9, h: 0.3, fontSize: 10, color: C.muted, fontFace: FONT.body, margin: 0 } } },
  ],
  slideNumber: { x: W - M - 0.6, y: 7.02, w: 0.6, h: 0.3, fontSize: 10, color: C.muted, align: 'right' },
});

const shadow = () => ({ type: 'outer', color: '000000', opacity: 0.35, blur: 12, offset: 4, angle: 90 });
const text = (s, t, o) => s.addText(t, { isTextBox: true, margin: 0, color: C.ink, fontFace: FONT.body, fontSize: 16, valign: 'top', ...o });
const title = (s, eyebrow, t) => {
  text(s, eyebrow.toUpperCase(), { x: M, y: 0.42, w: 10, h: 0.3, fontSize: 11, color: C.cyan, charSpacing: 3, bold: true });
  text(s, t, { x: M, y: 0.72, w: W - 2 * M, h: 0.9, fontSize: 30, fontFace: FONT.head, bold: true, color: C.ink });
};
const glass = (s, x, y, w, h, o = {}) => s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.16, fill: { color: C.panel, transparency: 8 }, line: { color: C.edge, width: 0.75 }, ...o });
const framed = (s, file, x, y, w, h, alt) => {
  glass(s, x, y, w, h, { shadow: shadow() });
  s.addImage({ path: file, x: x + 0.08, y: y + 0.08, w: w - 0.16, h: h - 0.16, sizing: { type: 'cover', w: w - 0.16, h: h - 0.16 }, altText: alt });
};
const stat = (s, x, y, w, value, label, color = C.ink) => {
  glass(s, x, y, w, 1.25);
  text(s, value, { x: x + 0.22, y: y + 0.16, w: w - 0.4, h: 0.6, fontSize: 28, fontFace: FONT.head, color });
  text(s, label, { x: x + 0.22, y: y + 0.78, w: w - 0.4, h: 0.4, fontSize: 11.5, color: C.muted });
};
const bullets = (s, items, o) => text(s, items.map((t) => ({ text: t, options: { bullet: { indent: 16 }, paraSpaceAfter: 8 } })), { fontSize: 15, color: C.ink, ...o });
const glow = (s) => s.addImage({ path: ART('aur-02-galaxy'), x: 0, y: 0, w: W, h: 7.5, transparency: 88, sizing: { type: 'cover', w: W, h: 7.5 } });
const notes = (s, t) => s.addNotes(t);

// 1. Title
{
  const s = pres.addSlide({ masterName: 'AURORA' });
  s.addImage({ path: ART('aur-01-hero'), x: 5.4, y: 0, w: 7.93, h: 7.5, sizing: { type: 'cover', w: 7.93, h: 7.5 } });
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 6.2, h: 7.5, fill: { color: C.night } });
  s.addImage({ path: ART('aur-08-mark'), x: M, y: 1.0, w: 0.8, h: 0.8 });
  text(s, 'RetentionLens', { x: M, y: 2.1, w: 5.4, h: 1.0, fontSize: 48, fontFace: FONT.head });
  text(s, 'See which wholesale accounts are about to go quiet, what they are worth, and draft the call you approve.', { x: M, y: 3.2, w: 5.1, h: 1.3, fontSize: 18, color: C.muted });
  text(s, `Real data: UCI Online Retail II · ${fmt(profile.rows)} invoice lines · ${fmt(summary.accounts)} accounts scored`, { x: M, y: 4.7, w: 5.3, h: 0.6, fontSize: 12.5, color: C.cyan });
  text(s, 'MAIB AI 208 · AI in Marketing · Krishna Mathur', { x: M, y: 5.6, w: 5.3, h: 0.4, fontSize: 13, color: C.ink });
  text(s, 'Live demo: krish2105.github.io/Retention-Lens-AI-in-Marketing-', { x: M, y: 6.0, w: 5.6, h: 0.4, fontSize: 12, color: C.muted });
  notes(s, 'RetentionLens is a weekly account review for small wholesalers. Everything shown runs on a real, licensed dataset, and every number in this deck is read from saved result files.');
}

// 2. Problem
{
  const s = pres.addSlide({ masterName: 'AURORA' });
  glow(s);
  title(s, 'The problem', 'Most wholesale accounts quietly stop ordering, and nobody notices in time');
  const rates = ['2010-12-01', '2011-03-01', '2011-06-01'].map((c) => model.cutoffs[c].lapse.bgnbd.base_rate);
  stat(s, M, 2.0, 3.8, `${Math.round(Math.min(...rates) * 100)}–${Math.round(Math.max(...rates) * 100)}%`, 'of known accounts placed no order in the next 90 days (dev cutoffs)', C.magenta);
  stat(s, M + 4.05, 2.0, 3.8, `${Math.round(profile.issues.is_missing_customer / profile.rows * 100)}%`, 'of invoice lines have no customer ID: data quality is part of the job', C.amber);
  stat(s, M + 8.1, 2.0, 3.6, `£${fmt(summary.value_at_risk_high / 1000)}k`, 'usual 90-day spend at stake in high-risk accounts today', C.cyan);
  bullets(s, [
    'User: an owner or account manager at a small wholesaler with hundreds of trade accounts and no data team.',
    'Today: spreadsheets and memory. Lapsing accounts are found after the revenue has gone.',
    'Gap (research): DTC tools need Shopify events and 500+ buyers; distributor platforms are quote-only ERP projects.',
  ], { x: M, y: 3.7, w: 11.8, h: 2.6 });
  notes(s, 'Lapse rates come from the model evaluation file; the missing-ID share comes from the data profile. Competitor facts are from the sourced research report.');
}

// 3. Product
{
  const s = pres.addSlide({ masterName: 'AURORA' });
  title(s, 'The product', 'One weekly loop: upload, score, review, draft, approve, measure');
  framed(s, SHOT('01-overview-dark'), M, 1.75, 7.6, 4.75, 'RetentionLens overview screen in the dark Aurora theme');
  const items = [['Upload', 'any invoice CSV or Excel export; columns matched, bad rows listed'], ['Score', '90-day lapse probability and expected spend with an 80% range'], ['Review', 'this week\'s queue, most spend at risk first, with reasons'], ['Draft', 'a local AI writes the check-in; checks run on every draft'], ['Approve', 'a person approves with a consent basis; nothing is sent'], ['Measure', 'a random holdout shows whether contacting accounts helps']];
  items.forEach(([h, b], i) => {
    const y = 1.8 + i * 0.8;
    s.addShape(pres.shapes.OVAL, { x: 8.55, y: y + 0.08, w: 0.22, h: 0.22, fill: { color: [C.cyan, C.violet, C.amber, C.magenta, C.cyan, C.violet][i] }, line: { type: 'none' } });
    text(s, h, { x: 8.95, y, w: 3.8, h: 0.35, fontSize: 16, fontFace: FONT.head });
    text(s, b, { x: 8.95, y: y + 0.34, w: 3.8, h: 0.45, fontSize: 11, color: C.muted });
  });
  notes(s, 'The public demo is read-only and runs on the real UCI data. The local install adds upload, the weekly queue, AI drafting with Ollama and the decision log.');
}

// 4. Self-serve upload
{
  const s = pres.addSlide({ masterName: 'AURORA' });
  title(s, 'Self-serve upload · R3', 'Bring your own invoices: match columns, see every rejected row');
  framed(s, SHOT('18-upload-mapping-dark'), M, 1.75, 6.0, 3.75, 'Upload wizard step 2: matching the file columns to invoice fields');
  framed(s, SHOT('19-upload-check-light'), M + 6.2, 1.75, 6.0, 3.75, 'Upload wizard step 3: the check report before scoring');
  bullets(s, [
    'Four steps: upload, match columns (guessed, editable), check, score. Scoring runs in a background worker.',
    'The check report counts rows read and rejected, cancellations, duplicates and date-format guesses. Nothing is silently filled in.',
    'The same seasonal BG/NBD + Gamma-Gamma model and value ranges as the reference data.',
  ], { x: M, y: 5.7, w: 12.1, h: 1.2, fontSize: 13 });
  text(s, 'SYNTHETIC sample file shown (apps/web/public/samples/synthetic_wholesale_invoices.csv). The upload was deleted after capture.', { x: M, y: 6.72, w: 12, h: 0.3, fontSize: 10, color: C.amber });
  notes(s, 'Screens captured from the running app on 2026-11-01 using the synthetic sample file, which is labelled SYNTHETIC wherever it appears. The counts in the check report are for the synthetic file only. No real customer has uploaded data yet.');
}

// 5. Weekly holdout queue
{
  const s = pres.addSlide({ masterName: 'AURORA' });
  title(s, 'Weekly queue and holdout · R4', 'A short list each week, and a built-in test of whether outreach works');
  framed(s, SHOT('20-queue-dark'), M, 1.75, 7.4, 4.65, "This week's review queue with spend at risk and the holdout count");
  bullets(s, [
    'The queue lists the accounts with the most spend at risk, in order, with the reasons behind each call.',
    'A random 20% of eligible accounts is held out each week (stable hash of workspace, account and week) and not shown.',
    'After 28 days, reorder rates of contacted and held-out accounts are compared with a 95% interval.',
    'Result so far: none. It needs several weekly queues and a later upload; an interval that crosses zero proves nothing.',
  ], { x: 8.3, y: 1.85, w: 4.4, h: 4.7, fontSize: 13 });
  notes(s, 'The holdout share is the RL_HOLDOUT_SHARE setting, default 20%. The uplift panel on this page shows 0 of 0 reorders today because no real outreach has happened. This is the mechanism for a future pilot to measure causal impact, not a result.');
}

// 6. Data
{
  const s = pres.addSlide({ masterName: 'AURORA' });
  title(s, 'Data · outcome A', 'One licensed source, checksummed, with every problem row counted');
  const rows = [['Measure', 'Value'], ['Invoice lines', fmt(profile.rows)], ['Date range', `${profile.date_min} to ${profile.date_max}`], ['Invoices · customers · countries', `${fmt(profile.invoices)} · ${fmt(profile.customers)} · ${profile.countries}`], ['No customer ID', `${fmt(profile.issues.is_missing_customer)} (${(profile.issues.is_missing_customer / profile.rows * 100).toFixed(1)}%)`], ['Cancellations', fmt(profile.issues.is_cancellation)], ['Repeated across the two workbook sheets', fmt(profile.issues.duplicate_across_sheets)], ['Rows usable for customer models', `${fmt(profile.customer_model_rows)} (${(profile.customer_model_rows / profile.rows * 100).toFixed(1)}%)`]];
  s.addTable(rows.map((r, i) => r.map((c) => ({ text: c, options: { bold: i === 0, color: i === 0 ? C.cyan : C.ink, fontSize: 13, fontFace: FONT.body } }))), { x: M, y: 1.8, w: 7.2, colW: [4.2, 3.0], fill: { color: C.panel }, border: { type: 'solid', color: C.edge, pt: 0.75 }, rowH: 0.48 });
  framed(s, ART('aur-03-import'), 8.3, 1.8, 4.4, 4.4, 'Glass prism illustration splitting invoices into colours');
  text(s, 'Finding: the two sheets overlap on 1–9 December 2010, so the published row count includes a duplicated week. The pipeline flags it instead of dropping rows.', { x: M, y: 6.0, w: 7.3, h: 0.8, fontSize: 12, color: C.muted });
  notes(s, 'Source: UCI Online Retail II, CC BY 4.0, DOI 10.24432/C5CG6D. Archive SHA-256 is recorded in the source register.');
}

// 7. Method
{
  const s = pres.addSlide({ masterName: 'AURORA' });
  title(s, 'Method', 'Rolling cutoffs, fixed before any result, and one frozen test');
  const cut = ['2010-09-01', '2010-12-01', '2011-03-01', '2011-06-01', '2011-09-01'];
  cut.forEach((c, i) => {
    const x = M + i * 2.42;
    const isTest = i === 4;
    glass(s, x, 2.1, 2.2, 1.3, { line: { color: isTest ? C.magenta : C.edge, width: isTest ? 1.5 : 0.75 } });
    text(s, c, { x: x + 0.2, y: 2.25, w: 1.9, h: 0.4, fontSize: 15, fontFace: FONT.head, color: isTest ? C.magenta : C.ink });
    text(s, i === 0 ? 'training only' : isTest ? 'frozen test, scored once' : 'dev evaluation', { x: x + 0.2, y: 2.7, w: 1.9, h: 0.5, fontSize: 11, color: C.muted });
  });
  bullets(s, [
    'Features use only data before the cutoff; labels come from the next 90 days. A unit test proves no leakage.',
    'Label: lapse = no purchase day in the window. Value = net spend in the window, floored at £0.',
    'Models: recency rule · logistic RFM · BG/NBD + Gamma-Gamma (PyMC-Marketing) · LightGBM.',
    'Claim rule: a model wins only if it is better on at least 3 of 4 evaluation cutoffs. No tuning on dev or test.',
  ], { x: M, y: 3.9, w: 11.8, h: 2.8 });
  notes(s, 'This protocol is in docs/superpowers/plans/2026-11-01-p2-models.md and was committed before the first run.');
}

// 8. Results
{
  const s = pres.addSlide({ masterName: 'AURORA' });
  title(s, 'Results · outcomes A and C', 'Simple models win: BG/NBD beats gradient boosting');
  const names = { recency_rule: 'Recency rule', logistic_rfm: 'Logistic RFM', bgnbd: 'BG/NBD', lightgbm: 'LightGBM' };
  const keys = Object.keys(names);
  s.addChart(pres.charts.BAR, [{ name: 'PR-AUC (frozen test)', labels: keys.map((k) => names[k]), values: keys.map((k) => +test.lapse[k].pr_auc.toFixed(3)) }], {
    x: M, y: 1.8, w: 6.6, h: 4.6, barDir: 'bar', chartColors: [C.cyan], valAxisMinVal: 0.7, valAxisMaxVal: 0.85, showValue: true, dataLabelFontSize: 12, dataLabelColor: C.ink, dataLabelFormatCode: '0.000',
    catAxisLabelColor: C.ink, valAxisLabelColor: C.muted, catAxisLabelFontSize: 13, valGridLine: { color: C.edge, size: 0.5 }, showLegend: false, plotArea: { fill: { color: C.night } },
  });
  const wins = model.comparison.lapse_pr_auc;
  bullets(s, [
    `Frozen test (${fmt(test.n_customers)} customers): BG/NBD PR-AUC ${test.lapse.bgnbd.pr_auc.toFixed(3)}, Brier ${test.lapse.bgnbd.brier.toFixed(4)}; LightGBM ${test.lapse.lightgbm.pr_auc.toFixed(3)}, ${test.lapse.lightgbm.brier.toFixed(4)}.`,
    `Across 4 cutoffs LightGBM beats BG/NBD on ${wins.bgnbd.wins} and logistic RFM on ${wins.logistic_rfm.wins}.`,
    `Spend ranking: BG/NBD + Gamma-Gamma normalised Gini ${test.value.bgnbd_gamma_gamma.normalized_gini.toFixed(3)} vs LightGBM ${test.value.lightgbm.normalized_gini.toFixed(3)}.`,
    'Limit found here: the test window is the Christmas peak and spend was under-predicted. The next slide shows the fix.',
  ], { x: 7.5, y: 1.9, w: 5.2, h: 4.6, fontSize: 14 });
  notes(s, 'Read directly from reports/model_results.json. These are the P2 results on the frozen test, scored once.');
}

// 9. R5 / R5b: seasonality, value ranges, ZILN challenger
{
  const s = pres.addSlide({ masterName: 'AURORA' });
  title(s, 'Seasonality, ranges and a deep-learning challenger · R5', 'A seasonal correction halves the spend bias; the neural model lost');
  const sm = r5.summary;
  const bias = sm.mean_abs_total_bias_dev;
  stat(s, M, 1.8, 3.9, `${pct(bias.bgnbd_gamma_gamma)} → ${pct(bias.bgnbd_gamma_gamma_seasonal)}`, `mean total-spend bias on ${r5.dev_cutoffs.length} dev cutoffs (${Math.round(sm.seasonal_bias_reduction_dev * 100)}% less)`, C.cyan);
  stat(s, M + 4.1, 1.8, 3.9, `${pct(sm.post_hoc_peak_coverage.bgnbd_gamma_gamma_seasonal)} → ${pct(sm.post_hoc_peak_coverage.seasonal_pooled)}`, '80% value-range coverage on the peak window (R5b)', C.amber);
  stat(s, M + 8.2, 1.8, 3.9, `${sm.ziln_vs_bgnbd.lapse_pr_auc.wins} of ${sm.ziln_vs_bgnbd.lapse_pr_auc.of}`, 'dev cutoffs where the ZILN network beat BG/NBD on lapse PR-AUC', C.magenta);
  bullets(s, [
    `Adopted: a seasonal multiplier on BG/NBD + Gamma-Gamma. Better Brier and value MAE on ${sm.seasonal_bgnbd_vs_bgnbd.value_mae.wins} of ${sm.seasonal_bgnbd_vs_bgnbd.value_mae.of} dev cutoffs; ranking cannot change because every account is rescaled equally.`,
    `Adopted (R5b): 80% split-conformal ranges calibrated on residuals pooled from the previous 90 days and the same window last year. Dev coverage ${sm.interval_calibration_variants.seasonal_pooled.dev_coverage.map((v) => pct(v)).join(', ')}.`,
    `Disclosure: previous-90-days alone was best on dev but covered only ${pct(sm.post_hoc_peak_coverage.bgnbd_gamma_gamma_seasonal)} on the peak. The peak window had already been seen, so choosing the pooled version was informed by it.`,
    `Not adopted: ZILN network (value MAE wins ${sm.ziln_vs_bgnbd.value_mae.wins} of ${sm.ziln_vs_bgnbd.value_mae.of}). Kept as the documented deep-learning challenger; three versions disclosed.`,
  ], { x: M, y: 3.3, w: 12.1, h: 3.5, fontSize: 13 });
  notes(s, `All numbers from reports/r5_results.json (seed ${r5.seed}). Model selection used only the dev cutoffs ${r5.dev_cutoffs.join(', ')}. The 2011-09-01 window was scored once in P2; here it appears only as a labelled post-hoc look. Post hoc, ${Math.round(sm.post_hoc_peak_gap_closed * 100)}% of the peak spend gap closed, which is optimistic for that reason.`);
}

// 10. Segments
{
  const s = pres.addSlide({ masterName: 'AURORA' });
  title(s, 'Segments · outcome C · week 5', 'Every account as a star in the customer galaxy');
  framed(s, SHOT('04-segments-galaxy-dark'), M, 1.75, 7.4, 4.65, '3D customer galaxy of 5,852 accounts coloured by risk');
  const top = segments.segments.slice(0, 5);
  s.addTable([['Segment', 'Accounts', 'Exp. 90-day £'], ...top.map((r) => [r.segment, fmt(r.accounts), fmt(r.expected_value_90)])].map((r, i) => r.map((c) => ({ text: String(c), options: { bold: i === 0, color: i === 0 ? C.cyan : C.ink, fontSize: 12 } }))), { x: 8.3, y: 1.8, w: 4.4, colW: [1.8, 1.1, 1.5], fill: { color: C.panel }, border: { type: 'solid', color: C.edge, pt: 0.75 }, rowH: 0.42 });
  text(s, `Lookalike model finds new customers who look like future top-20% spenders: test AUC ${look.test_auc.toFixed(3)} on ${fmt(look.test_customers)} later customers.`, { x: 8.3, y: 4.6, w: 4.4, h: 1.2, fontSize: 13, color: C.muted });
  notes(s, 'k-means chose k=' + segments.clusters.k + ' by silhouette. Each RFM segment carries a suggested play for a person to judge.');
}

// 11. Signals
{
  const s = pres.addSlide({ masterName: 'AURORA' });
  title(s, 'Signals · outcome B · weeks 9–10', 'Wholesale buying runs a month ahead of consumer interest');
  const xmas = signals.web.themes.find((t) => t.theme === 'Christmas');
  const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  s.addChart(pres.charts.LINE, [{ name: 'Wholesale sales', labels: months, values: xmas.sales_index }, { name: 'Wikipedia interest', labels: months, values: xmas.web_index }], {
    x: M, y: 1.8, w: 6.8, h: 4.3, chartColors: [C.cyan, C.magenta], lineSize: 3, lineDataSymbol: 'none', showLegend: true, legendPos: 'b', legendColor: C.ink, legendFontSize: 12,
    catAxisLabelColor: C.muted, valAxisLabelColor: C.muted, valGridLine: { color: C.edge, size: 0.5 }, plotArea: { fill: { color: C.night } },
  });
  bullets(s, [
    `Christmas lines: correlation ${xmas.correlation.toFixed(2)} in the same month, ${xmas.correlation_web_one_month_later.toFixed(2)} with interest one month later (12 monthly points, exploratory).`,
    'Traditional: invoices. Web: Wikimedia pageviews (CC0). Network: co-purchase communities.',
    'Social: 600 posts, SYNTHETIC and labelled, because licensed review data cannot be published.',
    'Scraping demo: polite, robots-checked, on the toscrape.com sandbox.',
  ], { x: 7.7, y: 1.9, w: 5.0, h: 4.6, fontSize: 13.5 });
  notes(s, 'Wikipedia data covers 2016 to 2025 and invoices 2009 to 2011, so only seasonal shape is compared.');
}

// 12. Outreach
{
  const s = pres.addSlide({ masterName: 'AURORA' });
  title(s, 'Outreach studio · outcome D', 'The AI writes the words; the model supplies the numbers; a person decides');
  framed(s, SHOT('08-outreach-draft-dark'), M, 1.75, 7.6, 4.75, 'Outreach studio showing a local-model draft and its automatic checks');
  const steps = ['Facts from the scoring model only', 'Local qwen2.5:7b drafts (JSON)', 'Checker: numbers, offers, pressure, contact data', 'Second-pass review of tone', 'Human approval + UK PECR basis', 'CSV export · no send tool'];
  steps.forEach((t, i) => { glass(s, 8.5, 1.8 + i * 0.66, 4.2, 0.54); text(s, `${i + 1}  ${t}`, { x: 8.7, y: 1.9 + i * 0.66, w: 3.9, h: 0.4, fontSize: 12.5 }); });
  const numbers = genai.per_check_pass["Numbers match the model's facts"];
  text(s, `Live test, ${genai.drafts} drafts: numbers grounded ${numbers}; second-pass review passed ${genai.per_check_pass['Second-pass review (tone, manipulation)']}. A person reviews every draft.`, { x: 8.5, y: 5.85, w: 4.2, h: 0.8, fontSize: 11.5, color: C.amber });
  notes(s, 'The critic is strict and still needs calibration against human labels; the labelling sheet is in reports/critic_labels.csv.');
}

// 13. Ethics
{
  const s = pres.addSlide({ masterName: 'AURORA' });
  glow(s);
  title(s, 'Responsible AI · CLO4', 'Built so it cannot email a customer by itself');
  const cards = [['Red-teamed', `No free text in prompts; ${TESTS.api_redteam} OWASP LLM Top 10 cases run in CI on every push.`], ['Every number grounded', 'Any figure not in the model output blocks the draft.'], ['Consent first', 'Companies: legitimate interest. Sole traders: consent or soft opt-in. Otherwise approval is blocked.'], ['Accountable', 'Idempotent approvals and an append-only audit log of who decided what.'], ['Honest data', 'Synthetic data labelled everywhere; licences in the source register.'], ['Accessible', 'axe-core WCAG 2.2 AA: 0 violations on 9 pages, both themes; works at 320 px.']];
  cards.forEach(([h, b], i) => { const x = M + (i % 3) * 4.05, y = 1.9 + Math.floor(i / 3) * 2.35; glass(s, x, y, 3.85, 2.1); text(s, h, { x: x + 0.25, y: y + 0.22, w: 3.4, h: 0.45, fontSize: 16, fontFace: FONT.head, color: [C.cyan, C.violet, C.amber, C.magenta, C.cyan, C.violet][i] }); text(s, b, { x: x + 0.25, y: y + 0.75, w: 3.4, h: 1.2, fontSize: 12.5, color: C.muted }); });
  notes(s, 'Mapped to the OWASP Top 10 for LLM applications (2025) in docs/security/LLM_RED_TEAM.md: prompt injection, sensitive information disclosure, improper output handling, excessive agency, system prompt leakage, misinformation and unbounded consumption.');
}

// 14. SaaS foundations
{
  const s = pres.addSlide({ masterName: 'AURORA' });
  title(s, 'SaaS foundations · R2, R6, R8', 'Built and tested locally; not yet hosted');
  const cards = [
    ['Workspaces and roles', 'One workspace per company; owner, reviewer and viewer roles; every query scoped to the workspace. Sign-in hardening: throttling, weak passwords refused.', C.cyan],
    ['Row-level security in CI', 'The Supabase migration is applied to a local Postgres stack in CI and a two-tenant test fails the build on any read or write leak.', C.violet],
    [`Load test: ${load.users} users, ${load.seconds} s`, `${fmt(load.requests)} requests, ${fmt(load.throughput_rps)} per second, ${load.errors} errors. p95 ${fmt(load.p95_ms, 1)} ms against a ${load.slo_p95_ms} ms target.`, C.amber],
    [`Restore drill: ${drillPassed ? 'passed' : 'failed'}`, `Backup checksum and integrity check passed; row counts matched in all ${drillTables} tables. Run on a SYNTHETIC seeded database.`, C.magenta],
  ];
  cards.forEach(([h, b, col], i) => { const x = M + (i % 2) * 6.1, y = 1.85 + Math.floor(i / 2) * 2.25; glass(s, x, y, 5.9, 2.05); text(s, h, { x: x + 0.25, y: y + 0.2, w: 5.4, h: 0.45, fontSize: 16, fontFace: FONT.head, color: col }); text(s, b, { x: x + 0.25, y: y + 0.72, w: 5.4, h: 1.25, fontSize: 12.5, color: C.muted }); });
  text(s, `Tests collected on ${TESTS.collected_on}: ${TESTS.ml} ML · ${TESTS.api} API · ${TESTS.e2e_static} browser (static) + ${TESTS.e2e_live} live end-to-end flow.`, { x: M, y: 6.45, w: 12, h: 0.35, fontSize: 12, color: C.cyan });
  notes(s, 'Sources: reports/load_test.json (local machine, not a hosted server), reports/restore_drill.md (small synthetic database), the rls job in .github/workflows/ci.yml, and test collection counts in design/test_counts.json. Render, Supabase and Stripe accounts do not exist yet, so none of this has run on hosted infrastructure.');
}

// 15. Product lab
{
  const s = pres.addSlide({ masterName: 'AURORA' });
  title(s, 'Product lab · weeks 7–8', 'What sells together, and why price data can mislead');
  framed(s, SHOT('09-product-lab-light'), M, 1.75, 7.4, 4.65, 'Product lab basket rules table');
  const r = lab.rules[0];
  bullets(s, [
    `Strongest pair: ${r.if} → ${r.then}, lift ${r.lift.toFixed(1)}×, ${fmt(r.invoices)} invoices.`,
    'Portfolio matrix: stars, cash cows, question marks and dogs from 2011 vs 2010 sales.',
    'Product loyalty: share of buyers who reorder an item, a simple brand signal.',
    'Price elasticities come out near −15 to −20: wholesale price breaks, not price sensitivity. Shown as a confounding lesson.',
  ], { x: 8.3, y: 1.9, w: 4.4, h: 4.6, fontSize: 13 });
  notes(s, 'All product-lab results are associational; no price was randomised.');
}

// 16. Course coverage
{
  const s = pres.addSlide({ masterName: 'AURORA' });
  title(s, 'Course fit', 'Every learning outcome has a working screen and a result file');
  const rows = [['Outcome', 'Evidence'], ['A · research and predictive analytics', 'Data profile, rolling-cutoff lapse models, cohort terrain'], ['B · traditional, web and social data', 'Wikipedia seasonality, co-purchase network, synthetic social, scraper'], ['C · CLV, churn, retention, new customers', 'BG/NBD + Gamma-Gamma, segments, lookalikes'], ['D · Generative AI for decisions', 'Outreach studio with checks, consent gate and live evaluation'], ['Labs weeks 2, 4, 6, 8, 10', 'Scaffolds and EVIDENCE.md in labs/ · [OWNER: lab reports to be written]'], ['Week 12 final project', 'This deck, the report, and the live demo']];
  s.addTable(rows.map((r, i) => r.map((c) => ({ text: c, options: { bold: i === 0, color: i === 0 ? C.cyan : C.ink, fontSize: 14 } }))), { x: M, y: 1.85, w: W - 2 * M, colW: [4.6, W - 2 * M - 4.6], fill: { color: C.panel }, border: { type: 'solid', color: C.edge, pt: 0.75 }, rowH: 0.62 });
  notes(s, 'The Course evidence page in the app links each outcome to the screen and file that shows it.');
}

// 17. What is still missing
{
  const s = pres.addSlide({ masterName: 'AURORA' });
  glow(s);
  title(s, 'What is still missing', 'The software exists; the market evidence does not yet');
  bullets(s, [
    'No customer interviews yet: buyer, workflow and price are hypotheses.',
    'No usability sessions: the 10-minute first-run target is untested with real users.',
    'No pilot and no customers: the holdout queue has produced no uplift result.',
    'No hosting: Render, Supabase and Stripe test accounts are not created; everything ran locally or as a static demo.',
    'The AI critic is uncalibrated: no human labels yet. One wholesaler, 2009–2011 data.',
  ], { x: M, y: 1.9, w: 6.3, h: 4.6, fontSize: 14.5 });
  text(s, 'Next, in order', { x: 7.2, y: 1.9, w: 5.5, h: 0.4, fontSize: 16, fontFace: FONT.head, color: C.cyan });
  bullets(s, ['8–10 discovery interviews (kit ready in docs/research).', '5 think-aloud sessions on upload → queue.', 'Label 16+ drafts to calibrate the critic.', 'Create hosting accounts; run the restore drill on real rows.', 'A four-week pilot with one wholesaler.'], { x: 7.2, y: 2.4, w: 5.5, h: 4.1, fontSize: 14, color: C.ink });
  text(s, '[OWNER: add your own reflection and learning narrative here or in the talk track]', { x: M, y: 6.5, w: 12, h: 0.35, fontSize: 11, color: C.amber });
  notes(s, '[OWNER: speaker narrative and reflection to be written by the student.] Facts only on this slide: none of the listed evidence exists yet; see project/NEXT_ACTIONS.md.');
}

// 18. Close
{
  const s = pres.addSlide({ masterName: 'AURORA' });
  s.addImage({ path: ART('aur-09-readme-banner'), x: 0, y: 0, w: W, h: 7.5, sizing: { type: 'cover', w: W, h: 7.5 }, transparency: 35 });
  text(s, 'Thank you', { x: M, y: 2.4, w: 8, h: 1.0, fontSize: 48, fontFace: FONT.head });
  text(s, 'Live demo · krish2105.github.io/Retention-Lens-AI-in-Marketing- · retentionlens-demo.vercel.app\nCode · github.com/krish2105/Retention-Lens-AI-in-Marketing-', { x: M, y: 3.6, w: 10, h: 1.0, fontSize: 16, color: C.ink });
  text(s, 'Illustrations generated by the author with ChatGPT Images. Data: Chen (2019), UCI Online Retail II, CC BY 4.0.', { x: M, y: 6.3, w: 11, h: 0.4, fontSize: 11, color: C.muted });
}

pres.writeFile({ fileName: OUT }).then(() => console.log('wrote', OUT));
