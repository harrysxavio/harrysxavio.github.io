# Profile Polish — Dark Mode, Home, Projects, and CV

## Objective
Implement the authorized local-only profile site correction on `codex/profile-polish-dark-home-cv`, preserving the static architecture, factual integrity, existing routes, SEO, accessibility, and user-provided assets.

## Problem and Why
The current portfolio needs a coherent dark theme, a more personal image-led home, clearer project storytelling and grouping, and a responsive, readable CV with a genuine PDF download and maintainable content source.

## Scope and Constraints
- In scope: global styles/script; Home; Projects listing and verification; CV and static PDF; hero portrait optimization; editable Spanish content source; build/verification and local commits.
- Out of scope: remote actions (push/deploy/PR), generated or stock imagery, dependency installation, unrelated `.codegraph/`, `.codex-remote-attachments/`, `odd/tasks/personal-brand-v4.md`, and `odd/tasks/v4-1-visual-experience.md`.
- Branch/base: `codex/profile-polish-dark-home-cv` / `6aa19b4`.
- Preserve the transparent supplied portrait; public copy stays natural professional Spanish; never invent accomplishments, precise hours, month-level dates, or other personal facts.
- TDD: off (existing project tracker). RDD: off (user choice); ordinary checks only.
- Delivery strategy: local work-unit commits only; no remote delivery.

## Authorized Scope
Local source files and assets needed for the requested changes, this feature tracker, and its Engram mirror `odd/profile-polish-dark-home-cv/tasks` in project `harryslanding`.

## Acceptance Criteria
- [ ] A persistent, keyboard-accessible dark-mode switch works on all routes, preserving light as default, with strong contrast and reduced-motion support.
- [ ] Home uses the supplied transparent portrait, removes the mechanical years eyebrow, elevates the name and concise personal copy, and presents connection, Control Tower automation, anomaly result, career, human notes, contact, and footer accurately.
- [ ] Home has one desktop row of three emblematic projects (mobile stack), consistent reference-inspired compact icons, purposeful keyboard/pointer states, and no total-count claim.
- [ ] Projects page has the exact evocative H1, truthful story, four #TOP4 cases and five additional projects grouped by type, with Control Tower separate from anomaly work; teasers use `Ver cómo lo abordamos →` and no invented detail route is required.
- [ ] CV has readable Natura progression with original year ranges, relevant case links, concise evidence-based scope/impact, requested value-area section and workflow line, and a working A4 PDF download; print remains secondary.
- [ ] `content/projects-and-cv.md` documents all nine projects, clear TOP4, role/career facts, source confidence/date precision, and update/sync workflow.
- [ ] Builder and verifier preserve all routes, metadata, canonical/structured data, sitemap/robots, assets, and printable CV; update project asset/count/group assertions.
- [ ] Responsive, contrast, keyboard, reduced-motion, image-alpha/size, route/404, and real PDF/A4 checks pass; browser viewports include 1440×900, 1024×768, and 390×844 for Home/Projects/CV in light/dark.

## Tasks
- [x] **PPC-1 — Establish factual content source and portrait asset.** Review existing facts, optimize the supplied portrait retaining alpha, and author the maintainable editorial source. Route: delegated direct writer. Trigger evidence: coordinated content/assets/builder changes require multiple non-trivial files.
- [ ] **PPC-2 — Rework shared theme and Home.** Implement global toggle, palette, interaction accessibility, responsive header, hero/profile and home project/career/contact sections. Route: delegated direct writer. Checks: builder/verifier, static interaction inspection, rendered browser QA.
- [ ] **PPC-3 — Restructure Projects inventory.** Add distinct ninth Control Tower entry, specified top-four and category grouping, project-list stories/icons/CTA, and nine-project static assertions without losing existing case routes. Route: delegated direct writer. Checks: builder/verifier, all local links/assets, visual/browser QA.
- [ ] **PPC-4 — Refine CV and provide real PDF.** Update progression, contribution vs. outcome, value areas and workflow; create A4 downloadable PDF from existing HTML/Chromium; ensure static serving and print behavior. Route: delegated direct writer. Checks: PDF opens, dimensions A4, download link resolves, browser/print visual QA.
- [ ] **PPC-5 — Full regression and local work-unit close.** Run mandated build, verifier, JS syntax and diff checks; inspect local built routes/metadata/theme/interactions/responsive screenshots; update tracker and Engram mirror after each task; create local Conventional Commits with no AI attribution. Route: delegated direct verification, parent spot check. Checks: commands and visual proof recorded below.

## Progress and Verification
- Exploration handoff: parent map agent identified `index.html`, `projects/index.html`, `cv/index.html`, `styles.css`, `script.js`, `tools/build_site.py`, and `tools/verify_site.py` as primary surfaces. This tracker intentionally supersedes neither prior V4 artifacts nor their historical decisions.
- Initial repository status: branch confirmed; pre-existing untracked `.codegraph/`, `.codex-remote-attachments/`, `odd/tasks/personal-brand-v4.md` preserved untouched.
- TDD source: existing project tracker; resolved off. RDD source: user instruction; disabled.
- PPC-1 evidence: added `content/projects-and-cv.md` covering nine projects and CV facts with provenance/date-precision distinctions; optimized the user-supplied transparent portrait to `assets/harrys-yusti-portrait.webp` (760×675 RGBA, alpha 0–255, 66,162 bytes; source 1330×1182). Visual readback confirmed portrait remains intact with transparency.
- Build: pending.
- Verifier: pending.
- `node --check script.js`: pending.
- `git diff --check`: pending.
- Browser/visual/PDF QA: pending.
- Work-unit commit evidence: pending.

## Next Step
Implement shared theme/Home (PPC-2), then Projects (PPC-3), then CV/PDF (PPC-4), recording commit identities and checks as observed.

## Relevant Files
- `odd/tasks/profile-polish-dark-home-cv.md` — recovery ledger for this feature.
- `index.html`, `projects/index.html`, `cv/index.html` — static page content to update.
- `styles.css`, `script.js` — shared visual/interaction layer.
- `tools/build_site.py`, `tools/verify_site.py` — public asset allowlist and regression checks.
- `content/projects-and-cv.md` — planned fact-managed source for all requested portfolio content.


