# Design system — Editorial Executive Profile

## Position

The site presents Harrys Yusti as a mechanical engineer working across projects, operations, Supply Chain, productivity, and operational transformation. Technology, data, automation, and AI are enablers—not the primary professional identity. The visual personality supports clarity and evidence rather than turning the profile into a field guide or a product dashboard.

## Visual language

- **Canvas:** warm paper `#f4f0e7`, navy ink, soft secondary ink, and restrained editorial red.
- **Type:** system sans-serif display headings and reading/navigation, Georgia for personal statements and quotes, selective monospaced metadata; no external font requests.
- **Composition:** fine rules, whitespace, open ledger rows, restrained numbering, and typographic impact measures rather than KPI cards.
- **Visuals:** Home uses an intentional abstract connection-flow drawing; project pages use small process diagrams, not portrait or project-photo substitutes. A future approved portrait may use `assets/harrys-portrait-800.webp`.

## Home — five acts

1. **Identity:** name, engineering background, experience, domains, and a concise value proposition.
2. **How I work:** understand friction, simplify, connect teams/data, automate with controls, and measure.
3. **Selected transformations:** three short, evidence-led examples with contribution separated from initiative outcome.
4. **Career and person:** professional evolution, a concise human perspective, and current AI/automation exploration.
5. **Continue the conversation:** clear recruiter-facing invitation and supplied LinkedIn/GitHub links.

Projects and the detailed CV live on their own routes so the Home remains scannable.

## Responsive and accessible behavior

Use one semantic document per route with a skip link, landmarks, one H1, clear heading order, visible keyboard focus, descriptive link names, and intrinsic image dimensions. Layouts collapse to one-column reading on narrow screens without horizontal scrolling. Motion is minimal and respects `prefers-reduced-motion`. The CV has a dedicated A4 print stylesheet. These implementation choices are not a claim of independently certified WCAG conformance.

## Content and evidence

Use only facts and outcomes confirmed in the V4 Master Plan. State the project outcome separately from Harrys's contribution; do not assign collective results to him individually. Do not invent current title, contact details, client names, testimonials, tools used on a particular project, or photography. Label AI as current exploration.

## SEO and publishing

Production base URL: `https://harrysxavio.github.io/`. Each page has a route-specific canonical and social URL. Home structured data identifies the Person and ProfilePage; other indexable pages use their page and breadcrumb entities. Sitemap contains all indexable routes and excludes the noindex 404. GitHub Pages continues to publish `main` from repository root; `tools/build_site.py` creates a local allowlisted artifact only.

## V4.1 visual and interaction direction

V4.1 preserves the static multipage architecture, the five Home acts, all route metadata, and all confirmed professional facts. The visual system moves to system-sans 700 headings with a 5.5rem desktop / 3.5rem mobile Home H1, 17–18px reading text, Georgia reserved for the personal statement and quotes, and sparse monospaced metadata. The existing paper, navy, restrained red, and pale-blue palette remains; rules and red all-caps labels are used more selectively.

The Home hero is a 58/42 editorial split with a code-native abstract connection-flow visual. It is intentionally not a portrait; `assets/harrys-portrait-800.webp` is only a documented future asset destination and no missing-image placeholder is rendered. The signature section keeps each real example in one native `<details>` source. JavaScript enhances desktop widths (1024px and above) into keyboard-operable tabs and one visible panel; mobile and no-JavaScript rendering remain native disclosures. Breakpoint changes retain the selected step and transfer focus only when the currently focused control is replaced.

Project detail visuals are lightweight, inline SVG explanations of the confirmed workflows: inventory reconciliation and exception control; Brazil-to-Chile master-data validation; patient transport allocation from demand and capacity; and order picking balanced across zones. They are explanatory diagrams, not screenshots or detailed depictions of a production system. The CV route retains its dedicated A4 print stylesheet and print control.
