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
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
DEFAULT_SITE_URL = "https://harrysxavio.github.io"
PUBLIC_ROOT_FILES = ("index.html", "404.html", "styles.css", "script.js", "favicon.svg", "robots.txt")
PUBLIC_DIRECTORIES = ("assets", "projects", "cv")
CONTENT_FILE = ROOT / "content" / "site.json"
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
    if not isinstance(data, dict) or data.get("schemaVersion") != 2:
        raise ValueError("content/site.json: schemaVersion must be 2")
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
        if project.get("route"):
            case_details = project.get("caseDetails")
            if not isinstance(case_details, list):
                raise ValueError(f"{field}.caseDetails must contain the existing case page copy")
            _validate_content_blocks(case_details, f"project {project['id']}.caseDetails")
    project_routes = {project["route"] for project in projects if project.get("route")}
    expected_project_routes = {
        "/projects/inventory-reconciliation/", "/projects/brazil-chile-data-migration/",
        "/projects/patient-transport-optimization/", "/projects/picking-line-balancing/",
    }
    if project_routes != expected_project_routes:
        raise ValueError("content/site.json: project route assignments must preserve the four existing case routes")
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
    if not isinstance(data.get("cvPage"), list) or len(data["cvPage"]) != 1 or data["cvPage"][0].get("type") != "linkGroup":
        raise ValueError("content/site.json: cvPage must contain only the route breadcrumb; CV facts belong in semantic fields")
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
        copy_key = {"not-found": "notFound", "projects": "projectPortfolio", "cv": "cvPage"}.get(page["id"], page["id"])
        if copy_key in {"home", "notFound", "projectPortfolio", "cvPage"}:
            if not isinstance(data.get(copy_key), list):
                raise ValueError(f"content/site.json: {copy_key} must be an array of semantic content blocks")
            _validate_content_blocks(data[copy_key], copy_key)
        else:
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
    return data


def _validate_content_blocks(blocks: list[object], field: str) -> None:
    known = {
        "contentSection", "contentItem", "media", "callout", "linkGroup", "contentGroup",
        "factGroup", "factLabel", "factValue", "measureGrid", "measureGroup", "measureRow",
        "measureCell", "formControls", "controlLabel", "actionButton", "textControl", "rule",
        "copy", "list", "listItem", "expandable", "expandableTitle", "copyText", "heading",
        "image", "link",
    }
    for index, block in enumerate(blocks):
        location = f"{field}[{index}]"
        if not isinstance(block, dict) or block.get("type") not in known:
            raise ValueError(f"{location}.type must be a supported semantic content block")
        if "anchor" in block and (not isinstance(block["anchor"], str) or not block["anchor"].strip()):
            raise ValueError(f"{location}.anchor must be a non-empty string")
        for child_key in ("blocks", "items"):
            if child_key in block:
                if not isinstance(block[child_key], list):
                    raise ValueError(f"{location}.{child_key} must be an array")
                _validate_content_blocks(block[child_key], f"{location}.{child_key}")
        if "runs" in block and not isinstance(block["runs"], list):
            raise ValueError(f"{location}.runs must be an array")
        if block["type"] == "heading" and block.get("level") not in {1, 2, 3, 4, 5, 6}:
            raise ValueError(f"{location}.level must be a heading level from 1 to 6")
        if block["type"] in {"heading", "copy", "link"}:
            runs = block.get("runs")
            if not isinstance(runs, list):
                raise ValueError(f"{location}.runs is required")
            _validate_runs(runs, f"{location}.runs")
        if block["type"] == "image" and not all(block.get(key) for key in ("src", "alt", "width", "height")):
            if not block.get("decorative") or not block.get("src") or not block.get("width") or not block.get("height"):
                raise ValueError(f"{location}.src, alt, width, and height are required")
        if block["type"] == "link" and not block.get("href"):
            raise ValueError(f"{location}.href is required")
        if block["type"] == "list" and not isinstance(block.get("items"), list):
            raise ValueError(f"{location}.items is required")
        if block["type"] == "listItem" and not isinstance(block.get("blocks"), list):
            raise ValueError(f"{location}.blocks is required")
        if block["type"] == "expandable" and (not isinstance(block.get("summary"), list) or not isinstance(block.get("blocks"), list)):
            raise ValueError(f"{location}.summary and blocks are required")


