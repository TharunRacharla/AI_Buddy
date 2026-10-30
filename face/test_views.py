from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from .slm import ChatGenerationError


@override_settings(SECURE_SSL_REDIRECT=False)
class ChatViewTests(SimpleTestCase):
    @patch("face.views.generate_reply", return_value="Hello!")
    def test_chat_returns_generated_reply(self, generate_reply):
        response = self.client.post(
            "/api/chat/",
            data='{"message":"Hello"}',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"reply": "Hello!", "tool_used": None})
        generate_reply.assert_called_once_with("Hello")

    def test_chat_rejects_invalid_json(self):
        response = self.client.post(
            "/api/chat/",
            data="{",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_chat_rejects_empty_message(self):
        response = self.client.post(
            "/api/chat/",
            data='{"message":"  "}',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_chat_rejects_oversized_message(self):
        response = self.client.post(
            "/api/chat/",
            data='{"message":"' + ("a" * 501) + '"}',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    @patch(
        "face.views.generate_reply",
        side_effect=ChatGenerationError("model unavailable"),
    )
    def test_chat_reports_generation_failure(self, _generate_reply):
        response = self.client.post(
            "/api/chat/",
            data='{"message":"Hello"}',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 503)

    def test_chat_rejects_non_post_requests(self):
        response = self.client.get("/api/chat/")

        self.assertEqual(response.status_code, 405)
