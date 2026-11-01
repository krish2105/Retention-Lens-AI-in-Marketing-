# RetentionLens: premium 3D analytics UI, theme system and ChatGPT image-prompt research (as of 2026-11-01)

Scope: research notes for the designer, who will propose 3-4 visual directions for the RetentionLens dashboard (customer retention and CLV decisions for wholesalers; Next.js + React 19 + TypeScript frontend, FastAPI backend; solo student, AI-in-Marketing course plus portfolio) and then build one.

Evidence labels:
- **VERIFIED OBSERVATION** means checked directly this session, either by `npm view` on 2026-11-01 or by fetching the page.
- **SECONDARY** means it comes from a search-result summary or a third-party article.
- **ASSUMPTION / INFERENCE** means it is my reasoning, not a sourced claim.

**VERIFIED OBSERVATION: npm `latest` versions on 2026-11-01** (run with `npm view <pkg> version`; each package page is at https://www.npmjs.com/package/<pkg>)

| Package | Version | Note |
|---|---|---|
| three | 0.187.0 | r187 |
| @react-three/fiber | 9.8.2 | |
| @react-three/drei | 10.7.9 | |
| @react-three/postprocessing | 3.2.2 | |
| motion | **14.9.0** | not v12, see below |
| next-themes | 0.4.6 | |
| tailwindcss | 4.3.3 | |
| recharts | 3.10.1 | |
| lenis | 1.3.27 | |
| gsap | 3.15.0 | |
| react-force-graph-3d | 1.29.2 | |
| globe.gl | 2.46.2 | |
| @splinetool/react-spline | 4.1.0 | |
| @visx/visx | 4.0.0 | |
| @nivo/core | 0.99.0 | |
| echarts | 6.1.0 | |
| @observablehq/plot | 0.6.17 | |
| geist (font package) | 1.9.0 | |
| next | **16.4.3** | project is on 15 |
| react | 19.3.1 | |

Two flags for the designer:
- `motion` latest is v14, not v12. The brief's assumption is out of date.
- `next` latest is v16, while the project is on Next.js 15. Pin to whatever the project's `package.json` actually uses. I did not read it, so that check is still a TODO.

---

## 1. Distinctive 2025-2026 dashboard/SaaS visual directions, and what makes them premium rather than templated

### Takeaway
I could not source a citable 2026 survey of design directions. The strongest primary evidence is Linear's own write-up of its theme system: three inputs (base, accent, contrast) in a perceptual colour space (LCH) generate every surface elevation, and the 2026 refresh made sidebars dimmer so content stands out. The lesson for premium work is that the system is restrained and the colour is perceptually derived; it is not about decoration.

### Cited Findings
- **Linear's theme generator.** Linear moved theme generation from HSL to LCH. Instead of defining 98 variables per theme, it now defines three: base colour, accent colour and contrast. LCH was chosen as one of the colour spaces "closest to human perception", and it derives the different surface elevations (backgrounds, panels, dialogs, modals). — [Linear: How we redesigned the Linear UI](https://linear.app/now/how-we-redesigned-the-linear-ui) (March 2024; summarised via search, not fetched in full)
- **Linear's 2026 refresh.** Linear's 2026 UI refresh changelog (dated 2026-03-12) describes a "calmer, more consistent interface", with navigation sidebars "slightly dimmer so the main content stands out". — [Linear changelog 2026-03-12 (mirror)](https://linear-web.pages.dev/changelog/2026-03-12-ui-refresh) (mirror domain, SECONDARY)
- **Third-party analysis of Linear's aesthetic.** It covers tokens, density and keyboard-first UX. — [buildmvpfast: The Linear Aesthetic, Decoded (2026)](https://www.buildmvpfast.com/blog/linear-aesthetic-tokens-density-keyboard-first-ux-2026) (SECONDARY, not fetched)
- **The same LCH/OKLCH logic is in this stack.** shadcn/ui converted its default palette from HSL to OKLCH (see Section 3). Linear's approach can therefore be reproduced directly with the project's own tooling. — [shadcn/ui Tailwind v4 docs](https://ui.shadcn.com/docs/tailwind-v4)

### Inferences (ASSUMPTION; design judgement, not sourced)

I propose four candidate directions for RetentionLens:

**A. "Ledger / Editorial"**
- Warm paper-white light theme with a deep ink dark theme.
- A serif display face (Instrument Serif) for the headline numbers and section titles, Geist Sans for UI text and Geist Mono for figures.
- Thin rules, generous whitespace and footnote-style provenance labels under every chart.
- 3D is used sparingly: a single "customer constellation" hero.
- Reads like a Financial Times or Stripe Press annual report. It suits a decision tool aimed at finance-minded wholesalers.

**B. "Instrument / Linear-dark"**
- Dark-first, dense, keyboard-first, with a command palette (cmdk).
- A three-variable OKLCH theme (base, accent, contrast) with a single saturated accent, for example electric teal for "retained" and coral for "at risk".
- Mono numerals and small caps labels.
- 3D lives in a "Galaxy" tab: an RFM point cloud on a near-black background with bloom.
- Closest to Linear, Raycast and Vercel. Premium comes from restraint, alignment and speed.

**C. "Soft Clay / Tactile 3D"**
- Light pastel surfaces with soft matte clay 3D objects, for example a stack of crates for wholesale and a magnet for retention.
- Large rounded bento cards.
- Assets are generated with ChatGPT Images (Section 8) and kept consistent with a locked style block.
- Friendliest for a portfolio. The risk is that it reads as "template Dribbble" unless the data views stay crisp.

**D. "Data-Art / Aurora"**
- A deep gradient-mesh (aurora) background held to low opacity behind frosted-glass panels.
- 3D cohort terrain: a retention surface where the x axis is cohort month, the y axis is months since acquisition, and height is retention %.
- Most "Awwwards". It carries the highest performance and accessibility risk, because text over gradients needs contrast checks.

What separates premium from templated, as a working heuristic:
- A single deliberate type pairing.
- Tabular numerals.
- A colour system derived in a perceptual space rather than picked swatches.
- One signature interaction (for example the galaxy, or the theme reveal), not ten.
- Consistent 4/8px spacing.
- Real data with provenance labels.
- No stock gradients or glass on every card.

### Gaps
- No primary sources were fetched for Vercel, Raycast, Arc, Stripe, Mercury, Ramp, Attio, Hex or Rive design rationale, or for specific Awwwards, Godly or Mobbin data-product entries. I stopped at the tool-call budget. Direction labels A-D are design judgement, not cited trends.
- There is no citable source that "bento grid", "aurora" or "clay 3D" are the 2026 trend leaders. Treat them as stylistic options, not evidence.

---

## 2. 3D on the web for data products: libraries, meaningful uses, performance, fallbacks and accessibility

### Takeaway
The stack that works with React 19 today is R3F v9 (9.8.2), drei 10.7.9, @react-three/postprocessing 3.2.2 and three 0.187. For a 5k-account RFM "customer galaxy", use one `instancedMesh` (or `points`), `frameloop="demand"`, capped `dpr` and `PerformanceMonitor`. Load the scene lazily, client-only. Pair it with a data-table equivalent, and with a static or 2D fallback for no-WebGL and `prefers-reduced-motion`. Keep WebGLRenderer as the default. WebGPURenderer falls back to WebGL2, but it does not support the classic EffectComposer post-processing.

### Cited Findings
- **R3F v9 and React 19.** R3F v9 is the React 19 compatibility release, with breaking changes around Strict Mode. — [R3F v9 migration guide](https://r3f.docs.pmnd.rs/tutorials/v9-migration-guide)
- **R3F v9 and React 19.0-19.2.** The v9.5.0 release notes say R3F works with React 19.0 to 19.2 because it now bundles its own reconciler. — [R3F v9.5.0 release](https://github.com/pmndrs/react-three-fiber/releases/tag/v9.5.0)
- **React 19.3 is unconfirmed (TODO).** npm `react` latest is 19.3.1 and R3F is 9.8.2 (VERIFIED, npm). I found no statement that R3F 9.8.x supports React 19.3, so verify with a smoke test.
- **R3F v8 does not work with React 19 or Next 15.** — [R3F v9 migration guide](https://r3f.docs.pmnd.rs/tutorials/v9-migration-guide)
- **drei peer dependencies and v11.** drei 10.7.x declares peer deps `@react-three/fiber ^9.0.0` and `three >=0.159`. A v11 line exists in alpha (11.0.0-alpha.6 seen). — [drei 10.7.7 package.json](https://cdn.jsdelivr.net/npm/@react-three/drei@10.7.7/package.json); [newreleases drei 10.7.8](https://newreleases.io/project/npm/@react-three/drei/release/10.7.8)
- **On-demand rendering.** `<Canvas frameloop="demand">` renders only on change. `invalidate()` requests a frame after external mutations, and drei controls call it automatically. — [R3F: Scaling performance](https://r3f.docs.pmnd.rs/advanced/scaling-performance) (fetched)
- **Instancing.** Each mesh is a draw call, so keep well under 1,000, ideally a few hundred. Use `<instancedMesh args={[null, null, count]}>` with `setMatrixAt` and `instanceMatrix.needsUpdate = true`. — [R3F: Scaling performance](https://r3f.docs.pmnd.rs/advanced/scaling-performance)
- **Adaptive quality.** Use `dpr` state plus `<PerformanceMonitor onIncline onDecline flipflops onFallback>`. `performance.regress()` lowers quality while moving, configured with `<Canvas performance={{ min: 0.5 }}>`. Other levers are `<Detailed distances>` for LOD, shared geometry and materials, `useLoader` caching, nested `<Suspense>` and `startTransition`. — [R3F: Scaling performance](https://r3f.docs.pmnd.rs/advanced/scaling-performance)
- **WebGPURenderer.** It uses a WebGPU backend by default with a WebGL 2 fallback. It needs an async init, and `forceWebGL` can force the fallback for testing. WebGLRenderer "is still maintained" and is the recommended choice for pure WebGL 2 apps. EffectComposer and its passes are not supported with WebGPURenderer. — [three.js manual: WebGPURenderer](https://threejs.org/manual/en/webgpurenderer) (via search summary)
- **WebGPU maturity claims conflict.** Some third-party guides claim WebGPU is "production-ready since r171". Others say it is still marked experimental. — [utsubo WebGPU migration guide 2026](https://www.utsubo.com/blog/webgpu-threejs-migration-guide); [OpenReplay WebGPU vs WebGL](https://blog.openreplay.com/webgpu-vs-webgl-industry-moving/) (SECONDARY, opinion)
- **Mobile WebGPU support** is reported to be uneven, so test the fallback path explicitly. — [utsubo WebGPU migration guide](https://www.utsubo.com/blog/webgpu-threejs-migration-guide) (SECONDARY)
- **Other 3D packages are current** (VERIFIED, npm): react-force-graph-3d 1.29.2, globe.gl 2.46.2 and @splinetool/react-spline 4.1.0.

### Inferences (ASSUMPTION)

**Meaningful 3D uses for RetentionLens** (each must answer a business question):
1. **Customer galaxy.**
   - Each point is an account, with x = recency, y = frequency, z = monetary (log-scaled).
   - Colour shows churn-risk band, and size shows predicted CLV.
   - Hovering or focusing a point shows a tooltip and opens the account drawer.
   - Implement with a single `instancedMesh` of low-poly spheres (5k instances means one draw call), or `<points>` with a custom size attenuation.
2. **Segment clusters.** Show a convex hull or soft sphere per RFM/k-means segment, labelled with drei `<Html>`, and dim non-selected segments.
3. **Cohort terrain.** A `PlaneGeometry` displaced by the retention matrix (cohort by month offset). Useful as a hero, but a 2D heatmap is more legible for actual decisions, so keep the heatmap as the primary view.
4. **Avoid globe.gl** unless the dataset has meaningful geography. **Avoid** react-force-graph-3d unless there is a real network, such as customer-to-product co-purchase.

**Performance budget** (my proposal, not a sourced standard):
- Lazy-load with `next/dynamic(() => import('./Galaxy'), { ssr: false })` so three.js (roughly hundreds of kB) is not in the dashboard's first-load JS.
- Use `dpr={[1, 1.5]}`, `frameloop="demand"` and `PerformanceMonitor`.
- Use bloom from @react-three/postprocessing only in the dark theme, and disable it on decline.
- Pause rendering when the canvas is off-screen.

**Fallbacks:**
- Detect WebGL. On failure, render a 2D scatter with the same encodings (Recharts or visx).
- If `prefers-reduced-motion: reduce`, disable auto-rotate and camera tweens, and keep `frameloop="demand"`.
- Always offer a "View as table" toggle.

**Canvas accessibility:**
- Give the `<canvas>` `role="img"` and an `aria-label` that summarises the view, for example "5,000 accounts plotted by recency, frequency, monetary; 412 high-risk".
- Provide an adjacent sortable data table with the same rows.
- Mirror selection state between the canvas and the table.
- Make keyboard focus on table rows highlight the corresponding point.

**Re-theming 3D:** Read CSS custom properties with `getComputedStyle(document.documentElement).getPropertyValue('--chart-1')` on theme change, convert to `THREE.Color`, then call `invalidate()`. Keep `THREE.ColorManagement` enabled, as R3F's docs advise when creating colours outside the Canvas.

### Gaps
- I did not fetch drei `<Html>`/`<Instances>` docs, @react-three/postprocessing docs or the Spline runtime docs. Their exact APIs should be checked when building.
- I did not confirm whether @react-three/postprocessing 3.x works with WebGPURenderer (likely not, given that EffectComposer is unsupported).
- I found no official R3F accessibility guidance in this session. The pmndrs `@react-three/a11y` package exists to my knowledge, but I did not verify that it is current, so treat it as UNVERIFIED.
- I did not measure bundle-size numbers for three or R3F.

---

## 3. Theme systems: next-themes, OKLCH tokens, Tailwind v4, shadcn/ui and the View Transitions toggle

### Takeaway
Use next-themes 0.4.6 with `attribute="class"`, `defaultTheme="system"`, `enableSystem`, `disableTransitionOnChange` and `suppressHydrationWarning` on `<html>`. Use Tailwind 4.3 with `@custom-variant dark (&:where(.dark, .dark *));` and shadcn/ui's OKLCH token pattern: raw `oklch()` values on `:root` and `.dark`, mapped through `@theme inline`. Optionally wrap the toggle in `document.startViewTransition` for a circular reveal, falling back to an instant switch.

### Cited Findings
- **next-themes is at 0.4.6** (VERIFIED, npm).
- **`suppressHydrationWarning`.** The README says you need it on `<html>`, because next-themes modifies the element before hydration. — [next-themes 0.4.6 README (unpkg)](https://app.unpkg.com/next-themes@0.4.6/files/README.md)
- **`disableTransitionOnChange`** is an optional prop, default `false`, that suppresses CSS transitions during the switch. — [next-themes 0.4.6 README](https://app.unpkg.com/next-themes@0.4.6/files/README.md)
- **`attribute="class"`** toggles a `.dark` class on `<html>`, which works with Tailwind's `dark:` variant. — [eastondev Next.js dark mode guide (2025-12-20)](https://eastondev.com/blog/en/posts/dev/20251220-nextjs-dark-mode-guide/) (SECONDARY)
- **Tailwind v4 `dark:` defaults to the media query.** Without a custom variant, `dark:` compiles to `prefers-color-scheme`. For class-based toggling, define `@custom-variant dark (&:where(.dark, .dark *));`. — [DEV: Tailwind v4 in Next.js](https://dev.to/whoffagents/tailwind-css-v4-in-nextjs-14-what-changed-and-how-to-migrate-30ik); [shadcn discussion #2996](https://github.com/shadcn-ui/ui/discussions/2996) (SECONDARY)
- **shadcn's variant selector varies** between `(&:is(.dark *))` and `(&:where(.dark, .dark *))` across sources. Use whichever the current shadcn CLI writes into `globals.css`. — same sources (conflict noted)
- **shadcn/ui on Tailwind v4 and React 19.** From the shadcn/ui Tailwind v4 page (fetched):
  - "All components are updated for Tailwind v4 and React 19."
  - "HSL colors are now converted to OKLCH."
  - It supports `@theme` and `@theme inline`.
  - `tailwindcss-animate` is deprecated in favour of `tw-animate-css` (`@import "tw-animate-css";`, 2025-03-19).
  - The `toast` component is deprecated in favour of `sonner`.
  - Every primitive has a `data-slot` attribute.
  - Chart config colours become `"var(--chart-1)"` without the `hsl()` wrapper.
  - Source: [shadcn/ui: Tailwind v4](https://ui.shadcn.com/docs/tailwind-v4)
- **Pitfall:** dark mode can fail when `@theme inline` is combined with a custom variant whose selector does not match the attribute the theme library sets, for example `data-mode` against `.dark`. — [sharedcontext tailwind-v4-dark-mode](https://sharedcontext.ai/skills/external/lohnim/tailwind-v4-dark-mode) (SECONDARY)
- **tailwindcss is at 4.3.3** (VERIFIED, npm).
- **Circular theme reveal.** The pattern is: call `document.startViewTransition()`, inside it call `flushSync(() => setTheme(next))`, then animate `clip-path: circle()` from the toggle button's `getBoundingClientRect()` centre on `::view-transition-new(root)`. Same-document view transitions are supported in Chrome, Edge and Safari 18+. Other browsers fall back to an instant toggle. — [Rebecca Deprey: View Transitions in React/Next](https://rebeccamdeprey.com/blog/view-transition-api); [addevin/theme-switch-animation](https://github.com/addevin/theme-switch-animation); [PrimeReact useViewTransition](https://v11.primereact.org/docs/hooks/use-view-transition) (SECONDARY)

### Inferences (ASSUMPTION)
- **Token architecture**, following Linear's three-variable idea:
  - Define `--base-l/c/h`, `--accent-h` and `--contrast`.
  - Derive `--background`, `--card`, `--popover`, `--muted`, `--border`, `--ring` and `--chart-1..5` in OKLCH per theme.
  - Expose them via `@theme inline { --color-background: var(--background); ... }`.
  - Use `font-variant-numeric: tabular-nums` for all KPI figures.
- **Skip the reveal** when `prefers-reduced-motion: reduce` is set. Do not combine `disableTransitionOnChange` with the view-transition animation (the snapshot already handles it).
- **Charts and 3D must subscribe to `resolvedTheme`** from `useTheme()`. Canvas, ECharts and three.js colours do not update from CSS variables automatically. SVG charts using `var(--chart-n)` re-theme for free.

### Gaps
- I did not fetch the official ui.shadcn.com/docs/dark-mode/next or the Tailwind dark-mode docs page, so the exact current selector in the shadcn template is unverified.
- MDN browser-support data for `startViewTransition` (Firefox status as of November 2026) is unverified.

---

## 4. Animation: Motion, Lenis, GSAP, and when to avoid them

### Takeaway
Use `motion` (import from `motion/react`) for UI micro-interactions and layout animations. The current npm major is v14 (14.9.0), not v12. GSAP 3.15 is now free, including the formerly paid plugins such as SplitText and MorphSVG, for commercial use. Lenis 1.3.27 smooth scroll is for marketing pages only. Do not use it inside a dense dashboard, where native scrolling, scroll-into-view and table virtualisation matter.

### Cited Findings
- **Migrating from framer-motion.** Uninstall `framer-motion`, install `motion`, and import from `motion/react`. Motion for React 12 had "no breaking changes". The known gotcha is that styled-components and Emotion may forward props to the DOM; fix with `@emotion/is-prop-valid` via `MotionConfig`. — [motion.dev React upgrade guide](https://motion.dev/docs/react-upgrade-guide) (via search summary)
- **`motion` is at 14.9.0** (VERIFIED, npm). I did not read the v13/v14 upgrade notes, so check https://motion.dev/docs/react-upgrade-guide for breaking changes before pinning.
- **GSAP licence.** Webflow made GSAP "100% free", including the former Club plugins, for everyone, Webflow customer or not. The Standard "No Charge" licence (effective 2025-04-30) allows commercial use. Webflow retains the IP and can terminate the licence for violations. — [Webflow blog: GSAP becomes free](https://webflow.com/blog/gsap-becomes-free); [GSAP Standard License](https://gsap.com/community/standard-license/)
- **`gsap-trial` is deprecated.** — [npm gsap-trial](https://npmjs.com/package/gsap-trial)
- **Current versions** (VERIFIED, npm): gsap 3.15.0 and lenis 1.3.27.

### Inferences (ASSUMPTION)
- **When to avoid animation.** Do not animate numbers that users are reading for decisions; count-up KPIs on every render are distracting. Skip scroll-jacking in the app shell, and parallax over data.
- **Reduced motion.** Respect `prefers-reduced-motion` globally with `<MotionConfig reducedMotion="user">`. This API exists in Motion to my knowledge, but I did not re-verify it this session.
- **Library split.** Use GSAP only if a marketing or landing page needs SplitText or timeline choreography. For the app itself, Motion alone is enough. Avoid shipping both to the dashboard route.

### Gaps
- I did not read the Motion v13/v14 changelogs, so whether `motion/react` imports remain unchanged in v14 is unverified.
- I did not fetch the Lenis docs.

---

## 5. Charts for a premium, themeable dashboard, and provenance labelling

### Takeaway
Recharts 3 (3.10.1) is the pragmatic default, because shadcn/ui's Chart components wrap it and take `var(--chart-n)` tokens directly. Use visx (4.0.0) for bespoke, editorial charts such as cohort heatmaps and survival curves, where full control matters. ECharts 6.1 is the choice if canvas performance with very large series is needed, but it requires manual re-theming. Upgrade Recharts past 3.0.1, which had a Strict Mode rendering bug.

### Cited Findings
- **Recharts 3.0.** It rewrote state management and added about 3,500 unit tests. `CategoricalChartState` was removed from event handlers and `Customized`. 3.0.1 did not render charts under React.StrictMode (fixed in 3.0.2). — [newreleases: recharts 3.0.0](https://newreleases.io/project/npm/recharts/release/3.0.0); [recharts releases](https://github.com/recharts/recharts/releases) (SECONDARY mirrors)
- **Recharts accessibility.** Keyboard navigation for categorical charts was added in 2.7. `role="application"` was removed from the wrapper for accessibility (2.12.5, and again in 3.1.0). — [recharts releases](https://github.com/recharts/recharts/releases)
- **shadcn chart config** uses `"var(--chart-1)"` colour tokens, so Recharts charts re-theme with CSS variables. — [shadcn/ui: Tailwind v4](https://ui.shadcn.com/docs/tailwind-v4)
- **Current versions** (VERIFIED, npm): recharts 3.10.1, @visx/visx 4.0.0, @nivo/core 0.99.0, echarts 6.1.0 and @observablehq/plot 0.6.17.

### Inferences (ASSUMPTION)

**Chart provenance labelling**, required by AGENTS.md: every chart card gets a footer line in this format:

> Source: `<dataset name + version/checksum>` · Model: `<model id, train window>` · Generated `<timestamp>` · Label: VERIFIED / SYNTHETIC DEMO

Show a visible "SYNTHETIC DEMO" badge whenever demo data is in use.

**Library fit:**
- **Nivo** is theme-object-based and heavier to restyle.
- **Observable Plot** is excellent for static editorial figures, but it is not React-native.
- **ECharts** renders to canvas. CSS variables do not apply, so call `setOption` with new colours on theme change.

### Gaps
- I did not fetch the visx, Nivo or ECharts accessibility documentation, and I did not compare bundle sizes.

---

## 6. Accessibility: WCAG 2.2 AA specifics and keyboard navigation in data tables

### Takeaway
The WCAG 2.2 AA criteria most relevant here are:
- 2.5.8 Target Size (Minimum): 24x24 CSS px.
- 2.4.11 Focus Not Obscured (Minimum): sticky headers and drawers must not hide the focused element.
- 1.4.3 contrast of 4.5:1 for text (3:1 for large text).
- 1.4.11 non-text contrast of 3:1 for UI parts and chart marks.
- 2.4.13 Focus Appearance is AAA, but a good target to aim for.

Data tables should use native `<table>` semantics with `aria-sort`. Reserve the ARIA grid pattern for cells that are actually interactive.

### Cited Findings
These criteria come from the W3C WCAG 2.2 Recommendation. I am relying on the W3C pages listed; I did not re-fetch them this session.
- 2.5.8 Target Size (Minimum), AA: targets at least 24x24 CSS px, with spacing exceptions. — [W3C Understanding 2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)
- 2.4.11 Focus Not Obscured (Minimum), AA: the focused component must not be entirely hidden by author-created content. — [W3C Understanding 2.4.11](https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html)
- 2.4.13 Focus Appearance, AAA: the focus indicator is at least as large as a 2 CSS px perimeter and has a 3:1 change in contrast. — [W3C Understanding 2.4.13](https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance.html)
- 1.4.3 Contrast (Minimum) and 1.4.11 Non-text Contrast. — [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
- Keyboard patterns for sortable tables versus data grids. — [WAI-ARIA APG: Table](https://www.w3.org/WAI/ARIA/apg/patterns/table/); [APG: Grid](https://www.w3.org/WAI/ARIA/apg/patterns/grid/)
- Recharts removed `role="application"` because it caused violations with more than one chart on a page. — [recharts releases](https://github.com/recharts/recharts/releases)

### Inferences (ASSUMPTION)
- **Check OKLCH tokens programmatically.** Test both themes for 4.5:1 text contrast and 3:1 for chart series against the card background in CI. Use axe-core or Playwright with @axe-core/playwright.
- **Never encode churn risk by hue alone.** Add an icon or pattern, plus the text label.
- **Focus ring:** a 2px `--ring` outline with a 2px offset, visible in both themes.

### Gaps
- The W3C pages were not fetched in this session. The figures quoted are standard WCAG 2.2 values, but the report writer may wish to re-confirm the exact wording.

---

## 7. Fonts: premium free options in 2026 and pairings

### Takeaway
Geist Sans/Mono (npm `geist` 1.9.0, SIL OFL) is the lowest-friction premium choice for Next.js. Satoshi and General Sans (Fontshare/ITF) are free for commercial use, but they are proprietary under the ITF Free Font License, which restricts redistribution and public hosting of the font files. That matters if the repo is public.

### Cited Findings
- **`geist` is at 1.9.0** (VERIFIED, npm).
- **ITF/Fontshare licence.** ITF says Fontshare fonts are "100% free for personal and commercial use" but are "not open-source" and remain under an ITF EULA. — [ITF: Introducing Fontshare](https://www.indiantypefoundry.com/news/introducing-fontshare)
- **Redistribution.** The ITF Free Font License restricts redistribution. One project declined to ship the font binaries publicly for this reason. — [Adom theme font LICENSES.md](https://wiki.adom.inc/adom/adom-theme/files/fonts/LICENSES.md) (SECONDARY)
- **Satoshi** is distributed via Fontshare, not Google Fonts. One aggregator claims it is "personal use only", which conflicts with ITF's own statement and is likely outdated. — [fontalternatives: Satoshi](https://fontalternatives.com/alternatives/satoshi/); [CufonFonts Satoshi](https://www.cufonfonts.com/font/satoshi)

### Inferences (ASSUMPTION)
I did not check licences for Inter, Instrument Serif, JetBrains Mono or Space Grotesk this session. To my knowledge they are all SIL OFL and on Google Fonts; verify before shipping.

Pairings:
- **A (Editorial):** Instrument Serif for display and KPIs, Geist Sans for UI, Geist Mono for figures.
- **B (Instrument):** Geist Sans plus Geist Mono throughout, or Inter Display for headers.
- **C (Clay):** General Sans or Satoshi for headings (self-hosted, files not committed publicly), Inter for body.
- **D (Aurora):** Space Grotesk for display, Inter for UI, JetBrains Mono for numbers.

Load fonts with `next/font` to avoid layout shift. Enable `tabular-nums`.

### Gaps
- The Inter Display distribution and licence, and the Instrument Serif licence, were not verified this session.

---

## 8. ChatGPT image generation (gpt-image-2 / ChatGPT Images 2.0): prompting, consistency, pitfalls and rights

### Takeaway
The current model is **gpt-image-2**: API launch 2026-04-21, rolled out as "ChatGPT Images 2.0" from about 2026-04-22. OpenAI's own Cookbook prompting guide recommends:
- a skimmable, labelled structure in the order scene → subject → key details → constraints, plus the intended use;
- literal text in quotes;
- small single-change iterations that repeat a "preserve" list;
- describing UI mockups as real products, without concept-art language.

Users own their outputs under OpenAI's terms. ChatGPT images carry C2PA metadata and a SynthID watermark.

### Cited Findings
- **Models.** gpt-image-2 is the "recommended default for new builds". gpt-image-1.5 and gpt-image-1 are for migration, with gpt-image-1 "legacy compatibility only". gpt-image-1-mini is for cheap drafts. `quality: low` on gpt-image-2 often matches gpt-image-1-mini. — [OpenAI Cookbook: GPT Image Generation Models Prompting Guide](https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide) (fetched; model table dated 2026-04-21)
- **Prompt structure.** Order as background/scene → subject → key details → constraints, and state the intended use (ad, UI mock, infographic). For complex requests use short labelled segments or line breaks. For production, prefer a "skimmable template" over clever syntax. — [OpenAI Cookbook guide](https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide)
- **Text rendering.**
  - Put literal text in quotes or ALL CAPS, and specify font, size, colour and placement.
  - Spell tricky words letter by letter.
  - Use medium or high quality for small or multi-font text.
  - For exact copy, demand "EXACT, verbatim, no extra characters".
  - Source: [OpenAI Cookbook guide](https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide)
- **Consistency and editing.**
  - Say "change only X" and "keep everything else the same".
  - Repeat the preserve list every iteration to reduce drift.
  - For a series, reuse the same subject description and add "Do not redesign the character".
  - For style transfer, state what must stay and what must change, and add hard constraints such as "no extra elements".
  - Source: [OpenAI Cookbook guide](https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide)
- **Camera language.** Camera specs are "loosely interpreted", so use them for look and framing, not physical accuracy. For photorealism, say "photorealistic" directly. — [OpenAI Cookbook guide](https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide)
- **UI mockups.** Describe the product as if it already exists. Focus on layout, hierarchy, spacing and real interface elements, avoid "concept art language", and specify a device frame if needed. For infographics, name the audience and the flow, and use `quality="high"` for dense text. — [OpenAI Cookbook guide](https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide)
- **Sizes (API).** Constraints:
  - max edge under 3840px;
  - both edges multiples of 16;
  - aspect ratio at most 3:1;
  - total pixels between 655,360 and 8,294,400.

  Reference sizes: 1024x1024, 1024x1536, 1536x1024 and 1536x864 (slide-style). 2560x1440 is the recommended upper reliability bound, and anything above it is "experimental". — [OpenAI Cookbook guide](https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide)
- **Transparency (API).** Use `background="transparent"` with PNG or WebP (JPEG does not support transparency). Describe an isolated subject with no backdrop, checkerboard or shadows. Restate transparency on edits, and do not convert RGBA to RGB. — [OpenAI Cookbook guide](https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide)
- **Doc inconsistency.** The guide says `input_fidelity` is disabled for gpt-image-2, but some of its examples pass `input_fidelity="high"`. Verify against the API reference. — [OpenAI Cookbook guide](https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide)
- **Launch.** gpt-image-2 launched 2026-04-21 in the API and Codex, and as "ChatGPT Images 2.0" to ChatGPT users around 2026-04-22. It adds native reasoning ("thinking"), up to roughly 2K output and better multilingual text. — [eWeek: OpenAI Debuts ChatGPT Images 2.0](https://www.eweek.com/news/openai-chatgpt-images-2-0/); [Neurohive](https://neurohive.io/en/news/chatgpt-images-2-0-openai-launches-image-generation-model-with-reasoning-2k-resolution-and-multilingual-text/) (SECONDARY; launch-day dates differ by one day between sources)
- **Ownership.** Under OpenAI's Terms of Use you retain rights in your input and own the output; OpenAI assigns to you its rights, if any, in the output. The assignment does not cover other users' similar outputs, and outputs may not be unique. — [OpenAI Terms of Use](https://openai.com/policies/terms-of-use/) (quoted via search; page dated 2026-01-01); [conductatlas summary](https://conductatlas.com/platform/openai/openai-terms-of-use/user-content-ownership-and-output-rights/) (SECONDARY)
- **Provenance marks.** Images generated with ChatGPT, Codex and the API include C2PA metadata and SynthID watermarks, which can be checked at openai.com/verify. Metadata "can easily be removed", so a missing signal is not proof of a non-AI image. — [OpenAI Help: C2PA in ChatGPT images](https://help.openai.com/en/articles/8912793-c2pa-in-chatgpt)

### Inferences (ASSUMPTION): a prompt template for RetentionLens assets

```
USE: Hero illustration for a B2B analytics web app landing page (RetentionLens), 1536x1024.
SCENE: Seamless soft studio backdrop in #F4F1EA (warm paper), no horizon line.
SUBJECT: A constellation of ~40 small matte spheres floating in loose clusters, connected by hairline arcs, suggesting customer accounts grouped into segments.
DETAILS: Three cluster colours only — #1F7A6D (retained), #E0703C (at risk), #8A8F98 (dormant). Matte clay material, subtle subsurface softness, soft contact shadows.
CAMERA/LIGHT: 3/4 elevated view, 50mm look, large soft key light from upper left, gentle fill, no harsh specular highlights.
COMPOSITION: Subject occupies right 60%; left 40% is clean negative space for a headline added later in HTML.
CONSTRAINTS: No text, no letters, no numbers, no logos, no UI chrome, no people, no extra objects.
```

**Series consistency:** keep a fixed "STYLE BLOCK" containing palette hexes, material, lighting, camera and the constraints line. Paste it verbatim into every prompt and change only SUBJECT. For each new image, use the first approved image as a reference and say "match the style of the reference exactly; change only the subject".

**What not to do:**
- Do not have the model render UI text, chart numbers or the RetentionLens logo inside images. Add real text and real data in HTML and SVG, because generated numbers would be fabricated data and conflict with the AGENTS.md provenance rules.
- No third-party brand logos.
- Do not present generated "dashboard screenshots" as the real product.
- Label generated art as illustrative.

**Transparency in ChatGPT:** there is no API parameter in the ChatGPT app, so ask for "transparent background PNG, isolated subject, no shadow". Verify the alpha channel, and fall back to background removal if needed. Whether ChatGPT reliably honours transparency in November 2026 is UNVERIFIED.

**Dark and light theme variants:** generate each asset twice from the same seed prompt, swapping only the backdrop hex (for example #F4F1EA and #0E1116), and keep everything else locked.

**Portfolio and course disclosure:** state in the README that the illustrations were generated with ChatGPT Images (gpt-image-2), with the date. Keep the prompts in the repo (for example `assets/prompts/*.md`) for reproducibility. C2PA metadata may be stripped by image optimisation (`next/image`), so the README disclosure is the durable record.

### Gaps
- I did not fetch the OpenAI Help Center article specifically on ChatGPT image generation for consumer-app limits (rate limits, transparency toggle, aspect-ratio presets in the ChatGPT UI).
- I did not fetch OpenAI's Usage Policies on depicting brands or trademarks; the logo guidance above is my recommendation.
- The exact current wording of the Terms (post-2026-01-01 revisions) is unverified.
- I did not check whether gpt-image-2 in ChatGPT exposes a seed or style-reference feature beyond uploading reference images.
