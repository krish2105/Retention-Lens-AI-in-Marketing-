# ChatGPT image prompts — RetentionLens (Aurora series)

For ChatGPT Images 2.0 (gpt-image-2). Prompts only: nothing here is generated yet. Save each approved image at the path given, then note the date in the README's image disclosure.

## How to use
1. Generate **AUR-01** first. When you like it, keep it as the style reference.
2. For every later image: upload AUR-01 and start with "Match the style of the reference image exactly; change only the subject."
3. Paste the **style block** unchanged into every prompt. Change only the SUBJECT and COMPOSITION lines.
4. Iterate one change at a time ("change only X; keep everything else the same").
5. Reject any image with letters, numbers, logos, fake charts, UI screenshots or people. Real text and data are added in code.

## Style block (paste verbatim every time)
```
STYLE: Premium data-art illustration for a B2B analytics web app. Deep night backdrop #070912. Soft aurora light fields in cyan #67E8F9, magenta #F472B6 and violet #7C3AED, heavily diffused, low saturation at the edges. Objects are frosted glass and polished translucent resin with fine inner refraction, thin luminous edges, subtle depth of field. Calm, precise, quiet luxury; no clutter.
LIGHT/CAMERA: Large soft light from upper left, faint cyan rim light, 3/4 elevated view, 50mm look, gentle falloff into darkness.
CONSTRAINTS: No text, no letters, no numbers, no logos, no UI chrome, no charts with labels, no people, no hands, no faces, no watermark, no extra objects.
```

For **light-theme twins**, change only the backdrop line to: `Pale backdrop #F3F4FB, aurora fields at 35% strength` and keep everything else.

---

### AUR-01 · Landing hero — `assets/generated/aur-01-hero.png`
Size 1536x1024 (dark) + light twin.
```
USE: Hero illustration for the RetentionLens landing page; headline is added later in HTML.
[STYLE BLOCK]
SUBJECT: A floating landscape of small glass tiles rising and falling like rolling hills, a retention terrain seen from above; tiles glow cyan on the high ground, warm amber on the slopes, faint magenta in the low valleys.
COMPOSITION: Terrain occupies the right 60%; left 40% is clean dark negative space for text. Horizon fades into the aurora.
```

### AUR-02 · Customer galaxy backdrop — `assets/generated/aur-02-galaxy.png`
Size 1536x864. Used behind the Segments page header only (never behind data).
```
USE: Decorative header band for the segments page.
[STYLE BLOCK]
SUBJECT: A loose spiral galaxy made of hundreds of tiny glass beads in three colour clusters (cyan, amber, magenta), a few larger beads near the core, hairline light trails between neighbours.
COMPOSITION: Galaxy centred slightly right, wide panoramic band, soft vignette, generous empty margins top and bottom.
```

### AUR-03 · Import / first-run — `assets/generated/aur-03-import.png`
Size 1024x1024, transparent background PNG, isolated subject.
```
USE: Empty-state illustration for the data import screen.
[STYLE BLOCK]
SUBJECT: A stack of three thin frosted-glass sheets, like invoices, sliding into a glowing glass prism that splits the light into cyan, amber and magenta beams.
COMPOSITION: Single centred object, transparent background, no backdrop, no shadow on the ground, clear silhouette at 128 px.
```

### AUR-04 · Outreach studio — `assets/generated/aur-04-outreach.png`
Size 1024x1024, transparent background PNG.
```
USE: Empty-state illustration for the AI outreach drafting screen.
[STYLE BLOCK]
SUBJECT: A sealed frosted-glass envelope resting on a small glass plinth, with a soft cyan ring of light hovering above it like an approval seal waiting to be pressed.
COMPOSITION: Single centred object, transparent background, no shadow, generous margin.
```

### AUR-05 · Model lab — `assets/generated/aur-05-model-lab.png`
Size 1024x1024, transparent background PNG.
```
USE: Empty state for the model lab before any run exists.
[STYLE BLOCK]
SUBJECT: A glass lens on a slim stand focusing scattered points of coloured light into one sharp cyan beam.
COMPOSITION: Single centred object, transparent background, no shadow.
```

### AUR-06 · Signals — `assets/generated/aur-06-signals.png`
Size 1024x1024, transparent background PNG.
```
USE: Empty state for the web and social signals page.
[STYLE BLOCK]
SUBJECT: Three concentric glass rings, slightly tilted, each carrying small beads of light travelling around it like orbiting messages, linked by faint threads.
COMPOSITION: Single centred object, transparent background, no shadow.
```

