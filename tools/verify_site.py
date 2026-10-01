#!/usr/bin/env python3
"""Verify routes, HTML semantics, local assets, SEO, sitemap, and dist allowlist."""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from build_site import DEFAULT_SITE_URL, PUBLIC_DIRECTORIES, PUBLIC_ROOT_FILES, ROOT, valid_site_url

REQUIRED_ROUTES = {
    "index.html", "404.html", "projects/index.html", "cv/index.html",
    "projects/inventory-reconciliation/index.html",
    "projects/brazil-chile-data-migration/index.html",
    "projects/patient-transport-optimization/index.html",
    "projects/picking-line-balancing/index.html",
}
EXPECTED_LINKS = {
    "https://www.linkedin.com/in/h-yusti/", "https://github.com/harrysxavio",
}
PROJECT_VISUALS = {
    "inventory-reconciliation-flow.svg": {"operación", "sistemas", "conciliar", "excepciones", "control"},
    "brazil-chile-data-flow.svg": {"brasil", "validación", "mapeo", "chile", "120.000"},
    "patient-transport-allocation.svg": {"demanda", "capacidad", "asignación", "rutas", "servicio", "pacientes"},
    "picking-workload-balance.svg": {"pedidos", "balanceo", "zona a", "zona b", "picking"},
}
CASE_VISUALS = {
    "projects/inventory-reconciliation/index.html": "inventory-reconciliation-flow.svg",
    "projects/brazil-chile-data-migration/index.html": "brazil-chile-data-flow.svg",
    "projects/patient-transport-optimization/index.html": "patient-transport-allocation.svg",
    "projects/picking-line-balancing/index.html": "picking-workload-balance.svg",
}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


class Parser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.errors: list[str] = []
        self.ids: list[str] = []
        self.links: list[str] = []
        self.resources: list[str] = []
        self.images: list[dict[str, str]] = []
        self.meta: list[dict[str, str]] = []
        self.canonical: list[str] = []
        self.title = ""
        self.in_title = False
        self.in_jsonld = False
        self.jsonld: list[str] = []
        self.headings: list[tuple[int, str]] = []
        self.current_heading: int | None = None
        self.lang = ""
        self.doctype = False
        self.text: list[str] = []

    def handle_decl(self, decl: str) -> None:
        self.doctype = decl.casefold() == "doctype html"

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.casefold(): value or "" for key, value in attrs}
        if tag == "html": self.lang = values.get("lang", "")
        if values.get("id"): self.ids.append(values["id"])
        if tag == "a" and values.get("href"): self.links.append(values["href"])
        if tag == "img": self.images.append(values)
        if tag in {"script", "source"} and values.get("src"): self.resources.append(values["src"])
        if tag == "source" and values.get("srcset"):
            self.resources.extend(candidate.split()[0] for candidate in values["srcset"].split(",") if candidate.split())
        if tag == "link":
            rel = values.get("rel", "").casefold().split()
            if "canonical" in rel: self.canonical.append(values.get("href", ""))
            if "stylesheet" in rel or "icon" in rel: self.resources.append(values.get("href", ""))
        if tag == "meta": self.meta.append(values)
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.headings.append((int(tag[1]), "")); self.current_heading = len(self.headings) - 1
        if tag == "title": self.in_title = True
        if tag == "script" and values.get("type") == "application/ld+json":
            self.in_jsonld = True; self.jsonld.append("")
        if tag not in VOID: self.stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title": self.in_title = False
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}: self.current_heading = None
        if tag == "script" and self.in_jsonld: self.in_jsonld = False
        if tag in VOID:
            self.errors.append(f"void element has closing tag: {tag}"); return
        if not self.stack:
            self.errors.append(f"unexpected closing tag: {tag}"); return
        opening = self.stack.pop()
        if opening != tag: self.errors.append(f"</{tag}> closes <{opening}>")

    def handle_data(self, data: str) -> None:
        self.text.append(data)
        if self.in_title: self.title += data
        if self.in_jsonld: self.jsonld[-1] += data
        if self.current_heading is not None:
            level, current = self.headings[self.current_heading]
            self.headings[self.current_heading] = (level, current + data.strip())

    def close(self) -> None:
        super().close()
        if self.stack: self.errors.append("unclosed tags: " + ", ".join(self.stack[-5:]))


