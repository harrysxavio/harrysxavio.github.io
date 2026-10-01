# Master Content Source — ODD Recovery Tracker

**Status:** In progress — MCS-1 semantic wiring is corrected; MCS-2 and MCS-3 are complete; MCS-4 remains.

## Objective
Establish one editable structured content source as the canonical input for Home, Projects, CV, and all nine project/case pages, then generate checked-in static HTML at the existing GitHub Pages routes and `dist/`. Improve project discovery with multi-assignable tags, accessible client-side text search and tag filters, and make typography, spacing, the name treatment, and secondary project CTA alignment consistent.

## Problem and Why
Content is currently maintained across multiple pages, making facts and presentation harder to keep consistent. A single structured source and a standard-library static build should make confirmed content maintainable while preserving the site's static, route-compatible deployment model. Search, filters, and focused visual polish improve discovery without adding a framework or dependency.

## Authorized Scope
- Local implementation on branch `codex/profile-polish-dark-home-cv`.
- One canonical structured content source for Home, Projects, CV, and the nine existing project/case pages.
- Templates and a static HTML generation workflow using only the Python standard library and static HTML/CSS/JavaScript; generated HTML remains checked in at current routes and under `dist/`.
- Multiple assignable tags per project, plus accessible client-side text search and tag filters on Projects.
- Consistent typography and spacing, comfortable letter spacing for the name, and aligned placement of the three secondary project CTAs.
- Preserve confirmed facts and existing routes. No new routes, frameworks, or dependencies.
- Work unit commits on the feature branch using Conventional Commit messages; never add Co-Authored-By or AI attribution.

## Constraints and Delivery
- Effective TDD: **off**, from the existing tracker resolution. Use ordinary functional checks; do not invent a test-first mode.
- RDD: **off**, from the current read-only status. Do not start or prompt for a native review transaction.
- Delivery strategy: **ask-on-risk**, local-only. No remote push, PR, merge, or deploy is authorized. Defer any chain-strategy decision until remote delivery is explicitly requested.
- Preserve unrelated pre-existing untracked paths; do not stage or alter them.
- Generated pages must remain at current GitHub Pages routes; no deploy claim without an authorized remote operation and confirmation.

## Route and Workload Forecast
**Route:** delegated direct implementation. The work is coordinated across canonical data, a generator and page templates, generated page outputs, interactive filtering, and visual consistency; reading that prepares those changes and multi-file edits belong in a bounded writer task, not inline edits. Verification is a separate final task.

**Forecast:** approximately 350–500 authored changed lines across four work units, excluding generated HTML from the authored-line estimate. This is an initial planning estimate only; update it from commit diffs. Strategy remains `ask-on-risk`; if the estimate or running authored count exceeds about 400, resolve delivery strategy before any remote-delivery planning. No chain choice is authorized or needed for local work.

## Tasks

### [x] MCS-1 — Establish canonical content and static generation
**Status:** Complete, including semantic-wiring correction. **Route:** delegated direct writer. **Initial commit:** `162e505` (`feat(content): generate static routes from canonical data`). **Corrective commit:** recorded after commit creation.

- [x] Define one author-friendly semantic JSON source covering Home, Projects, CV, and all nine existing project/case pages; remove the duplicated editorial facts document after migration.
- [x] Generate static HTML from that source using only the Python standard library and static HTML/CSS/JavaScript; check in outputs at current routes and `dist/`.
- [x] Preserve confirmed facts and current routes; add no framework or dependency.
- [x] Ensure CV-visible career, skills, education, languages, profile, and location render from the corresponding structured domain fields instead of parallel copy blocks. Reopened after final semantic audit found these fields were only validated while duplicate prose in `cvPage` drove visible output; migrated the copy into the structured fields and made `cvPage` breadcrumb-only.
- [x] Record the corrective work-unit commit and focused verification result here; exact commit identity will be filled immediately after commit creation.

**Acceptance criteria**
- [x] All in-scope pages are represented in the canonical source and visible domain facts are rendered from their semantic fields, without duplicate parallel CV prose.
- [x] Generated files exist at the existing public routes and in `dist/`, with no route additions.
- [x] Rebuilding is deterministic for unchanged input: 33 root-route/dist route-and-asset files retained identical SHA-256 hashes across two builds.

**Checks**
- [x] `python tools/build_site.py` — `Built 8 HTML pages and public assets at ...\Harryslanding\dist`; site URL `https://harrysxavio.github.io`.
- [x] `python tools/verify_site.py` — PASS for routes/HTML/resources, canonical/OpenGraph/JSON-LD/robots/sitemap/allowlist, and four cases/five teasers/diagrams.
- [x] Compared SHA-256 hashes for generated route and asset inventory across two unchanged builds; all 33 were identical. Verifier confirms eight routes, existing case routes, and preserved content structure.
- [x] Correct CV field wiring, rebuild, inspect emitted CV against `career[]`, `skills[]`, `education`, `languages[]`, and `profile`, then record the corrective commit.
- [x] `python tools/build_site.py`, `python tools/verify_site.py`, and `python -m py_compile tools/build_site.py tools/verify_site.py` — PASS; verifier compares all semantic profile, career, education, skills, tools, language and role-link values against generated CV text.
- [x] Local Playwright CV readback: rendered 3,733 characters, all source-driven headings, reported ~35% metric, education/year, and location; PDF and print actions remain present.

