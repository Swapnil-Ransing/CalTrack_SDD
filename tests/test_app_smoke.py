"""Smoke test: app.py boots without raising, and the theme/page config apply."""

from __future__ import annotations

from streamlit.testing.v1 import AppTest


def test_app_boots_without_exception() -> None:
    at = AppTest.from_file("../app.py")
    at.run()

    assert not at.exception


def test_app_renders_title_and_description() -> None:
    at = AppTest.from_file("../app.py")
    at.run()

    assert at.title[0].value == "HealthTracker"
    assert "voice-first" in at.markdown[0].value