def _validate_runs(runs: list[object], field: str) -> None:
    allowed = {"text", "link", "strong", "b", "em", "i", "small", "code", "sup", "sub", "break"}
    for index, run in enumerate(runs):
        location = f"{field}[{index}]"
        if not isinstance(run, dict) or run.get("type") not in allowed:
            raise ValueError(f"{location}.type must be an inline content type")
        if run["type"] == "text" and not isinstance(run.get("text"), str):
            raise ValueError(f"{location}.text must be a string")
        if run["type"] == "link":
            if not isinstance(run.get("href"), str) or not run["href"]:
                raise ValueError(f"{location}.href is required")
            if not isinstance(run.get("runs"), list):
                raise ValueError(f"{location}.runs must be an array")
            _validate_runs(run["runs"], f"{location}.runs")
        elif run["type"] in {"strong", "b", "em", "i", "small", "code", "sup", "sub"}:
            if not isinstance(run.get("runs"), list):
                raise ValueError(f"{location}.runs must be an array")
            _validate_runs(run["runs"], f"{location}.runs")


def _render_runs(runs: list[dict[str, object]], site_url: str) -> str:
    output = []
    for run in runs:
        kind = run.get("type")
        if kind == "text":
            value = str(run.get("text", "")).replace(DEFAULT_SITE_URL, site_url)
            if not value.strip() and ("\n" in value or "\r" in value):
                continue
            output.append(html.escape(value, quote=False))
        elif kind == "break":
            output.append("<br>")
        elif kind == "link":
            href = str(run.get("href", ""))
            output.append(f'<a href="{html.escape(href, quote=True)}">{_render_runs(run.get("runs", []), site_url)}</a>')
        elif kind in {"strong", "b", "em", "i", "small", "code", "sup", "sub"}:
            output.append(f"<{kind}>{_render_runs(run.get('runs', []), site_url)}</{kind}>")
    return "".join(output)


