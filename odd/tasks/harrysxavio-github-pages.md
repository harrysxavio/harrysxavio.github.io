# Harrys Yusti Editorial Executive Profile

## Objective

Turn the existing static landing into a credible, scannable executive profile for Harrys Yusti, emphasizing projects, operational transformation, Supply Chain, and productivity, and keeping technology and AI in supporting roles. The root files are the deployed product because GitHub Pages is already configured for `main` + `/(root)`.

## Problem and why

The first iteration of the page uses a field-guide/manual framing, overuses guide nomenclature, and does not yet expose the full confirmed career ledger and business impact quickly. The user provided a newer strategic brief and explicitly authorized implementation without another approval step. Work already started under the prior brief is unverified and must be adapted, not assumed complete.

## Scope and constraints

- Keep static HTML/CSS and current paper, navy, red, serif/sans, whitespace, and fine-rule design language; no redesign, generated images, false portrait, unnecessary JS, or new dependencies.
- Make the UI an Editorial Executive Profile, highly scannable and mobile-first. Remove fixed guide rail and labels such as `GUÍA DE CAMPO`, `FIG. 01`, and `NOTA DE CAMPO`; use simple top navigation: Harrys Yusti, Experiencia, Proyectos, Skills, Sobre mí, Contacto.
- Hero: eyebrow `INGENIERO MECÁNICO · 11 AÑOS DE EXPERIENCIA`; H1 `Harrys Yusti`; positioning `Proyectos · Transformación Operacional · Supply Chain · Productividad · Tecnología`; concise value proposition; retain `Mejorar cómo funciona el trabajo.` only as a subordinate statement.
- Page order: hero → professional snapshot → Selected Impact → Experience → Selected Projects → Capabilities/Skills → About → low-page AI explorations → Contact. Remove empty Ideas/coming-soon content.
- Use only the user's supplied facts. No invented credentials, employers, dates, results, social links, testimonial, photo, or current role.
- Experience ledger must retain all roles: Natura & Co Chile (2025–2026, Coordinador de Tecnología de Operaciones); Natura & Co Chile (2023–2025, Analista Senior de Operaciones y Logística); ACHS Servicios (2021–2023, Jefe de Operaciones); Natura & Co Chile (2019–2021, Analista Senior de Proyectos de Operaciones y Logística); Coprove (2017–2019, Jefe de Proyecto); 704 Ingeniería (2016–2017, Ingeniero de Proyecto), with scope/results from the current user brief.
- Projects: inventory reconciliation redesign/automation (-30% handling time, -40% support costs); Brazil–Chile ERP Data Migration (data focus, ~120K master records); patient transport fleet optimization (~15% less patient transport use in RM); distribution-center order-picking line balance (~95% post-go-live adoption). Do not imply patient cargo or manufacturing.
- Selected impact should use four editorial metrics, chosen from confirmed figures; preserve their context and do not imply unrelated outcomes belong to one project. Confirmed options also include ~2 days to 4 hours anomaly resolution.
- Capabilities should visibly foreground project delivery, operational productivity, process improvement, Supply Chain, logistics, warehousing, inventory, fulfillment, transport, picking, supply planning, SAP/WMS/KPIs; include scope, plans, stakeholders, risk, dependencies, budgets, testing, implementation, adoption, reporting. Group the named toolsets with AI explicitly labeled current exploration/applied learning.
- About: short human voice, Mechanical Engineer, 11 years across Ops/projects/Supply Chain/tech, systems/friction/problem-to-initiative, curiosity by building, current AI learning; education Universidad Central de Venezuela (2015), Spanish native and English advanced professional.
- SEO production URL is `https://harrysxavio.github.io/`. Use canonical, OG/Twitter, `Person`/`ProfilePage` JSON-LD, exact supplied LinkedIn/GitHub `sameAs`, robots, and sitemap. Do not change local Git origin, remote Pages settings, push, contact GitHub, or create a workflow: user confirmed Pages already uses `main` + root.
- Preserve useful partial edits from the superseded brief and ignored `.atl/` state; avoid deleting unrelated files.

## Authorization, route, and verification mode

- Authorized: local implementation and local verification only; user explicitly wants the new scope implemented without further approval.
- Route: delegated direct; mapping and writing span 4+ files and require interdependent HTML/CSS/build/verifier/docs changes.
- TDD: `strict_tdd=false`, Standard Mode by explicit user choice. Exact verification command: `python tools/verify_site.py`. Run functional and browser checks; no RED-before-code requirement.
- Delivery strategy: `ask-on-risk`; user-selected future chain strategy: `stacked-to-main`. Do not push or create a PR.
- Estimated authored diff: ~1,200–1,700 lines, generated WebP excluded. Slice by coherent deliverable, never artificial line count.
- RDD was last observed `on` globally; re-read status and assess each work-unit commit with the instructed `gentle-ai review assess` command. If review is due, stop and return the exact transition to parent; do not launch review lifecycle.