### AUR-07 · Offline / error state — `assets/generated/aur-07-offline.png`
Size 1024x1024, transparent background PNG.
```
USE: Shown when the local AI model or API is unavailable.
[STYLE BLOCK]
SUBJECT: The same glass prism as AUR-03, dimmed, with its light beams paused as faint frozen ribbons; calm, not alarming.
COMPOSITION: Single centred object, transparent background, no shadow.
```

### AUR-08 · App mark — `assets/generated/aur-08-mark.png`
Size 1024x1024, transparent background PNG. Use for favicon and README; redraw as SVG if it must be crisp below 32 px.
```
USE: Abstract app icon for RetentionLens.
[STYLE BLOCK]
SUBJECT: A single rounded glass lens shape with an inner cyan-to-magenta aurora glow and one bright point of light at its focus.
COMPOSITION: Perfectly centred, symmetrical, bold silhouette, readable at 32 px, transparent background, no letters.
```

### AUR-09 · README banner — `assets/generated/aur-09-readme-banner.png`
Size 1536x768 (2:1).
```
USE: Top banner for the GitHub README; the project name is added as real text in Markdown, not in the image.
[STYLE BLOCK]
SUBJECT: A wide panorama of the glass retention terrain from AUR-01 meeting the bead galaxy from AUR-02 on the horizon.
COMPOSITION: Calm centre band, darker edges so GitHub's dark and light modes both frame it well.
```

### AUR-10 · Social preview card — `assets/generated/aur-10-og.png`
Size 1536x816.
```
USE: Open Graph / LinkedIn preview image; title text is overlaid later in HTML.
[STYLE BLOCK]
SUBJECT: Close crop of the AUR-08 lens floating above a small patch of the glass terrain.
COMPOSITION: Lens left of centre, right half quiet for overlaid text.
```

## Review checklist (per image)
- Matches AUR-01 palette and material; no pseudo-letters or numbers anywhere.
- Text placed over it later still reaches 4.5:1 contrast (check in the app, not by eye).
- Exported as WebP/PNG under 400 KB for in-app use; keep the full-size original outside git if large.
- Logged in README: "Illustrations generated with ChatGPT Images (gpt-image-2) on [date]; prompts in `assets/IMAGE_GENERATION_PROMPTS.md`."

---

# Series 2 — roadmap screens (AUR-11 to AUR-28)

Same workflow as Series 1:
- Upload **AUR-01** as the style reference and start every prompt with: "Match the style of the reference image exactly; change only the subject."
- Paste the **style block** above, unchanged, where `[STYLE BLOCK]` appears.
- For spot illustrations (transparent), add: "transparent background PNG, isolated subject, no backdrop, no ground shadow".
- gpt-image-2 sizes must be multiples of 16 with an aspect ratio no wider than 3:1; 2560×1440 is the reliable upper limit.
- Never accept letters, numbers, logos, UI text or people. Real text is added in code.

Save each final image to `RetentionLens_AUR_Complete_Image_Collection/assets/generated/<file>.png`. Claude compresses them to WebP for the app.

| ID | File | Size | Where it is used |
|---|---|---|---|
| AUR-11 | aur-11-landing-hero.png (+ `-light`) | 2048×1152 | Marketing landing page hero |
| AUR-12a | aur-12a-step-upload.png | 1024×1024, transparent | "How it works", step 1 |
| AUR-12b | aur-12b-step-predict.png | 1024×1024, transparent | "How it works", step 2 |
| AUR-12c | aur-12c-step-approve.png | 1024×1024, transparent | "How it works", step 3 |
| AUR-13 | aur-13-auth.png (+ `-light`) | 1024×1536 | Sign-in / sign-up side panel |
| AUR-14 | aur-14-welcome.png | 1024×1024, transparent | Onboarding: empty workspace |
| AUR-15 | aur-15-dropzone.png | 1024×1024, transparent | Upload wizard drop zone |
| AUR-16 | aur-16-validated.png | 1024×1024, transparent | Validation passed |
| AUR-17 | aur-17-needs-fixes.png | 1024×1024, transparent | Validation found problems |
| AUR-18 | aur-18-scoring.png | 1024×1024, transparent | Scoring job running |
| AUR-19 | aur-19-all-done.png | 1024×1024, transparent | Weekly queue cleared |
| AUR-20 | aur-20-plans.png | 1024×1024, transparent | Billing and plans |
| AUR-21 | aur-21-team.png | 1024×1024, transparent | Team and roles |
| AUR-22 | aur-22-privacy.png | 1024×1024, transparent | Privacy, security, data deletion |
| AUR-23 | aur-23-not-found.png (+ `-light`) | 1536×1024 | 404 page |
| AUR-24 | aur-24-status.png | 1536×864 | Status page header |
| AUR-25 | aur-25-pricing-band.png | 2048×768 | Pricing page background band |
| AUR-26 | aur-26-case-study.png | 1536×1024 | Case study / report cover |
| AUR-27 | aur-27-linkedin.png | 1536×512 | LinkedIn and portfolio banner |
| AUR-28 | aur-28-app-icon.png | 1024×1024, opaque | Home-screen / PWA icon |

