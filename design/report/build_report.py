"""Build design/report/report.html from committed result files (no hand-typed numbers).

Run from the repo root: python3 design/report/build_report.py
Then print: node design/report/print.js <repoRoot>   (Playwright, A4, page numbers)
"""
import json
import re
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
J = lambda p: json.loads((ROOT / p).read_text())  # noqa: E731
model = J("reports/model_results.json")
profile = J("reports/data_profile.json")
summary = J("apps/web/public/data/summary.json")
segments = J("apps/web/public/data/segments.json")
look = J("apps/web/public/data/lookalikes.json")
signals = J("apps/web/public/data/signals.json")
lab = J("apps/web/public/data/product_lab.json")
genai = J("reports/genai_eval.json")
r5 = J("reports/r5_results.json")
load = J("reports/load_test.json")
drill = (ROOT / "reports/restore_drill.md").read_text()
DRILL_TABLES = re.search(r"for all (\d+) tables", drill).group(1)
DRILL_PASSED = "**PASSED**" in drill
TESTS = J("design/test_counts.json")
R5S = r5["summary"]
pct = lambda v, d=1: f"{v*100:.{d}f}%"  # noqa: E731
CUTS = list(model["cutoffs"])
TEST = model["cutoffs"]["2011-09-01"]
NAMES = {"recency_rule": "Recency rule", "logistic_rfm": "Logistic RFM", "bgnbd": "BG/NBD", "lightgbm": "LightGBM",
         "naive_last_90": "Last 90 days", "bgnbd_gamma_gamma": "BG/NBD + Gamma-Gamma",
         "bgnbd_seasonal": "BG/NBD + seasonal", "ziln_nn": "ZILN network"}
n = lambda v, d=0: f"{v:,.{d}f}"  # noqa: E731
shot = lambda name, cap: f'<figure><img src="../../submissions/screenshots/{name}.jpg" alt="{escape(cap)}"><figcaption>{escape(cap)}</figcaption></figure>'  # noqa: E731


def table(head, rows, cls=""):
    h = "".join(f"<th>{escape(str(c))}</th>" for c in head)
    b = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<table class="{cls}"><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>'


def metric_rows(kind, metric, digits):
    models = list(TEST[kind])
    rows = []
    for m in models:
        vals = [model["cutoffs"][c][kind][m][metric] for c in CUTS]
        rows.append([NAMES[m]] + [f"{v:.{digits}f}" for v in vals])
    return rows


rates = [model["cutoffs"][c]["lapse"]["bgnbd"]["base_rate"] for c in CUTS[:-1]]
xmas = next(t for t in signals["web"]["themes"] if t["theme"] == "Christmas")

