# Edit the site content

`content/site.json` is the single editable source for the profile, Home, Projects, CV, and all four case pages. Edit the named facts and copy fields in that file; do not edit generated route HTML directly.

## Edit and rebuild

1. Open `content/site.json` in a JSON-aware editor and keep valid JSON syntax (double quotes, commas between fields, no trailing comma).
2. Edit Home under `home.hero`, `home.signature.stages[]`, `home.selectedWork`, `home.careerStory`, `home.contact`, and `home.footer`. Selected project cards use `homeCard` fields on the corresponding `projects[]` records; `selectedWork.projectIds` controls which records appear.
3. Edit project facts and taxonomy under `projects[]` and `taxonomy.tags[]`. Keep tag IDs stable slugs; assign one or more existing IDs in each project's `tags` array. The four routed projects also have `caseDetails` fields for their hero, metrics, diagram, context, problem, role, approach decisions, outcome, and navigation labels. Teaser-only projects do not have case details.
4. Edit the Projects introduction in `projectsPage`, the 404 page in `notFound`, and CV facts in `profile`, `career[]`, `education`, `skills[]`, and `languages[]`. Career-story copy on Home is separate from the factual CV employment entries so each page can be edited in its own context.
5. Edit titles, descriptions, social metadata, and structured data under the matching `pages[].seo` record. Keep the eight existing page IDs and routes unchanged.
6. From the repository root, run `python tools/build_site.py` to generate the checked-in root routes and `dist/`, then run `python tools/verify_site.py`.

The builder uses only the Python standard library. It owns page structure, layout, HTML escaping, route mapping, shared navigation, SEO output, and the page shell; the JSON contains plain text, URLs, image data, and domain-specific arrays rather than HTML fragments or HTML element trees. Validation errors name the page, project ID, or field that needs correction.

## Schema version 3

| Field | Required shape | Purpose |
|---|---|---|
| `schemaVersion` | `3` | Rejects unsupported source versions. |
| `site` | `name`, `siteUrl`, `language`, `sameAs[]` | Shared identity, canonical URL, language, and profile links. |
| `profile` | `profession`, `location`, `positioning`, `summary`, `workflow`, `cvPdfUrl` | Profile facts and CV introduction. |
| `taxonomy` | `version: 1`, `tags[]` | Stable `{id, label}` taxonomy vocabulary. |
| `projects[]` | Exactly nine records | Project facts, tags, route, and featured status. Three Home cards also have `homeCard` copy; the four routed records have semantic `caseDetails`. |
| `home` | Named objects: `hero`, `signature`, `selectedWork`, `careerStory`, `contact`, `footer` | Home copy, image data, signature stages, selected project IDs, narrative milestones, human notes, and contact links. |
| `projectsPage`, `notFound` | Named objects containing plain text and link data | Projects introduction and 404-page copy. |
| `career[]` | Employer, period, optional summary, roles with period/title/bullets/optional project links | Confirmed employment copy and evidence; dates stay at year precision. |
| `education`, `skills[]`, `languages[]` | Structured object/arrays | Education, capabilities/tools, and language levels rendered by the CV template. |
| `pages[]` | Exactly eight `{id, route, seo}` records | Existing route inventory and per-page SEO title, description, social tags, and JSON-LD. |
| `editorialRules[]` | String array | Accuracy and copy guardrails for future edits. |

The generator validates required semantic fields and relationships, including Home-selected project IDs, project tag IDs, and the four stable case routes. Keep profile facts and claims accurate; do not add unverified dates, metrics, roles, technologies, or baselines.

## CV PDF

The downloadable PDF remains a static asset. After changing CV data, rebuild the site and use the CV page's print action to produce a refreshed PDF; a deterministic PDF generator is not configured.