## Stable tasks and acceptance criteria

- [x] **HYP-01 — Rebuild page hierarchy as an executive profile.** Rebuilt `index.html` and `styles.css` around the requested hero, snapshot, selected impact, chronological Experience, project rows, Skills, About, low-page AI exploration, and Contact. Removed manual/field-guide nomenclature and the empty section; preserved open editorial rows instead of cards. Standard-mode verification and browser inspection passed at 1440, 1024, 768, 390, and 360 CSS px. A nowrap impact figure initially overflowed at 1024/390 and was fixed with responsive wrapping.
  - Acceptance: required hero copy and top navigation; all six roles and dates retained; project facts/outcomes are precise; domains and project-delivery capabilities lead; AI is explicitly exploratory and late in the flow; no invented facts.
  - Checks: `python tools/verify_site.py`; keyboard/responsive Browser/IAB review.
- [x] **HYP-02 — Optimize assets, metadata, and local site build.** Added the visually reviewed ~370 KB WebP social preview (no portrait/project claim), production root canonical/social/schema URLs, stable builder markers, optional HTTPS path-prefix support, and a strict public-file allowlist. Root files remain production-ready for main/root Pages. The builder recovers if OneDrive marks prior generated `dist/assets` read-only. Root and path-prefix package builds were verified; final `dist` contains only HTML, CSS, favicon, WebP, robots, and sitemap.
  - Acceptance: one canonical and Twitter card; URLs/schema/robots/sitemap reflect site URL; no marker-string mismatch or duplicate SEO tags; internal files excluded from `dist`; the existing Pages source is unchanged.
  - Checks: builder for `https://harrysxavio.github.io`; base-path validation/metadata; dist allowlist inspection; `python tools/verify_site.py`.
- [x] **HYP-03 — Make structural verification content-independent.** Replaced keyword-oriented checks with structural HTML, heading/anchor, supplied-link, metadata uniqueness, schema relation, social image, robots/sitemap, URL validation, and dist allowlist checks. Exact project verifier passes for production root and generated path-prefix preview.
  - Acceptance: one H1, sane heading sequence, valid profile entities/sameAs, no missing anchors/assets, no duplicate metadata, no invented sameAs; no test forces exhaustive tools on public page.
  - Checks: `python tools/verify_site.py` plus focused in-memory valid/invalid base URL and build metadata cases.
- [x] **HYP-04 — Finish concise project docs and repository hygiene.** Rewrote README and DESIGN.md for the executive profile and main/root deployment; ignored `dist/`, browser-preview captures, and Python caches; staged removal of the single tracked Python bytecode file without deleting `.atl/` or unrelated state.
  - Acceptance: instructions match main/root publishing and local build; no Actions workflow added; Python cache no longer tracked.
  - Checks: doc/command readback, `git diff --check`, tracked-file/status inspection.
- [ ] **HYP-05 — Render, verify, commit, and report.** `python tools/verify_site.py`, root build, path-prefixed build/verification, and `git diff --check` passed. IAB was unavailable, so rendered in Chrome/Playwright instead: screenshots captured at 1440×1000 (`.playwright-mcp/page-2026-09-30T21-46-34-272Z.png`) and 390×844 (`.playwright-mcp/page-2026-09-30T21-46-41-266Z.png`); layout/overflow checked at 1024, 768, 390, and 360 px. Console errors: 0. No accepted concept screenshot is available. Remaining: commit the coherent work unit, record its identity and RDD assessment, then report fidelity and unresolved items.
  - Acceptance: record actual viewport checks and limitations; no fake concept comparison or unsupported design signoff; stop for parent on due native review; no remote operations.

## Progress

- [x] Created feature branch `codex/landing-pages-production` from clean `main` at `f298d54dd3565f8c7c7abe6e86ebfdf12233b60f`; local origin remains unchanged.
- [x] Standard Mode resolved: `strict_tdd=false`, verification command `python tools/verify_site.py`.
- [x] Updated the existing task file and Engram mirror to the newer authoritative scope and read back both before resuming source edits.
- [x] Adapted partial edits to HYP-01 through HYP-04 and completed the required project and responsive-browser checks.
- [ ] Commit coherent work units, append their commit IDs to this document and mirror, and run the required RDD assessment after each commit.

## Current local implementation (verified; commit identities pending)

Implementation files changed; verification/rendering is complete but commit identities are pending: `.gitignore`, `DESIGN.md`, `README.md`, `index.html`, `styles.css`, `tools/build_site.py`, `tools/verify_site.py`, `robots.txt`, `sitemap.xml`, new `assets/operations-transformation-illustration.webp`, and the exact tracked cache deletion `tools/__pycache__/build_site.cpython-313.pyc`. Browser preview screenshots are retained under ignored `.playwright-mcp/`.

## Next step

Commit the integrated profile/build/verification/doc deliverable as one coherent work unit, assess RDD immediately, then update this file and Engram with the commit identity and assessment.
