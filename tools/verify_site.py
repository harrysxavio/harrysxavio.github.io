#!/usr/bin/env python3
"""Check the static profile, public metadata, and optional packaged output."""

from __future__ import annotations

import json
import argparse
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

from build_site import DEFAULT_SITE_URL, PUBLIC_ASSETS, PUBLIC_FILES, SOCIAL_IMAGE, _set_site_meta, valid_site_url

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_LINKS = {
    "https://www.linkedin.com/in/h-yusti/",
    "https://github.com/harrysxavio",
}
REQUIRED_META = {
    "description", "og:type", "og:title", "og:description", "og:locale", "og:url",
    "og:image", "og:image:alt", "twitter:card", "twitter:title", "twitter:description",
    "twitter:image", "twitter:image:alt",
}
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.links: list[str] = []
        self.resources: list[str] = []
        self.headings: list[tuple[int, str]] = []
        self._active_heading: int | None = None
        self._stack: list[str] = []
        self.errors: list[str] = []
        self.title_parts: list[str] = []
        self._in_title = False
        self._jsonld_parts: list[str] = []
        self._in_jsonld = False
        self.metas: list[dict[str, str]] = []
        self.canonicals: list[str] = []
        self.language = ""
        self.doctype = False

    def handle_decl(self, decl: str) -> None:
        if decl.casefold() == "doctype html":
            self.doctype = True

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name.casefold(): value or "" for name, value in attrs}
        if tag == "html":
            self.language = values.get("lang", "")
        if values.get("id"):
            self.ids.append(values["id"])
        if tag == "a" and values.get("href"):
            self.links.append(values["href"])
        if tag == "link":
            rel = values.get("rel", "").casefold().split()
            if "canonical" in rel:
                self.canonicals.append(values.get("href", ""))
            if "stylesheet" in rel or "icon" in rel:
                self.resources.append(values.get("href", ""))
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.headings.append((int(tag[1]), ""))
            self._active_heading = len(self.headings) - 1
        if tag == "title":
            self._in_title = True
        if tag == "script" and values.get("type") == "application/ld+json":
            self._in_jsonld = True
            self._jsonld_parts.append("")
        if tag == "meta":
            self.metas.append(values)
        if tag not in VOID_TAGS:
            self._stack.append(tag)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._active_heading = None
        if tag == "title":
            self._in_title = False
        if tag == "script" and self._in_jsonld:
            self._in_jsonld = False
        if tag in VOID_TAGS:
            self.errors.append(f"void element has a closing tag: {tag}")
            return
        if not self._stack:
            self.errors.append(f"unexpected closing tag: {tag}")
            return
        current = self._stack.pop()
        if current != tag:
            self.errors.append(f"closing tag </{tag}> does not match <{current}>")

    def handle_data(self, data: str) -> None:
        if self._active_heading is not None:
            level, value = self.headings[self._active_heading]
            self.headings[self._active_heading] = (level, value + data.strip())
        if self._in_title:
            self.title_parts.append(data)
        if self._in_jsonld:
            self._jsonld_parts[-1] += data

    def close(self) -> None:
        super().close()
        if self._stack:
            self.errors.append("unclosed tags: " + ", ".join(self._stack[-5:]))


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def parse_page(path: Path) -> tuple[str, PageParser]:
    require(path.is_file(), f"page does not exist: {path}")
    source = path.read_text(encoding="utf-8")
    parser = PageParser()
    parser.feed(source)
    parser.close()
    return source, parser


