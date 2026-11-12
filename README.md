# SmokeTrail

A scroll story that follows the pollution from one cigarette: combustion, inhalation, exhaled and sidestream smoke, wind, rain, clothes and hair, thirdhand smoke indoors, butts, soil and plants, water, bystander health and Swiss numbers. It ends with a calculator, a methods section and 85 numbered sources.

Current version: 0.1.0 (12 November 2026)

## Files

```
index.html            the site (generated, do not edit by hand)
assets/css/styles.css styles, light and dark themes
assets/js/app.js      camera, labels, stage navigation, calculator
assets/img/favicon.svg
src/page.html         the story text, with {{c:key}} citations and {{chart:name}} charts
tools/build.py        bibliography (REFS), charts and calculator rows; builds index.html
tools/scene.py        draws the landscape and the close-up lenses as inline SVG
```

## Edit and rebuild

1. Change the text in `src/page.html`, or add a source to `REFS` in `tools/build.py`.
2. Cite with `{{c:key}}` or `{{c:key1,key2}}`. Numbers follow the order of first use, and the source list is generated.
3. Run `python tools/build.py` (Python 3, no packages needed). It rewrites `index.html` and stops if a citation key is unknown.

## Run locally

Open `index.html` in a browser, or run `python -m http.server` in this folder and go to http://localhost:8000.

## Publish on GitHub Pages

1. Create a repository (for example `SmokeTrail`) and push this folder to the `main` branch.
2. On GitHub: Settings → Pages → Build and deployment → Deploy from a branch → `main` / root.
3. The site appears at `https://<your-user>.github.io/SmokeTrail/` after a minute or two.

The `.nojekyll` file tells GitHub Pages to serve the files as they are.

## Notes on the content

- Values marked "derived" are calculated on the site from cited figures.
- All DOIs were checked against Crossref in November 2026. Four could not be reached by the automatic check (Hyland 2008, Ramírez 2014, Bertone 2002, Bahl 2014); their details come from the source papers' abstracts and citing literature.
- Fonts load from Google Fonts; the page falls back to system fonts without them.
