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

    def handle_decl(self, decl: str) -> None:
        self.doctype = decl.casefold() == "doctype html"

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.casefold(): value or "" for key, value in attrs}
        if tag == "html": self.lang = values.get("lang", "")
        if values.get("id"): self.ids.append(values["id"])
        if tag == "a" and values.get("href"): self.links.append(values["href"])
        if tag == "img": self.images.append(values)
        if tag in {"script", "source"} and values.get("src"): self.resources.append(values["src"])
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


def check_output(base: Path, site_url: str) -> None:
    pages = pages_under(base)
    seen = {p.relative_to(base).as_posix() for p in pages if p.is_file()}
    require(REQUIRED_ROUTES <= seen, f"required routes missing: {sorted(REQUIRED_ROUTES - seen)}")
    for page in pages:
        if page.is_file(): check_page(page, base, site_url)
    check_sitemap(base, site_url)


def check_dist(site_url: str) -> None:
    dist = ROOT / "dist"
    if not dist.exists(): return
    source = {p.relative_to(ROOT).as_posix() for p in (ROOT / name for name in PUBLIC_ROOT_FILES) if p.is_file()}
    for folder in PUBLIC_DIRECTORIES:
        directory = ROOT / folder
        if directory.is_dir(): source.update(p.relative_to(ROOT).as_posix() for p in directory.rglob("*") if p.is_file() and p.suffix.lower() in {".html", ".svg", ".webp", ".avif", ".jpg", ".jpeg", ".png"})
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


if __name__ == "__main__": main()