def fail(message: str) -> None:
    print(f"FAIL: {message}"); sys.exit(1)


def require(ok: bool, message: str) -> None:
    if not ok: fail(message)


def pages_under(base: Path) -> list[Path]:
    return sorted([base / "index.html", base / "404.html", *[p for folder in PUBLIC_DIRECTORIES if (base / folder).exists() for p in (base / folder).rglob("*.html")]], key=lambda p: p.as_posix())


def parse_page(path: Path) -> tuple[str, Parser]:
    source = path.read_text(encoding="utf-8")
    parser = Parser(); parser.feed(source); parser.close()
    return source, parser


def route_for(page: Path, base: Path) -> str:
    relative = page.relative_to(base).as_posix()
    return "/" if relative == "index.html" else "/" + relative.removesuffix("index.html")


def check_page(page: Path, base: Path, site_url: str) -> None:
    source, p = parse_page(page)
    relative = page.relative_to(base).as_posix()
    require(p.doctype and not p.errors, f"{relative}: HTML structure: {p.errors}")
    require(p.lang == "es", f"{relative}: lang must be es")
    require(bool(p.title.strip()) and "Harrys Yusti" in p.title, f"{relative}: title missing or not professional")
    if relative == "index.html":
        home_title = "Harrys Yusti | Transformación, Proyectos y Supply Chain"
        og_title = next((m.get("content", "") for m in p.meta if m.get("property", "").casefold() == "og:title"), "")
        twitter_title = next((m.get("content", "") for m in p.meta if m.get("name", "").casefold() == "twitter:title"), "")
        require(p.title == og_title == twitter_title == home_title, "index.html: Home title, Open Graph title, and Twitter title must match the V4 SEO title")
    require(len([h for h in p.headings if h[0] == 1]) == 1, f"{relative}: expected exactly one h1")
    require(p.headings and p.headings[0][0] == 1, f"{relative}: heading sequence must start at h1")
    require(all(b[0] - a[0] <= 1 for a, b in zip(p.headings, p.headings[1:])), f"{relative}: heading level skipped")
    require(len(p.ids) == len(set(p.ids)), f"{relative}: duplicate id")
    ids = set(p.ids)
    for href in p.links:
        u = urlsplit(href)
        if href.startswith("#"): require(u.fragment in ids, f"{relative}: missing fragment {href}")
        elif u.scheme in {"", "http", "https"} and u.netloc in {"", urlsplit(site_url).netloc}:
            if u.path and u.path != "/":
                local = base / u.path.lstrip("/")
                if u.path.endswith("/"): local /= "index.html"
                require(local.is_file(), f"{relative}: local link does not resolve: {href}")
    externals = {h for h in p.links if urlsplit(h).scheme in {"http", "https"} and urlsplit(h).netloc != urlsplit(site_url).netloc}
    require(externals <= EXPECTED_LINKS, f"{relative}: unexpected external link {sorted(externals - EXPECTED_LINKS)}")
    for resource in p.resources:
        u = urlsplit(resource)
        if u.scheme or u.netloc: continue
        local = base / u.path.lstrip("/") if u.path.startswith("/") else page.parent / u.path
        require(local.is_file(), f"{relative}: local resource missing: {resource}")
    for image in p.images:
        require("alt" in image, f"{relative}: image missing alt")
        require(image.get("width", "").isdigit() and image.get("height", "").isdigit(), f"{relative}: image needs intrinsic width and height")
        src = urlsplit(image.get("src", ""))
        if not src.scheme and not src.netloc:
            local = base / unquote(src.path.lstrip("/")) if src.path.startswith("/") else page.parent / unquote(src.path)
            resolved_base = base.resolve()
            resolved_local = local.resolve()
            require(resolved_local.is_relative_to(resolved_base) and resolved_local.is_file(), f"{relative}: local image does not resolve: {image.get('src', '')}")
    require(len(p.canonical) == 1 and p.canonical[0] == site_url.rstrip("/") + route_for(page, base), f"{relative}: canonical must match route")
    description = next((m.get("content", "") for m in p.meta if m.get("name", "").casefold() == "description"), "")
    if relative != "404.html": require(bool(description.strip()), f"{relative}: missing meta description")
    if relative == "404.html":
        require(any(m.get("name", "").casefold() == "robots" and "noindex" in m.get("content", "") for m in p.meta), "404 must be noindex")
    else:
        names = {m.get("name", "").casefold() for m in p.meta}
        props = {m.get("property", "").casefold() for m in p.meta}
        require({"twitter:card", "twitter:title", "twitter:description", "twitter:image"} <= names, f"{relative}: Twitter metadata missing")
        require({"og:type", "og:title", "og:description", "og:locale", "og:url", "og:image"} <= props, f"{relative}: Open Graph metadata missing")
        require(not any("data-site-meta" in tag for tag in re.findall(r"<(?:meta|link)\b[^>]*>", source, re.I)), f"{relative}: unresolved site metadata markers")
        require(len(p.jsonld) == 1, f"{relative}: exactly one JSON-LD block required")
        try: schema = json.loads(p.jsonld[0])
        except json.JSONDecodeError as exc: fail(f"{relative}: JSON-LD invalid: {exc}")
        serialized = json.dumps(schema)
        require("Harrys Yusti" in serialized and "https://www.linkedin.com/in/h-yusti/" in serialized and "https://github.com/harrysxavio" in serialized, f"{relative}: structured data missing identity/sameAs")
        require(site_url in serialized, f"{relative}: structured data URL not absolute/site-specific")
    require("próximamente" not in source.casefold() and "coming soon" not in source.casefold(), f"{relative}: placeholder text remains")


