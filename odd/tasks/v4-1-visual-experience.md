# V4.1 Visual Experience

## Objective
Refine the approved V4 personal site into a visually distinctive, responsive, accessible professional experience while preserving its static architecture, route set, SEO, factual content, and five-act Home order.

## Problem / Why
The current V4 structure and content are sound, but its serif-heavy headings, repetitive rule/list rhythm, and passive signature details feel more like a styled CV than a memorable personal profile. V4.1 changes the visual language and makes the signature system meaningfully interactive without changing architecture or inventing claims/assets.

## Scope
- Preserve all eight public routes, route-specific SEO metadata, existing professional facts, attribution, CV print behavior, and Home act order.
- Home: split 58/42 hero with name, 11-year engineering context, original personal question, one support sentence, subordinate domains and CTA set; abstract no-portrait visual. Then signature, selected projects, career/human notes, and navy contact.
- Use system sans-serif 700 display headings; H1 88px desktop/56px mobile; 17–18px body; Georgia only for the personal statement/quotes; selective mono metadata. Retain paper/navy/red/pale-blue palette; reduce red uppercase mono labels roughly by half and use fewer borders.
- Signature content remains one source with five evidence-backed details (`ver`, `simplificar`, `conectar`, `automatizar`, `medir`), progressively enhanced desktop tabs/one-panel view and native mobile/no-JS details. Implement keyboard roving focus, arrows/Home/End, click activation, ARIA links; breakpoint changes preserve selection and only restore focus when the focused control disappears. Initialization failure leaves fallback intact.
- Create four distinct, light, honest reusable SVG assets referenced by Home portfolio visuals and matching cases, with mobile variants that keep diagram text at least 12px; preserve domain constraints and outcomes. Inventory reconciliation is tied only to its 30% time / 40% support outcomes; the ~2-day-to-4-hour anomaly resolution remains separate Signature “Ver”/other work and is not assigned to inventory. Brazil–Chile data mapping (~120k); patient transport is patient allocation/routes/service, never freight; picking is orders/zones/workload balancing, never manufacturing. Four case pages use a consistent problem/outcome/visual/flow/contribution/confirmed decisions/before-after/outcome rhythm and distinguish personal contribution from collective results.
- Keep hero visual abstract and intentional, never a fake portrait. Document future `assets/harrys-portrait-800.webp` slot only; do not add missing image placeholder.
- Keep AI exploration copy factual and secondary; remove public pending-portrait, FTE, internal, defensive, or legal disclaimers.
- Update DESIGN.md and README where behavior/design system changes. Preserve unrelated untracked `.codegraph/`, `.codex-remote-attachments/`, and existing ODD work.

## Constraints / Authorization
- User explicitly authorizes implementation on branch `redesign/v4-1-visual-experience` and work-unit Conventional Commits, without Co-Authored-By attribution.
- No push, merge, PR, deployment, automation, or native review; parent owns delivery and has confirmed clone RDD off.
- TDD explicitly off; use ordinary functional checks. No imagegen; SVG/CSS abstract visuals and existing image use/correction explicitly authorized.
- Maintain static HTML/CSS and minimal JS; retain print layout and all SEO/routing.
- Delivery strategy: single branch / no PR now, explicit user-authorized direct branch/merge delivery exception to ~400-line heuristic; do not enforce a size-only split or open PR.

## Effective TDD / Verification
TDD: off (explicit prior-session instruction); ordinary checks required.
Commands: `python tools/build_site.py`; `python tools/verify_site.py`; `git diff --check`; `node --check script.js`.
Visual/interaction checks: browser if available; home at desktop and 390×844 and 360×800; signature selection, keyboard movement, fallback and breakpoint state. Do not claim screenshot/browser QA unless performed.
Native RDD: off by explicit parent instruction; do not start a review lifecycle.

## Route and Trigger
Route: delegated direct single writer (as assigned by parent); implementation touches multiple existing HTML/CSS/JS/doc files, so writer delegation trigger is 2+ non-trivial files. User authorized branch commits. Do not create SDD artifacts or use native review.

