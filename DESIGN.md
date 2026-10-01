# Design system — Personal Transformation Profile

## Position

The site presents Harrys Yusti's confirmed experience across engineering, projects, operations, Supply Chain, and transformation. Data, automation, and AI are practical enablers—not a claim to be an AI product company, SaaS template, or generic technology designer. Personal statements stay first-person and grounded in the supplied content; this document does not assert independent recruiter research or certified accessibility conformance.

## Visual language

- **Canvas and color:** light off-white, navy ink, strong blue, and restrained coral; dark mode swaps to corresponding deep-navy surfaces with readable text and focus states.
- **Type:** cohesive system sans-serif for headings, navigation, and body copy; normal tracking for names and titles; no external font requests.
- **Composition:** generous but purposeful spacing, balanced split portrait hero, rounded CTA hierarchy, quiet depth, connected process controls, and compact evidence-led cards instead of dense report rows.
- **Portrait and visual assets:** use the supplied transparent portrait at `assets/harrys-yusti-portrait.webp`. Use focused project marks in the Home band and the existing descriptive workflow diagrams within case pages.

## Home sequence

1. **Identity:** name, a specific design statement, concise first-person context, supplied portrait, and a clear route to projects.
2. **How I work:** five real stages with concrete supporting evidence; desktop uses an accessible connected tab system while mobile and no-JavaScript use native disclosures.
3. **Selected work:** three same-band project cards with compact Situation/Task/Action/Result evidence, domain-specific marks, and aligned case links.
4. **Career story:** scannable progression, four human notes—including practical applied-AI experience—and a distinct current exploration note.
5. **Contact:** one characterized contact block followed by one restrained global footer.

Projects and the CV have dedicated layouts rather than being forced into the Home composition. The projects index maintains the featured-case hierarchy and searchable/tag-filtered set. Cases use semantic hero, evidence, workflow, narrative, and navigation components. The CV has its own readable employer progression, value areas, capabilities, and browser print action.

## Responsive and accessible behavior

Use one semantic document per route with a skip link, landmarks, one H1, sensible heading order, visible keyboard focus, descriptive link names, native disclosure content, and intrinsic image dimensions. Desktop tab navigation supports arrow keys, Home, and End; the editor and filter controls have associated labels. Layouts are checked at 1440, 1280, 1024, 768, 430, 390, and 360 CSS pixels for horizontal overflow. Motion is short and respects `prefers-reduced-motion`. The CV can use the browser's print flow; automatic PDF generation is not part of the local editor.

## Content and evidence

`content/site.json` remains the single semantic source. Do not invent personal facts, dates, results, endorsements, or credentials; separate project outcomes from individual contributions. Content is neutral professional Spanish. The local editor writes only to the canonical source after schema validation and build success; it binds to loopback and previews public allowlisted files only. Saving rebuilds local files and does not publish them.

## SEO and publishing

Production base URL: `https://harrysxavio.github.io/`. Each route has route-specific canonical and social metadata. Structured data and sitemap are generated from canonical content. `tools/build_site.py` creates the local allowlisted artifact; GitHub Pages publication still requires the repository's normal review and publishing flow.
