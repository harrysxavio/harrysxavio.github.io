#!/usr/bin/env python3
"""Serve a loopback-only editor for the canonical portfolio content."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import build_site

CONTENT_FILE = ROOT / "content" / "site.json"
EDITOR_DIR = ROOT / "tools" / "content-editor"
MAX_BODY_BYTES = 1_000_000
SAVE_LOCK = threading.Lock()
ASSETS = {
    "/": (EDITOR_DIR / "index.html", "text/html; charset=utf-8"),
    "/app.js": (EDITOR_DIR / "app.js", "text/javascript; charset=utf-8"),
    "/app.css": (EDITOR_DIR / "app.css", "text/css; charset=utf-8"),
}
PUBLIC_EXTENSIONS = {".html", ".svg", ".webp", ".avif", ".jpg", ".jpeg", ".png", ".pdf"}


def _atomic_write(path: Path, content: bytes, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        if mode is not None:
            os.chmod(temporary, stat.S_IMODE(mode))
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _verified_generated_target(path: Path, root: Path, allow_leaf_link: bool = False) -> Path:
    root = root.resolve()
    target = path.absolute()
    if not target.is_relative_to(root) or target == root:
        raise ValueError("La ruta generada debe permanecer dentro del repositorio.")
    cursor = target
    while cursor != root:
        is_link = cursor.is_symlink() or (hasattr(cursor, "is_junction") and cursor.is_junction())
        if is_link and not (allow_leaf_link and cursor == target):
            raise ValueError("No se pueden guardar cambios si una ruta generada es un enlace.")
        cursor = cursor.parent
    is_leaf_link = target.is_symlink() or (hasattr(target, "is_junction") and target.is_junction())
    if not (allow_leaf_link and is_leaf_link) and not target.resolve(strict=False).is_relative_to(root):
        raise ValueError("La ruta generada resuelve fuera del repositorio.")
    return target


def _snapshot_generated_outputs(dist_snapshot: Path) -> tuple[dict[str, tuple[bytes, int] | None], bool]:
    root = build_site.ROOT.resolve()
    source_pages: dict[str, tuple[bytes, int] | None] = {}
    for route in sorted(build_site.REQUIRED_GENERATED_ROUTES):
        relative = Path(route)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("La lista de páginas generadas contiene una ruta insegura.")
        target = _verified_generated_target(root / relative, root)
        if target.exists():
            if not target.is_file():
                raise ValueError(f"La página generada no es un archivo regular: {route}")
            source_pages[route] = (target.read_bytes(), target.stat().st_mode)
        else:
            source_pages[route] = None

    dist = _verified_generated_target(build_site.DIST, root)
    if dist != root / "dist":
        raise ValueError("La salida dist debe ser el directorio generado del repositorio.")
    if not dist.exists():
        return source_pages, False
    if not dist.is_dir():
        raise ValueError("La salida dist debe ser un directorio regular.")
    for child in dist.rglob("*"):
        if child.is_symlink() or (hasattr(child, "is_junction") and child.is_junction()):
            raise ValueError("No se puede guardar si dist contiene enlaces de directorio o archivo.")
        if not child.resolve(strict=False).is_relative_to(root):
            raise ValueError("Una ruta de dist resuelve fuera del repositorio.")
    shutil.copytree(dist, dist_snapshot, copy_function=shutil.copy2)
    return source_pages, True


def _restore_generated_outputs(
    source_pages: dict[str, tuple[bytes, int] | None],
    dist_snapshot: Path,
    dist_existed: bool,
) -> None:
    root = build_site.ROOT.resolve()
    for route, snapshot in source_pages.items():
        target = _verified_generated_target(root / route, root, allow_leaf_link=True)
        if snapshot is None:
            if target.is_symlink() or (hasattr(target, "is_junction") and target.is_junction()):
                target.unlink()
            elif target.exists():
                if not target.is_file():
                    raise ValueError(f"No se puede retirar una salida inesperada: {route}")
                target.unlink()
        else:
            _atomic_write(target, snapshot[0], snapshot[1])

    dist = _verified_generated_target(build_site.DIST, root, allow_leaf_link=True)
    if dist != root / "dist":
        raise ValueError("La salida dist dejó de ser una ruta generada segura.")
    if dist.is_symlink() or (hasattr(dist, "is_junction") and dist.is_junction()):
        dist.unlink()
    elif dist.exists():
        if dist.is_dir():
            shutil.rmtree(dist)
        else:
            dist.unlink()
    if dist_existed:
        shutil.copytree(dist_snapshot, dist, copy_function=shutil.copy2)


def save_content(payload: object, build_fn=build_site.build) -> None:
    """Validate, save, and rebuild; restore source and generated outputs on failure."""
    if not isinstance(payload, dict):
        raise ValueError("El contenido debe ser un objeto JSON.")
    serialized = (json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8")
    build_site._validate_rendered_urls(payload)
    with SAVE_LOCK:
        original = CONTENT_FILE.read_bytes()
        source_mode = CONTENT_FILE.stat().st_mode
        with tempfile.TemporaryDirectory(prefix="portfolio-editor-") as temporary_directory:
            dist_snapshot = Path(temporary_directory) / "dist-snapshot"
            generated_snapshot, dist_existed = _snapshot_generated_outputs(dist_snapshot)
            try:
                _atomic_write(CONTENT_FILE, serialized, source_mode)
                build_site._load_content()
                build_fn()
            except Exception:
                _restore_generated_outputs(generated_snapshot, dist_snapshot, dist_existed)
                _atomic_write(CONTENT_FILE, original, source_mode)
                raise


class EditorHandler(BaseHTTPRequestHandler):
    server_version = "PortfolioEditor/1.0"

    def log_message(self, format: str, *args: object) -> None:
        print(f"[editor] {self.address_string()} {format % args}")

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, data: object) -> None:
        body = json.dumps(data, ensure_ascii=False, allow_nan=False).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8")

    def _host_is_local(self) -> bool:
        expected_port = self.server.server_port
        return self.headers.get("Host", "").lower() in {
            f"127.0.0.1:{expected_port}", f"localhost:{expected_port}"
        }

    def _origin_is_local(self) -> bool:
        origin = self.headers.get("Origin")
        if origin is None:
            return False
        parsed = urlsplit(origin)
        return (parsed.scheme == "http" and parsed.hostname in {"127.0.0.1", "localhost"}
                and parsed.port == self.server.server_port and not parsed.path and not parsed.query and not parsed.fragment)

    def do_GET(self) -> None:
        if not self._host_is_local():
            self._json(403, {"error": "Acceso local rechazado."})
            return
        path = unquote(urlsplit(self.path).path)
        if path == "/api/content":
            try:
                self._json(200, json.loads(CONTENT_FILE.read_text(encoding="utf-8")))
            except (OSError, json.JSONDecodeError):
                self._json(500, {"error": "No se pudo leer el contenido del sitio."})
            return
        asset = ASSETS.get(path)
        if asset is None:
            self._json(404, {"error": "No encontrado."})
            return
        source, content_type = asset
        try:
            self._send(200, source.read_bytes(), content_type)
        except OSError:
            self._json(500, {"error": "No se pudo cargar el editor."})

    def do_POST(self) -> None:
        if not self._host_is_local() or not self._origin_is_local():
            self._json(403, {"error": "El editor solo acepta cambios desde esta sesión local."})
            return
        if urlsplit(self.path).path != "/api/save":
            self._json(404, {"error": "No encontrado."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._json(400, {"error": "Tamaño de solicitud inválido."})
            return
        if length <= 0 or length > MAX_BODY_BYTES:
            self._json(413, {"error": "El contenido supera el tamaño permitido o está vacío."})
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            save_content(payload)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            self._json(400, {"error": f"JSON inválido: {exc}"})
        except Exception as exc:
            self._json(422, {"error": str(exc)})
        else:
            self._json(200, {"saved": True, "message": "Cambios guardados y vista previa reconstruida."})


class PreviewHandler(SimpleHTTPRequestHandler):
    """Serve only generated public website assets from the loopback preview port."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def translate_path(self, path: str) -> str:
        request_path = unquote(urlsplit(path).path).lstrip("/")
        if not request_path:
            request_path = "index.html"
        if request_path.endswith("/"):
            request_path += "index.html"
        relative = Path(request_path)
        if relative.is_absolute() or ".." in relative.parts:
            return str(ROOT / "__not_found__")
        first = relative.parts[0] if relative.parts else ""
        allowed = (len(relative.parts) == 1 and first in build_site.PUBLIC_ROOT_FILES)
        allowed = allowed or (first in build_site.PUBLIC_DIRECTORIES and relative.suffix.lower() in PUBLIC_EXTENSIONS)
        candidate = (ROOT / relative).resolve()
        if not allowed or not candidate.is_relative_to(ROOT.resolve()) or not candidate.is_file():
            return str(ROOT / "__not_found__")
        return str(candidate)

    def list_directory(self, path: str) -> None:
        self.send_error(404, "Not found")

    def do_GET(self) -> None:
        expected = f"127.0.0.1:{self.server.server_port}"
        if self.headers.get("Host", "").lower() not in {expected, f"localhost:{self.server.server_port}"}:
            self.send_error(403, "Local preview only")
            return
        super().do_GET()

    def log_message(self, format: str, *args: object) -> None:
        print(f"[preview] {self.address_string()} {format % args}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the local portfolio content editor.")
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--preview-port", type=int, default=8767)
    args = parser.parse_args()
    preview = ThreadingHTTPServer(("127.0.0.1", args.preview_port), PreviewHandler)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), EditorHandler)
    preview_thread = threading.Thread(target=preview.serve_forever, name="site-preview", daemon=True)
    preview_thread.start()
    print(f"Editor local: http://127.0.0.1:{args.port}/")
    print(f"Vista previa: http://127.0.0.1:{args.preview_port}/ (Ctrl+C para cerrar ambos)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nEditor cerrado.")
    finally:
        server.server_close()
        preview.shutdown()
        preview.server_close()


if __name__ == "__main__":
    main()
