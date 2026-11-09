import json
import unittest
from datetime import date
from io import BytesIO
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

from main import (
    MAX_GENERATION_TOKENS,
    MAX_GENERATED_POST_LENGTH,
    OPENROUTER_CHAT_COMPLETIONS_URL,
    OPENROUTER_MODEL,
    generate_post,
)


class OpenRouterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.api_key = "test-api-key"
        self.today = date(2026, 11, 8)

    @staticmethod
    def openrouter_response(content: str) -> MagicMock:
        response = MagicMock()
        response.__enter__.return_value = BytesIO(
            json.dumps({"choices": [{"message": {"content": content}}]}).encode(
                "utf-8"
            )
        )
        return response

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
    def test_generate_post_retries_oversized_post(self, mock_urlopen) -> None:
        mock_urlopen.side_effect = [
            self.openrouter_response("ก" * 304),
            self.openrouter_response("โพสต์ฉบับย่อ"),
        ]

        self.assertEqual(
            generate_post(self.api_key, "technology", self.today), "โพสต์ฉบับย่อ"
        )
        self.assertEqual(mock_urlopen.call_count, 2)
        retry_payload = json.loads(mock_urlopen.call_args.args[0].data)
        self.assertEqual(retry_payload["messages"][-1]["role"], "user")
        self.assertIn(
            str(MAX_GENERATED_POST_LENGTH),
            retry_payload["messages"][-1]["content"],
        )

    @patch("main.urlopen")
    def test_generate_post_rejects_oversized_post_after_retry(self, mock_urlopen) -> None:
        mock_urlopen.side_effect = [
            self.openrouter_response("ก" * 281),
            self.openrouter_response("ข" * 281),
        ]

        with self.assertRaisesRegex(ValueError, "after 2 attempts"):
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
