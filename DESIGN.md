# Design system — Editorial Executive Profile

## Position

The site presents Harrys Yusti as a mechanical engineer working across projects, operations, Supply Chain, productivity, and operational transformation. Technology, data, automation, and AI are enablers—not the primary professional identity. The visual personality supports clarity and evidence rather than turning the profile into a field guide or a product dashboard.

## Visual language

- **Canvas:** warm paper `#f4f0e7`, navy ink, soft secondary ink, and restrained editorial red.
- **Type:** system serif display headings, sans-serif reading/navigation, small monospaced section labels; no external font requests.
- **Composition:** fine rules, whitespace, open ledger rows, restrained numbering, and typographic impact measures rather than KPI cards.
- **Images:** the existing WebP illustration is decorative and explicitly not a portrait or project photograph. No personal portrait exists yet.

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
