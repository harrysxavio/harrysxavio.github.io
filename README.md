# Harrys Yusti — Professional Profile

A static, Spanish-language executive profile highlighting projects, operational transformation, Supply Chain, productivity, and technology.

## Stack

Semantic HTML, responsive CSS, and a small Python standard-library builder/verifier. No runtime framework or JavaScript dependency.

## Local preview and checks

Open `index.html` directly or serve the repository root with any local static HTTP server. Check the page with:

```powershell
python tools/verify_site.py
```

Build the safe public-file preview into `dist/`:

```powershell
python tools/build_site.py
```

For a project site with a path prefix, pass its HTTPS base URL with `--site-url`.

## Deployment

The production site is [https://harrysxavio.github.io/](https://harrysxavio.github.io/). GitHub Pages is configured to publish the `main` branch from the repository root. The root `index.html`, stylesheet, favicon, robots file, and sitemap are therefore the deployed source; `dist/` is only a local packaging check and is not the Pages source.

## Structure

- `index.html` — profile content, social metadata, and structured data.
- `styles.css` — responsive editorial visual system.
- `assets/` — supplied illustration and optimized social preview.
- `tools/` — standard-library static-site builder and structural verifier.
- `DESIGN.md` — design direction and responsive principles.

## Design and SEO

The profile uses warm paper, navy ink, restrained red accents, serif headings, sans-serif body copy, whitespace, and fine rules. Production canonical, Open Graph, Twitter, and JSON-LD URLs use the account-root domain. The builder validates and renders optional base-path URLs without copying private project files into `dist/`.