## Tasks / Progress
- [x] V41-1 — Add this recovery/acceptance document and full Engram mirror before source writes; read back both. Evidence: file read back; Engram topic `odd/v4-1-visual-experience/tasks` saved and read-back confirmed below.
- [x] V41-2 — Recompose Home into the approved 5-act visual system and update DESIGN.md / README. Evidence: source and documentation readback; five sections remain in order.
- [x] V41-3 — Implement progressive signature interaction with accessible tabs/detail fallback, preserving CV print behavior. Evidence: desktop tab click/End, mobile selected state + focus restoration, no-JS native details, and CV route checks passed.
- [x] V41-4 — Redesign four project case visuals/content rhythm and featured/secondary composition without changing facts. Evidence: all four case pages and both secondary Home visuals have distinct named SVGs; exact copy and route verifier passed.
- [x] V41-5 — Apply responsive design and typography across public routes; preserve metadata and route behavior. Evidence: no overflow at 1440×900, 1024×768, 390×844, or 360×800; all 8 routes build/verify.
- [x] V41-6 — Run required build, verifier, JS syntax, diff checks, and available browser viewport/interaction checks. Evidence: `python tools/build_site.py`, `python tools/verify_site.py`, `node --check script.js`, `git diff --check`, and Playwright assertions all passed; browser errors=0. Screenshots saved outside the repo under `%TEMP%\v41-final-*.png`.
- [x] V41-7 — Commit coherent tested work units; leave push/merge/deploy and native review to parent. Evidence: `6f3f5e7 docs: track v4.1 visual experience`; `76bc86c feat: refine v4.1 visual experience`.
- [x] V41-C1 — Correct Projects mobile layout cascade; ensure four featured + four compact entries have readable text at 360/390/600/1024/1440; extract four honest reusable SVG assets and reference them from Home and matching case pages; add Brazil/patient problem statements; run targeted width/readability/flow regression and standard checks. Evidence: measured browser widths, route/flow assertions, updated site verifier, screenshots, and correction commit recorded below.
- [x] V41-C2 — Recompose Projects into two explicit groups headed “Casos destacados” (inventory full-width lead plus three featured cases in a responsive grid) and “Otros proyectos” (four compact entries). Preserve metrics; replace internal confirmation language with natural factual control wording. Add a responsive mobile variant for each shared SVG so diagram labels render at ≥12px, confirm all Home/portfolio/case picture sources, add static regression coverage and 390px full-page portfolio/case screenshots. Trigger: parent readback found the current eight interleaved rows do not satisfy grouping/composition and desktop diagrams' text is microscopic on mobile. Bounded plan-conformance correction; no new facts/routes. Evidence: commit `8a58358 fix: group featured cases and improve mobile diagrams`; build/site verifier/Node syntax/diff checks pass; targeted Playwright verified group order and 4+4 grouping, copy widths 286/316/506px at 360/390/600px, responsive columns at 1024/1440, correct mobile SVG `currentSrc` at 390px, all 5 pages return 200, no overflow or page errors. Mobile SVG label CSS sizes are 14px and 16px. Full-page screenshots in `%TEMP%`: `v41-c2-projects-390-full.png` and four matching case screenshots `v41-c2-projects-{inventory-reconciliation,brazil-chile-data-migration,patient-transport-optimization,picking-line-balancing}-390-full.png`.

## Acceptance Criteria
1. All 8 routes remain buildable and retain their route-specific canonical/social/JSON-LD content and factual professional content.
2. Home order is exactly identity/hero, signature, selected transformations, career+human, contact; no sixth act.
3. Desktop hero is 58/42 and split; mobile 390 viewport shows name, statement, actions, and start of visual. No placeholder/fake portrait.
4. Signature preserves its single native content source, all five exact IDs and evidence, desktop tab interaction, mobile/no-JS details fallback, ARIA relationships and keyboard interaction; breakpoint changes do not steal focus.
5. All four project visuals are standalone reusable SVG assets with title/description, descriptive HTML alt text, and mobile versions with readable (≥12px) labels; they are distinct and factually honest; patient transport and picking contexts are accurately represented; contribution and outcomes remain separate.
6. Projects index has explicit “Casos destacados” and “Otros proyectos” groups; inventory leads full-width, the other three featured cases use a responsive grid, and four compact entries appear below. All text remains readable at 360, 390, 600, 1024, and 1440px.
7. Sans display and body, Georgia only for statements/quotes, selective metadata, less red/mono and fewer rules; palette retained.
8. Public copy contains no pending-portrait/FTE/internal/defensive/legal disclaimers; AI exploration uses approved framing.
9. `/cv/` print layout and eight SEO routes remain intact; no new dependencies/framework.
10. Required checks are run and reported accurately; commits contain only V4.1 files, no unrelated untracked content.

