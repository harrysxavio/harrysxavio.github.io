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

Modern editorial professional profile: a clear system-sans hierarchy, navy and blue contrast, restrained coral accents, spacious components, and a real portrait. Each indexable page retains route-specific canonical/social metadata and structured data; `robots.txt` points to the generated route sitemap.

## V4.1 experience

The Home uses a portrait-led introduction, five evidence-backed work steps, selected project examples, a career timeline, and one contact section. At desktop widths the work steps become keyboard-operable tabs; mobile and no-JavaScript use native disclosures. Project detail pages use compact, explanatory SVG process diagrams. The diagrams describe the documented workflow and do not represent a specific production system. The `/cv/` A4 print stylesheet and static, framework-free delivery remain in place.

## Edición local

En Windows, ejecuta `Editar-contenido.cmd` y abre `http://127.0.0.1:8766/`; la vista previa queda en `http://127.0.0.1:8767/`. El editor y la vista previa solo escuchan en este equipo. Guardar valida el contenido y reconstruye la vista previa local; no publica cambios en GitHub Pages. Consulta la guía en [`content/README.md`](content/README.md).
