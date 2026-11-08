import json
import unittest
from datetime import date
from io import BytesIO
from unittest.mock import patch
from urllib.error import HTTPError

from main import (
    OPENROUTER_CHAT_COMPLETIONS_URL,
    MAX_GENERATION_TOKENS,
    OPENROUTER_MODEL,
    generate_post,
)


class OpenRouterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.api_key = "test-api-key"
        self.today = date(2026, 11, 8)

    @patch("main.urlopen")
    def test_generate_post_uses_openrouter_and_returns_text(self, mock_urlopen) -> None:
        mock_response = BytesIO(
            json.dumps(
                {"choices": [{"message": {"content": "โพสต์ตัวอย่าง #AI"}}]}
            ).encode("utf-8")
        )
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = generate_post(self.api_key, "technology", self.today)

        self.assertEqual(result, "โพสต์ตัวอย่าง #AI")
        request = mock_urlopen.call_args.args[0]
        self.assertEqual(request.full_url, OPENROUTER_CHAT_COMPLETIONS_URL)
        self.assertEqual(request.get_header("Authorization"), f"Bearer {self.api_key}")
        payload = json.loads(request.data)
        self.assertEqual(payload["model"], OPENROUTER_MODEL)
        self.assertEqual(payload["max_tokens"], MAX_GENERATION_TOKENS)
        self.assertEqual(payload["messages"][0]["role"], "user")

    @patch("main.urlopen")
    def test_generate_post_rejects_empty_response(self, mock_urlopen) -> None:
        mock_response = BytesIO(
            json.dumps({"choices": [{"message": {"content": "  "}}]}).encode("utf-8")
        )
        mock_urlopen.return_value.__enter__.return_value = mock_response

        with self.assertRaisesRegex(ValueError, "empty post"):
            generate_post(self.api_key, "technology", self.today)

    @patch("main.urlopen")
    def test_generate_post_extracts_text_from_content_parts(self, mock_urlopen) -> None:
        mock_response = BytesIO(
            json.dumps(
                {
                    "choices": [
                        {
                            "message": {
                                "content": [
                                    {"type": "text", "text": "โพสต์ "},
                                    {"type": "text", "text": "ตัวอย่าง #AI"},
                                ]
                            }
                        }
                    ]
                }
            ).encode("utf-8")
        )
        mock_urlopen.return_value.__enter__.return_value = mock_response

        self.assertEqual(
            generate_post(self.api_key, "technology", self.today),
            "โพสต์ ตัวอย่าง #AI",
        )

    @patch("main.urlopen")
    def test_missing_text_includes_safe_response_diagnostics(self, mock_urlopen) -> None:
        mock_response = BytesIO(
            json.dumps(
                {
                    "model": "provider/model",
                    "choices": [
                        {
                            "message": {"content": None, "refusal": "blocked"},
                            "finish_reason": "stop",
                        }
                    ],
                }
            ).encode("utf-8")
        )
        mock_urlopen.return_value.__enter__.return_value = mock_response

        with self.assertRaisesRegex(
            RuntimeError, r"model=provider/model, finish_reason=stop"
        ):
            generate_post(self.api_key, "technology", self.today)

    @patch("main.urlopen")
    def test_generate_post_rejects_posts_over_x_limit(self, mock_urlopen) -> None:
        mock_response = BytesIO(
            json.dumps(
                {"choices": [{"message": {"content": "ก" * 281}}]}
            ).encode("utf-8")
        )
        mock_urlopen.return_value.__enter__.return_value = mock_response

        with self.assertRaisesRegex(ValueError, "281 characters"):
            generate_post(self.api_key, "technology", self.today)

    @patch("main.urlopen")
    def test_http_error_does_not_expose_api_key(self, mock_urlopen) -> None:
        mock_urlopen.side_effect = HTTPError(
            OPENROUTER_CHAT_COMPLETIONS_URL,
            401,
            "Unauthorized",
            hdrs=None,
            fp=BytesIO(
                json.dumps({"error": {"message": self.api_key}}).encode("utf-8")
            ),
        )

        with self.assertRaisesRegex(RuntimeError, r"HTTP 401") as context:
            generate_post(self.api_key, "technology", self.today)
        self.assertNotIn(self.api_key, str(context.exception))

    @patch("main.urlopen")
    def test_unknown_topic_is_rejected_without_api_call(self, mock_urlopen) -> None:
        with self.assertRaisesRegex(ValueError, "Unknown content topic"):
            generate_post(self.api_key, "unknown", self.today)
        mock_urlopen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
