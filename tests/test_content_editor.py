import json
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import build_site, content_editor


class ContentEditorSaveTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.content_path = Path(self.temporary_directory.name) / "site.json"
        self.content_path.write_bytes((content_editor.ROOT / "content" / "site.json").read_bytes())
        self.original = self.content_path.read_bytes()
        self.source = json.loads(self.original)
        self.repo_root = Path(self.temporary_directory.name) / "repo"
        self.repo_root.mkdir()
        self.dist_path = self.repo_root / "dist"
        self.dist_path.mkdir()
        self.root_home = self.repo_root / "index.html"
        self.root_home.write_bytes(b"original root home")
        self.dist_home = self.dist_path / "index.html"
        self.dist_home.write_bytes(b"original dist home")
        self.path_patch = patch.multiple(
            content_editor,
            CONTENT_FILE=self.content_path,
        )
        self.path_patch.start()
        self.builder_path_patch = patch.object(build_site, "CONTENT_FILE", self.content_path)
        self.builder_path_patch.start()
        self.root_patch = patch.object(build_site, "ROOT", self.repo_root)
        self.root_patch.start()
        self.dist_patch = patch.object(build_site, "DIST", self.dist_path)
        self.dist_patch.start()

    def tearDown(self):
        self.builder_path_patch.stop()
        self.dist_patch.stop()
        self.root_patch.stop()
        self.path_patch.stop()
        self.temporary_directory.cleanup()

    def _secondary_project(self):
        selected_ids = set(self.source["home"]["selectedWork"]["projectIds"])
        return next(project for project in self.source["projects"]
                    if project.get("route") is None and not project["featured"]
                    and project["id"] not in selected_ids)

    def _validate_and_render_projects(self):
        data = build_site._load_content()
        return data, build_site._render_project_portfolio(data, build_site.DEFAULT_SITE_URL)

    def test_tenth_secondary_project_with_one_valid_tag_is_supported(self):
        added = copy.deepcopy(self._secondary_project())
        added.update({"id": "new-secondary-project", "title": "Proyecto secundario agregado",
                      "featured": False, "route": None,
                      "tags": [self.source["taxonomy"]["tags"][0]["id"]]})
        self.source["projects"].append(added)

        content_editor.save_content(self.source, build_fn=self._validate_and_render_projects)
        data, rendered = self._validate_and_render_projects()

        self.assertEqual(len(data["projects"]), 10)
        self.assertEqual(data["projects"][-1]["tags"], [self.source["taxonomy"]["tags"][0]["id"]])
        self.assertEqual(sum(project["featured"] for project in data["projects"]), 4)
        self.assertIn('data-project-id="new-secondary-project"', rendered)
        self.assertIn("Proyecto secundario agregado", rendered)

    def test_secondary_project_can_be_removed_without_changing_case_routes(self):
        removed = self._secondary_project()
        removed_id = removed["id"]
        expected_routes = {project["route"] for project in self.source["projects"] if project.get("route")}
        self.source["projects"].remove(removed)

        content_editor.save_content(self.source, build_fn=self._validate_and_render_projects)
        data, rendered = self._validate_and_render_projects()

        self.assertEqual(len(data["projects"]), 8)
        self.assertEqual({project["route"] for project in data["projects"] if project.get("route")}, expected_routes)
        self.assertEqual(sum(project["featured"] for project in data["projects"]), 4)
        self.assertNotIn(f'data-project-id="{removed_id}"', rendered)

    def test_unknown_project_tag_is_rejected(self):
        self.source["projects"][0]["tags"] = ["unknown-tag"]
        rebuild = unittest.mock.Mock()

        with self.assertRaisesRegex(ValueError, "unknown taxonomy IDs"):
            content_editor.save_content(self.source, build_fn=rebuild)

        self.assertEqual(self.content_path.read_bytes(), self.original)
        rebuild.assert_not_called()

    def test_four_existing_case_routes_cannot_be_removed_or_reassigned(self):
        original_route_set = {project["route"] for project in self.source["projects"] if project.get("route")}
        case = next(project for project in self.source["projects"] if project.get("route"))
        case["route"] = "/projects/new-route/"

        with self.assertRaisesRegex(ValueError, "preserve the four existing case routes"):
            content_editor.save_content(self.source, build_fn=unittest.mock.Mock())

        self.assertEqual(self.content_path.read_bytes(), self.original)
        self.assertEqual(len(original_route_set), 4)

    def test_valid_content_is_written_and_rebuilt(self):
        self.source["home"]["hero"]["thesis"] = "Entender lo complejo. Hacerlo funcionar mejor."
        rebuild = unittest.mock.Mock()

        content_editor.save_content(self.source, build_fn=rebuild)

        self.assertEqual(json.loads(self.content_path.read_text(encoding="utf-8")), self.source)
        rebuild.assert_called_once_with()

    def test_schema_failure_restores_original_source(self):
        self.source["site"]["language"] = ""

        with self.assertRaises(ValueError):
            content_editor.save_content(self.source, build_fn=unittest.mock.Mock())

        self.assertEqual(self.content_path.read_bytes(), self.original)

    def test_build_failure_restores_original_source(self):
        def fail_build():
            raise RuntimeError("build failed")

        with self.assertRaisesRegex(RuntimeError, "build failed"):
            content_editor.save_content(self.source, build_fn=fail_build)

        self.assertEqual(self.content_path.read_bytes(), self.original)

    def test_late_build_failure_restores_source_root_pages_and_entire_dist_tree(self):
        root_before = self.root_home.read_bytes()
        dist_before = {path.relative_to(self.dist_path).as_posix(): path.read_bytes()
                       for path in self.dist_path.rglob("*") if path.is_file()}

        def fail_after_mutating_outputs():
            self.root_home.write_bytes(b"partial root home")
            partial_page = self.repo_root / "projects" / "index.html"
            partial_page.parent.mkdir(parents=True)
            partial_page.write_bytes(b"partial generated source page")
            self.dist_home.write_bytes(b"partial dist home")
            (self.dist_path / "partial-generated-page.html").write_bytes(b"partial dist page")
            raise RuntimeError("late build failure")

        with self.assertRaisesRegex(RuntimeError, "late build failure"):
            content_editor.save_content(self.source, build_fn=fail_after_mutating_outputs)

        dist_after = {path.relative_to(self.dist_path).as_posix(): path.read_bytes()
                      for path in self.dist_path.rglob("*") if path.is_file()}
        self.assertEqual(self.content_path.read_bytes(), self.original)
        self.assertEqual(self.root_home.read_bytes(), root_before)
        self.assertFalse((self.repo_root / "projects" / "index.html").exists())
        self.assertEqual(dist_after, dist_before)

    def test_unsafe_rendered_urls_are_rejected_before_source_or_build_changes(self):
        mutations = [
            ("site.sameAs", lambda data: data["site"]["sameAs"].__setitem__(0, "javascript:alert(1)")),
            ("profile.cvPdfUrl", lambda data: data["profile"].__setitem__("cvPdfUrl", "javascript:alert(2)")),
            ("home action", lambda data: data["home"]["hero"]["actions"][0].__setitem__("href", "data:text/html,unsafe")),
            ("nested project link", lambda data: data["career"][0]["roles"][0]["projects"][0].__setitem__("href", "//evil.example/path")),
            ("control character", lambda data: data["home"]["hero"]["actions"][0].__setitem__("href", "/cv/\n")),
        ]
        for name, mutate in mutations:
            with self.subTest(name=name):
                payload = copy.deepcopy(self.source)
                mutate(payload)
                rebuild = unittest.mock.Mock()
                with self.assertRaises(ValueError):
                    content_editor.save_content(payload, build_fn=rebuild)
                self.assertEqual(self.content_path.read_bytes(), self.original)
                self.assertEqual(self.root_home.read_bytes(), b"original root home")
                self.assertEqual(self.dist_home.read_bytes(), b"original dist home")
                rebuild.assert_not_called()


if __name__ == "__main__":
    unittest.main()
