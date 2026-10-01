# Visual recovery and content editor

## Objective
Restore the static portfolio's intended modern, accessible visual/interaction contract and provide a usable local form-based content editor without introducing dependencies or a public write surface.

## Problem and why
The semantic v3 renderer dropped component hooks required by the client interaction layer, leaving a generic, serif-heavy page with no signature tabs. The owner also needs an approachable way to edit canonical content without hand-editing JSON/HTML.

## Scope and constraints
- Preserve `content/site.json` as the canonical semantic source and the existing static build architecture.
- Use the supplied portrait only; do not invent personal claims, metrics, dates, or experience.
- No dependencies, frameworks, image generation, remote operations, PR, or RDD review. TDD is off; run ordinary checks.
- Keep protected untracked `.codegraph/`, `.codex-remote-attachments/`, `odd/tasks/personal-brand-v4.md`, and `output/` untouched.
- Code/comments in English; public copy and editing guide in neutral professional Spanish.
- Branch: `codex/visual-recovery-content-editor`; delivery exception is authorized, so no PR/chain selection.

## Resolved execution mode
- Route: delegated direct, one writer; trigger: implementation spans multiple non-trivial files and reading prepares the write.
- TDD: off, resolved from the existing task context; use ordinary focused regression checks.
- Native review: off (`clone_local`); do not start or re-enable it.
- Expected authored changes: more than 400 lines; no PR is authorized or planned.

## Checklist
- [ ] T1 — Restore modern semantic portfolio compositions and client component contracts across home, projects, CV, and case pages.
- [ ] T2 — Add a loopback-only Spanish form editor that validates and safely rebuilds the canonical content; document launch and preview/publication distinction.
- [ ] T3 — Add regression coverage, strengthen generated-site verification, run functional/browser/visual QA, and record evidence.

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
- Browser: Home/Projects/CV at 1440x900, 1024x768, 390x844, light/dark; tabs, keyboard, mobile disclosure, filters, theme, reduced motion, overflow/errors/links/print.

## Progress and evidence
- T1: in progress.
- T2: pending.
- T3: pending.
- Commits: pending.
- Screenshot evidence: `output/qa-visual-recovery/` (protected output directory; do not alter pre-existing contents).

## Next step
Implement T1, validate the rendering contracts, then commit the cohesive visual recovery before proceeding to the editor.
