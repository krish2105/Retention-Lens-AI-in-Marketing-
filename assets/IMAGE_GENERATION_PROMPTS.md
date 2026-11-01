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
