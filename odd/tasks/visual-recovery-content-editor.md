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
- [x] T1 — Restore and refine modern semantic portfolio compositions and client component contracts across home, projects, CV, and case pages. Visual follow-up fixed Projects copy/layout and ensured responsive tabs are hidden outside desktop mode while preserving focus across resizes.
- [x] T2 — Add a loopback-only Spanish form editor that validates canonical content and transactionally restores generated output on build failure; reject unsafe rendered URLs and preserve initial-page editing context.
- [x] T3 — Add regression coverage, strengthen generated-site verification, run functional/browser/visual QA, and record evidence, including the latest parent-reported regressions.
- [x] T4 — Remove fixed project-count and two-tag guidance/validation constraints; support adding/removing secondary records and one-or-more valid existing tags while preserving four unique routed cases, current facts/IDs, and four featured priorities. Add regressions for tenth project, one-tag project, secondary removal, duplicate-route rejection before writes, protected routes, and unknown-tag rejection. Reopened after independent verification found a duplicate route assignment could preserve the route set while increasing routed records to five.

## Acceptance criteria
- Five signature steps/tabs are restored with accessible desktop tabs and mobile/no-JS disclosure.
- Home/projects/CV/cases use deliberate system-sans typography, coherent layout, responsive behavior, theme and reduced-motion support.
- Local editor forms cover site/home/projects/CV and project metadata; unsafe or invalid writes are rejected and a failed build preserves source.
- Editor binds only to `127.0.0.1`; it is not emitted in the Pages allowlist.
- The Home page renders exactly one visible global footer, driven by editable `home.footer` name, tagline, and back-to-top label/href; other routes retain the global footer.
- Project record count may vary; each record must use at least one valid existing taxonomy tag. Exactly four project records must have unique assignments to the four current case routes; the four-featured priority limit remains protected.
- Existing routes/content facts remain intact; generated pages pass strengthened contract checks.

## Verification
- `python tools/build_site.py`
- `python tools/verify_site.py`
- `node --check script.js`
- `python -m py_compile tools/build_site.py tools/verify_site.py tools/content_editor.py`
- `python -m unittest discover -s tests -v`
- `git diff --check`
- Browser: Home/Projects/CV at 1440x900, 1280x800, 1024x768, 768x1024, 430x932, 390x844, 360x800, light/dark; tabs, keyboard, mobile disclosure, filters, theme, reduced motion, overflow/errors/links/print. Use installed shell Playwright for exact viewport sizing if the in-app browser ignores requested dimensions.
- T4 checks: `python -m unittest discover -s tests -v`, `python tools/build_site.py`, `python tools/verify_site.py`, `python -m py_compile tools/build_site.py tools/verify_site.py tools/content_editor.py`, `git diff --check`.