def check_url_builder(source_html: str) -> None:
    cases = {
        "https://harrysxavio.github.io": "https://harrysxavio.github.io",
        "https://harrysxavio.github.io/": "https://harrysxavio.github.io",
        "https://example.com/Harryslanding/": "https://example.com/Harryslanding",
    }
    for value, normalized in cases.items():
        require(valid_site_url(value) == normalized, f"site URL normalization failed: {value}")
    for invalid in (
        "http://example.com", "https://example.com?query=1", "https://example.com#fragment",
        "https://user@example.com", "https://example.com/../private",
    ):
        try:
            valid_site_url(invalid)
        except Exception:
            continue
        fail(f"invalid site URL was accepted: {invalid}")

    base = "https://example.com/Harryslanding"
    rendered = _set_site_meta(source_html, base)
    require(f'href="{base}/"' in rendered, "base-path canonical URL was not generated")
    require(f'content="{base}/{SOCIAL_IMAGE}"' in rendered, "base-path social image URL was not generated")
    require("data-site-meta=" not in rendered, "internal metadata template markers leaked into built HTML")
    match = re.search(r"<script\b[^>]*application/ld\+json[^>]*>(.*?)</script>", rendered, re.I | re.S)
    require(match is not None, "JSON-LD template is missing")
    graph = json.loads(match.group(1)).get("@graph", [])
    profile = next((item for item in graph if item.get("@type") == "ProfilePage"), {})
    person = next((item for item in graph if item.get("@type") == "Person"), {})
    require(profile.get("url") == f"{base}/", "base-path ProfilePage URL was not generated")
    require(person.get("url") == f"{base}/", "base-path Person URL was not generated")
    require(profile.get("mainEntity", {}).get("@id") == person.get("@id"), "base-path ProfilePage mainEntity reference was not updated")
    malformed = (
        source_html.replace(' data-site-meta="canonical"', "", 1),
        source_html.replace(' data-site-meta="canonical"', ' data-site-meta="unknown"', 1),
    )
    for template in malformed:
        try:
            _set_site_meta(template, base)
        except ValueError:
            continue
        fail("malformed site metadata template was accepted")


def check_html(path: Path, expected_site_url: str) -> PageParser:
    source, parser = parse_page(path)
    require(parser.doctype, "HTML5 doctype is missing")
    require(not parser.errors, "HTML structure is invalid: " + "; ".join(parser.errors))
    require(parser.language == "es", 'document language must be lang="es"')
    require("Harrys Yusti" in "".join(parser.title_parts), "title must identify Harrys Yusti")
    h1 = [heading for heading in parser.headings if heading[0] == 1]
    require(len(h1) == 1 and "Harrys Yusti" in h1[0][1], "expected one page-level h1 identifying Harrys Yusti")
    require(parser.headings and parser.headings[0][0] == 1, "heading hierarchy must begin with h1")
    require(all(nxt - level <= 1 for (level, _), (nxt, _) in zip(parser.headings, parser.headings[1:])), "heading levels must not skip a level")
    require(len(parser.ids) == len(set(parser.ids)), "duplicate HTML id attributes found")
    fragments = {urlsplit(link).fragment for link in parser.links if link.startswith("#") and urlsplit(link).fragment}
    missing = sorted(fragments - set(parser.ids))
    require(not missing, "unresolved in-page links: " + ", ".join(missing))

    meta_keys = [("name", values.get("name", "").casefold()) for values in parser.metas if values.get("name")]
    meta_keys += [("property", values.get("property", "").casefold()) for values in parser.metas if values.get("property")]
    require(len(meta_keys) == len(set(meta_keys)), "duplicate named or Open Graph meta declarations found")
    available = {values.get("name", "").casefold() for values in parser.metas} | {values.get("property", "").casefold() for values in parser.metas}
    require(REQUIRED_META.issubset(available), "required description/social metadata is missing: " + ", ".join(sorted(REQUIRED_META - available)))
    twitter = [values for values in parser.metas if values.get("name", "").casefold() == "twitter:card"]
    require(len(twitter) == 1 and twitter[0].get("content") == "summary_large_image", "exactly one summary_large_image Twitter card is required")
    expected_root = expected_site_url.rstrip("/") + "/"
    require(parser.canonicals == [expected_root], "exactly one canonical link matching the production URL is required")

    links = set(parser.links)
    require(EXPECTED_LINKS.issubset(links), "one or more supplied public profile links are missing")
    external = {link for link in links if urlsplit(link).scheme in {"http", "https"}}
    require(external == EXPECTED_LINKS, "unexpected public link found or supplied profile link missing")

    resources = list(parser.resources)
    for resource in resources:
        if resource and not resource.startswith(("http://", "https://", "data:")):
            require((path.parent / resource.split("#", 1)[0]).is_file(), f"local resource does not resolve: {resource}")
    image_urls = [values.get("content", "") for values in parser.metas if values.get("property", "").casefold() == "og:image"]
    require(len(image_urls) == 1 and image_urls[0].endswith("/" + SOCIAL_IMAGE), "Open Graph image must reference the supplied optimized preview")
    require((path.parent / SOCIAL_IMAGE).is_file(), "social preview image is missing")

    require(len(parser._jsonld_parts) == 1, "exactly one JSON-LD block is required")
    try:
        schema = json.loads(parser._jsonld_parts[0])
    except json.JSONDecodeError as exc:
        fail(f"JSON-LD is not valid JSON: {exc}")
    graph = schema.get("@graph", [])
    profile = next((item for item in graph if item.get("@type") == "ProfilePage"), None)
    person = next((item for item in graph if item.get("@type") == "Person"), None)
    require(profile is not None and person is not None, "JSON-LD must include ProfilePage and Person entities")
    require(profile.get("url") == expected_root and person.get("url") == expected_root, "ProfilePage and Person URLs must match canonical")
    require(profile.get("mainEntity", {}).get("@id") == person.get("@id"), "ProfilePage mainEntity must point to the Person entity")
    require(set(person.get("sameAs", [])) == EXPECTED_LINKS, "Person sameAs must contain only the supplied LinkedIn and GitHub URLs")
    require("Harrys Yusti" in person.get("name", "") and person.get("jobTitle") == "Mechanical Engineer | Projects, Supply Chain & Operational Transformation", "Person schema must use the confirmed professional positioning, not an invented current role")

    text = " ".join([*parser.title_parts, *(heading for _, heading in parser.headings)]).casefold()
    require("ideas" not in text and "coming soon" not in text, "empty ideas/coming-soon content remains")
    robots = path.parent / "robots.txt"
    sitemap = path.parent / "sitemap.xml"
    require(robots.is_file() and sitemap.is_file(), "robots.txt or sitemap.xml is missing")
    parsed_site = urlsplit(expected_site_url)
    expected_allow = f"Allow: {parsed_site.path.rstrip('/')}/" if parsed_site.path else "Allow: /"
    expected_sitemap = f"Sitemap: {expected_site_url.rstrip('/')}/sitemap.xml"
    robots_text = robots.read_text(encoding="utf-8")
    require("User-agent: *" in robots_text and expected_allow in robots_text and expected_sitemap in robots_text, "robots.txt directives do not match the site URL")
    try:
        sitemap_root = ET.parse(sitemap).getroot()
    except ET.ParseError as exc:
        fail(f"sitemap.xml is not valid XML: {exc}")
    require(sitemap_root.tag.endswith("urlset"), "sitemap.xml root must be urlset")
    locations = [node.text or "" for node in sitemap_root.iter() if node.tag.endswith("loc")]
    require(locations == [expected_root], "sitemap URL must contain exactly the canonical page")
    return parser


