# Edit the site content

`site.json` is the single editable source for the profile, Home, Projects, CV, and all four case pages. The generated HTML is checked in for GitHub Pages, but edits belong in this JSON file.

## Quick edit and rebuild

1. Open `content/site.json` in a JSON-aware editor.
2. Edit facts in their named fields: `profile`, `home`, `projects[]`, `career[]`, `education`, `skills[]`, `languages[]`, or `casePages`.
3. Edit visible page copy in the named domain fields for Home, project, career, profile, education, skills, and languages. The CV's `cvPage` array contains only its route breadcrumb; the builder lays out CV facts from `profile`, `career[]`, `skills[]`, `education`, and `languages[]` so those facts are not duplicated in page-copy blocks.
4. Edit page metadata under `pages[].seo`: `title`, `description`, `meta`, and `jsonLd`.
5. Run `python tools/build_site.py`, then `python tools/verify_site.py`.

The Python standard-library builder regenerates the existing root routes and `dist/`. No server, framework, or dependency install is needed. Keep each project tag ID stable; change its `label` when the visible vocabulary needs revision.

## Schema version 2

| Field | Required shape | Purpose |
|---|---|---|
| `schemaVersion` | `2` | Rejects unsupported source versions. |
| `site` | `name`, `siteUrl`, `language`, `sameAs[]` | Shared identity, canonical URL, language, and profile links. |
| `profile` | `profession`, `location`, `positioning`, `summary`, `workflow`, `cvPdfUrl` | Profile facts and copy rendered on CV; PDF URL drives its download action. |
| `taxonomy` | `version: 1`, `tags[]` | Stable `{id, label}` tag vocabulary. |
| `projects[]` | Exactly nine records | `{id, title, summary, route, featured, situation, task, contribution, result, evidence, tags[]}`. Use `null` for teaser-only `route`. |
| `career[]` | Employer, period, optional summary, roles with period/title/bullets/optional project links | Confirmed employment copy and evidence; dates stay at year precision. |
| `education`, `skills[]`, `languages[]` | Structured arrays/objects; skills have area, skill labels, tools, and optional description | Education, capabilities/tools, and language levels rendered by the CV template. |
| `home`, `projectPortfolio`, `cvPage`, `notFound` | Semantic content-block arrays; `cvPage` is breadcrumb-only | Page copy and sections for existing routes; CV facts are deliberately not repeated here. |
| `casePages` | Object keyed by project ID | Semantic content blocks for the four stable case routes. |
| `pages[]` | Exactly eight records | Stable page `{id, route, seo}` mappings. SEO title/description/social tags/JSON-LD are editable here. |
| `editorialRules[]` | String array | Accuracy and copy guardrails to keep with the source. |

Blocks have a `type` and plain text fields/runs. The builder owns the HTML elements, escaping, route mapping, shared navigation, and page shell. Validation errors identify the page, project ID, career employer/role, or field; fix the data shape instead of editing generated HTML.

## CV PDF

The downloadable PDF remains a static asset. After changing CV data, rebuild and use the CV page's print action to produce a refreshed PDF; a deterministic PDF generator is not configured.
