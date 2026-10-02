# Header monogram and palette refinement

## Goal
Make one restrained, coherent refinement to the shared site header: reduce its corner radius, replace the name wordmark with a more legible HY monogram, and use the supplied deep-navy palette as the primary blue direction.

## Scope and constraints
- Continue on `codex/header-monogram-palette` from published main `b5c23aa`.
- Keep the change limited to the header and the existing blue design token family needed to make the choice cohesive; retain all routes, content, dark mode, and behavior.
- Use palette 1's `#22396F` as the light-theme primary blue; select a readable navy-derived dark-theme blue if needed for text contrast. Preserve the existing pale background and coral accent.
- Use clear accessible text `HY` as the logo mark (not a generated/rough raster illustration); the link remains named accessibly as Harrys Yusti home.
- Do not publish in this step; local visual review first, then await the user's direction.
- TDD off; existing project checks from the content-editor task remain the functional baseline.

## Task
- [x] T1 — Refine the shared header and its blue tokens, align the public theme-color metadata, update generated pages, and verify the desktop/mobile light/dark appearance and navigation accessibility.

## Checks
- `python tools/build_site.py`
- `python tools/verify_site.py`
- `python -m unittest discover -s tests -v`
- `git diff --check`
- Browser screenshots at desktop and 390px mobile, light and dark; inspect radius, visual balance, contrast, logo clarity, overflow, keyboard focus, and preserved navigation.

## Progress
- Replaced the visible name wordmark with a bold typographic `HY` mark while retaining the link's `Harrys Yusti, inicio` accessible name. Updated the shared light blue to `#22396F`, selected `#526BA5` for dark mode (4.63:1 white-text contrast on the rendered header), and set desktop/mobile header corners to 12px.
- Regenerated all eight checked-in route pages and `dist/`; the builder and verifier now guard the logo/accessibility contract, approved light/dark token values, and both header radii.
- Checks passed: `python tools/build_site.py`; `python tools/verify_site.py`; `python -m unittest discover -s tests -v` (10 passed); `python -m py_compile tools/build_site.py tools/verify_site.py`; `node --check script.js`; `git diff --check`; deterministic regeneration (identical SHA-256 file inventory).
- Browser QA passed in Chrome at 1440x900 and 390x844, light/dark: the HY mark and nav fit, both layouts have 12px corners, no horizontal overflow was observed, and keyboard Tab focused the home link with its coral focus ring and unchanged accessible name. Screenshots: `.playwright-mcp/hy-header-desktop-light.png`, `.playwright-mcp/hy-header-mobile-light.png`, `.playwright-mcp/hy-header-desktop-dark.png`, `.playwright-mcp/hy-header-mobile-dark.png`.
- Published baseline and active branch confirmed before edits: `b5c23aa` and `codex/header-monogram-palette`.
- Reopened T1 after finding that only three route SEO records advertised the superseded `#135EEF` and the other five used the pale `#f4f0e7`; neither aligned browser theme-color chrome with the approved light primary. All eight route records now use `#22396F`; the dark CSS token remains `#526BA5` and is unchanged by metadata.
- Metadata-correction checks passed: `python tools/build_site.py`; `python tools/verify_site.py`; `python -m unittest discover -s tests -v` (10 passed); `git diff --check`.
- Prior implementation commit: `6f5067f` (`feat(site): refine shared header monogram and palette`); tracker evidence commit: `0af691a` (`docs(task): record header refinement evidence`).

## Next step
- T1 is locally complete, including route theme-color metadata alignment. No remote write authorized in this incremental step.
