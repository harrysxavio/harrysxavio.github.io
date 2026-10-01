# Harrys Yusti — Personal Website

Professional profile connecting projects, operational transformation, Supply Chain, and technology applied to business problems.

## Stack and preview

Semantic HTML, CSS, minimal JavaScript, and Python's standard library for the local builder and verifier. No framework or package installation is required. Open `index.html` or serve this directory with a static HTTP server.

```sh
python tools/build_site.py
python tools/verify_site.py
```

## Deployment

Production: [https://harrysxavio.github.io/](https://harrysxavio.github.io/). GitHub Pages publishes `main` from the repository root. `dist/` is a local allowlisted build, not the configured Pages source.

## Structure

- `/` — five-act professional profile.
- `/projects/` — selected work and four case studies.
- `/cv/` — print-ready professional CV.
- `/404.html` — helpful not-found page.
- `assets/`, `styles.css`, `script.js` — visuals and presentation.
- `tools/` — static build and verification.
- `DESIGN.md`, `docs/PHOTO_BRIEF.md` — design system and future portrait brief.

## Design and SEO

Editorial Executive Profile: warm paper, navy ink, a restrained red accent, serif display type, sans-serif reading text, open layouts, and fine rules. Each indexable page has route-specific canonical/social metadata and structured data; `robots.txt` points to the generated route sitemap.
