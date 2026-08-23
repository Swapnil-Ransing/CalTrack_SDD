"""Session glue: cookie-backed login persisted across reruns/refreshes (phase 02).

This is the only module that touches `st.session_state["user"]` or the cookie manager for
auth purposes — pages call `require_auth()` / `login_user()` / `logout_user()` and never
touch tokens or cookies directly.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import extra_streamlit_components as stx
import streamlit as st

from core.db import get_session
from models.user import User
from services import user_service
from services.auth_service import (
    SESSION_TOKEN_MAX_AGE_SECONDS,
    create_session_token,
    verify_session_token,
)

_COOKIE_NAME = "healthtracker_session"
_COOKIE_MANAGER_KEY = "healthtracker_auth_cookie_manager"


def _cookie_manager() -> stx.CookieManager:
    # CookieManager() re-registers its component under `key` on every construction
    # (fetching all cookies each time), so it must be instantiated at most once per
    # session — a second construction in the same script run raises
    # StreamlitDuplicateElementKey. Cache it in session_state instead of module scope,
    # since module state would otherwise leak across different users' sessions.
    if "_auth_cookie_manager" not in st.session_state:
        st.session_state["_auth_cookie_manager"] = stx.CookieManager(key=_COOKIE_MANAGER_KEY)
    manager: stx.CookieManager = st.session_state["_auth_cookie_manager"]
    return manager


def get_current_user() -> User | None:
    cached = st.session_state.get("user")
    if cached is not None:
        return cached

    if st.session_state.get("_explicitly_logged_out"):
        # Just called logout_user() this session. Its cookie deletion is a browser-side
        # side effect that the *same* cached "get_all" component value won't reflect on
        # an immediate rerun (components only refresh when the frontend reports back, not
        # synchronously on Python's next call) — without this, re-checking the cookie
        # right after logout would read the still-stale value and silently log the user
        # back in. A genuinely fresh page load starts a new session without this flag, so
        # it correctly re-checks the (by then really-updated) browser cookie.
        return None

    # .get_all() re-invokes the component (under its own stable "get_all" key) and
    # returns whatever the frontend most recently reported. .get() instead reads
    # self.cookies, a dict populated once at construction time and never refreshed —
    # on the first rerun after a fresh page load that's still the {} default (the
    # frontend hasn't responded yet), so it would permanently look logged-out for the
    # rest of the session even after the real cookie value arrives.
    token = _cookie_manager().get_all().get(_COOKIE_NAME)
    if not token:
        # Either genuinely logged out, or the cookie component hasn't reported back yet
        # on this first rerun — both cases correctly resolve to "not logged in" for now;
        # Streamlit automatically reruns once the frontend's real value arrives.
        return None

    user_id = verify_session_token(token)
    if user_id is None:
        return None

    db_session = get_session()
    try:
        user = user_service.get_user_by_id(db_session, user_id)
    finally:
        db_session.close()

    if user is not None:
        st.session_state["user"] = user
    return user


def login_user(user: User) -> None:
    st.session_state["user"] = user
    st.session_state["_explicitly_logged_out"] = False
    token = create_session_token(user.id)
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=SESSION_TOKEN_MAX_AGE_SECONDS)
    _cookie_manager().set(_COOKIE_NAME, token, expires_at=expires_at)


def logout_user() -> None:
    st.session_state["user"] = None
    st.session_state["_explicitly_logged_out"] = True
    manager = _cookie_manager()
    # CookieManager.delete() does `del self.cookies[cookie]`, which raises KeyError if
    # that cookie was never fetched into its local dict — e.g. a session restored purely
    # from the session_state cache (get_current_user()'s fast path) never calls
    # .get_all() first. Calling it here guarantees the dict is populated before deleting.
    if _COOKIE_NAME in manager.get_all():
        manager.delete(_COOKIE_NAME)


def require_auth() -> User:
    user = get_current_user()
    if user is None:
        st.info("Please log in to continue.")
        st.stop()
    return user
