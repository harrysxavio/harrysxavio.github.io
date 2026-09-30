#!/usr/bin/env python3
"""Build a deployable static site, optionally adding metadata for a verified origin."""

from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
ORIGIN_MARKER = "<!-- Canonical and absolute social metadata are added by tools/build_site.py when a verified site origin is supplied. -->"


def valid_origin(value: str) -> str:
    parsed = urlparse(value)
    host = parsed.hostname or ""
    try:
        port = parsed.port
    except ValueError as exc:
        raise argparse.ArgumentTypeError("site origin contains an invalid port") from exc
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
        or not re.fullmatch(r"[A-Za-z0-9.-]+", host)
        or parsed.path not in ("", "/")
        or parsed.query
        or parsed.fragment
        or (port is not None and not 1 <= port <= 65535)
    ):
        raise argparse.ArgumentTypeError("site origin must be an HTTPS origin, for example https://example.com")
    return value.rstrip("/")


def build(origin: str | None) -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(ROOT, DIST, ignore=shutil.ignore_patterns(".git", ".codegraph", "dist", "__pycache__"))

    page = DIST / "index.html"
    html = page.read_text(encoding="utf-8")
    schema_start = '<script type="application/ld+json">'
    schema_end = "</script>"
    start = html.index(schema_start) + len(schema_start)
    end = html.index(schema_end, start)
    profile = json.loads(html[start:end])

    if origin:
        canonical = f'<link rel="canonical" href="{origin}/">\n'
        absolute_image = f"{origin}/assets/operations-transformation-illustration.png"
        social = (
            f'<meta property="og:url" content="{origin}/">\n'
            f'<meta property="og:image" content="{absolute_image}">\n'
            '<meta name="twitter:card" content="summary_large_image">\n'
        )
        html = html.replace(ORIGIN_MARKER, canonical + social)
        profile["url"] = f"{origin}/"
        profile["mainEntity"]["url"] = f"{origin}/"
        start = html.index(schema_start) + len(schema_start)
        end = html.index(schema_end, start)
        html = html[:start] + "\n      " + json.dumps(profile, ensure_ascii=False, indent=2) + "\n    " + html[end:]
        sitemap = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
        ET.SubElement(sitemap, "url").append(ET.Element("loc"))
        sitemap.find("url/loc").text = f"{origin}/"
        ET.ElementTree(sitemap).write(DIST / "sitemap.xml", encoding="utf-8", xml_declaration=True)
        robots = DIST / "robots.txt"
        robots.write_text(f"User-agent: *\nAllow: /\nSitemap: {origin}/sitemap.xml\n", encoding="utf-8")
    else:
        html = html.replace(ORIGIN_MARKER, "")

    page.write_text(html, encoding="utf-8")
    print(f"Built static site at {DIST}")
    print(f"Site origin: {origin if origin else 'not configured; absolute metadata and sitemap URLs omitted'}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-origin", type=valid_origin, help="verified production HTTPS origin")
    args = parser.parse_args()
    build(args.site_origin)


if __name__ == "__main__":
    main()
