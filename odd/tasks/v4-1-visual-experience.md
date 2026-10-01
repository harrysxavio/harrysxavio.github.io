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
- Create four distinct, light, honest reusable SVG/CSS project visuals; preserve domain constraints and outcomes. Inventory reconciliation is tied only to its 30% time / 40% support outcomes; the ~2-day-to-4-hour anomaly resolution remains separate Signature “Ver”/other work and is not assigned to inventory. Brazil–Chile data mapping (~120k); patient transport is patient allocation/routes/service, never freight; picking is orders/zones/workload balancing, never manufacturing. Four case pages use a consistent problem/outcome/visual/flow/contribution/confirmed decisions/before-after/outcome rhythm and distinguish personal contribution from collective results.
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
- [ ] V41-7 — Commit coherent tested work units; record commit IDs; leave push/merge/deploy and native review to parent. Initial tracker commit: `6f3f5e7`; source work commit pending.

## Acceptance Criteria
1. All 8 routes remain buildable and retain their route-specific canonical/social/JSON-LD content and factual professional content.
2. Home order is exactly identity/hero, signature, selected transformations, career+human, contact; no sixth act.
3. Desktop hero is 58/42 and split; mobile 390 viewport shows name, statement, actions, and start of visual. No placeholder/fake portrait.
4. Signature preserves its single native content source, all five exact IDs and evidence, desktop tab interaction, mobile/no-JS details fallback, ARIA relationships and keyboard interaction; breakpoint changes do not steal focus.
5. All four project visuals are distinct and factually honest; patient transport and picking contexts are accurately represented; contribution and outcomes remain separate.
6. Sans display and body, Georgia only for statements/quotes, selective metadata, less red/mono and fewer rules; palette retained.
7. Public copy contains no pending-portrait/FTE/internal/defensive/legal disclaimers; AI exploration uses approved framing.
8. `/cv/` print layout and eight SEO routes remain intact; no new dependencies/framework.
9. Required checks are run and reported accurately; commits contain only V4.1 files, no unrelated untracked content.

## Progress Evidence
- Initial branch: `redesign/v4-1-visual-experience`.
- Initial tracked state was clean; unrelated untracked `.codegraph/`, `.codex-remote-attachments/`, and `odd/tasks/personal-brand-v4.md` remain untouched.
- CodeGraph index is healthy but only covers Python/JS/XML, not HTML; structural HTML/CSS mapping therefore requires narrow source inspection after checking `codegraph status` and `codegraph files`.
- Existing public pages: `/`, `/projects/`, four case pages, `/cv/`, and `/404.html`.
- `tools/build_site.py` and `tools/verify_site.py` support multipage route discovery and SEO checks; build invocation is `python tools/build_site.py`, verifier invocation `python tools/verify_site.py`.
- Original V4 case content and professional facts remain the source of truth; the supplied V4.1 execution brief supersedes any visual implementation assumptions.
- Tracker work unit commit: `6f3f5e7 docs: track v4.1 visual experience`.
- Verification passed: build created 8 HTML pages; verifier passed required routes, semantics, links, resources, SEO/social metadata, structured data, robots/sitemap, and output allowlist; Node syntax check passed; diff check passed with only expected Windows LF→CRLF notices.
- Browser assertions passed for desktop tabs/click/End, connected-node state, desktop-to-mobile focus/selection preservation, mobile full-width primary CTA, no-JavaScript details fallback, all 8 route responses, the four case diagram accessible names/descriptions, and no horizontal overflow at 1440×900, 1024×768, 390×844, and 360×800; page errors: 0.
- Screenshots: `%TEMP%\v41-final-1440x900.png`, `%TEMP%\v41-final-1024x768.png`, `%TEMP%\v41-final-390x844.png`, `%TEMP%\v41-final-360x800.png`, `%TEMP%\v41-final-brazil-mobile.png`.

## Next Step
Commit the verified source/documentation work unit, record its commit identity, and hand off for parent IAB visual review and independent verification. No push/merge/PR/deploy.

## Relevant Files
- `index.html` — five-act homepage and signature detail content.
- `styles.css` — shared responsive visual system and CV print styles.
- `script.js` — progressive signature interaction.
- `projects/` — projects index and four case studies.
- `cv/index.html` — standalone print-ready CV.
- `DESIGN.md`, `README.md` — design/product and local usage documentation.
- `tools/build_site.py`, `tools/verify_site.py` — public site build and route validation.
