# Design system — Editorial Executive Profile

## Intent

Present Harrys Yusti as a business-minded mechanical engineer whose work connects projects, operational transformation, Supply Chain, productivity, and technology. The page should read like a polished professional profile: direct, human, evidence-led, and easy to scan. It is not a field guide, product dashboard, or conventional boxed résumé.

## Visual language

- **Canvas and ink:** warm paper (`#f4f0e7`), deep navy (`#172d45`), soft ink (`#4d5d69`), and a restrained signal red (`#a33d34`).
- **Typography:** Georgia/Times serif for display headings; Arial/Helvetica sans serif for reading and navigation; Courier New for small editorial labels. System fonts avoid external requests.
- **Structure:** fine rules, open ledger rows, calm whitespace, fluid type, and a centered reading measure. Impact figures are typographic highlights, not KPI cards.
- **Imagery:** no portrait or project-photo claims. The existing operations illustration is a social-preview asset, not a fabricated depiction of Harrys or a case study.

## Page sequence

1. Simple name and section navigation.
2. Text-first hero identifying Harrys, professional domains, and value proposition.
3. Compact professional snapshot and selected impact.
4. Chronological experience ledger and concise project rows.
5. Capabilities and grouped tools, with business outcomes before technology.
6. Brief About section, then clearly labeled AI exploration.
7. Direct contact invitation with supplied public profile links only.

## Responsive behavior and accessibility

Use CSS grid/flex reflow rather than a separate mobile page. Navigation may wrap, the snapshot and impact lists reduce columns, timeline/project rows stack, and skills become single-column reading rows. Preserve semantic landmarks, a single H1, descriptive links, visible keyboard focus, a skip link, sufficient contrast, and reduced-motion support. Avoid horizontal overflow at narrow widths.

## Content and evidence

Use only supplied profile facts, roles, dates, tools, education, languages, and project outcomes. Keep each result attached to its confirmed context. No invented current title, employer, client, testimonial, photo, contact detail, or additional metric. AI is applied exploration, not a claimed specialty.

## SEO and publishing

The account-root production URL is `https://harrysxavio.github.io/`. Keep one canonical URL and one set of Open Graph/Twitter tags, plus `ProfilePage` and `Person` JSON-LD that use the supplied LinkedIn and GitHub links. The root directory is the current Pages publishing source; the Python builder creates an allowlisted local `dist/` package and can also render a path-prefixed URL for local verification.