def check_dist(expected_site_url: str) -> None:
    dist = ROOT / "dist"
    if not dist.exists():
        print("NOTE: dist/ is absent; run tools/build_site.py to verify packaged output.")
        return
    expected = set(PUBLIC_FILES) | set(PUBLIC_ASSETS) | {"robots.txt", "sitemap.xml"}
    actual = {item.relative_to(dist).as_posix() for item in dist.rglob("*") if item.is_file()}
    require(actual == expected, "dist contains missing or unexpected files: " + repr(sorted(actual ^ expected)))
    allowed_dirs = {item.relative_to(dist).as_posix() for item in dist.rglob("*") if item.is_dir()}
    require(allowed_dirs <= {"assets"}, "dist contains an unexpected directory")
    check_html(dist / "index.html", expected_site_url)


def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--site-url", type=valid_site_url, default=DEFAULT_SITE_URL, help="expected HTTPS URL for the dist preview")
    args = cli.parse_args()
    page = ROOT / "index.html"
    source, _ = parse_page(page)
    try:
        root_url = valid_site_url(DEFAULT_SITE_URL)
    except Exception as exc:
        fail(f"configured production site URL is invalid: {exc}")
    check_url_builder(source)
    check_html(page, root_url)
    check_dist(valid_site_url(args.site_url))
    require((ROOT / "styles.css").is_file(), "stylesheet is missing")
    require((ROOT / "favicon.svg").is_file(), "favicon is missing")
    print("PASS: HTML structure, locale, title, headings, anchors, and profile links")
    print("PASS: canonical, Open Graph/Twitter metadata, ProfilePage/Person JSON-LD, robots, sitemap, and social asset")
    print("PASS: HTTPS site URL validation, root/base-path metadata generation, and local resources")
    if (ROOT / "dist").exists():
        print("PASS: dist contains only the public allowlist and matching metadata")


if __name__ == "__main__":
    main()
