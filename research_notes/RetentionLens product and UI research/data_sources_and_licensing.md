# Data sources and licensing for RetentionLens (MAIB AI 208, outcome B)

Research date: 2026-11-01. Researcher notes for the report writer. Labels used: VERIFIED OBSERVATION (fetched or executed in this session), UNVERIFIED (not confirmed from a primary source), CONFLICT (sources disagree), INFERENCE (my reasoning, not a sourced fact). Nothing here is legal advice.

Method note: primary pages were fetched with WebFetch or `curl` (UCI page and API, Kaggle public metadata API, OpenML API, Hugging Face API, Reddit Data API Terms HTML, Yelp Dataset Terms PDF, GDELT, Common Crawl, Wikimedia, toscrape/webscraper.io robots.txt, GitHub/PyPI APIs). Secondary sources (law-firm alerts, blogs) are marked as such. The Online Retail II file itself was NOT downloaded in this session (not present in `data/raw/`), so dataset-quality counts come from OpenML's profile and must be re-verified locally.

## 1. UCI Online Retail II: licence, citation, schema, size, quality issues, redistribution

### Takeaway
Online Retail II is CC BY 4.0 on UCI (DOI 10.24432/C5CG6D), 1,067,371 rows across one .xlsx with two sheets, 01/12/2009 to 09/12/2011; redistribution in a public repo is legally permitted with attribution, but committing a fetch script plus SHA-256 checksum is the better choice than committing the 43.5 MB file. About 22.8% of rows (243,007) have no Customer ID, so they cannot be used for customer-level CLV or churn.