def check_sitemap(base: Path, site_url: str) -> None:
    robots = base / "robots.txt"; sitemap = base / "sitemap.xml"
    require(robots.is_file() and sitemap.is_file(), "robots.txt or sitemap.xml missing")
    require(f"Sitemap: {site_url.rstrip('/')}/sitemap.xml" in robots.read_text(encoding="utf-8"), "robots.txt sitemap reference is incorrect")
    try: root = ET.parse(sitemap).getroot()
    except ET.ParseError as exc: fail(f"sitemap invalid XML: {exc}")
    locs = [node.text or "" for node in root.iter() if node.tag.endswith("loc")]
    expected = [site_url.rstrip("/") + route_for(page, base) for page in pages_under(base) if page.relative_to(base).as_posix() != "404.html"]
    require(root.tag.endswith("urlset") and set(locs) == set(expected) and len(locs) == len(expected), "sitemap must list each indexable route exactly once and exclude 404")


def check_project_visuals(base: Path) -> None:
    portfolio = (base / "projects" / "index.html").read_text(encoding="utf-8")
    content_path = ROOT / "content" / "site.json"
    try:
        content = json.loads(content_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"content/site.json: invalid project master data: {exc}")
    projects = content.get("projects", [])
    tags = {tag.get("id"): tag.get("label") for tag in content.get("taxonomy", {}).get("tags", [])}
    require(len(projects) >= 4, "content/site.json: the four existing case records are required")
    require(len(tags) == len(content.get("taxonomy", {}).get("tags", [])), "content/site.json: taxonomy IDs must be unique")
    require(sum(bool(project.get("featured")) for project in projects) == 4, "content/site.json: four featured case records are required")
    routed_projects = [project for project in projects if project.get("route")]
    routed_urls = [project["route"] for project in routed_projects]
    require(len(routed_projects) == 4 and len(set(routed_urls)) == 4,
            "content/site.json: exactly four project records must have unique case routes")
    require(sum(project.get("route") is None for project in projects) == len(projects) - 4,
            "content/site.json: all additional project records must remain secondary to the four routed cases")
    require(projects[0].get("id") == "inventory-reconciliation", "content/site.json: inventory must lead the featured projects")
    require(content["projectsPage"]["title"] in portfolio,
            "projects/index.html: the page heading must render the canonical editable title")
    top_four = re.search(r'<ul\b[^>]*class="project-grid project-grid--featured"', portfolio, flags=re.I)
    require(top_four is not None, "projects/index.html: a semantic featured-project grid is required")
    featured_section_end = portfolio.find("</section>", top_four.start())
    featured_markup = portfolio[top_four.start():featured_section_end] if featured_section_end > top_four.start() else ""
    featured_cards = re.findall(r'<li\b(?=[^>]*class="project-card project-card--(?:lead|featured)")',
                                featured_markup, flags=re.I)
    require(len(featured_cards) == 4, "projects/index.html: all four featured projects must form one grid")
    require(featured_markup.count('class="project-card__mark"') == 4,
            "projects/index.html: each featured project needs its own meaningful visual mark")
    for internal_phrase in ("El portafolio presenta", "no atribuir", "no hay cifra exacta",
                            "No hay atribución", "Sin métrica publicada"):
        require(internal_phrase.casefold() not in portfolio.casefold(),
                f"projects/index.html: remove internal editorial note {internal_phrase!r}")
    card_matches = re.findall(r'<li\b(?=[^>]*class="project-card\b)([^>]*)>(.*?)</article></li>', portfolio, flags=re.I | re.S)
    require(len(card_matches) == len(projects), "projects/index.html: every project record must render as a card")
    for project in projects:
        require(bool(project.get("tags")), f"content/site.json project {project.get('id')}: assign at least one taxonomy tag")
        require(set(project.get("tags", [])) <= set(tags), f"content/site.json project {project.get('id')}: unknown taxonomy tag")
        require(project.get("title", "") in portfolio, f"projects/index.html: project title missing from generated page: {project.get('id')}")
        card = next((attrs for attrs, _ in card_matches if f'data-project-id="{project["id"]}"' in attrs), None)
        require(card is not None, f"projects/index.html: missing card identity for {project['id']}")
        rendered_tags = re.search(r'data-project-tags="([^"]+)"', card or "")
        require(rendered_tags is not None and set(rendered_tags.group(1).split()) == set(project["tags"]),
                f"projects/index.html: taxonomy assignment differs for {project['id']}")
        for tag_id in project["tags"]:
            require(tags[tag_id] in next(body for attrs, body in card_matches if attrs == card),
                    f"projects/index.html: visible tag label missing for {project['id']} / {tag_id}")
    require("mejora cualitativa del proceso confirmada" not in portfolio.casefold(), "projects/index.html: remove internal confirmation language")
    expected_case_links = [project["route"] for project in projects if project.get("route")]
    _, parsed_portfolio = parse_page(base / "projects" / "index.html")
    require(set(expected_case_links) <= set(parsed_portfolio.links), "projects/index.html: each case record needs a working case link")
    require('id="control-tower"' in portfolio and 'id="transport-anomalies"' in portfolio,
            "projects/index.html: Control Tower and anomaly projects must remain distinct")
    require('data-project-filters hidden' in portfolio and 'for="project-search"' in portfolio
            and 'type="search"' in portfolio, "projects/index.html: labeled search controls must be hidden until enhanced")
    require('<fieldset class="project-filter-tags"><legend>Filtrar por temas</legend>' in portfolio
            and 'type="checkbox"' in portfolio, "projects/index.html: tag filters must use a native labeled fieldset")
    require('data-project-results role="status" aria-live="polite"' in portfolio
            and 'data-project-empty hidden' in portfolio, "projects/index.html: accessible result and empty states are required")
    require('type="reset"' in portfolio and 'data-project-clear' in portfolio,
            "projects/index.html: a native clear/reset action is required")
    js = (base / "script.js").read_text(encoding="utf-8")
    require("setupProjectFilters" in js and "selectedTags.size === 0 || [...selectedTags].some" in js,
            "script.js: text search and OR semantics across selected tags are required")
    require("textMatches && tagMatches" in js and "normalize(card.textContent).includes(query)" in js,
            "script.js: search must include card titles, copy, and visible tag labels, combined with filters")
    for relative, asset_name in CASE_VISUALS.items():
        page = base / relative
        _, parsed = parse_page(page)
        images = [image for image in parsed.images if asset_name in image.get("src", "")]
        require(len(images) == 1 and bool(images[0].get("alt", "").strip()), f"{relative}: expected its shared SVG asset and descriptive alt text")
        source, _ = parse_page(page)
        require(f'/assets/mobile/{asset_name}' in source, f"{relative}: expected its responsive mobile diagram")
    for asset_name, required_labels in PROJECT_VISUALS.items():
        asset = base / "assets" / asset_name
        try:
            svg = ET.parse(asset).getroot()
        except (ET.ParseError, OSError) as exc:
            fail(f"assets/{asset_name}: invalid or unavailable SVG: {exc}")
        ids = {node.attrib.get("id", ""): node for node in svg.iter() if node.attrib.get("id")}
        labelled = svg.attrib.get("aria-labelledby", "").split()
        require(svg.tag.endswith("svg") and svg.attrib.get("role") == "img", f"assets/{asset_name}: root must be an accessible image")
        require(len(labelled) == 2 and all(label in ids for label in labelled), f"assets/{asset_name}: title and description references are required")
        require(ids[labelled[0]].tag.endswith("title") and ids[labelled[1]].tag.endswith("desc"), f"assets/{asset_name}: accessible labels must reference title then description")
        labels = " ".join((node.text or "") for node in svg.iter()).casefold()
        require(all(label in labels for label in required_labels), f"assets/{asset_name}: expected workflow labels missing")
        mobile_name = base / "assets" / "mobile" / asset_name
        try:
            mobile_source = mobile_name.read_text(encoding="utf-8")
            mobile_svg = ET.fromstring(mobile_source)
        except (ET.ParseError, OSError) as exc:
            fail(f"assets/mobile/{asset_name}: invalid or unavailable mobile SVG: {exc}")
        mobile_ids = {node.attrib.get("id", ""): node for node in mobile_svg.iter() if node.attrib.get("id")}
        mobile_refs = mobile_svg.attrib.get("aria-labelledby", "").split()
        mobile_labels = " ".join((node.text or "") for node in mobile_svg.iter()).casefold()
        require(mobile_svg.tag.endswith("svg") and len(mobile_refs) == 2 and all(ref in mobile_ids for ref in mobile_refs), f"assets/mobile/{asset_name}: accessible title and description are required")
        require(all(label in mobile_labels for label in required_labels), f"assets/mobile/{asset_name}: expected workflow labels missing")
        font_sizes = [int(size) for size in re.findall(r"font-size:\s*(\d+)px", mobile_source)]
        require(font_sizes and min(font_sizes) >= 12, f"assets/mobile/{asset_name}: labels must remain at least 12px")