### AUR-11 · Landing hero
```
USE: Full-width hero for the RetentionLens marketing landing page; the headline is added later in HTML on the left.
[STYLE BLOCK]
SUBJECT: A vast glass retention terrain at dusk, rolling hills of small luminous tiles; a single large frosted-glass lens floats above the terrain, focusing scattered points of light into one bright cyan path that leads to the horizon.
COMPOSITION: Lens and terrain in the right 55%; the left 45% is calm dark negative space for text. Deep perspective, horizon a third from the top.
```
Light twin: swap the backdrop line for `Pale backdrop #F3F4FB, aurora fields at 35% strength` and keep everything else.

### AUR-12a/b/c · How it works (three-image set; keep identical scale and lighting)
```
USE: Step icon for a three-step "how it works" row; must match its two siblings exactly in size, angle and lighting.
[STYLE BLOCK]
SUBJECT (12a): A stack of three frosted-glass sheets sliding into an open glass tray, cyan light along their edges.
SUBJECT (12b): A glass lens over a small cluster of beads, one bead magnified and glowing amber.
SUBJECT (12c): A frosted-glass envelope with a soft cyan approval ring hovering above it, not yet pressed.
COMPOSITION: Single centred object at 3/4 view, same scale across the set, transparent background, no shadow, generous margin.
```

### AUR-13 · Sign-in side panel
```
USE: Tall decorative panel beside the sign-in form.
[STYLE BLOCK]
SUBJECT: A vertical column of floating glass tiles rising like a gentle staircase into the aurora, one tile glowing brighter near the top.
COMPOSITION: Portrait; the subject is centred, with soft fade to darkness at top and bottom.
```

### AUR-14 · Welcome / empty workspace
```
USE: Empty state for a brand-new workspace with no data yet.
[STYLE BLOCK]
SUBJECT: An empty frosted-glass tray on a slim plinth with a faint cyan glow inside, waiting to be filled.
COMPOSITION: Single centred object, transparent background, no shadow.
```

### AUR-15 · Upload drop zone
```
USE: Illustration inside the file drop zone of the upload wizard.
[STYLE BLOCK]
SUBJECT: Thin frosted-glass sheets drifting down toward an open glowing glass portal ring, light trails behind them.
COMPOSITION: Single centred object, transparent background, no shadow.
```

### AUR-16 · Validation passed
```
USE: Success state after an upload passes validation.
[STYLE BLOCK]
SUBJECT: The glass sheets from AUR-15 now neatly stacked and aligned, with a calm cyan glow and a smooth glass ring around the stack.
COMPOSITION: Single centred object, transparent background, no shadow; calm and complete.
```

### AUR-17 · Validation found problems
```
USE: Gentle warning state when some rows need fixing; must feel helpful, not alarming.
[STYLE BLOCK]
SUBJECT: The same glass sheet stack with two sheets slightly out of line, glowing soft amber at their edges.
COMPOSITION: Single centred object, transparent background, no shadow. No red, no warning symbols.
```

### AUR-18 · Scoring in progress
```
USE: Shown while the scoring job runs.
[STYLE BLOCK]
SUBJECT: A glass lens with beads of light orbiting it in a slow spiral, a few beads passing through the lens and turning cyan.
COMPOSITION: Single centred object, transparent background, no shadow; sense of gentle motion.
```

### AUR-19 · Weekly queue cleared
```
USE: Empty state when every account in this week's review is done.
[STYLE BLOCK]
SUBJECT: A small calm glass terrain where every tile glows an even soft cyan, under a faint sunrise of aurora light.
COMPOSITION: Single centred object, transparent background, no shadow; restful.
```