def _render_blocks(blocks: list[dict[str, object]], site_url: str) -> str:
    output = []
    for block in blocks:
        kind = block["type"]
        if kind == "copyText" and not str(block.get("text", "")).strip():
            continue
        anchor = f' id="{html.escape(block["anchor"], quote=True)}"' if block.get("anchor") else ""
        if kind == "heading":
            level = int(block["level"])
            output.append(f'<h{level}{anchor} class="content-heading content-heading--{level}">{_render_runs(block.get("runs", []), site_url)}</h{level}>')
        elif kind in {"copy", "copyText"}:
            body = _render_runs(block.get("runs", []), site_url) if "runs" in block else html.escape(str(block.get("text", "")), quote=False)
            output.append(f'<p{anchor} class="content-copy">{body}</p>' if kind == "copy" else body)
        elif kind == "link":
            download = " download" if block.get("download") else ""
            output.append(f'<a{anchor} href="{html.escape(str(block.get("href", "")), quote=True)}" class="content-link"{download}>{_render_runs(block.get("runs", []), site_url)}</a>')
        elif kind == "image":
            alt = "" if block.get("decorative") else str(block.get("alt", ""))
            hidden = ' aria-hidden="true"' if block.get("decorative") else ""
            dimensions = "".join(f' {name}="{html.escape(str(block[name]), quote=True)}"' for name in ("width", "height") if block.get(name))
            image = f'<img src="{html.escape(str(block.get("src", "")), quote=True)}" alt="{html.escape(alt, quote=True)}"{dimensions}{hidden}>'
            sources = block.get("sources", [])
            source_markup = "".join(
                f'<source srcset="{html.escape(str(source["srcset"]), quote=True)}" media="{html.escape(str(source["media"]), quote=True)}">'
                for source in sources
            )
            output.append(f"<picture>{source_markup}{image}</picture>" if sources else image)
        elif kind == "list":
            tag = "ol" if block.get("ordered") else "ul"
            output.append(f"<{tag}>{_render_blocks(block.get('items', []), site_url)}</{tag}>")
        elif kind == "listItem":
            output.append(f"<li{anchor}>{_render_blocks(block.get('blocks', []), site_url)}</li>")
        elif kind == "expandable":
            opened = " open" if block.get("open") else ""
            title = _render_runs(block.get("summary", []), site_url)
            output.append(f"<details{anchor}{opened}><summary>{title}</summary>{_render_blocks(block.get('blocks', []), site_url)}</details>")
        else:
            tag = {
                "contentSection": "section", "contentItem": "article", "media": "figure", "callout": "blockquote",
                "linkGroup": "nav", "contentGroup": "div", "factGroup": "dl", "factLabel": "dt",
                "factValue": "dd", "measureGrid": "table", "measureGroup": "tbody", "measureRow": "tr",
                "measureCell": "td", "formControls": "form", "controlLabel": "label", "rule": "hr",
                "actionButton": "button", "textControl": "input", "expandableTitle": "span",
            }[kind]
            attrs = anchor
            if kind == "linkGroup" and block.get("label"):
                attrs += f' aria-label="{html.escape(str(block["label"]), quote=True)}"'
            if kind == "contentSection" and block.get("labelledBy"):
                attrs += f' aria-labelledby="{html.escape(str(block["labelledBy"]), quote=True)}"'
            if kind == "actionButton":
                attrs += ' type="button"'
                if block.get("action"): attrs += f' data-action="{html.escape(str(block["action"]), quote=True)}"'
            content = html.escape(str(block.get("label", "")), quote=False) if kind == "actionButton" else _render_blocks(block.get("blocks", []), site_url)
            if kind == "textControl":
                input_type = html.escape(str(block.get("inputType", "text")), quote=True)
                name = html.escape(str(block.get("name", "")), quote=True)
                value = html.escape(str(block.get("value", "")), quote=True)
                labelled = html.escape(str(block.get("labelledBy", "")), quote=True)
                output.append(f'<input{anchor} type="{input_type}" name="{name}" value="{value}" aria-labelledby="{labelled}">')
            elif kind == "rule":
                output.append(f"<{tag}{attrs}>")
            else:
                output.append(f'<{tag}{attrs} class="content-block content-block--{kind}">{content}</{tag}>')
    return "".join(output)


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
    heading = _cv_group(
        f'<p class="content-copy">{_cv_copy(label)}</p>'
        f'<h2 id="{html.escape(anchor, quote=True)}" class="content-heading content-heading--2">{_cv_copy(title)}</h2>'
    )
    return f'<section id="{html.escape(anchor.removesuffix("-title"), quote=True)}" aria-labelledby="{html.escape(anchor, quote=True)}" class="content-block content-block--contentSection">{heading}{_cv_group(content)}</section>'


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
            pieces.append(_cv_group("".join(role_parts)))
        employers.append(f'<article class="content-block content-block--contentItem">{"".join(pieces)}</article>')
    return _cv_section("TRAYECTORIA", "Experiencia profesional", "experience-title", "".join(employers))


def _render_cv_skills(skills: list[dict[str, object]], profile: dict[str, object]) -> str:
    items = []
    for skill in skills:
        pieces = [f'<h3 class="content-heading content-heading--3">{_cv_copy(skill["area"])}</h3>']
        pieces.append(f'<p class="content-copy">{_cv_copy(" · ".join(skill["skills"]))}</p>')
        if skill["tools"]:
            pieces.append(f'<p class="content-copy">{_cv_copy(" · ".join(skill["tools"]))}</p>')
        items.append(f'<article class="content-block content-block--contentItem">{"".join(pieces)}</article>')
    return _cv_section("HERRAMIENTAS", "Capacidades y herramientas", "skills-title", "".join(items))


