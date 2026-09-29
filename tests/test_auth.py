"""Security boundary tests for local OAuth callback parsing."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


AUTH = (
    Path(__file__).resolve().parents[1]
    / "plugins"
    / "baidu-netdisk-codex"
    / "scripts"
    / "auth.py"
)
spec = importlib.util.spec_from_file_location("baidu_auth", AUTH)
auth = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(auth)


class OAuthParsingTests(unittest.TestCase):
    token = "123.sample-token.example_abcdefghijklmnopqrstuvwxyz"

    def test_official_callback_fragment(self) -> None:
        callback = (
            "https://openapi.baidu.com/oauth/2.0/login_success"
            f"#expires_in=2592000&access_token={self.token}&scope=basic+netdisk"
        )
        self.assertEqual(auth.extract_token(callback), self.token)
        self.assertEqual(
            auth.extract_token(callback, official_url_only=True), self.token
        )

    def test_rejects_lookalike_hosts_and_insecure_links(self) -> None:
        for callback in (
            f"https://openapi.baidu.com.evil.example/oauth/2.0/login_success#access_token={self.token}",
            f"https://openapi.baidu.com@evil.example/oauth/2.0/login_success#access_token={self.token}",
            f"http://openapi.baidu.com/oauth/2.0/login_success#access_token={self.token}",
            f"https://openapi.baidu.com/oauth/2.0/other#access_token={self.token}",
        ):
            with self.subTest(callback=callback):
                self.assertEqual(auth.extract_token(callback), "")

    def test_raw_token_only_in_manual_mode(self) -> None:
        self.assertEqual(auth.extract_token(self.token), self.token)
        self.assertEqual(
            auth.extract_token(self.token, official_url_only=True), ""
        )
        self.assertEqual(auth.extract_token("not a token"), "")

    def test_authorization_url_is_official(self) -> None:
        url = auth.authorization_url("exampleClientId")
        self.assertTrue(url.startswith("https://openapi.baidu.com/oauth/2.0/authorize?"))
        self.assertIn("client_id=exampleClientId", url)
        self.assertIn("redirect_uri=oob", url)


if __name__ == "__main__":
    unittest.main()