def check_output(base: Path, site_url: str) -> None:
    pages = pages_under(base)
    seen = {p.relative_to(base).as_posix() for p in pages if p.is_file()}
    require(REQUIRED_ROUTES <= seen, f"required routes missing: {sorted(REQUIRED_ROUTES - seen)}")
    for page in pages:
        if page.is_file(): check_page(page, base, site_url)
    check_sitemap(base, site_url)
    check_project_visuals(base)
    home = (base / "index.html").read_text(encoding="utf-8")
    stylesheet = (base / "styles.css").read_text(encoding="utf-8")
    controller = (base / "script.js").read_text(encoding="utf-8")
    require('data-signature' in home and len(re.findall(r'class="signature-step"', home)) == 5,
            "index.html: the semantic five-step signature contract is missing")
    require('class="selected-project"' in home and home.count('class="selected-project"') == 3,
            "index.html: three featured project cards must use their semantic component")
    require('class="career-timeline"' in home and 'class="career-milestone"' in home,
            "index.html: the connected career timeline component is missing")
    require('class="contact-section"' in home and 'class="site-footer simple-footer simple-footer--home"' in home,
            "index.html: contact and single source-driven footer components are required")
    require(home.count('<footer class="site-footer') == 1,
            "index.html: exactly one visible global footer is required")
    require('.signature-tabs [role="tab"]' in stylesheet and '.signature--tabs .signature-step > summary { display: none; }' in stylesheet
            and '.signature-tabs {' in stylesheet and 'display: none;' in stylesheet[stylesheet.index('.signature-tabs {'):stylesheet.index('.signature-tabs {') + 260]
            and '.signature--tabs .signature-tabs { display: grid; }' in stylesheet,
            "styles.css: responsive tab visibility and duplicate-summary suppression are required")
    require('min-height: 4rem' in stylesheet and 'ArrowRight' in controller and 'event.key === "End"' in controller,
            "signature tabs: minimum target size and keyboard navigation hooks are required")
    for route, required_classes in {
        "cv/index.html": ("cv-hero", "cv-section", "experience-entry", "cv-project-cta"),
        "projects/inventory-reconciliation/index.html": ("case-hero", "case-metrics", "case-flow", "case-navigation"),
    }.items():
        source = (base / route).read_text(encoding="utf-8")
        for class_name in required_classes:
            require(f'class="{class_name}' in source, f"{route}: semantic component .{class_name} is missing")
    require('src="/assets/harrys-yusti-portrait.webp"' in home and 'alt="Retrato de Harrys Yusti"' in home,
            "index.html: the supplied transparent portrait must be the accessible hero image")
    require("hero-eyebrow" not in home and len(re.findall(r"<h1\b", home, flags=re.I)) == 1,
            "index.html: remove the experience eyebrow and preserve a single home heading")
    require(len(re.findall(r"<h1\b", home, flags=re.I)) == 1, "index.html: Home must have exactly one h1")
    cv = (base / "cv" / "index.html").read_text(encoding="utf-8")
    cv_parser = Parser()
    cv_parser.feed(cv)
    cv_text = " ".join(cv_parser.text)
    source = json.loads((ROOT / "content" / "site.json").read_text(encoding="utf-8"))
    home_footer = source["home"]["footer"]
    require(all(value in home for value in (
        home_footer["name"], home_footer["tagline"],
        home_footer["backToTop"]["label"], home_footer["backToTop"]["href"],
    )), "index.html: footer name, tagline, and back-to-top link must render from home.footer")
    require(".page-main--home + .simple-footer" not in (ROOT / "styles.css").read_text(encoding="utf-8"),
            "styles.css: the global footer must remain visible on Home")
    def assert_semantic(value: object, location: str) -> None:
        forbidden = {"type", "blocks", "runs", "attrs", "level", "element", "contentGroup", "html", "fragment"}
        if isinstance(value, dict):
            for key, item in value.items():
                require(key not in forbidden, f"{location}.{key}: presentation/HTML AST fields are not authorable content")
                assert_semantic(item, f"{location}.{key}")
        elif isinstance(value, list):
            for index, item in enumerate(value):
                assert_semantic(item, f"{location}[{index}]")
        elif isinstance(value, str):
            require(re.search(r"<\/?[a-z][^>]*>", value, flags=re.I) is None,
                    f"{location}: content fields must be plain text, not HTML fragments")

    require(source.get("schemaVersion") == 3, "content/site.json: semantic schema version 3 is required")
    assert_semantic(source["home"], "home")
    assert_semantic(source["projectsPage"], "projectsPage")
    assert_semantic(source["notFound"], "notFound")
    for project in source["projects"]:
        if project.get("homeCard"):
            assert_semantic(project["homeCard"], f"project {project['id']}.homeCard")
        if project.get("caseDetails"):
            assert_semantic(project["caseDetails"], f"project {project['id']}.caseDetails")
    pdf_href = re.escape(source["profile"]["cvPdfUrl"])
    require(re.search(r'<a\b(?=[^>]*href="' + pdf_href + r'")(?=[^>]*\bdownload(?:[=\s]|>))[^>]*>', cv, flags=re.I) is not None,
            "cv/index.html: a real downloadable CV PDF is required")
    profile = source["profile"]
    cv_values = [source["site"]["name"], *[profile[field] for field in ("profession", "location", "positioning", "summary", "workflow")],
                 source["education"]["degree"], source["education"]["institution"], source["education"]["year"]]
    cv_values.extend(item[key] for item in source["languages"] for key in ("language", "level"))
    cv_values.extend(employer["employer"] for employer in source["career"])
    cv_values.extend(role[key] for employer in source["career"] for role in employer["roles"] for key in ("period", "title"))
    cv_values.extend(bullet for employer in source["career"] for role in employer["roles"] for bullet in role["bullets"])
    cv_values.extend(project["title"] for employer in source["career"] for role in employer["roles"] for project in role.get("projects", []))
    cv_values.extend(skill["area"] for skill in source["skills"])
    cv_values.extend(label for skill in source["skills"] for label in skill["skills"] + skill["tools"])
    cv_values.extend(skill["description"] for skill in source["skills"] if skill.get("description"))
    missing_cv_values = [value for value in cv_values if value not in cv_text]
    require(not missing_cv_values, f"cv/index.html: semantic CV source fields are not rendered: {missing_cv_values}")
    require("Áreas donde aporto valor" in cv and "Entender" in cv and "medir" in cv,
            "cv/index.html: value areas and workflow are required")
    home_parser = Parser()
    home_parser.feed(home)
    home_text = " ".join(home_parser.text)
    home_values = [source["home"]["hero"]["name"], source["home"]["hero"]["thesis"],
                   source["home"]["careerStory"]["introduction"],
                   source["home"]["careerStory"]["milestones"][0]["employer"],
                   source["home"]["careerStory"]["milestones"][0]["description"]]
    missing_home = [value for value in home_values if value not in home_text]
    require(not missing_home, f"index.html: semantic Home and career story fields are not rendered: {missing_home}")
    inventory = next(item for item in source["projects"] if item["id"] == "inventory-reconciliation")
    case_parser = Parser()
    case_parser.feed((base / "projects" / "inventory-reconciliation" / "index.html").read_text(encoding="utf-8"))
    case_text = " ".join(case_parser.text)
    case = inventory["caseDetails"]
    case_values = [case["hero"]["title"], case["role"]["body"], case["approach"]["decisions"][0], case["outcome"]["body"]]
    missing_case = [value for value in case_values if value not in case_text]
    require(not missing_case, f"inventory case: semantic hero/role/decision/outcome fields are not rendered: {missing_case}")
    for page in pages:
        if page.is_file() and page.name != "sitemap.xml":
            source = page.read_text(encoding="utf-8")
            require("harrys-site-theme" in source and 'src="/script.js"' in source,
                    f"{page.relative_to(base).as_posix()}: persistent global theme startup and controller are required")