def _render_cv_value_areas(skills: list[dict[str, object]], profile: dict[str, object]) -> str:
    descriptions = [skill["description"] for skill in skills if skill.get("description")]
    names = [skills[0]["area"], skills[1]["area"], "Datos y automatización"]
    items = "".join(
        f'<article class="content-block content-block--contentItem"><h3 class="content-heading content-heading--3">{_cv_copy(name)}</h3><p class="content-copy">{_cv_copy(description)}</p></article>'
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
        panels.append(_cv_group(f'<p class="content-copy">{label}</p><h2 class="content-heading content-heading--2">{title}</h2>{content}'))
    heading = _cv_group('<h2 class="content-heading content-heading--2">Formación y datos complementarios</h2>')
    return f'<section aria-label="Formación y datos complementarios" class="content-block content-block--contentSection">{heading}{"".join(panels)}</section>'


def _render_cv(data: dict[str, object], site_url: str) -> str:
    profile = data["profile"]
    intro = (
        f'<p class="content-copy">PERFIL PROFESIONAL</p>'
        f'<h1 class="content-heading content-heading--1">{_cv_copy(data["site"]["name"])}</h1>'
        f'<p class="content-copy">{_cv_copy(profile["positioning"])}</p>'
        f'<p class="content-copy"><strong>{_cv_copy(profile["profession"])}.</strong> {_cv_copy(profile["summary"])}</p>'
    )
    actions = (
        f'<a class="content-link" href="{html.escape(profile["cvPdfUrl"], quote=True)}" download>Descargar CV PDF ↓</a>'
        '<button type="button" data-action="print" class="content-block content-block--actionButton">Imprimir</button>'
    )
    opening = f'{_cv_group(intro)}{_cv_group(actions)}'
    lead = _render_cv_career(data["career"])
    return (
        _render_blocks(data["cvPage"], site_url) + opening + _render_cv_value_areas(data["skills"], profile) + lead
        + _render_cv_skills(data["skills"], profile)
        + _render_cv_education(data)
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
    return (
        f'<li class="project-card project-card--{"featured" if featured else "secondary"}" id="{anchor}" '
        f'data-project-id="{html.escape(project["id"], quote=True)}" data-project-tags="{html.escape(" ".join(tag_ids), quote=True)}">'
        '<article class="project-card__inner"><div class="project-card__body">'
        f'<p class="project-card__category">{html.escape(str(project.get("group", " · ".join(tag_labels))))}</p>'
        f'<h3>{html.escape(project["title"])}</h3><p class="project-card__summary">{html.escape(project["summary"])}</p>'
        f'<ul class="project-tags" aria-label="Temas del proyecto">{tags}</ul>'
        f'<div class="project-card__detail" id="{html.escape(detail_id, quote=True)}">'
        f'<p>{html.escape(project["situation"])}</p><p>{html.escape(project["contribution"])}</p>'
        f'<p class="project-card__result">{html.escape(project["result"])}</p></div></div>'
        f'<div class="project-card__actions">{action}</div></article></li>'
    )


def _render_project_portfolio(data: dict[str, object], site_url: str) -> str:
    labels = {tag["id"]: tag["label"] for tag in data["taxonomy"]["tags"]}
    projects = data["projects"]
    featured = [project for project in projects if project["featured"]]
    secondary = [project for project in projects if not project["featured"]]
    parts = [
        _render_blocks(data["projectPortfolio"], site_url),
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
        copy_key = {"not-found": "notFound", "projects": "projectPortfolio", "cv": "cvPage"}.get(page["id"], page["id"])
        if copy_key == "projectPortfolio":
            main = _render_project_portfolio(data, site_url)
        elif copy_key == "cvPage":
            main = _render_cv(data, site_url)
        elif copy_key in {"home", "notFound"}:
            main = _render_blocks(data[copy_key], site_url)
        else:
            target = "/projects/" + page["route"].removeprefix("projects/").removesuffix("/index.html") + "/"
            project = next(project for project in data["projects"] if project.get("route") == target)
            main = _render_blocks(project["caseDetails"], site_url)
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
            '<nav class="top-nav" aria-label="Navegación principal"><a href="/projects/">Proyectos</a><a href="/cv/">CV</a>'
            f'<a href="{html.escape(data["site"]["sameAs"][0], quote=True)}" target="_blank" rel="noopener noreferrer">LinkedIn <span aria-hidden="true">↗</span></a></nav></header>'
            f'<main id="main" class="page-main page-main--{html.escape(page["id"], quote=True)}">{main}</main>'
            '<footer class="site-footer simple-footer">'
            f'<span>{html.escape(data["site"]["name"])}</span><a href="/projects/">Proyectos</a><a href="/">Inicio</a>'
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
