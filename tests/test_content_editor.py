import json
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
        self.path_patch = patch.multiple(
            content_editor,
            CONTENT_FILE=self.content_path,
        )
        self.path_patch.start()
        self.builder_path_patch = patch.object(build_site, "CONTENT_FILE", self.content_path)
        self.builder_path_patch.start()

    def tearDown(self):
        self.builder_path_patch.stop()
        self.path_patch.stop()
        self.temporary_directory.cleanup()

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


if __name__ == "__main__":
    unittest.main()
