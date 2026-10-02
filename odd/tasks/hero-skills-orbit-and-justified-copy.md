# Hero Skills Orbits and Justified Copy — Organic Work Tracker

## Objective
Replace the decorative hero spark with three accessible, editable professional-area circles around the portrait and make long-form site copy consistently justified and readable.

## Problem and Why
The orange spark has no professional meaning, while prose alignment differs across the site. On narrow screens, justification without hyphenation produces distracting gaps.

## Scope and Constraints
- Keep the existing static HTML/CSS/JavaScript architecture and content-editor workflow.
- Use only supported professional areas already present in the site: Projects & Transformation, Supply Chain, and Operations. Do not invent named technical tools or credentials.
- Keep the three labels in the canonical `content/site.json` hero content and editable from the content editor.
- Circles must remain legible and accessible, responsive, and respect reduced-motion preferences.
- Justify editorial prose while keeping short labels, section kickers, and controls naturally aligned; enable Spanish hyphenation and keep final lines left-aligned.
- Local feature branch only; no push, deploy, PR, or merge without explicit user authorization.
- Preserve existing untracked user/helper files.

## Authorized Scope
- Repository: `C:\Users\harry\OneDrive\Documentos\GitHub\Harryslanding`.
- Branch: `codex/header-monogram-palette`.
- Authorized: local source/content/editor updates, generated output, focused verification, and work-unit commits.
- Not authorized: remote publication or changes to unrelated user files.

## Execution Mode and Route
- Route: T1/T2 delegated direct for the coordinated multi-file implementation; T3 direct inline as a bounded one-file CSS correction after visual QA.
- TDD: Standard Mode, `strict_tdd=false`, based on the existing project tracker’s explicit project choice. Focused structural check: `python tools/verify_site.py`; relevant test suite: `python -m unittest tests.test_content_editor`.
- Forecast: below 400 authored changed lines, excluding generated output.
- Work units: each task closes with a Conventional Commit on this feature branch.

## Acceptance Criteria
- No orange spark remains in the hero.
- Three visible, readable skill-area circles are sourced from editable master content and rendered as meaningful text, not decorative-only marks.
- Content validation rejects missing, blank, or incorrectly sized circle labels.
- Motion is subtle, does not obscure the portrait, adapts to mobile, and is disabled/reduced for `prefers-reduced-motion`.
- Editorial prose across site pages is justified with Spanish hyphenation and a naturally aligned final line; short interface labels remain unaffected.
- Generated pages, editor, and content source remain consistent.
- Focused checks pass and screenshots at desktop/mobile show no clipping, awkward gaps, or obscured face.

## Checklist
- [x] T1 — Add the three source-driven hero areas, expose them in the content editor, validate them, render accessible orbit markup, and add focused regression tests. Commit: `7c8f2f33323704c6695eaad4c9ee722100c7b101` (`feat(hero): render editable profile areas`).
- [x] T2 — Replace spark styling with responsive, reduced-motion-safe orbit circles; apply readable global prose justification and verify desktop/mobile. Commit: `86f2903a276fcadd7ca012aa27e418b76ea7e316` (`style(hero): add responsive orbit and prose rhythm`).
- [x] T3 — Correct narrow-tablet paragraph measure without removing justified alignment; recheck the hero and working-method introduction at 754px and 390px, then rerun the focused checks. Commit: `75479442d68827cf44b97bd001c7e26c67dff807` (`fix(styles): improve justified copy at tablet widths`).

## Verification Plan and Results
- `python -m unittest tests.test_content_editor`
- `python tools/build_site.py`
- `python tools/verify_site.py`
- `git diff --check`
- Local browser check at desktop and mobile widths; inspect rendered hero, paragraph spacing, and reduced-motion behavior.
- T1: `python -m unittest tests.test_content_editor` — PASS (12 tests); `python tools/build_site.py` — PASS (8 source HTML pages); `git diff --check` — PASS before commit.
- T2: `python -m unittest tests.test_content_editor` — PASS (12 tests); `python tools/build_site.py` — PASS (8 source HTML pages); `python tools/verify_site.py` — PASS (required routes, semantic HTML, links/resources, metadata, output allowlist, portfolio copy/diagrams); `git diff --check` — PASS before commits.
- Browser: desktop 1440×960 and mobile 390×844 inspected at `http://localhost:8000/`; profile text circles remain readable and do not cover the face. Computed hero introduction styles: `text-align: justify`, `text-align-last: left`, `hyphens: auto`; section kicker remains start-aligned. With reduced motion emulated, orbit animation duration computes to `1e-05s`.
- Screenshots: `.playwright-cli/page-2026-10-02T14-17-25-038Z.png` (desktop), `.playwright-cli/page-2026-10-02T14-17-29-306Z.png` (mobile), `.playwright-cli/page-2026-10-02T14-17-37-228Z.png` (mobile with reduced motion).
- T3: At 754px, hero and working-method copy use readable full-width measures (453px/512px) and remain justified; at 390px, 16px copy in a 332px measure improves spacing while retaining justification. No clipping or horizontal overflow at either width. `python -m unittest tests.test_content_editor` — PASS (12 tests); `python tools/build_site.py` — PASS (8 pages); `python tools/verify_site.py` — PASS; `git diff --check` — PASS (line-ending warnings only). Browser console: zero errors.

## Progress
- Read-only mapping confirmed `content/site.json` → `tools/content-editor/app.js` → `tools/build_site.py` as the editable content pipeline; `styles.css` controls hero and prose presentation.
- TDD mode inherited from the existing project task record: Standard Mode (`strict_tdd=false`).
- T1 complete: added editable `home.hero.profileAreas` labels, exact-three/non-empty validation, accessible list markup, and editor/render regression coverage.
- T1 commit: `7c8f2f33323704c6695eaad4c9ee722100c7b101`.
- T2 complete: replaced the spark with three responsive text circles; added subtle float motion, mobile placement/sizing, reduced-motion compatibility, and scoped long-form justification with Spanish hyphenation and left-aligned final lines.
- T2 commit: `86f2903a276fcadd7ca012aa27e418b76ea7e316`.
- T3 complete: responsive hero and working-method layouts now stack at tablet widths, and their intro copy reduces to 1rem on small mobile screens to improve justified line spacing without changing alignment.
- T3 commit: `75479442d68827cf44b97bd001c7e26c67dff807`.
- No remote operations performed.

## Relevant Files
- `content/site.json` — canonical site and hero content.
- `tools/content-editor/app.js` — editable Home fields.
- `tools/build_site.py` — content validation and static markup generation.
- `styles.css` — responsive hero, motion, and typography.
- `tests/test_content_editor.py` — editor save and validation regression tests.