## Progress and evidence
- T1: original commit `001c3b9` (`fix(site): restore modern semantic portfolio compositions`); visual follow-up `68e16e9` (`fix(site): polish featured project portfolio`). Restored system-sans/blue composition, real-portrait hero and CTA hierarchy, semantic five-stage tab/disclosure hooks, featured project cards, career timeline/notes, case narratives and footer de-duplication. Follow-up corrected Projects content/layout and project-specific marks.
- T1 checks: `python -m py_compile tools/build_site.py tools/verify_site.py tools/content_editor.py` PASS; `node --check script.js` PASS; `node --check tools/content-editor/app.js` PASS; `python tools/build_site.py` PASS (8 pages); `python tools/verify_site.py` PASS (canonical Projects H1, four featured projects/marks, no internal editorial notes); `python -m unittest discover -s tests -v` PASS (3 tests); `git diff --check` PASS (Git reports LF-to-CRLF warnings only).
- Parent design feedback preserved: concise headline; five-step component on the same horizontal band as its explanation; compact evidence with meaningful project-specific visual marks; CV has its own hierarchy. Compatible external audit guidance: semantic component hooks, no positional nth-child styling, consolidated tokens/components, readable seven-width review. Keep existing dark mode, search, applied-AI note, and compact STAR.
- T2: complete — `7a5fae0` (`feat(editor): add local Spanish content editor`). Editor binds to loopback, limits preview to the public build, validates schema before build, and restores source if validation/build fails. Spanish launcher and workflow guide distinguish local preview/save from publication.
- Parent-reported follow-up regressions are now corrected: failed saves restore canonical JSON, all required root-generated pages, and the complete `dist/` tree; URL validation allows same-site paths/anchors and HTTPS only, rejecting control characters and executable/protocol-relative schemes; initial editor load stays at the explanatory top section.
- T3: complete — verification follow-up `6a15ce6` (`test(site): verify editable portfolio components`). Strengthened `verify_site.py` for canonical Projects H1, four TOP4 cards with distinct marks, and absence of internal editorial copy. `python tools/build_site.py`, `python tools/verify_site.py`, `node --check script.js`, `python -m py_compile tools/build_site.py tools/verify_site.py tools/content_editor.py`, `node --check tools/content-editor/app.js`, `python -m unittest discover -s tests -v` (3 pass), and `git diff --check` all passed. Browser checked Projects at 1440x900, 1024x768, 768x1024, 430x932, 390x844, and 360x800: no horizontal overflow, four featured cards, no internal copy. Earlier visual/browser matrix and interaction coverage are in `output/qa-visual-recovery/`; actual screenshot inspection used shell Playwright because IAB viewport requests were ignored.
- Latest regression checks: five editor tests pass, including failed-build mutations to source HTML and `dist/`, partial-file cleanup, plus `javascript:`, `data:`, protocol-relative, nested Home/project-link, and control-character rejection before writes. Playwright verified desktop tablist visible with five tabs; mobile tablist hidden with five accessible summaries; resize back preserves selected step/focus; focus outside the component remains unchanged. Initial editor load has `scrollY=0`; explicit section navigation scrolls to the form.
- Commits: `001c3b9` initial visual restoration; `68e16e9` visual follow-up; `461b1a8` follow-up evidence; `7a5fae0` editor/docs; `6a15ce6` verifier and QA; `1841e80` refreshed A4 CV PDF; `e203c72` transactional save and URL validation; `be03db1` responsive tabs and editor context.
- Screenshot evidence: `output/qa-visual-recovery/` (created for this task; refreshed final 1440x900 Projects image is `projects-1440-light.png`). Follow-up PDF refresh: `cv/harrys-yusti-cv.pdf`, generated from the final `/cv/` print rendering via Playwright on A4 (3 pages); checked title, page dimensions, extracted text, file validity, and raster-rendered every page.
- Final structural readback found Home's global footer was hidden by CSS while `home.footer` was loaded but not rendered. Commit `4ed8ab7` (`fix(home): restore source-driven footer`) removes the hide rule, renders the single global Home footer from its canonical editable fields, and strengthens `verify_site.py` to assert those fields and footer uniqueness. `python tools/build_site.py`, `python tools/verify_site.py`, `python -m py_compile tools/build_site.py tools/verify_site.py`, and `git diff --check` passed. Browser checks at 1440x900 and 390x844 confirmed one visible footer, canonical copy and `#top` link, no page errors; inspected screenshots saved outside the repository under the system temp directory.
- T4 diagnosis confirmed the builder and verifier each enforced exactly nine project records, and the editor confirmation/callout plus Spanish guide repeated that restriction. The builder already accepted one tag; the verifier and guide incorrectly required two. Commit `1ca88ad` (`fix(editor): support variable secondary projects`) now permits variable counts while requiring the four existing case routes, requires each project to have at least one valid existing taxonomy tag, and keeps exactly four featured priorities. The guide/editor now describe adding/removing secondary projects accurately. Regressions cover adding a tenth one-tag secondary project, removing a secondary project, retaining the four routes and featured priorities, and rejecting unknown tags. `python -m unittest discover -s tests -v` PASS (9 tests); `python tools/build_site.py` PASS (8 pages); `python tools/verify_site.py` PASS; `python -m py_compile tools/build_site.py tools/verify_site.py tools/content_editor.py` PASS; `node --check tools/content-editor/app.js` PASS; `git diff --check` PASS. Build changed tracked generated pages only by EOL normalization; confirmed no semantic diff and restored those generated files.
- Follow-up on T4: independent verification found the set-equality check allowed a fifth record to duplicate an existing case URL while preserving the four-route set. Commit `dfce436` (`fix(content): enforce unique case route assignments`) now requires exactly four route-bearing projects with unique assignments in both builder and verifier. A regression copies a routed case into a new project with the same URL and asserts rejection occurs before the content source, generated output, or build call changes. `python -m unittest discover -s tests -v` PASS (10 tests); `python tools/verify_site.py` PASS; Python compilation and `git diff --check` PASS.

## Next step
Published visual version 41d6718 is independently verified. The final content-only variable-project patch is independently verified and ready for authorized publication; it leaves default public page/asset bytes unchanged.

## Independent closure
- Targeted independent retest on 3577dfe PASS: all three reproduced blockers resolved; valid edits still rebuild. Five unit tests, site verifier and JS syntax checks pass. Browser resize 1440 to 390 to 1440 preserves selection/focus and renders tabs only on desktop. Editor starts at scrollY=0. Three A4 PDF pages parsed/raster-inspected; printed skip-link is a remaining cosmetic issue.
- Parent spot-check on 67c0a54: site verifier and git diff --check PASS. Final Home footer desktop/mobile screenshots inspected and visibly coherent. Lighthouse was pending at this earlier checkpoint; see final production evidence below; internal perception checks are not recruiter research or formal accessibility certification.

## Final production and editor evidence
- Production41d6718: all eight HTML routes and CSS, JS, supplied portrait, CV PDF match committed bytes (text EOL normalized); unknown route returns404. Desktop1440x900 and mobile390x844: Home/Projects/CV and case routes load without overflow, console errors, failed resources or duplicate footers. Tabs/keyboard/theme/search/multi-tag/mobile disclosures pass; six production screenshots saved in output/qa-visual-recovery.
- Standalone official Lighthouse13.5.0 via temporary npx/installed Chrome, no site dependency changes: desktop1350x940 preset simulated40ms RTT/10240Kbps/1xCPU and mobile412x823 simulated150ms RTT/1638Kbps/4xCPU both score100 Performance/Accessibility/Best Practices/SEO. DesktopFCP/LCP0.5s/0.5s CLS0.001; mobileFCP/LCP1.1s/1.2s CLS0.002. Single-run lab audit, not accessibility certification or recruiter research. JSON reports in output/qa-visual-recovery/qa-prod-lighthouse-desktop.json and qa-prod-lighthouse-mobile.json.
- Independent targeted editor retest84a3be3 PASS: fifth duplicated case route rejected before source/output writes; tenth secondary one-tag project accepted; all10 unit tests pass. Parent spot-check of earlier9-test suite passed; final suite spot-check recorded at publication.
- Remaining limitations: downloadable CV PDF is static and must be refreshed after future CV edits; its printed skip link is cosmetic. Local editor saves rebuild local HTML only, not public deployment.
