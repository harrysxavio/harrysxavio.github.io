#!/usr/bin/env python3
"""Build the allowlisted static profile into dist."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import stat
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
DEFAULT_SITE_URL = "https://harrysxavio.github.io"
PUBLIC_ROOT_FILES = ("index.html", "404.html", "styles.css", "script.js", "favicon.svg", "robots.txt")
PUBLIC_DIRECTORIES = ("assets", "projects", "cv")
CONTENT_FILE = ROOT / "content" / "site.json"
PROJECT_MARKS = {
    "inventory-reconciliation": '<svg viewBox="0 0 64 64"><path d="m12 22 20-11 20 11v22L32 55 12 44V22Z"/><path d="m12 22 20 11 20-11M32 33v22M22 17l20 11"/></svg>',
    "brazil-chile-data-migration": '<svg viewBox="0 0 64 64"><circle cx="14" cy="32" r="6"/><circle cx="50" cy="17" r="6"/><circle cx="50" cy="47" r="6"/><path d="M20 32h11c8 0 8-15 16-15M31 32c8 0 8 15 16 15"/></svg>',
    "patient-transport-optimization": '<svg viewBox="0 0 64 64"><path d="M8 22h31v24H8zM39 30h10l8 9v7H39zM44 30v9h13"/><circle cx="19" cy="48" r="4"/><circle cx="48" cy="48" r="4"/><path d="M22 30h12M28 24v12"/></svg>',
    "picking-line-balancing": '<svg viewBox="0 0 64 64"><path d="M10 18h44M10 32h44M10 46h44"/><circle cx="19" cy="18" r="4"/><circle cx="43" cy="32" r="4"/><circle cx="29" cy="46" r="4"/><path d="M23 18h10M39 32H25M33 46h9"/></svg>',
}
REQUIRED_GENERATED_ROUTES = {
    "index.html", "404.html", "projects/index.html", "cv/index.html",
    "projects/inventory-reconciliation/index.html",
    "projects/brazil-chile-data-migration/index.html",
    "projects/patient-transport-optimization/index.html",
    "projects/picking-line-balancing/index.html",
}


def valid_site_url(value: str) -> str:
    parsed = urlsplit(value)
    host = parsed.hostname or ""
    path = parsed.path.rstrip("/")
    if (parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password
            or parsed.query or parsed.fragment or "?" in value or "#" in value
            or any(part in {".", ".."} for part in path.split("/") if part)):
        raise argparse.ArgumentTypeError("site URL must be HTTPS without credentials, query, or fragment")
    return f"https://{parsed.netloc.lower()}{path}"


def validate_link_url(value: object, location: str) -> None:
    """Allow only same-site paths/anchors or HTTPS links in rendered URL fields."""
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError(f"{location} must be a non-empty safe URL")
    if any(unicodedata.category(char) == "Cc" or char.isspace() for char in value) or "\\" in value:
        raise ValueError(f"{location} contains unsafe whitespace or control characters")
    if value.startswith("//"):
        raise ValueError(f"{location} must not be protocol-relative")
    try:
        parsed = urlsplit(value)
    except ValueError as exc:
        raise ValueError(f"{location} is not a valid URL") from exc
    if parsed.scheme:
        if (parsed.scheme.lower() != "https" or not parsed.netloc or parsed.username or parsed.password
                or not parsed.hostname):
            raise ValueError(f"{location} must use HTTPS without credentials")
        return
    if parsed.netloc or parsed.query or value.startswith("?"):
        raise ValueError(f"{location} must be a same-site path or anchor")
    if value.startswith("#"):
        if not parsed.fragment:
            raise ValueError(f"{location} must contain a non-empty anchor")
        return
    if not value.startswith("/") or parsed.path.startswith("//"):
        raise ValueError(f"{location} must be a same-site slash path, anchor, or HTTPS URL")
    decoded_parts = [part for part in unquote(parsed.path).split("/") if part]
    if any(part in {".", ".."} for part in decoded_parts):
        raise ValueError(f"{location} must not contain traversal segments")


def _validate_rendered_urls(data: dict[str, object]) -> None:
    url_keys = {"href", "src", "mobileSrc", "url", "@id", "sameAs", "siteUrl", "cvPdfUrl"}

    def visit(value: object, path: str = "content/site.json") -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                item_path = f"{path}.{key}"
                if key in url_keys:
                    if isinstance(item, list):
                        for index, entry in enumerate(item):
                            validate_link_url(entry, f"{item_path}[{index}]")
                    elif key == "siteUrl":
                        validate_link_url(item, item_path)
                        try:
                            valid_site_url(item)
                        except (argparse.ArgumentTypeError, TypeError) as exc:
                            raise ValueError(f"{item_path} must be a valid HTTPS site URL") from exc
                    else:
                        validate_link_url(item, item_path)
                elif key == "content" and isinstance(item, str):
                    # Open Graph/Twitter URL metadata is emitted as a content attribute.
                    parent_key = str(value.get("property", value.get("name", ""))).lower()
                    if parent_key in {"og:url", "og:image", "twitter:image", "twitter:player", "twitter:player:stream"}:
                        validate_link_url(item, item_path)
                    else:
                        visit(item, item_path)
                else:
                    visit(item, item_path)
        elif isinstance(value, list):
            for index, item in enumerate(value):
                visit(item, f"{path}[{index}]")

    visit(data)


def _remove_readonly(function: object, path: str, error: object) -> None:
    os.chmod(path, stat.S_IREAD | stat.S_IWRITE)
    function(path)  # type: ignore[operator]


def _public_files() -> list[Path]:
    files = [ROOT / name for name in PUBLIC_ROOT_FILES if (ROOT / name).is_file()]
    for directory in PUBLIC_DIRECTORIES:
        base = ROOT / directory
        if base.is_dir():
            files.extend(path for path in base.rglob("*") if path.is_file() and path.suffix.lower() in {".html", ".svg", ".webp", ".avif", ".jpg", ".jpeg", ".png", ".pdf"})
    return sorted(set(files), key=lambda path: path.relative_to(ROOT).as_posix())


def _write_sitemap(site_url: str, html_files: list[Path]) -> None:
    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    root = ET.Element("urlset", xmlns=namespace)
    for source in html_files:
        relative = source.relative_to(ROOT).as_posix()
        if relative == "404.html":
            continue
        route = "/" if relative == "index.html" else "/" + relative.removesuffix("index.html")
        ET.SubElement(ET.SubElement(root, "url"), "loc").text = f"{site_url}{route}"
    ET.ElementTree(root).write(DIST / "sitemap.xml", encoding="utf-8", xml_declaration=True)


def _load_content() -> dict[str, object]:
    try:
        data = json.loads(CONTENT_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"content/site.json: cannot read valid JSON: {exc}") from exc
    if not isinstance(data, dict) or data.get("schemaVersion") != 3:
        raise ValueError("content/site.json: schemaVersion must be 3")
    if not isinstance(data.get("site"), dict) or not isinstance(data["site"].get("siteUrl"), str):
        raise ValueError("content/site.json: site.siteUrl is required")
    for field in ("name", "language"):
        if not isinstance(data["site"].get(field), str) or not data["site"][field].strip():
            raise ValueError(f"content/site.json: site.{field} is required")
    if not isinstance(data["site"].get("sameAs"), list) or not all(isinstance(url, str) for url in data["site"]["sameAs"]):
        raise ValueError("content/site.json: site.sameAs must be an array of profile URLs")
    if not isinstance(data.get("profile"), dict) or not all(data["profile"].get(key) for key in ("profession", "location", "positioning", "summary", "cvPdfUrl", "workflow")):
        raise ValueError("content/site.json: profile.profession, location, positioning, summary, cvPdfUrl, and workflow are required")
    taxonomy = data.get("taxonomy")
    if not isinstance(taxonomy, dict) or taxonomy.get("version") != 1 or not isinstance(taxonomy.get("tags"), list):
        raise ValueError("content/site.json: taxonomy.version 1 and taxonomy.tags array are required")
    tag_ids: set[str] = set()
    for index, tag in enumerate(taxonomy["tags"]):
        field = f"content/site.json: taxonomy.tags[{index}]"
        if not isinstance(tag, dict) or not isinstance(tag.get("id"), str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", tag["id"]):
            raise ValueError(f"{field}.id must be a stable lowercase slug")
        if tag["id"] in tag_ids:
            raise ValueError(f"{field}.id is duplicated: {tag['id']}")
        if not isinstance(tag.get("label"), str) or not tag["label"].strip():
            raise ValueError(f"{field}.label is required")
        tag_ids.add(tag["id"])
    projects = data.get("projects")
    if not isinstance(projects, list) or len(projects) != 9:
        raise ValueError("content/site.json: projects must contain exactly nine records")
    project_ids: set[str] = set()
    for index, project in enumerate(projects):
        if not isinstance(project, dict) or not isinstance(project.get("id"), str):
            raise ValueError(f"content/site.json: projects[{index}].id is required")
        field = f"content/site.json: project {project['id']}"
        if project["id"] in project_ids:
            raise ValueError(f"{field}.id is duplicated")
        project_ids.add(project["id"])
        for required in ("title", "summary", "situation", "task", "contribution", "result", "evidence"):
            if not isinstance(project.get(required), str) or not project[required].strip():
                raise ValueError(f"{field}.{required} is required")
        assigned = project.get("tags")
        if not isinstance(assigned, list) or not assigned or not all(isinstance(tag_id, str) for tag_id in assigned):
            raise ValueError(f"{field}.tags must be a non-empty array of unique tag IDs")
        if len(assigned) != len(set(assigned)):
            raise ValueError(f"{field}.tags must be a non-empty array of unique tag IDs")
        unknown = sorted(set(assigned) - tag_ids)
        if unknown:
            raise ValueError(f"{field}.tags references unknown taxonomy IDs: {unknown}")
        if project.get("route") is not None and not isinstance(project["route"], str):
            raise ValueError(f"{field}.route must be a route string or null")
        if not isinstance(project.get("featured"), bool):
            raise ValueError(f"{field}.featured must be a boolean")
        if project.get("homeCard") is not None:
            card = project["homeCard"]
            if not isinstance(card, dict) or not all(isinstance(card.get(key), str) and card[key].strip() for key in ("title", "situation", "task", "contribution", "result")):
                raise ValueError(f"{field}.homeCard requires title, situation, task, contribution, and result prose")
        if project.get("route"):
            _validate_case_details(project.get("caseDetails"), f"{field}.caseDetails")
    project_routes = {project["route"] for project in projects if project.get("route")}
    expected_project_routes = {
        "/projects/inventory-reconciliation/", "/projects/brazil-chile-data-migration/",
        "/projects/patient-transport-optimization/", "/projects/picking-line-balancing/",
    }
    if project_routes != expected_project_routes:
        raise ValueError("content/site.json: project route assignments must preserve the four existing case routes")
    featured_projects = [project for project in projects if project["featured"]]
    if len(featured_projects) != 4:
        raise ValueError("content/site.json: exactly four projects must remain featured")
    if featured_projects[0]["id"] != "inventory-reconciliation":
        raise ValueError("content/site.json: inventory reconciliation must lead the featured projects")
    if not isinstance(data.get("career"), list) or not data["career"]:
        raise ValueError("content/site.json: career must be a non-empty array")
    for index, employer in enumerate(data["career"]):
        field = f"content/site.json: career[{index}]"
        if not isinstance(employer, dict) or not isinstance(employer.get("employer"), str) or not employer["employer"].strip():
            raise ValueError(f"{field}.employer is required")
        if not isinstance(employer.get("period"), str) or not isinstance(employer.get("roles"), list) or not employer["roles"]:
            raise ValueError(f"{field}.period and roles are required")
        for role_index, role in enumerate(employer["roles"]):
            role_field = f"{field} ({employer['employer']}).roles[{role_index}]"
            if not isinstance(role, dict) or not all(isinstance(role.get(key), str) and role[key].strip() for key in ("period", "title")):
                raise ValueError(f"{role_field}.period and title are required")
            if not isinstance(role.get("bullets"), list) or not role["bullets"] or not all(isinstance(item, str) and item.strip() for item in role["bullets"]):
                raise ValueError(f"{role_field}.bullets must be a non-empty array of prose")
            projects_for_role = role.get("projects", [])
            if not isinstance(projects_for_role, list) or any(not isinstance(item, dict) or not item.get("title") or not item.get("href") for item in projects_for_role):
                raise ValueError(f"{role_field}.projects must be an array of title/href links")
    if not isinstance(data.get("skills"), list) or not data["skills"]:
        raise ValueError("content/site.json: skills must be a non-empty array")
    for index, skill in enumerate(data["skills"]):
        field = f"content/site.json: skills[{index}]"
        if not isinstance(skill, dict) or not isinstance(skill.get("area"), str) or not skill["area"].strip():
            raise ValueError(f"{field}.area is required")
        if not isinstance(skill.get("skills"), list) or not skill["skills"] or not all(isinstance(item, str) and item.strip() for item in skill["skills"]):
            raise ValueError(f"{field}.skills must be a non-empty array of labels")
        if not isinstance(skill.get("tools"), list) or not all(isinstance(item, str) and item.strip() for item in skill["tools"]):
            raise ValueError(f"{field}.tools must be an array of labels")
    if not isinstance(data.get("education"), dict) or not all(data["education"].get(key) for key in ("degree", "institution", "year")):
        raise ValueError("content/site.json: education.degree, institution, and year are required")
    if not isinstance(data.get("languages"), list) or not data["languages"] or any(not isinstance(item, dict) or not item.get("language") or not item.get("level") for item in data["languages"]):
        raise ValueError("content/site.json: languages[] requires language and level")
    _validate_home(data.get("home"), project_ids)
    for name in ("projectsPage", "notFound"):
        if not isinstance(data.get(name), dict):
            raise ValueError(f"content/site.json: {name} must be an object of named page copy fields")
    _validate_semantic_object(data["projectsPage"], "content/site.json: projectsPage", ("title", "introduction", "context"))
    _validate_semantic_object(data["notFound"], "content/site.json: notFound", ("eyebrow", "title", "description"))
    for index, link in enumerate(data["notFound"].get("actions", [])):
        _validate_semantic_object(link, f"content/site.json: notFound.actions[{index}]", ("label", "href"))
    if not isinstance(data.get("editorialRules"), list) or not data["editorialRules"]:
        raise ValueError("content/site.json: editorialRules must preserve content-authoring guardrails")
    pages = data.get("pages")
    if not isinstance(pages, list) or not pages:
        raise ValueError("content/site.json: pages must be a non-empty array")
    routes: list[str] = []
    page_ids: set[str] = set()
    for index, page in enumerate(pages):
        field = f"content/site.json: pages[{index}]"
        if not isinstance(page, dict) or not isinstance(page.get("id"), str) or not isinstance(page.get("route"), str):
            raise ValueError(f"{field}.id and {field}.route are required")
        field = f"content/site.json: page {page['id']}"
        if page["id"] in page_ids:
            raise ValueError(f"{field}.id is duplicated")
        page_ids.add(page["id"])
        route = page["route"]
        candidate = Path(route)
        if candidate.is_absolute() or ".." in candidate.parts or not route.endswith(".html"):
            raise ValueError(f"{field}.route: expected a safe repository-relative HTML route, got {route!r}")
        if route in routes:
            raise ValueError(f"{field}.route: duplicate route {route!r}")
        routes.append(route)
        if not isinstance(page.get("seo"), dict):
            raise ValueError(f"{field}.seo is required")
        if page["id"] not in {"home", "notFound", "projectPortfolio", "cvPage"}:
            target = "/projects/" + page["route"].removeprefix("projects/").removesuffix("/index.html") + "/"
            if not any(project.get("route") == target for project in projects):
                raise ValueError(f"content/site.json: page {page['id']} does not map to a project record")
        seo = page.get("seo")
        if not isinstance(seo, dict) or not isinstance(seo.get("title"), str) or not seo["title"].strip():
            raise ValueError(f"{field}.seo.title is required")
        if not isinstance(seo.get("description"), str) or not seo["description"].strip():
            raise ValueError(f"{field}.seo.description is required")
        if not isinstance(seo.get("meta"), list) or not isinstance(seo.get("jsonLd"), (dict, type(None))):
            raise ValueError(f"{field}.seo requires meta array and jsonLd object or null")
        for meta_index, meta in enumerate(seo["meta"]):
            if not isinstance(meta, dict) or not isinstance(meta.get("content"), str):
                raise ValueError(f"{field}.seo.meta[{meta_index}].content is required")
            if not (isinstance(meta.get("name"), str) or isinstance(meta.get("property"), str)):
                raise ValueError(f"{field}.seo.meta[{meta_index}] requires name or property")
    if set(routes) != REQUIRED_GENERATED_ROUTES:
        missing = sorted(REQUIRED_GENERATED_ROUTES - set(routes))
        extra = sorted(set(routes) - REQUIRED_GENERATED_ROUTES)
        raise ValueError(f"content/site.json: route inventory mismatch; missing={missing}, extra={extra}")
    _validate_rendered_urls(data)
    return data


def _validate_semantic_object(value: object, field: str, required: tuple[str, ...]) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be an object")
    for key in required:
        if not isinstance(value.get(key), str) or not value[key].strip():
            raise ValueError(f"{field}.{key} is required")
    return value


def _validate_case_details(value: object, field: str) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be a semantic object, not presentation blocks")
    for key in ("hero", "context", "problem", "role", "approach", "outcome", "diagram", "navigation"):
        if not isinstance(value.get(key), dict):
            raise ValueError(f"{field}.{key} must be a named semantic object")
    for key in ("context", "problem", "role", "outcome"):
        _validate_semantic_object(value[key], f"{field}.{key}", ("kicker", "heading", "body"))
    _validate_semantic_object(value["hero"], f"{field}.hero", ("eyebrow", "title", "summary"))
    _validate_semantic_object(value["approach"], f"{field}.approach", ("heading",))
    if not isinstance(value["approach"].get("decisions"), list) or not value["approach"]["decisions"]:
        raise ValueError(f"{field}.approach.decisions must be a non-empty array of prose")
    if not isinstance(value["approach"].get("kicker"), str) or not value["approach"]["kicker"].strip():
        raise ValueError(f"{field}.approach.kicker is required")
    if not isinstance(value.get("metrics"), list) or not value["metrics"]:
        raise ValueError(f"{field}.metrics must be an array of value/label facts")
    if not isinstance(value["diagram"].get("steps"), list) or not isinstance(value["navigation"].get("breadcrumbTitle"), str):
        raise ValueError(f"{field}.diagram.steps and navigation.breadcrumbTitle are required")


def _validate_home(value: object, project_ids: set[str]) -> None:
    if not isinstance(value, dict):
        raise ValueError("content/site.json: home must be a named object")
    for section in ("hero", "signature", "selectedWork", "careerStory", "contact", "footer"):
        if not isinstance(value.get(section), dict):
            raise ValueError(f"content/site.json: home.{section} must be a named object")
    _validate_semantic_object(value["hero"], "content/site.json: home.hero", ("name", "thesis", "introduction", "positioning"))
    _validate_semantic_object(value["signature"], "content/site.json: home.signature", ("kicker", "title", "introduction"))
    signature_stages = value["signature"].get("stages")
    if not isinstance(signature_stages, list) or not signature_stages:
        raise ValueError("content/site.json: home.signature.stages must be a non-empty array")
    for index, stage in enumerate(signature_stages):
        field = f"content/site.json: home.signature.stages[{index}]"
        _validate_semantic_object(stage, field, ("id", "number", "title", "description", "evidenceLabel", "evidence"))
    selected = value["selectedWork"]
    _validate_semantic_object(selected, "content/site.json: home.selectedWork", ("kicker", "title"))
    if not isinstance(selected.get("projectIds"), list) or not set(selected["projectIds"]).issubset(project_ids):
        raise ValueError("content/site.json: home.selectedWork.projectIds must reference known project IDs")
    story = value["careerStory"]
    _validate_semantic_object(story, "content/site.json: home.careerStory", ("heading", "introduction"))
    if not isinstance(story.get("milestones"), list) or not story["milestones"] or not isinstance(story.get("notes"), list):
        raise ValueError("content/site.json: home.careerStory.milestones and notes must be arrays")
    for index, milestone in enumerate(story["milestones"]):
        _validate_semantic_object(milestone, f"content/site.json: home.careerStory.milestones[{index}]", ("phase", "employer", "description"))
    for index, note in enumerate(story["notes"]):
        _validate_semantic_object(note, f"content/site.json: home.careerStory.notes[{index}]", ("title", "body"))


def _copy(value: str) -> str:
    return html.escape(str(value), quote=False)


def _attr(value: str) -> str:
    return html.escape(str(value), quote=True)


def _copy_p(value: str, class_name: str = "content-copy") -> str:
    return f'<p class="{_attr(class_name)}">{_copy(value)}</p>'


def _heading(value: str, level: int, anchor: str | None = None) -> str:
    ident = f' id="{_attr(anchor)}"' if anchor else ""
    return f'<h{level}{ident} class="content-heading content-heading--{level}">{_copy(value)}</h{level}>'


def _semantic_link(link: dict[str, str], class_name: str = "content-link") -> str:
    return f'<a class="{_attr(class_name)}" href="{_attr(link["href"])}">{_copy(link["label"])}</a>'


def _semantic_image(image: dict[str, object] | None) -> str:
    if not image:
        return ""
    src = _attr(image["src"])
    alt = _attr(image.get("alt", ""))
    dimensions = "".join(f' {key}="{_attr(image[key])}"' for key in ("width", "height") if image.get(key))
    img = f'<img src="{src}" alt="{alt}"{dimensions}>'
    mobile = image.get("mobileSrc")
    return f'<picture><source srcset="{_attr(mobile)}" media="(max-width: 42rem)">{img}</picture>' if mobile else img


def _semantic_section(content: str, anchor: str | None = None, labelled_by: str | None = None) -> str:
    attrs = f' id="{_attr(anchor)}"' if anchor else ""
    attrs += f' aria-labelledby="{_attr(labelled_by)}"' if labelled_by else ""
    return f'<section{attrs} class="content-block content-block--contentSection">{content}</section>'


def _render_home(data: dict[str, object]) -> str:
    home = data["home"]
    hero = home["hero"]
    hero_copy = _copy_p(hero["thesis"]) + _copy_p(hero["introduction"]) + _copy_p(hero["positioning"])
    hero_actions = "".join(_semantic_link(link, "button" if index == 0 else "text-link text-link--secondary") for index, link in enumerate(hero["actions"]))
    hero_main = f'<div class="hero-copy"><h1 id="hero-title">{_copy(hero["name"])}</h1><p class="hero-thesis">{_copy(hero["thesis"])}</p>{_copy_p(hero["introduction"], "hero-introduction")}{_copy_p(hero["positioning"], "hero-positioning")}<div class="hero-actions">{hero_actions}</div></div>'
    hero_markup = f'<section class="hero" aria-labelledby="hero-title"><div class="hero-art"><div class="hero-art__shape"></div><figure class="hero-portrait">{_semantic_image(hero["image"])}</figure><span class="hero-art__spark" aria-hidden="true">✳</span></div>{hero_main}</section>'

    signature = home["signature"]
    stage_markup = "".join(
        f'<details id="{_attr(stage["id"])}" class="signature-step"{" open" if index == 0 else ""}>'
        f'<summary><span class="signature-step__number">{_copy(stage["number"])}</span><span class="signature-step__title">{_copy(stage["title"])}</span></summary>'
        f'<div class="signature-step__content"><p>{_copy(stage["description"])}</p><p class="signature-evidence"><strong>{_copy(stage["evidenceLabel"])}</strong> {_copy(stage["evidence"])}</p></div>'
        f'</details>' for index, stage in enumerate(signature["stages"])
    )
    route_nodes = "".join(f'<span class="signature-route__node" data-node="{index}" aria-hidden="true"></span>{"<span class=\"signature-route__connection\" data-connection=\"" + str(index) + "\" aria-hidden=\"true\"></span>" if index < len(signature["stages"]) - 1 else ""}' for index, _ in enumerate(signature["stages"]))
    signature_body = f'<div class="signature-layout"><div class="section-heading"><p class="section-kicker">{_copy(signature["kicker"])}</p><h2 id="signature-title">{_copy(signature["title"])}</h2><p>{_copy(signature["introduction"])}</p></div><div class="signature-steps"><div class="signature-route" data-active-index="0" aria-hidden="true">{route_nodes}</div>{stage_markup}</div></div>'
    signature_markup = f'<section id="como-trabajo" class="signature-section" data-signature aria-labelledby="signature-title">{signature_body}</section>'

    selected = home["selectedWork"]
    projects_by_id = {item["id"]: item for item in data["projects"]}
    cards=[]
    for project_id in selected["projectIds"]:
        project=projects_by_id[project_id]; card=project["homeCard"]
        labels=(("Situación","situation"),("Tarea","task"),("Acción","contribution"),("Resultado","result"))
        facts="".join(f'<div class="selected-project__fact selected-project__fact--{field}"><dt>{label}</dt><dd>{_copy(card[field])}</dd></div>' for label,field in labels)
        emblem = PROJECT_MARKS[project_id]
        cards.append(f'<article class="selected-project"><div class="selected-project__emblem" aria-hidden="true"><span>{str(len(cards) + 1).zfill(2)}</span>{emblem}</div><h3><a href="{_attr(project["route"])}">{_copy(card["title"])} <span aria-hidden="true">↗</span></a></h3><dl>{facts}</dl><a class="text-link" href="{_attr(project["route"])}">Ver cómo lo abordamos →</a></article>')
    selected_body=f'<div class="section-heading section-heading--row"><div><p class="section-kicker">{_copy(selected["kicker"])}</p><h2 id="transformations-title">{_copy(selected["title"])}</h2></div>{_semantic_link(selected["moreLink"], "button button--quiet")}</div><div class="selected-projects">{"".join(cards)}</div>'
    selected_markup=f'<section class="selected-work" aria-labelledby="transformations-title">{selected_body}</section>'

    story=home["careerStory"]
    milestones="".join(f'<li class="career-milestone"><span class="career-milestone__phase">{_copy(item["phase"])}</span><h3>{_copy(item["employer"])}</h3><p>{_copy(item["description"])}</p></li>' for item in story["milestones"])
    notes="".join(f'<article class="career-note"><span aria-hidden="true">✳</span><h3>{_copy(item["title"])}</h3><p>{_copy(item["body"])}</p></article>' for item in story["notes"])
    explore=story["exploration"]
    story_body=f'<div class="section-heading"><p class="section-kicker">Cómo llegué hasta aquí</p><h2 id="career-title">{_copy(story["heading"])}</h2><p>{_copy(story["introduction"])}</p></div><ol class="career-timeline">{milestones}</ol><div class="career-notes">{notes}</div><div class="career-exploration"><div><p class="section-kicker">{_copy(explore["kicker"])}</p><h3>{_copy(explore["title"])}</h3></div><p>{_copy(explore["description"])}</p></div>'
    story_markup=f'<section id="trayectoria" class="career-section" aria-labelledby="career-title">{story_body}</section>'

    contact=home["contact"]
    contact_markup=f'<section id="contacto" class="contact-section" aria-labelledby="contact-title"><div><p class="section-kicker">{_copy(contact["eyebrow"])}</p><h2 id="contact-title">{_copy(contact["title"])}</h2><p class="contact-introduction">{_copy(contact["introduction"])}</p></div><nav aria-label="Más información y contacto" class="contact-links">{"".join(_semantic_link(link, "button button--contact") for link in contact["links"])}</nav></section>'
    footer=home["footer"]
    return hero_markup+signature_markup+selected_markup+story_markup+contact_markup


def _render_case(project: dict[str, object], all_projects: list[dict[str, object]]) -> str:
    case=project["caseDetails"]; nav=case["navigation"]
    breadcrumb=f'<nav aria-label="Ruta de navegación" class="case-breadcrumb"><a href="/">Inicio</a><span aria-hidden="true">/</span><a href="/projects/">Proyectos</a><span aria-hidden="true">/</span><span aria-current="page">{_copy(nav["breadcrumbTitle"])}</span></nav>'
    hero=case["hero"]
    hero_markup=f'<header class="case-hero"><p class="section-kicker">{_copy(hero["eyebrow"])}</p>{_heading(hero["title"],1)}{_copy_p(hero["summary"],"case-summary")}</header>'
    metric_items="".join(f'<div class="case-metric"><span class="case-metric__value">{_copy(item["value"])}</span><span class="case-metric__label">{_copy(item["label"])}</span></div>' for item in case["metrics"])
    metrics=f'<div class="case-metrics" aria-label="Resultados destacados">{metric_items}</div>'
    diagram=case["diagram"]; image=diagram["image"]
    diagram_markup=f'<figure class="case-flow"><div class="case-flow__image">{_semantic_image(image)}</div><figcaption><p class="section-kicker">{_copy(diagram["kicker"])}</p>{_heading(diagram["title"],2)}{_copy_p(diagram["description"])}</figcaption><ol class="case-flow__steps">{"".join(f"<li>{_copy(step)}</li>" for step in diagram["steps"])}</ol></figure>'
    sections=[]
    for item in (case["context"],case["problem"],case["role"]):
        sections.append(f'<section class="case-section"><p class="section-kicker">{_copy(item["kicker"])}</p>{_heading(item["heading"],2)}{_copy_p(item["body"])}</section>')
    approach=case["approach"]
    sections.append(f'<section class="case-section"><p class="section-kicker">{_copy(approach["kicker"])}</p>{_heading(approach["heading"],2)}<ul>{"".join(f"<li>{_copy(decision)}</li>" for decision in approach["decisions"])}</ul></section>')
    outcome=case["outcome"]
    sections.append(f'<section class="case-section case-section--outcome"><p class="section-kicker">{_copy(outcome["kicker"])}</p>{_heading(outcome["heading"],2)}{_copy_p(outcome["body"])}</section>')
    sections_markup=f'<div class="case-sections">{"".join(sections)}</div>'
    projects_by_id = {item["id"]: item for item in all_projects}
    bottom=[]
    if nav.get("previousProjectId"):
        previous = projects_by_id[nav["previousProjectId"]]
        label = previous["caseDetails"]["navigation"]["navTitle"]
        bottom.append({'label':f'← Caso anterior: {label}', 'href':previous["route"]})
    else:
        bottom.append({'label':'← Todos los proyectos','href':'/projects/'})
    if nav.get("nextProjectId"):
        following = projects_by_id[nav["nextProjectId"]]
        label = following["caseDetails"]["navigation"]["navTitle"]
        bottom.append({'label':f'Siguiente caso: {label} →','href':following["route"]})
    else:
        bottom.append({'label':'Todos los proyectos →','href':'/projects/'})
    bottom_markup=f'<nav aria-label="Navegación de proyectos" class="case-navigation">{"".join(_semantic_link(item, "button button--quiet") for item in bottom)}</nav>'
    return breadcrumb+hero_markup+metrics+diagram_markup+sections_markup+bottom_markup


def _render_projects_page(data: dict[str, object]) -> str:
    page=data["projectsPage"]
    content=f'<div class="section-heading"><p class="section-kicker">Proyectos seleccionados</p>{_heading(page["title"],1,"projects-title")}{_copy_p(page["introduction"])}{_copy_p(page["context"])}</div>'
    return f'<section class="portfolio-intro" aria-labelledby="projects-title">{content}</section>'


def _render_not_found(data: dict[str, object]) -> str:
    page=data["notFound"]
    return f'<div class="content-block content-block--contentGroup">{_copy_p(page["eyebrow"])}{_heading(page["title"],1)}{_copy_p(page["description"])}{"".join(_semantic_link(link) for link in page["actions"])}</div>'


def _seo_markup(page: dict[str, object], site_url: str) -> str:
    seo = page["seo"]
    parts = [
        f"<title>{html.escape(seo['title'], quote=False)}</title>",
        f'<meta name="description" content="{html.escape(seo["description"], quote=True)}">',
    ]
    for meta in seo["meta"]:
        attrs = "".join(
            f' {name}="{html.escape(str(value).replace(DEFAULT_SITE_URL, site_url), quote=True)}"'
            for name, value in meta.items()
        )
        parts.append(f"<meta{attrs}>")
    route = page["route"]
    canonical_route = "/" if route == "index.html" else "/" + route.removesuffix("index.html")
    parts.append(f'<link rel="canonical" href="{html.escape(site_url.rstrip("/") + canonical_route, quote=True)}">')
    if seo["jsonLd"] is not None:
        serialized = json.dumps(seo["jsonLd"], ensure_ascii=False, separators=(",", ":"))
        serialized = serialized.replace("<", "\\u003c").replace("&", "\\u0026")
        parts.append(f'<script type="application/ld+json">{serialized}</script>')
    return "".join(parts)


def _cv_copy(value: str) -> str:
    return html.escape(value, quote=False)


def _cv_group(content: str) -> str:
    return f'<div class="content-block content-block--contentGroup">{content}</div>'


def _cv_section(label: str, title: str, anchor: str, content: str) -> str:
    heading = (
        '<div class="cv-heading">'
        f'<p class="content-copy">{_cv_copy(label)}</p>'
        f'<h2 id="{html.escape(anchor, quote=True)}" class="content-heading content-heading--2">{_cv_copy(title)}</h2>'
        '</div>'
    )
    semantic_name = anchor.removesuffix("-title")
    section_class = "capabilities" if semantic_name == "skills" else semantic_name
    return f'<section id="{html.escape(semantic_name, quote=True)}" aria-labelledby="{html.escape(anchor, quote=True)}" class="cv-section cv-section--{html.escape(section_class, quote=True)}">{heading}<div class="cv-section__content">{content}</div></section>'


def _render_cv_career(career: list[dict[str, object]]) -> str:
    employers = []
    for employer in career:
        pieces = [
            f'<h3 class="content-heading content-heading--3">{_cv_copy(employer["employer"])}</h3>',
            f'<p class="content-copy">{_cv_copy(employer["period"])}</p>',
        ]
        if employer.get("summary"):
            pieces.append(f'<p class="content-copy">{_cv_copy(employer["summary"])}</p>')
        for role in employer["roles"]:
            role_parts = [
                f'<p class="content-copy"><strong>{_cv_copy(role["title"])}</strong> · {_cv_copy(role["period"])}</p>',
                "<ul>" + "".join(f"<li>{_cv_copy(item)}</li>" for item in role["bullets"]) + "</ul>",
            ]
            if role.get("projects"):
                role_parts.append('<p class="content-copy">' + " · ".join(
                    f'<a href="{html.escape(project["href"], quote=True)}">{_cv_copy(project["title"])}</a>'
                    for project in role["projects"]
                ) + "</p>")
            pieces.append(f'<section class="experience-role">{"".join(role_parts)}</section>')
        employers.append(f'<article class="experience-entry">{"".join(pieces)}</article>')
    return _cv_section("TRAYECTORIA", "Experiencia profesional", "experience-title", "".join(employers))


def _render_cv_skills(skills: list[dict[str, object]], profile: dict[str, object]) -> str:
    items = []
    for skill in skills:
        pieces = [f'<h3 class="content-heading content-heading--3">{_cv_copy(skill["area"])}</h3>']
        pieces.append(f'<p class="content-copy">{_cv_copy(" · ".join(skill["skills"]))}</p>')
        if skill["tools"]:
            pieces.append(f'<p class="content-copy">{_cv_copy(" · ".join(skill["tools"]))}</p>')
        items.append(f'<article class="capability-group">{"".join(pieces)}</article>')
    return _cv_section("HERRAMIENTAS", "Capacidades y herramientas", "skills-title", "".join(items))


def _render_cv_value_areas(skills: list[dict[str, object]], profile: dict[str, object]) -> str:
    descriptions = [skill["description"] for skill in skills if skill.get("description")]
    names = [skills[0]["area"], skills[1]["area"], "Datos y automatización"]
    items = "".join(
        f'<article class="cv-impact"><h3 class="content-heading content-heading--3">{_cv_copy(name)}</h3><p class="content-copy">{_cv_copy(description)}</p></article>'
        for name, description in zip(names, descriptions)
    )
    items += f'<p class="content-copy"><strong>Cómo trabajo</strong> {_cv_copy(profile["workflow"])}</p>'
    return _cv_section("EN QUÉ PUEDO APORTAR", "Áreas donde aporto valor", "value-title", items)


def _render_cv_education(data: dict[str, object]) -> str:
    education = data["education"]
    profile = data["profile"]
    education_content = (
        f'<p class="content-copy"><strong>{_cv_copy(education["degree"])}</strong><br>'
        f'{_cv_copy(education["institution"])} · {_cv_copy(education["year"])}</p>'
    )
    language_content = "<p class=\"content-copy\">" + "<br>".join(
        f'{_cv_copy(item["language"])} · {_cv_copy(item["level"])}' for item in data["languages"]
    ) + "</p>"
    location_content = f'<p class="content-copy">{_cv_copy(profile["location"])}</p>'
    panels = []
    for label, title, content in (
        ("FORMACIÓN", "Educación", education_content),
        ("IDIOMAS", "Idiomas", language_content),
        ("UBICACIÓN", "Base", location_content),
    ):
        panels.append(f'<article class="cv-education__item"><p class="section-kicker">{label}</p><h3 class="content-heading content-heading--3">{title}</h3>{content}</article>')
    heading = '<div class="cv-heading"><h2 class="content-heading content-heading--2">Formación y datos complementarios</h2></div>'
    return f'<section aria-label="Formación y datos complementarios" class="cv-section cv-section--education">{heading}<div class="cv-section__content cv-education">{"".join(panels)}</div></section>'


def _render_cv(data: dict[str, object], site_url: str) -> str:
    profile = data["profile"]
    intro = (
        f'<p class="section-kicker">Perfil profesional</p>'
        f'<h1 class="content-heading content-heading--1">{_cv_copy(data["site"]["name"])}</h1>'
        f'<p class="cv-positioning">{_cv_copy(profile["positioning"])}</p>'
        f'<p class="content-copy"><strong>{_cv_copy(profile["profession"])}.</strong> {_cv_copy(profile["summary"])}</p>'
    )
    actions = (
        f'<a class="button" href="{html.escape(profile["cvPdfUrl"], quote=True)}" download>Descargar CV PDF ↓</a>'
        '<button type="button" data-action="print" class="button button--quiet">Imprimir</button>'
    )
    opening = f'<header class="cv-hero">{intro}<div class="cv-actions">{actions}</div></header>'
    lead = _render_cv_career(data["career"])
    return (
        '<nav aria-label="Ruta de navegación" class="case-breadcrumb"><a href="/">Inicio</a><span aria-hidden="true">/</span><span aria-current="page">CV</span></nav>'
        + opening + _render_cv_value_areas(data["skills"], profile) + lead
        + _render_cv_skills(data["skills"], profile)
        + _render_cv_education(data)
        + '<section class="cv-project-cta"><h2>Proyectos en contexto</h2><p>Explora los casos y resultados que acompañan esta trayectoria.</p><a class="button" href="/projects/">Ver proyectos <span aria-hidden="true">→</span></a></section>'
    )


def _render_project_card(project: dict[str, object], labels: dict[str, str], featured: bool) -> str:
    anchor = html.escape(str(project.get("anchor", project["id"])), quote=True)
    tag_ids = project["tags"]
    tag_labels = [labels[tag_id] for tag_id in tag_ids]
    tags = "".join(f"<li>{html.escape(label)}</li>" for label in tag_labels)
    detail_id = f"project-detail-{project['id']}"
    if featured:
        action = f'<a class="project-card__action" href="{html.escape(str(project["route"]), quote=True)}">Ver cómo lo abordamos <span aria-hidden="true">→</span></a>'
    else:
        action = f'<a class="project-card__action" href="#{detail_id}">Ver cómo lo abordamos <span aria-hidden="true">↓</span></a>'
    mark = f'<span class="project-card__mark" aria-hidden="true">{PROJECT_MARKS[project["id"]]}</span>' if featured else ""
    identity = (
        f'<div class="project-card__identity"><p class="project-card__category">{html.escape(str(project.get("group", " · ".join(tag_labels))))}</p>'
        f'<h3>{html.escape(project["title"])}</h3><p class="project-card__summary">{html.escape(project["summary"])}</p></div>'
    )
    evidence = (
        f'<div class="project-card__evidence" id="{html.escape(detail_id, quote=True)}">'
        f'<p><strong>Situación</strong><span>{html.escape(project["situation"])}</span></p>'
        f'<p><strong>Aporte</strong><span>{html.escape(project["contribution"])}</span></p>'
        f'<p class="project-card__result"><strong>Resultado</strong><span>{html.escape(project["result"])}</span></p></div>'
    )
    return (
        f'<li class="project-card project-card--{"lead" if featured and project["id"] == "inventory-reconciliation" else "featured" if featured else "secondary"}" id="{anchor}" '
        f'data-project-id="{html.escape(project["id"], quote=True)}" data-project-tags="{html.escape(" ".join(tag_ids), quote=True)}">'
        f'<article class="project-card__inner"><div class="project-card__body">{mark}{identity}'
        f'<ul class="project-tags" aria-label="Temas del proyecto">{tags}</ul></div>{evidence}'
        f'<div class="project-card__actions">{action}</div></article></li>'
    )


def _render_project_portfolio(data: dict[str, object], site_url: str) -> str:
    labels = {tag["id"]: tag["label"] for tag in data["taxonomy"]["tags"]}
    projects = data["projects"]
    featured = [project for project in projects if project["featured"]]
    secondary = [project for project in projects if not project["featured"]]
    parts = [
        _render_projects_page(data),
        '<form class="project-filters" data-project-filters hidden>',
        '<label class="project-search-label" for="project-search">Buscar por proyecto, descripción o tema</label>',
        '<input id="project-search" type="search" name="q" autocomplete="off" data-project-search>',
        '<fieldset class="project-filter-tags"><legend>Filtrar por temas</legend><div class="project-filter-tags__options">',
    ]
    for tag in data["taxonomy"]["tags"]:
        parts.append(f'<label class="project-filter-tag"><input type="checkbox" name="tag" value="{html.escape(tag["id"], quote=True)}" data-project-tag><span>{html.escape(tag["label"])}</span></label>')
    parts.extend([
        '</div></fieldset><button type="reset" class="project-filters__clear" data-project-clear>Limpiar filtros</button></form>',
        '<p class="project-results" data-project-results role="status" aria-live="polite" aria-atomic="true" hidden></p>',
        '<p class="project-empty" data-project-empty hidden>No hay proyectos que coincidan. Prueba con otros términos o temas.</p>',
        '<section class="portfolio-group portfolio-group--featured" id="TOP4" aria-labelledby="featured-projects-title">',
        '<p class="section-kicker">#TOP4</p><h2 id="featured-projects-title">Proyectos que muestran cómo trabajo</h2><ul class="project-grid project-grid--featured">',
    ])
    parts.extend(_render_project_card(project, labels, True) for project in featured)
    parts.append('</ul></section><section class="portfolio-group portfolio-group--other" aria-labelledby="other-projects-title"><p class="section-kicker">Más experiencias</p><h2 id="other-projects-title">Otros proyectos, agrupados por el problema</h2>')
    groups = list(dict.fromkeys(project.get("group", "Otros proyectos") for project in secondary))
    for index, group in enumerate(groups):
        parts.append(f'<section class="project-category" aria-labelledby="project-category-{index}"><h3 id="project-category-{index}">{html.escape(group)}</h3><ul class="project-grid project-grid--secondary">')
        parts.extend(_render_project_card(project, labels, False) for project in secondary if project.get("group") == group)
        parts.append('</ul></section>')
    parts.append('</section>')
    return "".join(parts)


def _generate_source_pages(data: dict[str, object], site_url: str) -> list[Path]:
    generated: list[Path] = []
    for page in data["pages"]:
        destination = (ROOT / page["route"]).resolve()
        if not destination.is_relative_to(ROOT.resolve()):
            raise ValueError(f"content/site.json: unsafe output route {page['route']!r}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        copy_key = page["id"]
        if copy_key == "projectPortfolio":
            main = _render_project_portfolio(data, site_url)
        elif copy_key == "cvPage":
            main = _render_cv(data, site_url)
        elif copy_key == "home":
            main = _render_home(data)
        elif copy_key == "notFound":
            main = _render_not_found(data)
        else:
            target = "/projects/" + page["route"].removeprefix("projects/").removesuffix("/index.html") + "/"
            project = next(project for project in data["projects"] if project.get("route") == target)
            main = _render_case(project, data["projects"])
        canonical_route = "/" if page["route"] == "index.html" else "/" + page["route"].removesuffix("index.html")
        head = (
            '<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            + _seo_markup(page, site_url)
            + '<link rel="icon" href="/favicon.svg" type="image/svg+xml">'
            + '<script>try{document.documentElement.dataset.theme=localStorage.getItem("harrys-site-theme")==="dark"?"dark":"light"}catch{document.documentElement.dataset.theme="light"}</script>'
            + '<link rel="stylesheet" href="/styles.css">'
        )
        markup = (
            f'<!doctype html><html lang="{html.escape(data["site"]["language"], quote=True)}"><head>{head}</head><body>'
            '<a class="skip-link" href="#main">Saltar al contenido</a><div class="page-shell">'
            f'<header class="site-header" id="top"><a class="wordmark" href="/" aria-label="{html.escape(data["site"]["name"], quote=True)}, inicio">{html.escape(data["site"]["name"])}</a>'
            '<nav class="top-nav" aria-label="Navegación principal"><a href="/projects/">Proyectos</a><a href="/cv/">CV</a></nav></header>'
            f'<main id="main" class="page-main page-main--{html.escape(page["id"], quote=True)}">{main}</main>'
            '<footer class="site-footer simple-footer">'
            f'<span class="footer-name">{html.escape(data["site"]["name"])}</span><a href="/projects/">Proyectos</a><a href="/">Inicio</a>'
            f'<a href="{html.escape(data["site"]["sameAs"][0], quote=True)}" target="_blank" rel="noopener noreferrer">LinkedIn ↗</a></footer>'
            '</div><script src="/script.js" defer></script></body></html>'
        )
        destination.write_text(markup + "\n", encoding="utf-8", newline="\n")
        generated.append(destination)
    return generated


def build(site_url: str = DEFAULT_SITE_URL) -> None:
    site_url = valid_site_url(site_url)
    data = _load_content()
    canonical_site_url = valid_site_url(data["site"]["siteUrl"])
    if canonical_site_url != DEFAULT_SITE_URL and site_url == DEFAULT_SITE_URL:
        site_url = canonical_site_url
    source_pages = _generate_source_pages(data, site_url)
    if DIST.is_symlink() or DIST.resolve().parent != ROOT.resolve():
        raise ValueError("dist must be a real child directory of the repository root")
    if DIST.exists():
        shutil.rmtree(DIST, onexc=_remove_readonly)
    DIST.mkdir()

    files = _public_files()
    html_files = [path for path in files if path.suffix.lower() == ".html"]
    if not html_files:
        raise ValueError("no public HTML pages were found")
    for source in files:
        relative = source.relative_to(ROOT)
        destination = DIST / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.suffix.lower() == ".html":
            content = source.read_text(encoding="utf-8").replace(DEFAULT_SITE_URL, site_url)
            destination.write_text(content, encoding="utf-8")
        else:
            shutil.copy2(source, destination)

    (DIST / "robots.txt").write_text(
        f"User-agent: *\nAllow: {urlsplit(site_url).path or '/'}\nSitemap: {site_url}/sitemap.xml\n",
        encoding="utf-8",
    )
    _write_sitemap(site_url, html_files)
    print(f"Built {len(html_files)} HTML pages and public assets at {DIST}")
    print(f"Site URL: {site_url}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-url", type=valid_site_url, default=DEFAULT_SITE_URL)
    build(parser.parse_args().site_url)


if __name__ == "__main__":
    main()
