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
- [x] A persistent, keyboard-accessible dark-mode switch works on all routes, preserving light as default, with strong contrast and reduced-motion support.
- [x] Home uses the supplied transparent portrait, removes the mechanical years eyebrow, elevates the name and concise personal copy, and presents connection, Control Tower automation, anomaly result, career, human notes, contact, and footer accurately.
- [x] Home has one desktop row of three emblematic projects (mobile stack), consistent reference-inspired compact icons, purposeful keyboard/pointer states, and no total-count claim.
- [x] Projects page has the exact evocative H1, truthful story, four #TOP4 cases and five additional projects grouped by type, with Control Tower separate from anomaly work; teasers use `Ver cómo lo abordamos →` and no invented detail route is required.
- [x] CV has readable Natura progression with original year ranges, relevant case links, concise evidence-based scope/impact, requested value-area section and workflow line, and a working A4 PDF download; print remains secondary.
- [x] `content/projects-and-cv.md` documents all nine projects, clear TOP4, role/career facts, source confidence/date precision, and update/sync workflow.
- [x] Builder and verifier preserve all routes, metadata, canonical/structured data, sitemap/robots, assets, and printable CV; update project asset/count/group assertions.
- [x] Responsive, contrast, keyboard, reduced-motion, image-alpha/size, route/404, and real PDF/A4 checks pass; browser viewports include 1440×900, 1024×768, and 390×844 for Home/Projects/CV in light/dark.

## Tasks
- [x] **PPC-1 — Establish factual content source and portrait asset.** Review existing facts, optimize the supplied portrait retaining alpha, and author the maintainable editorial source. Route: delegated direct writer. Trigger evidence: coordinated content/assets/builder changes require multiple non-trivial files.
- [x] **PPC-2 — Rework shared theme and Home.** Implement global toggle, palette, interaction accessibility, responsive header, hero/profile and home project/career/contact sections. Route: delegated direct writer. Checks: builder/verifier, static interaction inspection, rendered browser QA.
- [x] **PPC-3 — Restructure Projects inventory.** Add distinct ninth Control Tower entry, specified top-four and category grouping, project-list stories/icons/CTA, and nine-project static assertions without losing existing case routes. Route: delegated direct writer. Checks: builder/verifier, all local links/assets, visual/browser QA.
- [x] **PPC-4 — Refine CV and provide real PDF.** Update progression, contribution vs. outcome, value areas and workflow; create A4 downloadable PDF from existing HTML/Chromium; ensure static serving and print behavior. Route: delegated direct writer. Checks: PDF opens, dimensions A4, download link resolves, browser/print visual QA.
- [x] **PPC-5 — Full regression and local work-unit close.** Run mandated build, verifier, JS syntax and diff checks; inspect local built routes/metadata/theme/interactions/responsive screenshots; update tracker and Engram mirror after each task; create local Conventional Commits with no AI attribution. Route: delegated direct verification, parent spot check. Checks: commands and visual proof recorded below.

## Progress and Verification
- Exploration handoff: parent map agent identified `index.html`, `projects/index.html`, `cv/index.html`, `styles.css`, `script.js`, `tools/build_site.py`, and `tools/verify_site.py` as primary surfaces. This tracker intentionally supersedes neither prior V4 artifacts nor their historical decisions.
- Initial repository status: branch confirmed; pre-existing untracked `.codegraph/`, `.codex-remote-attachments/`, `odd/tasks/personal-brand-v4.md` preserved untouched.
- TDD source: existing project tracker; resolved off. RDD source: user instruction; disabled.
- PPC-1 evidence: added `content/projects-and-cv.md` covering nine projects and CV facts with provenance/date-precision distinctions; optimized the user-supplied transparent portrait to `assets/harrys-yusti-portrait.webp` (760×675 RGBA, alpha 0–255, 66,162 bytes; source 1330×1182). Visual readback confirmed portrait remains intact with transparency.
- PPC-2 evidence: implemented global persistent light/dark switch, vivid sticky header, responsive portrait-led Home, concise personal copy, signature/project/career/contact content, and accessible hover/focus/reduced-motion styling. Added early theme boot and shared script to 404 and all four case routes. Commit `120336f` (`feat(profile): add portrait-led home and dark mode`).
- PPC-3 evidence: replaced Projects listing with exact requested headline/story, four #TOP4 cases and five extra entries in three type groups; compact reference-inspired icons, details teasers, exact CTA text; Tower remains distinct from anomaly project. Static verifier checks new count/grouping and 9 icons. Commit `30dc1db` (`feat(projects): group nine portfolio case studies`).
- PPC-5 discovery/fix: final full-page Home readback exposed contact links/body copy inheriting `--ink`, yielding low contrast against the light-theme navy contact panel. Changed those descendants to inherit the panel’s contextual color so contrast is correct in both light and dark themes. Rebuilt, reran verifier, rechecked screenshots and all local paths afterward.
- Browser QA: rendered Home at 1024×768 dark and 390×844; Projects at 1024×768 light, 1440×900 dark, and 390×844 dark; CV at 1024×768 light and 390×844 dark. Confirmed no horizontal overflow, theme persists across route/reload, Space toggles theme and updates `aria-pressed`/label, and no console errors.
- PDF: real A4 PDF generated from current CV with installed Chrome via existing Playwright package; 2 pages, A4 media box 594.96×841.92 pt, 93,647 bytes, 3,526 extracted text chars; browser downloadMedia saved it as `C:\Users\harry\Downloads\harrys-yusti-cv.pdf`.
- Build: `python tools/build_site.py` passed (8 HTML pages plus public assets).
- Verifier: `python tools/verify_site.py` passed (all routes/semantic checks; SEO/sitemap/robots/allowlist; four #TOP4 and five categorized projects).
- `node --check script.js`: passed.
- `git diff --check`: passed (only normal Git LF→CRLF warnings).
- PPC-4 evidence: revised professional profile, 3 Natura roles grouped under one employer progression with source year ranges, role contributions/results distinguished, relevant project links, three value areas and workflow. Generated and verified genuine downloadable A4 PDF with system Chrome and preinstalled Playwright, no package installation. Commit `0543a69` (`feat(cv): add downloadable A4 profile`).
- PPC-5 local validation: final `python tools/build_site.py`, `python tools/verify_site.py`, `node --check script.js`, and `git diff --check` passed. Build produced 8 HTML pages plus assets; all 9 public URL checks (home, projects, CV, four case routes, 404.html, PDF) returned HTTP 200; PDF served as `application/pdf`. Canonical/social metadata, JSON-LD, sitemap, robots, local resources, semantic/heading checks, and optimized image dimensions passed verifier. Browser confirmed home default light on fresh origin; persistent dark mode, accessible keyboard Space, no horizontal overflow at requested breakpoints, disclosures keyboard-operable, and no console errors.
- Work-unit commits: PPC-1 `bcd999b`; PPC-2 `120336f`; PPC-3 `30dc1db`; PPC-4 `0543a69`; PPC-5 tracker/final contrast fix close commit pending.

## Next Step
Implementation and requested checks are complete. Record the PPC-5 close commit identity and keep local delivery only.

## Relevant Files
- `odd/tasks/profile-polish-dark-home-cv.md` — recovery ledger for this feature.
- `index.html`, `projects/index.html`, `cv/index.html` — static page content to update.
- `styles.css`, `script.js` — shared visual/interaction layer.
- `tools/build_site.py`, `tools/verify_site.py` — public asset allowlist and regression checks.
- `content/projects-and-cv.md` — fact-managed source for all requested portfolio content.
