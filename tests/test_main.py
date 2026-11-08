import contextlib
import io
import unittest
from unittest.mock import patch

from main import main


class MainTests(unittest.TestCase):
    @patch("main.post_to_x")
    @patch("main.generate_post", return_value="โพสต์ตัวอย่าง")
    @patch("main.load_dotenv")
    @patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-key"}, clear=True)
    @patch("sys.argv", ["main.py", "--dry-run"])
    def test_dry_run_generates_post_without_x_credentials(
        self, mock_load_dotenv, mock_generate_post, mock_post_to_x
    ) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            main()

        self.assertIn("โพสต์ตัวอย่าง", output.getvalue())
        mock_load_dotenv.assert_called_once_with()
        mock_generate_post.assert_called_once()
        mock_post_to_x.assert_not_called()


if __name__ == "__main__":
    unittest.main()
