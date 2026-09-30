#!/usr/bin/env python3
"""Dependency-free structural integrity checks for the static landing page."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_IDS = (
    "main",
    "enfoque",
    "forma-de-trabajo",
    "experiencia",
    "exploraciones",
    "casos",
    "ideas",
    "sobre-mi",
    "contacto",
)
EXPECTED_LINKS = {
    "https://www.linkedin.com/in/h-yusti/",
    "https://github.com/harrysxavio",
}
REQUIRED_PROFILE_TERMS = (
    "ingeniero mecánico",
    "más de 10 años",
    "supply chain",
    "logística",
    "operaciones",
    "inventario",
    "mejora de procesos",
    "proyectos de tecnología",
    "transformación de negocio",
    "datos",
    "automatización",
    "gestión de proyectos",
    "iniciativas ejecutables",
    "productividad personal, de equipos y operacional",
    "pensamiento sistémico",
    "finanzas",
    "servicio al cliente",
    "sap ewm",
    "bigquery",
    "power bi",
    "databricks",
    "python",
    "n8n",
    "agentes",
    "rag",
    "ollama",
    "codex",
    "opencode",
    "pmi / pmbok",
    "kanban",
    "lean",
)


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.headings: list[tuple[int, str]] = []
        self.heading_text = ""
        self.in_heading = False
        self.title_parts: list[str] = []
        self.in_title = False
        self.jsonld = ""
        self.in_jsonld = False
        self.images: list[str] = []
        self.description = False
        self.og_fields: set[str] = set()
        self.language = ""
        self.page_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "html":
            self.language = values.get("lang", "") or ""
        if values.get("id"):
            self.ids.add(values["id"] or "")
        if tag == "a" and values.get("href"):
            self.links.append(values["href"] or "")
        if tag == "img" and values.get("src"):
            self.images.append(values["src"] or "")
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.headings.append((int(tag[1]), ""))
            self.in_heading = True
        if tag == "title":
            self.in_title = True
        if tag == "script" and values.get("type") == "application/ld+json":
            self.in_jsonld = True
        if tag == "meta":
            self.description |= values.get("name") == "description" and bool(values.get("content"))
            if values.get("property", "").startswith("og:"):
                self.og_fields.add(values["property"] or "")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.in_heading = False
        if tag == "title":
            self.in_title = False
        if tag == "script" and self.in_jsonld:
            self.in_jsonld = False

    def handle_data(self, data: str) -> None:
        if not self.in_jsonld:
            self.page_text.append(data)
        if self.in_heading and self.headings:
            level, current = self.headings[-1]
            self.headings[-1] = (level, current + data.strip())
        if self.in_title:
            self.title_parts.append(data)
        if self.in_jsonld:
            self.jsonld += data


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def main() -> None:
    html_path = ROOT / "index.html"
    html = html_path.read_text(encoding="utf-8")
    parser = PageParser()
    parser.feed(html)
    page_text = " ".join(parser.page_text).casefold()

    if parser.language != "es":
        fail('the document language must be declared as lang="es"')

    if not parser.title_parts or "Harrys Yusti" not in "".join(parser.title_parts):
        fail("page title is missing or does not identify Harrys Yusti")
    if not parser.description:
        fail("meta description is missing")
    if "ingeniero mecánico" not in page_text or "más de 10 años" not in page_text:
        fail("Spanish title/profile copy must include the supplied profession and experience")
    missing_profile_terms = [term for term in REQUIRED_PROFILE_TERMS if term not in page_text]
    if missing_profile_terms:
        fail("profile coverage is missing: " + ", ".join(missing_profile_terms))
    if not {"og:type", "og:title", "og:description"}.issubset(parser.og_fields):
        fail("required Open Graph fields are missing")
    if len(re.findall(r"<h1\b", html, re.I)) != 1:
        fail("expected exactly one h1")
    if not parser.headings or parser.headings[0][0] != 1 or any(
        current - previous > 1 for (previous, _), (current, _) in zip(parser.headings, parser.headings[1:])
    ):
        fail("heading levels must start at h1 and must not skip a level")
    for anchor in EXPECTED_IDS:
        if anchor not in parser.ids:
            fail(f"missing expected landmark or section id: {anchor}")
    if not EXPECTED_LINKS.issubset(set(parser.links)):
        fail("one or more supplied public profile links are missing")
    if set(parser.links) - EXPECTED_LINKS - {f"#{item}" for item in parser.ids}:
        fail("unexpected external or unresolved navigation link found")
    for asset in parser.images:
        if not (ROOT / asset).is_file():
            fail(f"local image reference does not resolve: {asset}")
    if 'href="styles.css"' not in html or not (ROOT / "styles.css").is_file():
        fail("stylesheet reference does not resolve")
    if 'href="favicon.svg"' not in html or not (ROOT / "favicon.svg").is_file():
        fail("on-brand favicon reference does not resolve")
    try:
        schema = json.loads(parser.jsonld)
    except json.JSONDecodeError as exc:
        fail(f"JSON-LD is not valid JSON: {exc}")
    person = schema.get("mainEntity", {})
    if schema.get("@type") != "ProfilePage" or person.get("@type") != "Person":
        fail("JSON-LD must describe a ProfilePage with a Person mainEntity")
    if set(person.get("sameAs", [])) != EXPECTED_LINKS:
        fail("Person sameAs must contain only the two supplied profile URLs")

    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if "User-agent: *" not in robots or "Allow: /" not in robots:
        fail("robots.txt must allow public crawling")
    sitemap = ET.parse(ROOT / "sitemap.xml").getroot()
    if not sitemap.tag.endswith("urlset"):
        fail("sitemap.xml has an unexpected root element")
    sitemap_locations = [node.text or "" for node in sitemap.iter() if node.tag.endswith("loc")]
    if sitemap_locations and any(not location.startswith("https://") for location in sitemap_locations):
        fail("sitemap contains a non-HTTPS location")
    if not sitemap_locations and ("Sitemap:" in robots or "<loc>" in (ROOT / "sitemap.xml").read_text(encoding="utf-8")):
        fail("unconfigured domain must not be published as a sitemap URL")

    print("PASS: Spanish locale/profile coverage, title, description, Open Graph, landmarks, headings, links, JSON-LD, and local assets")
    print(f"PASS: robots.txt permits crawling; sitemap.xml is valid ({len(sitemap_locations)} absolute URL entries)")
    print("NOTE: this is a structural integrity check, not a build or rendered-browser test")


if __name__ == "__main__":
    main()
