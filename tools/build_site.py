#!/usr/bin/env python3
"""Build the allowlisted static profile into dist."""

from __future__ import annotations

import argparse
import os
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


def build(site_url: str = DEFAULT_SITE_URL) -> None:
    site_url = valid_site_url(site_url)
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
