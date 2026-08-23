from datetime import date

import streamlit as st
from pydantic import ValidationError

from core.auth import get_current_user, login_user, logout_user
from core.db import get_session
from models.user import ActivityLevel, Goal, Sex, User
from schemas.user import UserLogin, UserSignup
from services.user_service import EmailAlreadyRegisteredError, authenticate_user, create_user

st.set_page_config(page_title="HealthTracker", page_icon="🎙️", layout="centered")


def _show_validation_errors(exc: ValidationError) -> None:
    for error in exc.errors():
        field = error["loc"][0] if error["loc"] else "form"
        st.error(f"{field}: {error['msg']}")


def _render_home(user: User) -> None:
    st.title("HealthTracker")
    st.write(f"Welcome back, **{user.email}**!")
    st.caption("A voice-first tracker for calories, water, weight, and activity.")
    if st.button("Log out", key="logout_button"):
        logout_user()
        st.rerun()


def _render_login_tab() -> None:
    with st.form("login_form"):
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        submitted = st.form_submit_button("Log in")

    if not submitted:
        return

    try:
        data = UserLogin(email=email, password=password)
    except ValidationError as exc:
        _show_validation_errors(exc)
        return

    db_session = get_session()
    try:
        authenticated = authenticate_user(db_session, data)
    finally:
        db_session.close()

    if authenticated is None:
        st.error("Invalid email or password.")
        return

    login_user(authenticated)
    st.rerun()


def _render_signup_tab() -> None:
    with st.form("signup_form"):
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")
        password_confirm = st.text_input(
            "Confirm password", type="password", key="signup_password_confirm"
        )
        date_of_birth = st.date_input(
            "Date of birth",
            value=date(2000, 1, 1),
            min_value=date(1900, 1, 1),
            max_value=date.today(),
            key="signup_dob",
        )
        sex = st.selectbox(
            "Sex", options=list(Sex), format_func=lambda s: s.value.title(), key="signup_sex"
        )
        height_cm = st.number_input(
            "Height (cm)", min_value=1.0, max_value=300.0, value=170.0, key="signup_height"
        )
        weight_kg = st.number_input(
            "Weight (kg)", min_value=1.0, max_value=400.0, value=70.0, key="signup_weight"
        )
        activity_level = st.selectbox(
            "Activity level",
            options=list(ActivityLevel),
            format_func=lambda a: a.value.replace("_", " ").title(),
            key="signup_activity",
        )
        goal = st.selectbox(
            "Goal",
            options=list(Goal),
            format_func=lambda g: g.value.replace("_", " ").title(),
            key="signup_goal",
        )
        submitted = st.form_submit_button("Sign up")

    if not submitted:
        return

    try:
        data = UserSignup(
            email=email,
            password=password,
            password_confirm=password_confirm,
            date_of_birth=date_of_birth,
            sex=sex,
            height_cm=height_cm,
            weight_kg=weight_kg,
            activity_level=activity_level,
            goal=goal,
        )
    except ValidationError as exc:
        _show_validation_errors(exc)
        return

    db_session = get_session()
    try:
        created = create_user(db_session, data)
    except EmailAlreadyRegisteredError:
        st.error("An account with this email already exists.")
        return
    finally:
        db_session.close()

    login_user(created)
    st.rerun()


def _render_auth_gate() -> None:
    st.title("HealthTracker")
    st.write("A voice-first tracker for calories, water, weight, and activity.")

    login_tab, signup_tab = st.tabs(["Log in", "Sign up"])
    with login_tab:
        _render_login_tab()
    with signup_tab:
        _render_signup_tab()


current_user = get_current_user()
if current_user is not None:
    _render_home(current_user)
else:
    _render_auth_gate()