### [x] MCS-2 — Add project tag taxonomy, search, and filters
**Status:** Complete. **Route:** delegated direct writer. **Commit:** `98c854c` (`feat(projects): add accessible client-side discovery`).

- [x] Added a stable slug/label taxonomy in `content/site.json`, with multiple tags assigned to each of the nine project records and visible HTML labels.
- [x] Added accessible, client-side text search and tag filtering to the existing Projects page without a new route or dependency.
- [x] Implemented empty-query, combined search/filter, no-results, and clear/reset behavior.
- [x] Recorded the work-unit commit and focused verification result here.

**Acceptance criteria**
- [x] Each project supports multiple tags from the documented taxonomy; the verifier checks full project coverage and label/slugs.
- [x] Search and filters work together on the existing Projects route without a server or network request.
- [x] Controls have programmatic labels and native keyboard semantics; result changes use a polite live region and keep focus in place.
- [x] Empty and no-results states are understandable, and reset restores all projects.

**Checks**
- [x] `python tools/build_site.py` — built eight HTML pages and public assets; `python tools/verify_site.py` — PASS for routes/HTML/resources, SEO/output allowlist, taxonomy coverage, filter hooks, and case diagrams.
- [x] In local Playwright at 390×844, typed `inventario` into search, navigated with Tab to the third checkbox and toggled it with Space (1/9 result); `no-match` showed 0/9 and the empty state; clear/reset restored 9/9, empty query, and unchecked tags.
- [x] Network log contained only local route and static-asset requests; no new route/dependency was introduced. `node --check script.js` and `git diff --check` passed.

### [x] MCS-3 — Normalize typography, spacing, and project CTA alignment
**Status:** Complete. **Route:** delegated direct writer. **Commit:** `c1539c9` (`style: consolidate responsive site typography and cards`).

- [x] Consolidated the stylesheet to shared type, spacing, theme, focus, responsive layout, and route-type rules instead of layering overrides.
- [x] Gave the site wordmark positive tracking and reduced the Home h1's negative tracking while preserving desktop/mobile wrapping.
- [x] Made project-card internals flexible columns with actions bottom-aligned across variable-length summaries/details.
- [x] Recorded the work-unit commit and focused verification result here.

**Acceptance criteria**
- [x] Shared type/spacing rules now cover Home, Projects, CV, and all four case routes with page-type refinements.
- [x] The name treatment uses positive tracking and remains readable on mobile; the Home title tracking is no longer aggressively tight.
- [x] Desktop browser measurements confirmed equal action baselines within the two-card secondary categories (transport: both y=2986; control/engineering: both y=3482), despite different content lengths.
- [x] Existing content/routes remain intact; the route verifier passes.

**Checks**
- [x] `python tools/build_site.py` — built eight pages and public assets; `python tools/verify_site.py` — all three PASS summaries; `node --check script.js`, `python -m py_compile tools/build_site.py`, and `git diff --check` passed.
- [x] Inspected Home, Projects, CV, and a long-form inventory case in local Playwright at 1440×900 and/or 390×844; verified headings, nav wrapping, content, portrait/diagram, card layout, and comfortable mobile rendering. Projects/Home were captured at both required viewport sizes.
- [x] Screenshot evidence is in untracked `output/playwright/`; filters and CTA baselines were also interaction/geometry checked in the browser.

### [ ] MCS-4 — End-to-end verification and visual QA
**Status:** Planned. **Route:** delegated verification after implementation; independent from the writer so the complete generated site can be checked in a fresh context.

- [ ] Verify the structured source, generator, generated routes, search/filter behavior, and visual changes together.
- [ ] Resolve only issues within the authorized scope; preserve unrelated working-tree state.
- [ ] Record exact checks, results, screenshots or browser evidence location (if any), remaining limitations, and final local state.

**Acceptance criteria**
- [ ] Every page in scope is generated from the canonical source and available at its pre-existing route and under `dist/`.
- [ ] Search and tag filtering pass the supported keyboard and interaction scenarios.
- [ ] Visual QA confirms normalized type/spacing, readable name tracking, responsive layout, and aligned secondary CTAs.
- [ ] Verification distinguishes local results from remote publication; no push, PR, merge, or deployment is claimed.

**Checks**
- [ ] Run `python tools/build_site.py` and `python tools/verify_site.py`; include observed outputs/status.
- [ ] Run local desktop and mobile browser walkthroughs for all routes; focus deeply on Projects interactions and representative long/short content pages, while confirming route presence for every page.
- [ ] Inspect `git status` and changed-path inventory to ensure unrelated pre-existing untracked paths were not changed or staged.

## Progress and Next Step
MCS-1's initial generator is at `162e505`; its final semantic audit found CV-visible facts came from parallel `cvPage` copy instead of career/skills/education/languages/profile fields. The corrective work migrates those values into semantic fields and makes the page template render them; emitted CV content is checked against the source. Record the corrective commit identity after creation. MCS-2 is complete at `98c854c`; MCS-3 at `c1539c9`. Complete MCS-4 route inventory, final regeneration and verification, working-tree reconciliation, and sync the final mirror.

## Relevant Files
- `odd/tasks/master-content-source.md` — this feature's recovery tracker; separate from `odd/tasks/profile-polish-dark-home-cv.md`.
- `tools/build_site.py` — existing static-copy builder; intended extension point for canonical content generation.
- `tools/verify_site.py` — existing static-site verification entry point.
- `odd/tasks/profile-polish-dark-home-cv.md` — separate existing tracker; preserve without modification.
