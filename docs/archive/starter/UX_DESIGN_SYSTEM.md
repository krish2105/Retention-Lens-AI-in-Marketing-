# Premium product UI/UX specification — RetentionLens

## Brand position
RetentionLens: 90-day repeat-purchase and customer value forecasting with human-led account reviews.
Visual mood: restrained, thoughtful enterprise product; no fake 3D graphs, implausible metrics or decoration that crowds real workflows.

## Semantic tokens (proposed, contrast-test before signoff)
- Accent light: `#A8528E`; accent dark: `#EF9DD3`.
- Page background light: `#FBF6FA`; dark: `#1E1020`.
- Surface light `#FFFFFF`; surface dark `#162127`; text light `#142527`; text dark `#EDF7F7`.
- Status: success, warning, error, unavailable use **words and icons in addition to color**.
- **Theme selector:** Light / Dark / System, persistent local preference, updates charts and tooltips. Respect prefers-reduced-motion.

## Information architecture
- Overview
- Customer cohorts
- Account queue
- Campaign reviews
- Settings

## Core screens (and interaction specifications)
1. **First run / source connection:** explanatory empty state, download schema sample, privacy note and data type selection.
2. **Overview:** dataset mode banner, data freshness, 3-4 verified action-oriented summary cards, recent actions and next step.
3. **Work queue:** search, multi-filter, sort, pagination, typed status, row click, keyboard focus, bulk actions only with safe confirmation.
4. **Evidence/decision detail:** original source / exact record; calculation or prediction and limitations; review notes; approval workflow.
5. **Model / methodology:** run version, training data version, baseline comparison, uncertainty, cohorts and known failures. 'No trained model yet' until evidence exists.
6. **Settings:** theme, accessibility, data retention, roles, export and permissioned configuration.

## Design quality bar
- Support 320px mobile through desktop, though dense analytical work is desktop-first.
- Minimum accessible target areas, obvious focus rings, descriptive labels, no hover-only meaning.
- Test contrast of text (WCAG 2.2 AA target); choose a verified foreground for both accent variations.
- Tables expose provenance and meaning; no fake percentages, mislabeled axes or misleading truncated bounds.
- Import -> error -> fix -> retry, empty -> import, saved -> return and network-interruption flows must exist.
- Autosave drafts, version changes and visible 'saved' state for user-authored notes.
- Long text truncation only with accessible expansion, sensible number/date precision.
- Avoid reliance on images for labels or critical instructions.

## Image asset usage
Use illustrations sparingly: landing marketing hero, first-use setup and empty states, not behind tables or charts. Use `assets/IMAGE_GENERATION_PROMPTS.md`; export appropriately optimized individual images. Do not insert image-generation text directly as UI copy or claim an asset has been generated until saved and verified.

## Sample web scaffold
The included dashboard implements primary type, theme selector and demo case queue, and is a starting reference rather than the completed spec.