### AUR-20 · Billing and plans
```
USE: Illustration for the plans and billing page.
[STYLE BLOCK]
SUBJECT: Three frosted-glass pillars of increasing height, each holding a glowing bead (cyan, violet, amber), like tiers.
COMPOSITION: Single centred group, transparent background, no shadow. No currency symbols, no numbers.
```

### AUR-21 · Team and roles
```
USE: Illustration for team members and roles settings.
[STYLE BLOCK]
SUBJECT: Three glass orbs of different sizes connected by thin luminous threads, forming a balanced triangle, one orb slightly brighter.
COMPOSITION: Single centred group, transparent background, no shadow. No people, faces or hands.
```

### AUR-22 · Privacy and security
```
USE: Illustration for privacy, security and "delete my data" settings.
[STYLE BLOCK]
SUBJECT: A frosted-glass vault cube with a soft internal glow, its seams lit cyan, a faint protective ring of light around it.
COMPOSITION: Single centred object, transparent background, no shadow. No padlock icon, no keyhole text.
```

### AUR-23 · 404 page
```
USE: Background for the "page not found" screen; text is added in HTML.
[STYLE BLOCK]
SUBJECT: A single glass lens resting tilted on an empty patch of the glass terrain, its light pointing at nothing, aurora overhead.
COMPOSITION: Subject lower right; large calm space upper left for text. Slightly melancholic but friendly.
```

### AUR-24 · Status page header
```
USE: Header band for the system status page.
[STYLE BLOCK]
SUBJECT: A single smooth line of cyan light running across the frame like a steady heartbeat, with a few glass beads resting along it.
COMPOSITION: Wide panoramic band, line across the centre, dark calm space above and below.
```

### AUR-25 · Pricing page band
```
USE: Low-contrast background band behind pricing cards; must stay subtle so text on cards stays readable.
[STYLE BLOCK]
SUBJECT: Soft rolling aurora light over a distant, out-of-focus glass terrain.
COMPOSITION: Very wide band, minimal detail, dark overall, brightest at the centre top.
```

### AUR-26 · Case study cover
```
USE: Cover image for the case study and report.
[STYLE BLOCK]
SUBJECT: A glass lens held above the glass terrain, focusing a beam onto one small cluster of glowing amber tiles amid a field of cyan, as if finding the accounts that matter.
COMPOSITION: Centred subject, room at top for a title added later.
```

### AUR-27 · LinkedIn and portfolio banner
```
USE: Banner for LinkedIn and portfolio pages; it will be cropped, so keep the subject in the centre third.
[STYLE BLOCK]
SUBJECT: Wide panorama where the glass terrain meets the bead galaxy on the horizon, the lens floating at the centre.
COMPOSITION: 3:1 panorama, subject in the middle third, dark edges.
```

### AUR-28 · App icon (opaque)
```
USE: Home-screen and PWA app icon; iOS icons cannot be transparent.
[STYLE BLOCK]
SUBJECT: The AUR-08 rounded glass lens with its inner cyan-to-magenta glow and one bright focal point, on a solid #070912 background.
COMPOSITION: Perfectly centred, bold silhouette, readable at 60 px, solid background, no letters, no rounded-corner mask (the OS adds it).
```

## Handing them back
Drop the PNGs into `RetentionLens_AUR_Complete_Image_Collection/assets/generated/` and tell Claude. Claude will check sizes and transparency, compress to WebP (under 400 KB, under 120 KB for spot art), place them in `apps/web/public/img/`, and log the generation date in the README image disclosure.

## Series 2 import log (2026-11-01)

Imported from `RetentionLens_AUR_All_Images.zip`. Web copies are in `apps/web/public/img/` (WebP; spot art trimmed to its subject and squared at 512 px).

- **In place:** 12a/b/c, 13, 14–22, 23, 24, 25, 26 (portrait, used as the A4 report cover), 27 (plus a 1584×396 LinkedIn crop in the collection folder), and 11 light (v1 chosen; v2 kept as an alternative).
- **Still needed:** AUR-11 **dark** hero (the dark theme uses AUR-01 until then); optional light versions of AUR-13 and AUR-23.
- **Brand decision:** app and home-screen icons are built from the AUR-08 lens mark on #070912. AUR-28 (magnifier) is kept in the collection but not used, so the brand mark stays consistent.