### Cited Findings
- Licence: "Creative Commons Attribution 4.0 International (CC BY 4.0)", which permits sharing and adaptation for any purpose with credit. VERIFIED OBSERVATION. [UCI dataset page](https://archive.ics.uci.edu/dataset/502/online+retail+ii)
- DOI 10.24432/C5CG6D. Citation: Chen, D. (2012). Online Retail II [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D. Creator: Daqing Chen. Donated 2019-09-20. [UCI dataset page](https://archive.ics.uci.edu/dataset/502/online+retail+ii)
- Instances: 1,067,371. Characteristics: Multivariate, Sequential, Time-Series, Text. Subject area: Business. Missing values flagged "Yes" on the HTML page. [UCI dataset page](https://archive.ics.uci.edu/dataset/502/online+retail+ii)
- CONFLICT: the UCI JSON API returns `has_missing_values: "no"`, `num_features: 0` and blank variable rows for id 502 (last_updated "Fri Jan 05 2024"), contradicting the HTML page. The API metadata is unreliable for this dataset. VERIFIED OBSERVATION. [UCI API id=502](https://archive.ics.uci.edu/api/dataset?id=502)
- File: `online_retail_II.xlsx`, 43.5 MB, distributed as a zip. Date range 01/12/2009 to 09/12/2011. A UK-based, registered, non-store online retailer selling mainly "unique all-occasion gift-ware"; many customers are wholesalers. [UCI dataset page](https://archive.ics.uci.edu/dataset/502/online+retail+ii)
- Documented variables (UCI "Additional Variable Information"): InvoiceNo (nominal, 6-digit; starts with "c" = cancellation), StockCode (nominal, 5-digit product code), Description (nominal), Quantity (numeric), InvoiceDate (date-time), UnitPrice (numeric, GBP), CustomerID (nominal, 5-digit), Country (nominal). [UCI dataset page](https://archive.ics.uci.edu/dataset/502/online+retail+ii)
- CONFLICT, header names: OpenML's ingested copy names the columns `Invoice, StockCode, Description, Quantity, InvoiceDate, Price, Customer_ID, Country`, so the actual file headers (Invoice, Price, "Customer ID") differ from UCI's documented names (InvoiceNo, UnitPrice, CustomerID). Code must not hard-code the documented names. [OpenML features API, d/43368](https://www.openml.org/api/v1/json/data/features/43368)
- Two sheets, "Year 2009-2010" and "Year 2010-2011". A Kaggle listing shows 525,461 rows in the 2009-2010 sheet (secondary). [Kaggle mirror, jillwang87](https://www.kaggle.com/datasets/jillwang87/online-retail-ii); [Kaggle, amelieinsights](https://www.kaggle.com/datasets/amelieinsights/online-retail-ii-data-set)
- Missing values (OpenML profile, both sheets combined): 1,067,371 instances; 243,007 instances with a missing value; 247,481 missing cells; Customer_ID missing 243,007; Description missing 4,474; all other columns 0 missing. VERIFIED OBSERVATION via API. [OpenML qualities API](https://www.openml.org/api/v1/json/data/qualities/43368); [OpenML features API](https://www.openml.org/api/v1/json/data/features/43368)
- 5,942 unique Customer IDs and 43 unique countries (from the OpenML dataset profile as quoted in search results; the features API call did not return distinct counts). [OpenML d/43368](https://api.openml.org/d/43368)
- Cancellations are flagged by an invoice starting with "C"; negative quantities appear as returns. Cleaning guides commonly drop exact duplicates or dedupe on (invoice, stock code, customer). Secondary sources. [RPubs analysis](https://rstudio-pubs-static.s3.amazonaws.com/1370599_f96adaeaffcd4ddd965e0f4169a8c281.html); [technetexperts cleaning guide](https://www.technetexperts.com/ecommerce-data-cleaning-imputation/amp/)
- An independent pipeline built on the file excluded cancellations, "six bad-debt adjustments" and invoices with no positive value, leaving 40,076 purchase invoices (Dec 2009 to Dec 2011). [Meridian Online Retail II protocol](https://meridian.online/protocols/library/online_retail_ii)
- Do not mix figures with the older 541,909-row "Online Retail" (I) dataset, which has different counts (e.g. 135,080 missing CustomerIDs). [OpenML / search summary](https://api.openml.org/d/43368); [UCI API id=352](https://archive.ics.uci.edu/api/dataset?id=352)
- CONFLICT, licence labels on mirrors: Kaggle mirror `mashlyn/online-retail-ii-uci` is labelled "CC0: Public Domain" by its uploader; OpenML d/43368 also says "CC0: Public Domain" with no original URL or citation. The upstream UCI licence (CC BY 4.0) governs. These mirror labels are not authoritative. VERIFIED OBSERVATION. [Kaggle API, mashlyn](https://www.kaggle.com/api/v1/datasets/view/mashlyn/online-retail-ii-uci); [OpenML API d/43368](https://www.openml.org/api/v1/json/data/43368)

### Inferences
- Redistribution: CC BY 4.0 allows copying and redistribution in a public GitHub repo if you credit the creator, link the licence, and indicate changes. INFERENCE from the licence named on the UCI page. Recommended practice: keep the raw file out of git (43.5 MB is near GitHub's soft limits and bloats history). Commit `scripts/fetch_online_retail_ii.py` that downloads from UCI, records URL, retrieval date and SHA-256 in `data/raw/MANIFEST`, plus a small, attributed derived sample (e.g. 1-5k rows) for tests.
- Special or non-product StockCodes (POST, M, D, BANK CHARGES, AMAZONFEE, DOT, C2, ADJUST, TEST) are widely reported in notebooks, but I found no primary source with counts. Treat this as a TODO: compute it locally with a profiling script and save the output as evidence. Exclude non-product codes from CLV monetary value but keep POST/DOT as a "shipping" feature.
- Wholesale signal: quantity distribution and the "many customers are wholesalers" note support a B2B framing, but there is no explicit B2B/B2C flag. Any "wholesaler" segment is a HYPOTHESIS derived from basket size, not ground truth.
- Privacy: Customer IDs are pseudonymous 5-digit codes with country. Re-identification risk looks low, but under UK GDPR, pseudonymised data can still count as personal data. INFERENCE. Never enrich IDs with external data.
- Required cleaning flags for the pipeline (TODO, verify locally): cancellation flag (`Invoice` starts with "C"), negative quantity, zero or negative price, missing Customer ID, duplicate rows, non-product StockCode, overlap of Dec 2010 days across the two sheets (Meridian notes the sheets share days).

### Gaps
- Exact counts of cancellations, negative quantities, exact duplicates, zero-price rows and special StockCodes: no primary source found. Must be computed from the file.
- Whether the two sheets overlap on 2010-12-01 to 2010-12-09: only Meridian's note says they share days. Unverified, check locally.
- SHA-256 of the official zip was not computed (file not downloaded in this session).

## 2. Other transactional retail/CLV datasets: licence and suitability

### Takeaway
Only Online Retail I/II (CC BY 4.0, UCI) and Olist (CC BY-NC-SA 4.0, verified via Kaggle API) have clearly stated licences. Dunnhumby, Instacart and CDNOW licences could not be confirmed from the data owners, so the repo should link to them but not redistribute them.

### Cited Findings
- Online Retail (I), UCI id 352: 541,909 instances, the same 8 variables, 01/12/2010 to 09/12/2011, a subset of the same retailer (API last_updated "Mon Oct 21 2024"). Licence not returned by the API; the UCI site generally lists CC BY 4.0, but that was UNVERIFIED for id 352 in this session. [UCI API id=352](https://archive.ics.uci.edu/api/dataset?id=352)
- Olist Brazilian E-Commerce: licence "CC BY-NC-SA 4.0" (non-commercial, share-alike); ~126.2 MB; about 100k orders from 2016 to 2018 across multiple Brazilian marketplaces, with order status, price, payment, freight, customer location, product attributes and review text. It is real, anonymised commercial data, with partner names in reviews replaced by "Game of Thrones great houses". A companion Marketing Funnel dataset can be joined to it. VERIFIED OBSERVATION. [Kaggle API, olistbr/brazilian-ecommerce](https://www.kaggle.com/api/v1/datasets/view/olistbr/brazilian-ecommerce); [Kaggle page](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- Olist structure: 8 related tables (customers, sellers, products, payments, reviews, etc.). Secondary. [scripts-and-tables course page](https://scripts-and-tables.github.io/daa/data/)
- Dunnhumby "The Complete Journey": household-level transactions over two years from 2,500 frequent-shopper households, all categories, with demographics and direct-marketing contact history for some households. The Kaggle mirror `frtgnn` is labelled "Database: Open Database, Contents: Database Contents" (ODbL-style; uploader label), 847 MB, updated 2019-11-07. [Kaggle API, frtgnn](https://www.kaggle.com/api/v1/datasets/view/frtgnn/dunnhumby-the-complete-journey)
- Dunnhumby distributes it via its "Source Files" page as a teaching and practice resource; the licence text was not visible in results. [dunnhumby source files](https://www.dunnhumby.com/source-files/)
- The `completejourney` R package attributes its data to 84.51°'s Complete Journey study. The Python port `completejourney_py` describes its data as simulated, for education, and says to contact 84.51° for real-data licensing. [CRAN completejourney](https://search.r-project.org/CRAN/packages/completejourney/index.html); [completejourney_py licence page](https://cunningjames.github.io/completejourney_py/about/license)
- Instacart Market Basket: Kaggle mirrors (`psparks`, `yasserh`) are labelled "CC0: Public Domain" by their uploaders (~713 MB). The original Instacart release page (`instacart.com/datasets/grocery-shopping-2017`) now returns 404, so the original terms are UNVERIFIED. VERIFIED OBSERVATION of labels and 404. [Kaggle API, psparks](https://www.kaggle.com/api/v1/datasets/view/psparks/instacart-market-basket-analysis); [Instacart original URL (404)](https://www.instacart.com/datasets/grocery-shopping-2017)
- CDNOW: Bruce Hardie hosts a 1/10th sample (ZIP 51k) and the full dataset (ZIP 424k). No licence text was found on the page. [Bruce Hardie datasets](https://www.brucehardie.com/datasets/)
- Kaggle `carrie1/ecommerce-data` (Online Retail I mirror) is labelled licence "Unknown". [Kaggle API, carrie1](https://www.kaggle.com/api/v1/datasets/view/carrie1/ecommerce-data)

### Inferences
- Suitability for CLV/churn (INFERENCE):
  - Online Retail II is the best fit: B2B-leaning giftware, multi-year, repeat purchases, BG/NBD and Gamma-Gamma friendly.
  - CDNOW is the canonical BG/NBD benchmark (Fader/Hardie). Use it for model-validation parity but do not redistribute it, since no licence was found.
  - Olist is mostly one-off customers (low repeat rate per common analyses, unverified here), so it is weak for CLV but strong for review text, delivery and satisfaction. Its NC-SA licence means derived data in the repo must also be CC BY-NC-SA and non-commercial.
  - Dunnhumby is B2C grocery with campaign history, useful for uplift and outreach-response modelling, but its licence is unverified.
  - Instacart has no timestamps (relative days only, widely known but unverified here), so it is poor for CLV.
- Recommendation: Online Retail II is the primary dataset. CDNOW serves only as a reproducibility benchmark, fetched at runtime. Olist is an optional "review text + transactions" secondary demo under NC-SA, kept in a separate `data/external/olist/` with its own LICENSE note.

### Gaps
- Dunnhumby's own terms of use text (not retrieved).
- Instacart original 2017 licence/terms (page now 404; no archived copy checked).
- CDNOW licence (none stated on host page).
- UCI id 352 licence (not returned by the API in this session).

## 3. Web and social-media sources for outcome B (traditional + web + social)

### Takeaway
Licence-clean, linkable web signals for UK giftware exist:
- Wikimedia pageviews: CC0, verified working.
- GDELT: free, with citation.
- Google Trends: manual export, or the official alpha API if approved.

Social and review text is the hard part:
- Amazon Reviews 2023 declares no licence.
- Yelp's dataset terms forbid public display, redistribution and commercial use, and require Yelp review before publication.
- Reddit's Data API Terms (last revised 20 July 2026) bar AI/ML training on user content without rightsholder permission, and require deletion of data beyond the approved use.
- Bluesky search now needs authentication.

The safest outcome-B design is real traditional data (UCI), real aggregate web signals (Wikipedia, Trends, GDELT), and clearly labelled synthetic social posts.

### Cited Findings

#### Amazon Reviews 2023 (McAuley Lab)
- 571.54M reviews, 54.51M users, 48.19M items, 33 domains, May 1996 to September 2023. Cite Hou, Li, He, Yan, Chen and McAuley (2024), "Bridging Language and Items for Retrieval and Recommendation", arXiv:2403.03952. [Amazon Reviews'23 site](https://amazon-reviews-2023.github.io/)
- Giftware-relevant categories: Home_and_Kitchen (67.4M ratings, 3.7M items), Arts_Crafts_and_Sewing (9.0M ratings), Handmade_Products (664.2K ratings, 164.7K items), Office_Products (12.8M ratings). Files are `.jsonl.gz` per category plus `meta_` files.
  - Review fields: rating, title, text, images, asin, parent_asin, user_id, timestamp, verified_purchase, helpful_vote.
  - Metadata fields include main_category, title, average_rating, price, store, categories, details and bought_together.
  - [Amazon Reviews'23 site](https://amazon-reviews-2023.github.io/)
- Licence: the documentation site states no licence or terms. The Hugging Face dataset card has no licence tag (API: no `license:` tag; not gated; lastModified 2024-12-08). VERIFIED OBSERVATION. [HF API](https://huggingface.co/api/datasets/McAuley-Lab/Amazon-Reviews-2023); [HF dataset](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023)

#### Yelp Open Dataset
- 6,990,280 reviews, 150,346 businesses, 11 metropolitan areas, 200,100 pictures. The JSON download is 4.35 GB compressed (8.65 GB uncompressed: 1 PDF + 5 JSON). Described as "intended for educational use". [Yelp Open Dataset page](https://business.yelp.com/data/resources/open-dataset/)
- Yelp Dataset Terms of Use, "Last Updated: July 7, 2023" (VERIFIED, text extracted from the PDF). [Yelp Dataset Terms PDF](https://s3-media0.fl.yelpcdn.com/assets/srv0/engineering_pages/f64cb2d3efcc/assets/vendor/Dataset_User_Agreement.pdf)
  - The licence is solely for academic use, defined as use by nonprofits, government, educational institutions and think tanks that is not for profit or commercial. For EU data, use is limited to academic research.
  - Before any public presentation or publication of results involving the Data or the Yelp name, findings must be submitted to Yelp for review and approval.
  - Section 4 prohibits public display, distribution and sharing with third parties, and disclosing summaries or metrics without consent (academic-publication carve-out). It also prohibits commercial use, competitive use, and rating or commenting on the content.
  - Yelp owns derivative works.
  - The term is 12 months. On termination you must delete all copies.
  - Governing law: California.
- A second agreement URL is circulated by mirrors (`.../bea5c1e92bf3/.../yelp-dataset-agreement.pdf`); not fetched. [HF mirror README](https://huggingface.co/datasets/noahnsimbe/yelp-dataset/blob/main/README.md)
- Category fit: Yelp is local business (restaurants, services), not wholesale giftware. Weak fit. INFERENCE.

#### Google Trends
- The official Google Trends API is in alpha, "accepting applications for alpha testers". It covers a rolling 5-year window at daily, weekly, monthly or yearly aggregation, by country and sub-region. Data is "consistently scaled" (not 0-100 per request), which allows comparing dozens of terms. No quota or terms are published on the page. The announcement dates from July 2025. VERIFIED OBSERVATION. [Google Trends API page](https://developers.google.com/search/apis/trends); [Google Search Central blog, July 2025](https://developers.google.cn/search/blog/2025/07/trends-api)
- Third-party sources report access is still limited or invite-only during 2026. Secondary, CONFLICT on how open it is. [konabayev.com, 2026](https://konabayev.com/blog/google-trends-api-landscape-2026/); [SERoundtable](https://www.seroundtable.com/google-trends-api-applications-approvals-39978.html)
- pytrends (unofficial): the GitHub repo GeneralMills/pytrends is archived (`archived: true`, last push 2024-08-10). The latest PyPI release is 4.9.2. VERIFIED OBSERVATION. [GitHub API](https://api.github.com/repos/GeneralMills/pytrends); [PyPI](https://pypi.org/project/pytrends/). A blog headline calls it "dead" in 2026 (secondary). [dev.to](https://dev.to/esteban_ortega/pytrends-is-dead-heres-how-to-get-google-trends-data-in-2026-1a18)

#### Reddit Data API
- Data API Terms: "Effective June 19, 2023. Last Revised July 20, 2026". VERIFIED OBSERVATION from the fetched HTML. [Reddit Data API Terms](https://redditinc.com/policies/data-api-terms)
  - No rights are granted to use User Content for training a machine-learning or AI model without the express permission of the rightsholders.
  - Commercial use, or research in excess of rate limits, needs a separate agreement.
  - You may not sell or derive revenue without written approval.
  - You must not use or retain data beyond the approved use case, and must immediately delete data not required for it.
  - You must not use the Reddit trademarks in your app name.
- Research access goes through the "Reddit for Researchers" programme or a request form. The 2023 conditions were non-commercial use, no redistribution of data or derivatives, credit to Reddit and anonymised results. Secondary.
- CONFLICT, unverified claims of 2026-2027 public-API closure dates (31 Oct 2026 vs Jan/Mar 2027). Do not rely on them without Reddit confirmation.
- [apiserpent 2026](https://apiserpent.com/blog/reddit-search-api-2026-access); [socialcrawl 2026](https://www.socialcrawl.dev/blog/reddit-data-api-2026.md)

#### Bluesky and Mastodon
- Bluesky: an unauthenticated `GET https://public.api.bsky.app/xrpc/app.bsky.feed.searchPosts?q=giftware` returned HTTP 403 on 2026-11-01. Post search now needs authentication. VERIFIED OBSERVATION (single request). The Bluesky ToS page fetched contained no scraping/AI clause matched by keyword search. [Bluesky ToS](https://bsky.social/about/support/tos)

#### Wikimedia pageviews
- "All Analytics datasets are available under the Creative Commons CC0 dedication." [Wikimedia pageviews readme](https://dumps.wikimedia.org/other/pageviews/readme.html)
- The Pageviews REST API works without a key, with a descriptive User-Agent. Example: `en.wikipedia/all-access/user/Gift_wrapping/monthly` returned 1,193 views for Jan 2025 and 837 for Feb 2025. VERIFIED OBSERVATION. [Wikimedia REST API](https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/Gift_wrapping/monthly/2025010100/2025030100)
- Bot traffic is separated into "spider" and "automated" agent categories. [Wikimedia AQS docs](https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/concepts/page-views.html)

#### Common Crawl
- Terms of Use were last updated March 7, 2024. They grant a limited, non-exclusive licence to use the Service. Use must comply with all applicable laws, and CC disclaims responsibility for Crawled Content, which remains subject to third-party rights. [Common Crawl ToU](https://commoncrawl.org/terms-of-use)

#### GDELT
- All GDELT datasets are "available for unlimited and unrestricted use for any academic, commercial, or governmental use", with redistribution allowed if it includes a citation to GDELT and a link to gdeltproject.org. [GDELT about](https://www.gdeltproject.org/about.html)

### Inferences
- Mapping to UK giftware/homeware (INFERENCE):
  - Wikipedia pageviews for articles such as Gift wrapping, Christmas decoration, Candle, Tea set and Cake stand can act as a seasonal demand index. CC0, safe to commit.
  - Google Trends (geo=GB, categories such as "Gifts & Special Event Items", "Home & Garden") gives a seasonality signal. Use a manual CSV export from trends.google.com for a handful of terms, or the alpha API if approved. Do not depend on pytrends (archived, scrapes an undocumented endpoint).
  - GDELT news-volume/tone for UK retail/gift topics gives a market-context signal.
  - Amazon Reviews 2023 Home_and_Kitchen / Handmade_Products / Arts_Crafts can supply preference text that maps to Online Retail II product descriptions (e.g. "LANTERN", "CAKE STAND"). Because no licence is declared, use it only for local analysis, publish aggregate results, cite the paper, and do not commit raw review text to the public repo.
- Yelp, Reddit and Bluesky are poor fits:
  - Yelp's terms (no public display, Yelp pre-publication review, academic institution use) conflict with a public portfolio repo and demo UI. Avoid it.
  - Reddit's terms are restrictive for an ML pipeline; its use for a coursework demo would need Reddit for Researchers approval. Avoid it in the portfolio.
  - Bluesky could serve live demos with an authenticated app account, but the ToS for AI use was not confirmed.
- Common Crawl is too heavy for a 20-hour-a-week solo project, and its content carries third-party rights. Skip it.

### Gaps
- Mastodon: instance-specific terms; not researched. Unverified.
- Bluesky Developer Guidelines on AI/ML use and rate limits: not retrieved. Unverified.
- Amazon Reviews 2023: no licence or terms found anywhere official; whether Amazon's own terms apply to downstream use is unclear.
- Google Trends website export terms (Google ToS) not fetched.
- Reddit for Researchers programme current eligibility (2026) not confirmed from a Reddit primary page; help-centre article fetch returned nothing usable.

## 4. Legal and ethical rules for web scraping (Week 10: Competitive Intelligence and Web Data Acquisition)

### Takeaway
In US case law, scraping public, logged-out data is not automatically illegal: Meta lost on logged-out scraping and dropped its appeal. But contract (ToS) and trespass claims can bite: hiQ ended with a consent judgment against it. In the UK and EU, the binding constraint is data protection; per the ICO, legitimate interests is the only realistic basis for scraping personal data. For a student, the defensible demo is a polite, robots-aware scraper against a purpose-built sandbox (toscrape.com), never personal data.

### Cited Findings
- hiQ v. LinkedIn:
  - In Nov 2022 the N.D. Cal. found hiQ breached LinkedIn's User Agreement.
  - On 6 Dec 2022 the parties filed a stipulated consent judgment, granted 8 Dec 2022 with a permanent injunction and a $500,000 judgment against hiQ. hiQ also stipulated liability for trespass to chattels and misappropriation.
  - Sources: [Proskauer New Media & Technology Law blog](https://newmedialaw.proskauer.com/2022/12/08/hiq-and-linkedin-reach-proposed-settlement-in-landmark-scraping-case/); [Wikipedia](https://en.wikipedia.org/wiki/HiQ_Labs_v._LinkedIn); [Privacy World](https://www.privacyworld.blog/2022/12/linkedins-data-scraping-battle-with-hiq-labs-ends-with-proposed-judgment/)
- Meta v. Bright Data:
  - On 23 Jan 2024, Judge Edward Chen (N.D. Cal.) granted summary judgment to Bright Data. Meta's terms did not bar logged-out scraping of public data, and a "survival" clause purporting to bar scraping indefinitely was unenforceable.
  - The ruling covers only Meta's terms and does not address logged-in scraping.
  - Sources: [Farella Braun + Martel](https://www.fbm.com/business-litigation/publications/major-decision-affects-law-of-scraping-and-online-data-collection-meta-platforms-v-bright-data/); [TechCrunch](https://techcrunch.com/2024/01/24/court-rules-in-favor-of-a-web-scraper-bright-data-which-meta-had-used-and-then-sued)
- On 23 Feb 2024, Meta dismissed its remaining claim without prejudice and waived its appeal. [TechCrunch](https://techcrunch.com/2024/02/26/meta-drops-lawsuit-against-web-scraping-firm-bright-data-that-sold-millions-of-instagram-records); [Eric Goldman blog](https://blog.ericgoldman.org/archives/2024/02/facebook-drops-anti-scraping-lawsuit-against-bright-data-guest-blog-post.htm)
- UK ICO (generative-AI consultation outcome, 2024):
  - Legitimate interests is the only lawful basis the ICO considers available for scraping personal data to train generative AI.
  - Developers must demonstrate necessity and pass the balancing test, and alternatives such as licensed data or data collected directly from individuals are viable.
  - Secondary summaries: [SCL](https://www.scl.org/ico-responds-to-consultation-series-on-generative-ai/); [JD Supra](https://production.jdsupra.com/legalnews/ico-publish-outcome-report-on-ai-2666684)
- EDPB Opinion on AI models (Dec 2024) applies the three-step legitimate-interest test and stresses Article 14 transparency for indirectly collected data. Secondary. A claimed July 2026 EDPB web-scraping guideline is UNVERIFIED. [SKW Schwarz](https://www.skwschwarz.de/en/news/ki-flash-edpb-guidelines-web-scraping-ai)
- UK Data (Use and Access) Act 2025 commences in stages: from 20 Aug 2025, most Part 2 measures on 1 Dec 2025, and the bulk via Commencement No. 6 on 5 Feb 2026. Secondary plus gov.uk. [gov.uk commencement plan](https://www.gov.uk/guidance/data-use-and-access-act-2025-plans-for-commencement); [JD Supra](https://www.jdsupra.com/legalnews/key-data-protection-changes-under-the-6191325/)
- UAE PDPL (Federal Decree-Law No. 45 of 2021): sources conflict on whether and under which Cabinet Decision the Executive Regulations were issued (111/2023, 33/2024, or "2026"). Status is UNVERIFIED. [uppersetup guide](https://uppersetup.com/en/article/uae-personal-data-protection-law-pdpl-the-complete-business); [centraleyes](https://www.centraleyes.com/privacy-laws/uae/)
- Sandbox sites:
  - toscrape.com describes itself as a "Web Scraping Sandbox". books.toscrape.com is "a fictional bookstore that desperately wants to be scraped": 1,000 items, 20 per page, no JavaScript required. quotes.toscrape.com offers multiple endpoint challenges. [toscrape.com](https://toscrape.com/)
  - `https://books.toscrape.com/robots.txt` returns HTTP 404, so no robots file. VERIFIED OBSERVATION.
  - webscraper.io's robots.txt disallows `/test-sites/product/`, `/test-sites/pagination/`, `/test-sites/scroll/` and `/test-sites/load-more/` for all user-agents. Even a "test site" has paths a polite crawler must skip. VERIFIED OBSERVATION. [webscraper.io robots.txt](https://webscraper.io/robots.txt)

### Inferences
- A safe student demonstration (INFERENCE / recommended practice):
  - Scrape books.toscrape.com only, as a stand-in for "competitor catalogue price monitoring".
  - Check robots.txt with `urllib.robotparser` even when it returns 404, and log the result.
  - Set an identifying User-Agent with contact info, use 1 request/sec or slower with jitter, cache responses, and stop on 429/5xx with exponential backoff.
  - Never log in, never bypass CAPTCHAs or paywalls, and collect no personal data.
  - Store URL, timestamp, HTTP status and a content hash per record as provenance.
  - Pair this with a "decision memo" slide covering hiQ (contract/trespass risk survives), Meta v. Bright Data (logged-out public data, ToS limits), UK GDPR/ICO (personal data needs a lawful basis, legitimate-interest assessment and transparency), and copyright/database rights.
- For real competitor sites (UK giftware wholesalers), the deliverable should be a written legitimate-interest and ToS assessment plus a manual sample, not an automated crawl.
- The project already has an `ethical-web-agent` skill available. The report writer may reference it as the implementation checklist.

### Gaps
- RFC 9309 (Robots Exclusion Protocol) text was not fetched this session. Cite [RFC 9309](https://www.rfc-editor.org/rfc/rfc9309) as the standard, but the content is unverified here.
- UK sui generis database right and the CDPA s.29A text-and-data-mining exception (non-commercial research): not researched in this session.
- No primary ICO outcome-report URL was fetched (only secondary summaries).
- No UAE-specific case law or guidance on scraping was found.

## 5. Synthetic social posts and reviews when no licensed source fits

### Takeaway
Generate synthetic posts and reviews grounded in the real UCI product catalogue. Use a seeded, versioned generator with an explicit `is_synthetic=true` column, a provenance manifest, and a visible "SYNTHETIC DEMO" badge in the UI. Faker (MIT) is fine for scaffolding. SDV's licence is not a standard OSI licence and should be checked before use.

### Cited Findings
- Faker on PyPI: version 40.44.0, licence "MIT License". VERIFIED OBSERVATION. [PyPI Faker](https://pypi.org/project/Faker/)
- SDV (Synthetic Data Vault): GitHub reports its licence as "Other" (SPDX NOASSERTION). PyPI 2.1.0 has no licence field. The repo was active (last push 2026-10-30). The exact licence terms are UNVERIFIED in this session. VERIFIED OBSERVATION of metadata. [GitHub API sdv-dev/SDV](https://api.github.com/repos/sdv-dev/SDV); [PyPI sdv](https://pypi.org/project/sdv/)
- Olist demonstrates a real precedent for de-identifying review text by replacing company and partner names with fictional placeholders. [Kaggle Olist description](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- Reddit's terms prohibit using Reddit content to train ML/AI models without rightsholder permission, so Reddit text must not be used as few-shot seeds or fine-tuning data for a synthetic generator. [Reddit Data API Terms](https://redditinc.com/policies/data-api-terms)

### Inferences
- Recommended method (INFERENCE):
  1. Sample real product descriptions and countries from Online Retail II (CC BY 4.0, attributable).
  2. Use an LLM with a fixed prompt template, temperature and seed. For each (product, persona, sentiment target, channel ∈ {review, social post, B2B email reply}), generate short text. Persona types are fictional (e.g. "independent gift-shop owner, Leeds"), with no real people or brands.
  3. Store `synthetic_id, source_stockcode, channel, target_sentiment, generator_model, prompt_version, seed, created_at, is_synthetic=true` in `data/synthetic/MANIFEST.json`.
  4. Validate by running the same sentiment/aspect model on the synthetic set and reporting agreement with target labels. Report that this measures generator controllability, not real customer preference.
  5. In the UI, badge every synthetic-derived chart as "SYNTHETIC DEMO" and keep it out of any CLV figure.
- Positioning for outcome B: be honest that "social" evidence is synthetic, while the "web" evidence (Wikipedia pageviews CC0, Google Trends export, GDELT) is real aggregate data. The synthesis across traditional, web and social then has real, real and simulated legs, which the assessment write-up should state explicitly.
- A tabular synthetic copy of transactions (e.g. SDV GaussianCopula) is optional and should only be used for privacy-safe test fixtures, not for reported model metrics.

### Gaps
- No academic or regulatory guidance on labelling synthetic marketing text was retrieved in this session (e.g. EU AI Act Art. 50 transparency obligations and their application dates were not checked).
- SDV licence text (believed to be a source-available Business Source License) was not confirmed. Treat it as unverified until LICENSE is read.
