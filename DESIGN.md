# Design system — Field Guide

## Concept

An editorial field guide for improving how work gets done: practical, observant and human. The selected concept is expressed as warm paper, navy ink, restrained signal-red annotations, pale-blue working notes, numbered section markers and fine ruled dividers. The operations illustration is the sole large visual asset and anchors the opening story: a complex network becoming more connected and legible. The page is a magazine-like reading experience rather than a product dashboard or a conventional résumé.

## Typography

- **Display and editorial headings:** Georgia with a Times New Roman serif fallback; regular weight, tight tracking and compact leading. Italic emphasis uses the signal-red accent.
- **Body and navigation:** Arial/Helvetica system sans, chosen for clarity and zero remote font dependencies.
- **Index, captions and small annotations:** Courier New system monospace with modest letter spacing.
- Hierarchy uses responsive `clamp()` sizes. Navigation, captions and controls are sized explicitly; no remote font load is required.

## Color

| Token | Value | Use |
| --- | --- | --- |
| Paper | `#f4f0e7` | Main page canvas |
| Deep paper | `#ece6da` | Selected-work band |
| Navy ink | `#172d45` | Primary text and contact band |
| Soft ink | `#4d5d69` | Supporting text |
| Signal red | `#a33d34` | Editorial emphasis, indexes and focus |
| Pale blue | `#d7e3e9` | Working-sequence band |
| Rule | `#b9b6ab` | Light separators |
| Dark rule | `#87909a` | Structural dividers |

The red accent is reserved for emphasis and is not used for long body copy. Pale blue is a surface, not a text color. Focus rings use signal red against the paper and blue surfaces.

## Spacing, grid and containers

- The centered page shell caps at `100rem`, with fluid side gutters from `1.15rem` on narrow screens.
- The reading grid pairs a roughly `10.5rem` editorial rail with a flexible content column; the content measure caps at `70rem`.
- Sections use generous fluid vertical spacing (`clamp`) and align to a shared content edge.
- Lists use open rows and hairline rules rather than repeated cards. The approach sequence is a deliberate pale-blue band; selected work uses a quiet paper band.
- The hero balances editorial copy with one large illustration. Its caption and margin note echo a printed figure reference.

## Borders, radius and depth

Rules are thin, mostly square and low-contrast; the page avoids card borders, drop shadows and nested panels. The only notable rounded treatment is the small circular field-note stamp. The art blends into paper with multiply compositing, without a color overlay or decorative frame.

## Motion and interaction

Navigation is native anchor navigation; no client-side JavaScript is needed. The page does not rely on animation. Smooth scrolling is enabled for anchor navigation and disabled under `prefers-reduced-motion`; focus-visible outlines and the skip link support keyboard use.

## Components and page rhythm

- **Header:** compact wordmark, name and essential section links.
- **Section rail:** numbered editorial contents navigation on wide screens; a compact numbered link strip on mobile.
- **Hero:** direct headline, short positioning statement, anchor action and supplied transformation illustration.
- **Discipline rows:** productivity and supply chain/operations are explicit core pillars; project transformation connects them, while data and technology remain enablers.
- **Approach sequence:** four steps presented as a numbered reading path.
- **Experience and tools:** open, ruled entries group tools by operational, data, automation and AI use rather than treating tools as the identity.
- **Exploration note:** one open question, not a list of invented current projects.
- **Selected work:** honest explanation that validated, shareable case studies will be added later.
- **Ideas and About:** concise editorial notes and a short introduction.
- **Contact:** LinkedIn and GitHub only, the supplied public profile destinations.

## Responsive philosophy

At desktop widths the contents rail and two-column hero create a magazine spread. From `851px` down to `621px`, the rail becomes a four-column contents index while the hero retains a compact two-column composition, preserving an editorial tablet layout. At `620px` and below, the rail becomes a deliberate two-column guide, the hero shifts to a clear text-first composition with the illustration on a pale-blue field, and the approach becomes a numbered vertical timeline. Pillar rows use a narrow index/title/description hierarchy; experience groups become ruled entries instead of cards. At `360px` and below, gutters and navigation spacing tighten explicitly. Content order remains consistent and the document avoids horizontal overflow.

## Requested design principles

- **Clarity before novelty:** direct language, restrained accents and one primary illustration.
- **Human-centered change:** people and real work come before technology.
- **Connected systems:** disciplines and sequence are shown as related, not isolated service cards.
- **Honest evidence:** no fabricated clients, case studies, outcomes, metrics, credentials, location or contact details.
- **Accessible by default:** semantic landmarks, one page-level heading, visible keyboard focus, descriptive image text, responsive reflow and reduced-motion support.
- **Minimal and durable:** static HTML/CSS, no framework, no external font dependency and no required JavaScript.

## SEO and domain configuration

The source page has a useful title, description, Open Graph profile metadata and `ProfilePage`/`Person` JSON-LD with only the supplied LinkedIn and GitHub `sameAs` URLs. No canonical URL or absolute social image URL is fabricated. `python tools/build_site.py --site-origin https://your-verified-domain.example` writes a deployable `dist/` with canonical and absolute Open Graph URLs, schema URLs, a one-page sitemap and a matching robots sitemap directive. Replace the example with the actual owner-confirmed HTTPS origin before deployment. Without that value, the local page remains valid and the sitemap contains no fabricated URL.