def check_dist(site_url: str) -> None:
    dist = ROOT / "dist"
    if not dist.exists(): return
    source = {p.relative_to(ROOT).as_posix() for p in (ROOT / name for name in PUBLIC_ROOT_FILES) if p.is_file()}
    for folder in PUBLIC_DIRECTORIES:
        directory = ROOT / folder
        if directory.is_dir(): source.update(p.relative_to(ROOT).as_posix() for p in directory.rglob("*") if p.is_file() and p.suffix.lower() in {".html", ".svg", ".webp", ".avif", ".jpg", ".jpeg", ".png", ".pdf"})
    expected = source | {"sitemap.xml"}
    actual = {p.relative_to(dist).as_posix() for p in dist.rglob("*") if p.is_file()}
    require(actual == expected, f"dist output differs from public allowlist: {sorted(actual ^ expected)}")
    check_output(dist, site_url)


def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--site-url", type=valid_site_url, default=DEFAULT_SITE_URL)
    site_url = valid_site_url(cli.parse_args().site_url)
    check_output(ROOT, site_url)
    check_dist(site_url)
    print("PASS: all required routes, semantic HTML, headings, links, local resources, and image dimensions")
    print("PASS: canonical URLs, social metadata, structured data, robots.txt, sitemap, and public output allowlist")
    print("PASS: canonical project heading, four visual #TOP4 cards, clean public copy, and preserved detail diagrams")


if __name__ == "__main__": main()
