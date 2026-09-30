#!/usr/bin/env python3
"""Build the public static site into dist for a verified HTTPS site URL."""

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
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
DEFAULT_SITE_URL = "https://harrysxavio.github.io"
PUBLIC_FILES = ("index.html", "styles.css", "favicon.svg")
PUBLIC_ASSETS = ("assets/operations-transformation-illustration.webp",)
SOCIAL_IMAGE = "assets/operations-transformation-illustration.webp"
SITE_META_PATTERN = re.compile(
    r'<(?P<tag>meta|link)\b(?P<attrs>[^>]*\bdata-site-meta=["\'](?P<key>[^"\']+)["\'][^>]*)>',
    re.IGNORECASE,
)
JSON_LD_PATTERN = re.compile(
    r'(<script\b(?=[^>]*\btype=["\']application/ld\+json["\'])[^>]*>)(.*?)(</script\s*>)',
    re.IGNORECASE | re.DOTALL,
)


def valid_site_url(value: str) -> str:
    """Validate an HTTPS site URL and normalize away trailing slashes."""
    parsed = urlsplit(value)
    host = parsed.hostname or ""
    try:
        port = parsed.port
    except ValueError as exc:
        raise argparse.ArgumentTypeError("site URL contains an invalid port") from exc

    path = parsed.path.rstrip("/")
    valid_path = re.fullmatch(r"(?:/[A-Za-z0-9._~-]+)*", path) is not None
    if any(segment in {".", ".."} for segment in path.split("/") if segment):
        valid_path = False
    if (
        parsed.scheme.lower() != "https"
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
        or not re.fullmatch(r"[A-Za-z0-9.-]+", host)
        or not valid_path
        or parsed.query
        or parsed.fragment
        or "?" in value
        or "#" in value
        or (port is not None and not 1 <= port <= 65535)
    ):
        raise argparse.ArgumentTypeError(
            "site URL must be an HTTPS URL without credentials, query, or fragment; "
            "an optional path is allowed (for example https://example.com/site)"
        )

    netloc = parsed.netloc.lower()
    return urlunsplit(("https", netloc, path, "", ""))


def _replace_attribute(tag: str, attribute: str, value: str) -> str:
    escaped = html.escape(value, quote=True)
    attr_pattern = re.compile(rf'(\b{re.escape(attribute)}\s*=\s*)(["\']).*?\2', re.IGNORECASE)
    if attr_pattern.search(tag):
        return attr_pattern.sub(lambda match: f'{match.group(1)}"{escaped}"', tag, count=1)
    return tag[:-1] + f' {attribute}="{escaped}">'


def _set_site_meta(page: str, site_url: str) -> str:
    canonical = f"{site_url}/"
    values = {
        "canonical": ("href", canonical),
        "og-url": ("content", canonical),
        "og-image": ("content", f"{site_url}/{SOCIAL_IMAGE}"),
        "twitter-image": ("content", f"{site_url}/{SOCIAL_IMAGE}"),
    }
    found: dict[str, int] = {}

    def replace(match: re.Match[str]) -> str:
        key = match.group("key")
        if key not in values:
            return match.group(0)
        found[key] = found.get(key, 0) + 1
        attribute, value = values[key]
        tag = _replace_attribute(match.group(0), attribute, value)
        return re.sub(r'\sdata-site-meta=["\'][^"\']+["\']', "", tag, count=1)

    page = SITE_META_PATTERN.sub(replace, page)
    missing = set(values) - set(found)
    duplicated = [key for key, count in found.items() if count != 1]
    unknown = re.search(r'\bdata-site-meta\s*=', page, re.IGNORECASE) is not None
    if missing or duplicated or unknown:
        raise ValueError(
            f"site metadata template is invalid; missing={sorted(missing)}, "
            f"duplicated={duplicated}, unknown_markers={unknown}"
        )

    script = JSON_LD_PATTERN.search(page)
    if not script:
        raise ValueError("index.html must contain a JSON-LD script")
    profile = json.loads(script.group(2))
    graph = profile.get("@graph")
    if not isinstance(graph, list):
        raise ValueError("JSON-LD must expose ProfilePage and Person in an @graph")
    person_id = f"{site_url}/#person"
    for entity in graph:
        types = entity.get("@type", [])
        if isinstance(types, str):
            types = [types]
        if "ProfilePage" in types:
            entity["@id"] = f"{site_url}/#profile"
            entity["url"] = canonical
        if "Person" in types:
            entity["@id"] = person_id
            entity["url"] = canonical
        if "ProfilePage" in types and isinstance(entity.get("mainEntity"), dict):
            entity["mainEntity"]["@id"] = person_id
    page = page[: script.start(2)] + "\n      " + json.dumps(profile, ensure_ascii=False, indent=2) + "\n    " + page[script.end(2) :]
    return page


def _write_robots_and_sitemap(site_url: str) -> None:
    parsed = urlsplit(site_url)
    base_path = parsed.path
    allowed_path = f"{base_path}/" if base_path else "/"
    (DIST / "robots.txt").write_text(
        f"User-agent: *\nAllow: {allowed_path}\nSitemap: {site_url}/sitemap.xml\n",
        encoding="utf-8",
    )

    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    sitemap = ET.Element("urlset", xmlns=namespace)
    entry = ET.SubElement(sitemap, "url")
    ET.SubElement(entry, "loc").text = f"{site_url}/"
    ET.ElementTree(sitemap).write(DIST / "sitemap.xml", encoding="utf-8", xml_declaration=True)


def _remove_readonly(function: object, path: str, error: object) -> None:
    """Retry removal when Windows/OneDrive marks prior generated output read-only."""
    os.chmod(path, stat.S_IREAD | stat.S_IWRITE)
    function(path)  # type: ignore[operator]


def build(site_url: str = DEFAULT_SITE_URL) -> None:
    site_url = valid_site_url(site_url)
    if DIST.is_symlink() or DIST.resolve().parent != ROOT.resolve():
        raise ValueError("dist must be a real child directory of the repository root")
    if DIST.exists():
        shutil.rmtree(DIST, onexc=_remove_readonly)
    DIST.mkdir()

    for relative_path in PUBLIC_FILES + PUBLIC_ASSETS:
        source = ROOT / relative_path
        if not source.is_file():
            raise FileNotFoundError(f"required public file is missing: {relative_path}")
        destination = DIST / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    page = DIST / "index.html"
    page.write_text(_set_site_meta(page.read_text(encoding="utf-8"), site_url), encoding="utf-8")
    _write_robots_and_sitemap(site_url)
    print(f"Built static site at {DIST}")
    print(f"Site URL: {site_url}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-url", type=valid_site_url, default=DEFAULT_SITE_URL, help="verified HTTPS site URL, with an optional base path")
    args = parser.parse_args()
    build(args.site_url)


if __name__ == "__main__":
    main()