html = f"""<!doctype html><html lang="en-GB"><head><meta charset="utf-8"><title>RetentionLens project report</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
@page {{ size: A4; margin: 16mm 16mm 18mm; }}
:root {{ --ink:#11132a; --muted:#4e5470; --cyan:#0e7490; --magenta:#be185d; --violet:#6d28d9; --amber:#8a5d07; --edge:#e2e4ee; --paper:#f3f4fb; }}
* {{ box-sizing: border-box; }}
body {{ font-family: "Space Grotesk", "Segoe UI", system-ui, sans-serif; color: var(--ink); font-size: 10.5pt; line-height: 1.55; margin: 0; }}
h1 {{ font-size: 30pt; letter-spacing: -1px; margin: 0 0 6px; line-height: 1.05; }}
h2 {{ font-size: 17pt; letter-spacing: -.4px; margin: 0 0 8px; padding-top: 4px; border-top: 3px solid var(--cyan); display: inline-block; }}
h3 {{ font-size: 12pt; margin: 14px 0 4px; }}
p {{ margin: 0 0 8px; }}
section {{ break-before: page; }}
.eyebrow {{ font-family: "IBM Plex Mono", monospace; font-size: 8.5pt; letter-spacing: 1.6px; text-transform: uppercase; color: var(--cyan); margin-bottom: 6px; }}
.cover {{ height: 255mm; display: flex; flex-direction: column; justify-content: flex-end; background: #070912 url("../deck/img/aur-01-hero.jpg") center/cover; color: #eef0ff; padding: 18mm; border-radius: 6px; }}
.cover p {{ color: #c9cde6; font-size: 12pt; max-width: 120mm; }}
.cover .meta {{ font-family: "IBM Plex Mono", monospace; font-size: 9pt; color: #a7adc8; margin-top: 10mm; }}
.kpis {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin: 10px 0 14px; }}
.kpi {{ border: 1px solid var(--edge); border-radius: 10px; padding: 10px 12px; background: var(--paper); }}
.kpi b {{ display: block; font-size: 17pt; letter-spacing: -.5px; }}
.kpi span {{ font-size: 8.5pt; color: var(--muted); }}
table {{ width: 100%; border-collapse: collapse; margin: 6px 0 12px; font-size: 9pt; font-variant-numeric: tabular-nums; break-inside: avoid; }}
th {{ text-align: left; font-family: "IBM Plex Mono", monospace; font-size: 7.5pt; letter-spacing: .6px; text-transform: uppercase; color: var(--muted); border-bottom: 1.5px solid var(--ink); padding: 5px 6px; }}
td {{ border-bottom: 1px solid var(--edge); padding: 5px 6px; vertical-align: top; }}
figure {{ margin: 8px 0 12px; break-inside: avoid; }}
figure img {{ width: 100%; border-radius: 8px; border: 1px solid var(--edge); }}
figcaption {{ font-size: 8.5pt; color: var(--muted); margin-top: 4px; }}
.two {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
.note {{ border-left: 3px solid var(--amber); padding: 6px 10px; background: #fbf6ea; font-size: 9.5pt; margin: 8px 0; }}
.mono {{ font-family: "IBM Plex Mono", monospace; font-size: 8.5pt; }}
ul {{ margin: 0 0 8px 16px; padding: 0; }}
li {{ margin-bottom: 3px; }}
.phones {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }}
</style></head><body>

<div class="cover">
  <div class="eyebrow" style="color:#67e8f9">MAIB AI 208 · AI in Marketing · Project report</div>
  <h1>RetentionLens</h1>
  <p>Ninety-day lapse risk and customer value for every wholesale account, the evidence behind each call, and outreach a person approves before anything leaves.</p>
  <div class="meta">Krishna Mathur · {date.today().strftime('%d %B %Y')}<br>Live demo: krish2105.github.io/Retention-Lens-AI-in-Marketing-<br>Code: github.com/krish2105/Retention-Lens-AI-in-Marketing-</div>
</div>

<section>
<div class="eyebrow">1 · Executive summary</div><h2>What was built and what it shows</h2>
<p>RetentionLens scores {n(summary['accounts'])} trade accounts from a real UK giftware wholesaler (UCI Online Retail II, {n(profile['rows'])} invoice lines, CC BY 4.0) for the chance they place no order in the next 90 days and for their expected spend. It explains each call, groups accounts into segments, adds web and network signals, and drafts a check-in email with a local language model that a person must approve. Since the first version it also accepts a company's own invoice export, builds a weekly review queue with a random holdout to measure whether outreach works, and has the foundations of a multi-tenant service (workspaces, roles, row-level security, load and restore tests). None of this has yet been used by a real customer.</p>
<div class="kpis">
 <div class="kpi"><b>{n(summary['bands']['high'])}</b><span>accounts at high lapse risk (≥ 75%)</span></div>
 <div class="kpi"><b>£{n(summary['value_at_risk_high']/1000)}k</b><span>usual 90-day spend at stake in them</span></div>
 <div class="kpi"><b>{TEST['lapse']['bgnbd']['pr_auc']:.3f}</b><span>PR-AUC of BG/NBD on the frozen test</span></div>
 <div class="kpi"><b>{look['test_auc']:.3f}</b><span>AUC of the new-customer lookalike model</span></div>
</div>
<h3>Main findings</h3>
<ul>
<li><b>Simple probabilistic models win.</b> Across four rolling cutoffs, LightGBM beat BG/NBD on {model['comparison']['lapse_pr_auc']['bgnbd']['wins']} and logistic RFM on {model['comparison']['lapse_pr_auc']['logistic_rfm']['wins']}. A neural model is not justified by this evidence.</li>
<li><b>A seasonal correction halves the spend bias.</b> Mean total-spend bias on the development cutoffs fell from {pct(R5S['mean_abs_total_bias_dev']['bgnbd_gamma_gamma'])} to {pct(R5S['mean_abs_total_bias_dev']['bgnbd_gamma_gamma_seasonal'])}; a ZILN neural challenger won {R5S['ziln_vs_bgnbd']['lapse_pr_auc']['wins']} of {R5S['ziln_vs_bgnbd']['lapse_pr_auc']['of']} cutoffs on lapse PR-AUC and was not adopted.</li>
<li><b>Wholesale buying leads consumer interest by about a month.</b> For Christmas lines the correlation with Wikipedia interest rises from {xmas['correlation']:.2f} (same month) to {xmas['correlation_web_one_month_later']:.2f} (one month later). Twelve monthly points: exploratory.</li>
<li><b>New customers can be spotted from their first order</b> (test AUC {look['test_auc']:.3f} on later customers).</li>
<li><b>A small local LLM needs a person in the loop.</b> {genai['per_check_pass']["Numbers match the model's facts"]} drafts kept to the model's numbers; its own second-pass review passed only {genai['per_check_pass']['Second-pass review (tone, manipulation)']}.</li>
</ul>
{shot('01-overview-dark', 'Figure 1. Overview screen (dark theme): key figures and the cohort retention terrain.')}
</section>

<section>
<div class="eyebrow">2 · Problem and user</div><h2>Who it is for and why it matters</h2>
<p>The target user is the owner or account manager of a small wholesaler with hundreds of trade accounts and no data team. Between {min(rates)*100:.0f}% and {max(rates)*100:.0f}% of known accounts placed no order in the following 90 days at the development cutoffs, and lapses are usually noticed only after revenue has gone.</p>
<p>Desk research found a gap between self-serve direct-to-consumer tools (which need e-commerce events and hundreds of buyers) and distributor platforms (quote-only, ERP-integrated). No tool combined CSV-first input, small-sample uncertainty, approval-gated AI drafts and published pricing. Buyer, workflow and price are <b>hypotheses</b>: no interviews or pilot have been run yet.</p>
<div class="eyebrow" style="margin-top:14px">3 · Data</div><h2>One licensed source, every problem counted</h2>
{table(['Measure', 'Value'], [
  ['Invoice lines', n(profile['rows'])], ['Date range', f"{profile['date_min']} to {profile['date_max']}"],
  ['Invoices · customers · countries', f"{n(profile['invoices'])} · {n(profile['customers'])} · {profile['countries']}"],
  ['No customer ID', f"{n(profile['issues']['is_missing_customer'])} ({profile['issues']['is_missing_customer']/profile['rows']*100:.1f}%)"],
  ['Cancellations · negative quantities', f"{n(profile['issues']['is_cancellation'])} · {n(profile['issues']['is_negative_qty'])}"],
  ['Duplicates (across sheets / within a sheet)', f"{n(profile['issues']['duplicate_across_sheets'])} / {n(profile['issues']['duplicate_within_sheet'])}"],
  ['Rows usable for customer models', f"{n(profile['customer_model_rows'])} ({profile['customer_model_rows']/profile['rows']*100:.1f}%), {n(profile['customer_model_customers'])} customers"],
])}
<p>The two workbook sheets overlap on 1–9 December 2010, so the published row count includes a duplicated week. Rows are flagged, never silently dropped. The archive is SHA-256 checked (<span class="mono">{summary['data_sha256'][:16]}…</span>).</p>
</section>

<section>
<div class="eyebrow">3b · The weekly loop (R3, R4)</div><h2>Upload your own invoices, review a short queue, measure the effect</h2>
<p>A wholesaler uploads a CSV or Excel export with one row per invoice line. The wizard guesses the column mapping (editable), then a check report counts rows read and rejected, cancellations, duplicates and date-format assumptions before anything is scored. Missing customer fields are never filled with defaults. Scoring runs in a background worker with the same seasonal model and value ranges as the reference data.</p>
<div class="two">{shot('18-upload-mapping-dark', 'Figure 5. Upload step 2: match columns (dark). SYNTHETIC sample file.')}{shot('19-upload-check-light', 'Figure 6. Upload step 3: the check report before scoring (light). SYNTHETIC sample file.')}</div>
<p>Each week the queue lists the accounts with the most spend at risk. A random share of eligible accounts (setting <span class="mono">RL_HOLDOUT_SHARE</span>, default 20%) is held out by a stable hash of workspace, account and week and is not shown. After the observation period the reorder rates of contacted and held-out accounts are compared with a 95% interval. <b>No uplift result exists yet</b>: it needs several weekly queues and later uploads from a real customer.</p>
{shot('20-queue-dark', "Figure 7. This week's review queue on the reference data (dark).")}
<p class="mono">The screenshots use apps/web/public/samples/synthetic_wholesale_invoices.csv, which is SYNTHETIC. The upload was deleted after capture.</p>
</section>

<section>
<div class="eyebrow">4 · Method</div><h2>A protocol fixed before any result</h2>
<ul>
<li>Snapshots at {', '.join(CUTS[:0] + ['2010-09-01'] + CUTS)}; development cutoffs {', '.join(CUTS[:-1])}; <b>frozen test 2011-09-01, scored once</b>.</li>
<li>Features use only data before the cutoff and labels the next 90 days (a unit test proves no leakage). Lapse = no purchase day in the window; value = net spend, floored at £0.</li>
<li>Models: recency rule, logistic RFM, BG/NBD + Gamma-Gamma (PyMC-Marketing 1.3, MAP), LightGBM 4.7. Fixed settings, no tuning.</li>
<li>A model "wins" only if better on at least 3 of 4 cutoffs.</li>
</ul>
<div class="eyebrow" style="margin-top:12px">5 · Results</div><h2>Lapse prediction (PR-AUC)</h2>
{table(['Model'] + [f"{c}{' (test)' if c == '2011-09-01' else ''}" for c in CUTS], metric_rows('lapse', 'pr_auc', 3))}
<h3>Calibration (Brier score, lower is better)</h3>
{table(['Model'] + CUTS, metric_rows('lapse', 'brier', 4))}
<h3>90-day spend ranking (normalised Gini)</h3>
{table(['Model'] + CUTS, metric_rows('value', 'normalized_gini', 3))}
<div class="note">The test window is the Christmas peak. All P2 models over-predict lapse there and under-predict spend. Section 5b reports the seasonal correction added afterwards (R5), selected on development cutoffs only.</div>
</section>

<section>
<div class="eyebrow">5b · Seasonality, value ranges and a deep-learning challenger (R5, R5b)</div><h2>Fixing the peak-season gap, honestly</h2>
<p>Experiment run {r5['generated_at'][:10]}, seed {r5['seed']}. Models were chosen on the development cutoffs {', '.join(r5['dev_cutoffs'])} only; the {r5['post_hoc_cutoff']} window had already been scored once in P2 and appears here only as a labelled post-hoc look.</p>
<div class="kpis">
 <div class="kpi"><b>{pct(R5S['mean_abs_total_bias_dev']['bgnbd_gamma_gamma'])} → {pct(R5S['mean_abs_total_bias_dev']['bgnbd_gamma_gamma_seasonal'])}</b><span>mean total-spend bias, dev cutoffs</span></div>
 <div class="kpi"><b>{pct(R5S['post_hoc_peak_coverage']['bgnbd_gamma_gamma_seasonal'])} → {pct(R5S['post_hoc_peak_coverage']['seasonal_pooled'])}</b><span>80% range coverage on the peak window (post hoc)</span></div>
 <div class="kpi"><b>{R5S['ziln_vs_bgnbd']['lapse_pr_auc']['wins']} / {R5S['ziln_vs_bgnbd']['lapse_pr_auc']['of']}</b><span>dev wins for ZILN on lapse PR-AUC</span></div>
 <div class="kpi"><b>{pct(R5S['post_hoc_peak_gap_closed'], 0)}</b><span>peak spend gap closed, post hoc (optimistic)</span></div>
</div>
{table(['Cutoff', 'Model', 'PR-AUC', 'Brier', 'Value MAE (£)', 'Total-spend bias'], [[c + (' (post hoc)' if r5['cutoffs'][c]['role'] != 'dev' else ''), NAMES.get(m, m), f"{v['pr_auc']:.3f}", f"{v['brier']:.4f}", n(r5['cutoffs'][c]['value'][vm]['mae'], 1), f"{r5['cutoffs'][c]['value'][vm]['total_bias']*100:+.1f}%"] for c in r5['cutoffs'] for m, vm in [('bgnbd', 'bgnbd_gamma_gamma'), ('bgnbd_seasonal', 'bgnbd_gamma_gamma_seasonal'), ('ziln_nn', 'ziln_nn')] for v in [r5['cutoffs'][c]['lapse'][m]]])}
<ul>
<li><b>Adopted:</b> a seasonal multiplier on BG/NBD + Gamma-Gamma (better Brier and value MAE on {R5S['seasonal_bgnbd_vs_bgnbd']['value_mae']['wins']} of {R5S['seasonal_bgnbd_vs_bgnbd']['value_mae']['of']} dev cutoffs; ranking metrics cannot change because every account is rescaled equally).</li>
<li><b>Adopted (R5b):</b> 80% split-conformal value ranges calibrated on residuals pooled from the previous 90 days and the same window last year. Dev coverage {', '.join(pct(v) for v in R5S['interval_calibration_variants']['seasonal_pooled']['dev_coverage'])}.</li>
<li><b>Not adopted:</b> the ZILN network (value MAE wins {R5S['ziln_vs_bgnbd']['value_mae']['wins']} of {R5S['ziln_vs_bgnbd']['value_mae']['of']}); kept as the documented deep-learning challenger. Seasonal features for LightGBM were mixed and also not adopted.</li>
</ul>
<div class="note"><b>Disclosure.</b> Calibrating on the previous 90 days alone was best on the development cutoffs but covered only {pct(R5S['post_hoc_peak_coverage']['bgnbd_gamma_gamma_seasonal'])} of accounts on the peak window; the pooled version covered {pct(R5S['post_hoc_peak_coverage']['seasonal_pooled'])}. The peak window had already been seen, so choosing the pooled version was informed by it. The ZILN network went through three versions after dev results were seen; all three are listed in reports/r5_results.md.</div>
</section>

<section>
<div class="eyebrow">6 · Segments and new customers</div><h2>Who to call, who to nurture</h2>
{table(['Segment', 'Accounts', 'Median net spend', 'Expected 90-day spend', 'High risk', 'Suggested play'], [[s['segment'], n(s['accounts']), '£' + n(s['median_net_spend']), '£' + n(s['expected_value_90']), f"{s['high_risk_share']*100:.0f}%", escape(s['play'])] for s in segments['segments']])}
<p>k-means on log recency, frequency and spend chose k = {segments['clusters']['k']} by silhouette score. The lookalike model scores customers whose first order was in the last 90 days for the chance of becoming a top-20% first-year spender: test AUC {look['test_auc']:.3f} on {n(look['test_customers'])} later customers ({escape(look['split'])}).</p>
{shot('04-segments-galaxy-dark', 'Figure 2. The 3D customer galaxy: every account positioned by recency, purchase days and spend, coloured by lapse risk.')}
</section>

<section>
<div class="eyebrow">7 · Traditional, web and social data (outcome B)</div><h2>Signals around the invoices</h2>
{table(['Theme', 'Same-month r', 'r with interest 1 month later', 'Sales peak', 'Interest peak'], [[t['theme'], f"{t['correlation']:.2f}", f"{t['correlation_web_one_month_later']:.2f}", t['sales_peak_month'], t['web_peak_month']] for t in signals['web']['themes'] if t.get('available')])}
<p>Wikipedia pageviews (CC0) cover 2016–2025 while invoices cover 2009–2011, so only the seasonal shape is compared. The co-purchase network links the top {len(signals['network']['nodes'])} products into {len(signals['network']['communities'])} communities (modularity {signals['network']['modularity']:.3f}); it shows products bought together, not social influence.</p>
<p><b>Social data is synthetic.</b> Licensed review and social sources (Yelp, Reddit, Amazon reviews) cannot be published in a public repository, so {signals['social']['posts']} posts were generated from real product names and labelled SYNTHETIC everywhere; {signals['social']['injection_flagged']} of {signals['social']['injection_posts']} prompt-injection posts were flagged. A polite scraper (robots.txt, identifying user agent, delays, caching) collected {signals['competitor']['items']} listings from the toscrape.com practice site.</p>
{shot('06-signals-light', 'Figure 3. Signals page (light theme): wholesale sales against Wikipedia interest by theme.')}
</section>

<section>
<div class="eyebrow">8 · Generative AI for decisions (outcome D)</div><h2>Grounded drafts, human approval</h2>
<p>The analytics core supplies every fact; the local model (qwen2.5:7b via Ollama) only writes the words. No free text from customers or posts enters the prompt. Each draft passes a deterministic checker and a second-pass review, then needs a person to approve it with a UK PECR consent basis. Approvals are idempotent, every action is audit-logged, and there is no send tool: approved drafts are exported as CSV.</p>
{table(['Check (live run, ' + str(genai['drafts']) + ' drafts)', 'Passed'], [[escape(k), v] for k, v in genai['per_check_pass'].items()])}
<p>The second-pass reviewer is strict. Whether its flags are right is unknown until a person labels the drafts; the labelling sheet and scoring script (Cohen's kappa) are in the repository.</p>
{shot('08-outreach-draft-dark', 'Figure 4. Outreach studio: a local-model draft with its automatic checks and the approval form.')}
</section>

<section>
<div class="eyebrow">9 · Responsible AI and accessibility (CLO4)</div><h2>Built so it cannot email a customer by itself</h2>
<ul>
<li><b>Prompt injection (OWASP LLM01):</b> no free text in prompts; injection posts detected and tested.</li>
<li><b>Excessive agency:</b> no send tool; export only after approval.</li>
<li><b>Consent:</b> companies under legitimate interest; sole traders need consent or the soft opt-in, otherwise approval is blocked.</li>
<li><b>Honesty:</b> synthetic data labelled; every chart has a source line; limitations stated in the app.</li>
<li><b>Accessibility:</b> axe-core WCAG 2.2 AA scan reports 0 violations on 9 pages in both themes; layout verified at 320–768 px.</li>
</ul>
<div class="eyebrow" style="margin-top:12px">10 · Product lab (weeks 7–8)</div><h2>What sells together</h2>
{table(['If they buy', 'They also buy', 'Confidence', 'Lift'], [[escape(r['if']), escape(r['then']), f"{r['confidence']*100:.0f}%", f"{r['lift']:.1f}×"] for r in lab['rules'][:6]])}
<p>Price elasticities from weekly log-log regressions come out implausibly large (around −15 to −20) because wholesale price breaks give big orders lower unit prices. They are presented as a lesson in confounding, not as pricing guidance.</p>
</section>

<section>
<div class="eyebrow">10b · SaaS foundations (R2, R6, R8)</div><h2>Built and tested locally; not yet hosted</h2>
{table(['Area', 'What exists', 'Evidence'], [
  ['Workspaces and roles', 'One workspace per company; owner, reviewer and viewer roles; every query scoped to the workspace; sign-in throttling and weak-password refusal', f"{TESTS['api']} API tests collected"],
  ['Row-level security', 'Supabase migration with Postgres policies; a two-tenant test raises on any cross-tenant read or viewer write', 'CI job <span class="mono">rls</span> applies the migration to a local Supabase stack'],
  ['Load test', f"{load['users']} concurrent users for {load['seconds']} s: {n(load['requests'])} requests, {n(load['throughput_rps'])} per second, {load['errors']} errors", f"p95 {load['p95_ms']:.1f} ms vs {load['slo_p95_ms']} ms target ({'met' if load['meets_slo'] else 'missed'}); reports/load_test.json"],
  ['Restore drill', f"Backup restored; checksum and integrity check {'passed' if DRILL_PASSED else 'failed'}; row counts matched in all {DRILL_TABLES} tables", 'SYNTHETIC seeded database; reports/restore_drill.md'],
  ['LLM red team', 'OWASP Top 10 for LLM Applications (2025) mapped to deterministic controls', f"{TESTS['api_redteam']} cases in CI; docs/security/LLM_RED_TEAM.md"],
  ['Browser tests', 'Every route, both themes, accessibility and mobile layout; one live upload → score → review → draft → approve flow', f"{TESTS['e2e_static']} static + {TESTS['e2e_live']} live Playwright tests"],
])}
<p>Test counts were collected on {TESTS['collected_on']} with the commands in design/test_counts.json ({TESTS['ml']} ML, {TESTS['api']} API, {TESTS['e2e_static']} + {TESTS['e2e_live']} browser). The load test ran on a local machine and the restore drill on a small synthetic database; neither has run on hosted infrastructure because no Render, Supabase or Stripe account exists yet.</p>
<div class="two">{shot('22-status-light', 'Figure 8. Status page: live component checks and service-level targets (light).')}{shot('16-landing-dark', 'Figure 9. Public landing page (dark). Pilot stage: no paying customers.')}</div>
</section>

<section>
<div class="eyebrow">11 · Course outcome mapping</div><h2>Where each outcome is shown</h2>
{table(['Outcome', 'Evidence in RetentionLens'], [
  ['A · Marketing research and predictive analytics', 'Data profile and card; rolling-cutoff lapse models; cohort terrain'],
  ['B · Traditional, web and social data', 'Wikipedia seasonality; co-purchase network; synthetic social posts; scraper'],
  ['C · CLV, churn, retention, new customers', 'BG/NBD + Gamma-Gamma; RFM segments; k-means; lookalike scoring'],
  ['D · Generative AI for marketing decisions', 'Outreach studio with checker, critic, consent gate and live evaluation'],
  ['Weeks 1–11', 'Mapped topic by topic on the Course evidence page'],
  ['Labs (weeks 2, 4, 6, 8, 10)', 'Scaffolds and generated EVIDENCE.md in labs/ · <b>[OWNER: lab reports to be written]</b>'],
])}
<div class="eyebrow" style="margin-top:12px">12 · What is still missing</div><h2>The software exists; the market evidence does not yet</h2>
<ul>
<li><b>No customer interviews</b>: buyer, workflow and price remain hypotheses (kit ready in docs/research).</li>
<li><b>No usability sessions</b>: the ten-minute first-run target is untested with real users.</li>
<li><b>No pilot and no customers</b>: the holdout queue has produced no uplift result, so there is no causal evidence that outreach helps.</li>
<li><b>No hosting</b>: Render, Supabase and Stripe test accounts are not created; everything ran locally or as a static demo.</li>
<li>The AI reviewer is uncalibrated (no human labels); social data is synthetic; one UK giftware wholesaler, 2009–2011.</li>
</ul>
<h3>Reflection</h3>
<div class="note"><b>[OWNER: reflection and learning narrative to be written by the student. Not generated.]</b></div>
<h3>References</h3>
<p class="mono">Chen, D. (2019). Online Retail II. UCI Machine Learning Repository. doi:10.24432/C5CG6D · Fader, Hardie &amp; Lee (2005). Counting your customers the easy way. Marketing Science 24(2) · Wang, Liu &amp; Miao (2019). A deep probabilistic model for CLV prediction. arXiv:1912.07753 · Hwang (2019). Hands-on Data Science for Marketing. Packt · Winston (2014). Marketing Analytics. Wiley · Grigsby (2018). Marketing Analytics. Kogan Page · OWASP Top 10 for LLM Applications (2025).</p>
</section>

<section>
<div class="eyebrow">Appendix · Mobile</div><h2>The same product on a phone</h2>
<div class="phones">
{shot('13-phone-overview-dark', 'Overview, 390 px, dark')}{shot('14-phone-accounts-light', 'Account evidence, 390 px, light')}{shot('15-phone-segments-dark', 'Segments, 390 px, dark')}
{shot('24-phone-landing-dark', 'Landing page, 390 px, dark')}{shot('25-phone-queue-light', 'Weekly queue, 390 px, light')}
</div>
<p class="mono">Illustrations generated by the author with ChatGPT Images (gpt-image-2). Screenshots captured from the running application on {date.today().isoformat()}.</p>
</section>
</body></html>"""

out = ROOT / "design" / "report" / "report.html"
out.write_text(html)
print("wrote", out.relative_to(ROOT))
