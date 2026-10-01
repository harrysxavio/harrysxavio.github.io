# Visual recovery and content editor

## Objective
Restore the static portfolio's intended modern, accessible visual/interaction contract and provide a usable local form-based content editor without introducing dependencies or a public write surface.

## Problem and why
The semantic v3 renderer dropped component hooks required by the client interaction layer, leaving a generic, serif-heavy page with no signature tabs. The owner also needs an approachable way to edit canonical content without hand-editing JSON/HTML.

## Scope and constraints
- Preserve `content/site.json` as the canonical semantic source and the existing static build architecture.
- Use the supplied portrait only; do not invent personal claims, metrics, dates, or experience.
- No dependencies, frameworks, image generation, remote operations, PR, or RDD review. TDD is off; run ordinary checks.
- Keep protected untracked `.codegraph/`, `.codex-remote-attachments/`, and `odd/tasks/personal-brand-v4.md` untouched. Preserve all pre-existing `output/` content; create screenshots only under the previously absent `output/qa-visual-recovery/` requested for QA.
- Code/comments in English; public copy and editing guide in neutral professional Spanish.
- Branch: `codex/visual-recovery-content-editor`; delivery exception is authorized, so no PR/chain selection.

## Resolved execution mode
- Route: delegated direct, one writer; trigger: implementation spans multiple non-trivial files and reading prepares the write.
- TDD: off, resolved from the existing task context; use ordinary focused regression checks.
- Native review: off (`clone_local`); do not start or re-enable it.
- Expected authored changes: more than 400 lines; no PR is authorized or planned.

## Checklist
- [x] T1 — Restore and refine modern semantic portfolio compositions and client component contracts across home, projects, CV, and case pages. Follow-up visual review fixed the editable Projects H1, removed internal editorial notes from public cards, added four distinct TOP4 marks in a balanced 2x2 layout, and aligned secondary project rows into a full-width ledger.
- [x] T2 — Add a loopback-only Spanish form editor that validates and safely rebuilds the canonical content; document launch and preview/publication distinction.
- [x] T3 — Add regression coverage, strengthen generated-site verification, run functional/browser/visual QA, and record evidence.

## Acceptance criteria
- Five signature steps/tabs are restored with accessible desktop tabs and mobile/no-JS disclosure.
- Home/projects/CV/cases use deliberate system-sans typography, coherent layout, responsive behavior, theme and reduced-motion support.
- Local editor forms cover site/home/projects/CV and project metadata; unsafe or invalid writes are rejected and a failed build preserves source.
- Editor binds only to `127.0.0.1`; it is not emitted in the Pages allowlist.
- Existing routes/content facts remain intact; generated pages pass strengthened contract checks.

## Verification
- `python tools/build_site.py`
- `python tools/verify_site.py`
- `node --check script.js`
- `python -m py_compile tools/build_site.py tools/verify_site.py tools/content_editor.py`
- `python -m unittest discover -s tests -v`
- `git diff --check`
- Browser: Home/Projects/CV at 1440x900, 1280x800, 1024x768, 768x1024, 430x932, 390x844, 360x800, light/dark; tabs, keyboard, mobile disclosure, filters, theme, reduced motion, overflow/errors/links/print. Use installed shell Playwright for exact viewport sizing if the in-app browser ignores requested dimensions.

## Progress and evidence
- T1: original commit `001c3b9` (`fix(site): restore modern semantic portfolio compositions`); visual follow-up `68e16e9` (`fix(site): polish featured project portfolio`). Restored system-sans/blue composition, real-portrait hero and CTA hierarchy, semantic five-stage tab/disclosure hooks, featured project cards, career timeline/notes, case narratives and footer de-duplication. Follow-up corrected Projects content/layout and project-specific marks.
- T1 checks: `python -m py_compile tools/build_site.py tools/verify_site.py tools/content_editor.py` PASS; `node --check script.js` PASS; `node --check tools/content-editor/app.js` PASS; `python tools/build_site.py` PASS (8 pages); `python tools/verify_site.py` PASS (canonical Projects H1, four featured projects/marks, no internal editorial notes); `python -m unittest discover -s tests -v` PASS (3 tests); `git diff --check` PASS (Git reports LF-to-CRLF warnings only).
- Parent design feedback preserved: concise headline; five-step component on the same horizontal band as its explanation; compact evidence with meaningful project-specific visual marks; CV has its own hierarchy. Compatible external audit guidance: semantic component hooks, no positional nth-child styling, consolidated tokens/components, readable seven-width review. Keep existing dark mode, search, applied-AI note, and compact STAR.
- T2: complete — `7a5fae0` (`feat(editor): add local Spanish content editor`). Editor binds to loopback, limits preview to the public build, validates schema before build, and restores source if validation/build fails. Spanish launcher and workflow guide distinguish local preview/save from publication.
- T3: complete — verification follow-up `6a15ce6` (`test(site): verify editable portfolio components`). Strengthened `verify_site.py` for canonical Projects H1, four TOP4 cards with distinct marks, and absence of internal editorial copy. `python tools/build_site.py`, `python tools/verify_site.py`, `node --check script.js`, `python -m py_compile tools/build_site.py tools/verify_site.py tools/content_editor.py`, `node --check tools/content-editor/app.js`, `python -m unittest discover -s tests -v` (3 pass), and `git diff --check` all passed. Browser checked Projects at 1440x900, 1024x768, 768x1024, 430x932, 390x844, and 360x800: no horizontal overflow, four featured cards, no internal copy. Earlier visual/browser matrix and interaction coverage are in `output/qa-visual-recovery/`; actual screenshot inspection used shell Playwright because IAB viewport requests were ignored.
- Commits: `001c3b9` initial visual restoration; `68e16e9` visual follow-up; `461b1a8` follow-up evidence; `7a5fae0` editor/docs.
- Screenshot evidence: `output/qa-visual-recovery/` (created for this task; refreshed final 1440x900 Projects image is `projects-1440-light.png`). Static CV PDF was not automatically regenerated and should be refreshed separately if its layout no longer matches.

## Next step
Record the T3 work-unit commit identity, sync the full task record to its Engram mirror, and hand off for parent independent verification/publication.