## Progress Evidence
- Initial branch: `redesign/v4-1-visual-experience`.
- Initial tracked state was clean; unrelated untracked `.codegraph/`, `.codex-remote-attachments/`, and `odd/tasks/personal-brand-v4.md` remain untouched.
- CodeGraph index is healthy but only covers Python/JS/XML, not HTML; structural HTML/CSS mapping therefore requires narrow source inspection after checking `codegraph status` and `codegraph files`.
- Existing public pages: `/`, `/projects/`, four case pages, `/cv/`, and `/404.html`.
- `tools/build_site.py` and `tools/verify_site.py` support multipage route discovery and SEO checks; build invocation is `python tools/build_site.py`, verifier invocation `python tools/verify_site.py`.
- Original V4 case content and professional facts remain the source of truth; the supplied V4.1 execution brief supersedes any visual implementation assumptions.
- Tracker work unit commit: `6f3f5e7 docs: track v4.1 visual experience`.
- Verified implementation commit: `76bc86c feat: refine v4.1 visual experience` (11 in-scope files; unrelated untracked files excluded).
- Verification passed: build created 8 HTML pages; verifier passed required routes, semantics, links, resources, SEO/social metadata, structured data, robots/sitemap, and output allowlist; Node syntax check passed; diff check passed with only expected Windows LF→CRLF notices.
- Browser assertions passed for desktop tabs/click/End, connected-node state, desktop-to-mobile focus/selection preservation, mobile full-width primary CTA, no-JavaScript details fallback, all 8 route responses, the four case diagram accessible names/descriptions, and no horizontal overflow at 1440×900, 1024×768, 390×844, and 360×800; page errors: 0.
- Screenshots: `%TEMP%\v41-final-1440x900.png`, `%TEMP%\v41-final-1024x768.png`, `%TEMP%\v41-final-390x844.png`, `%TEMP%\v41-final-360x800.png`, `%TEMP%\v41-final-brazil-mobile.png`.
- Parent QA found the Projects list's later base `.portfolio-item` grid rule overrode the mobile one-column rule, collapsing copy/actions into narrow columns. The conflicting grid reset is removed; featured and compact variants now use separate responsive layouts.
- Four standalone accessible SVG assets with `<title>` and `<desc>` are shared by Home, the Projects portfolio, and matching case pages. Brazil/patient Home entries now state the problem; the portfolio clearly separates four featured cases from four compact projects.
- Targeted browser regression at 360×800, 390×844, 600×900, 1024×768, and 1440×900 measured featured copy widths at 283, 313, 503, 451, and 751 CSS px. Featured/compact text fits, images load, the document does not overflow, all four case flows load, and browser errors are zero.
- `tools/verify_site.py` now asserts four featured/four compact entries, their four matching project assets, descriptive case-page alt text, SVG title/description references, and required flow labels.
- Correction work-unit commit: `e03b429 fix: restore responsive project portfolio layout`.
- Correction screenshots: `%TEMP%\v41-portfolio-360.png`, `%TEMP%\v41-portfolio-390.png`, `%TEMP%\v41-portfolio-600.png`, `%TEMP%\v41-portfolio-1024.png`, `%TEMP%\v41-portfolio-1440.png`.
- C2 correction commit: `8a58358 fix: group featured cases and improve mobile diagrams`.
- Projects index now has separate, ordered `Casos destacados` and `Otros proyectos` sections; the inventory reconciliation lead spans the featured section and three cases follow in a responsive grid. Removed internal confirmation phrasing from the compact inventory-control entry.
- Added four mobile-only SVG compositions with readable 14–16px text and accurate concept flow; `<picture>` selects each variant for Home, portfolio, and its matching case page at ≤600px. `tools/verify_site.py` validates group structure, mobile source availability, accessible labels, workflow terms, and minimum mobile SVG label size.
- Responsive Playwright inspection at 360, 390, 600, 1024, and 1440 measured featured text widths of 286, 316, 506, 261/504, and 380/704px respectively; no document overflow or browser page errors. At 390px, Projects and all four case routes loaded with status 200 and each selected its correct mobile SVG.
- Full-page 390px screenshot evidence: `%TEMP%\v41-c2-projects-390-full.png`; `%TEMP%\v41-c2-projects-inventory-reconciliation-390-full.png`; `%TEMP%\v41-c2-projects-brazil-chile-data-migration-390-full.png`; `%TEMP%\v41-c2-projects-patient-transport-optimization-390-full.png`; `%TEMP%\v41-c2-projects-picking-line-balancing-390-full.png`.

## Next Step
Implementation and bounded C2 correction are complete and committed locally. Parent to perform independent visual readback and final verification; no push/merge/PR/deploy performed.

## Relevant Files
- `index.html` — five-act homepage and signature detail content.
- `styles.css` — shared responsive visual system and CV print styles.
- `script.js` — progressive signature interaction.
- `projects/` — projects index and four case studies.
- `cv/index.html` — standalone print-ready CV.
- `DESIGN.md`, `README.md` — design/product and local usage documentation.
- `tools/build_site.py`, `tools/verify_site.py` — public site build and route validation.
