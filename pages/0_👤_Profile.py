from datetime import date

import streamlit as st
from pydantic import ValidationError

from core.auth import logout_user, require_auth
from core.db import get_session
from models.user import ActivityLevel, Goal, Sex
from schemas.user import UserProfileUpdate
from services.user_service import EmailAlreadyRegisteredError, update_profile

st.set_page_config(page_title="Profile — HealthTracker", page_icon="👤", layout="centered")

user = require_auth()

st.title("Your profile")

if st.button("Log out", key="logout_button"):
    logout_user()
    st.rerun()

with st.form("profile_form"):
    email = st.text_input("Email", value=user.email, key="profile_email")
    date_of_birth = st.date_input(
        "Date of birth",
        value=user.date_of_birth,
        min_value=date(1900, 1, 1),
        max_value=date.today(),
        key="profile_dob",
    )
    sex = st.selectbox(
        "Sex",
        options=list(Sex),
        index=list(Sex).index(user.sex),
        format_func=lambda s: s.value.title(),
        key="profile_sex",
    )
    height_cm = st.number_input(
        "Height (cm)",
        min_value=1.0,
        max_value=300.0,
        value=float(user.height_cm),
        key="profile_height",
    )
    weight_kg = st.number_input(
        "Weight (kg)",
        min_value=1.0,
        max_value=400.0,
        value=float(user.weight_kg),
        key="profile_weight",
    )
    activity_level = st.selectbox(
        "Activity level",
        options=list(ActivityLevel),
        index=list(ActivityLevel).index(user.activity_level),
        format_func=lambda a: a.value.replace("_", " ").title(),
        key="profile_activity",
    )
    goal = st.selectbox(
        "Goal",
        options=list(Goal),
        index=list(Goal).index(user.goal),
        format_func=lambda g: g.value.replace("_", " ").title(),
        key="profile_goal",
    )
    submitted = st.form_submit_button("Save changes")

if submitted:
    try:
        data = UserProfileUpdate(
            email=email,
            date_of_birth=date_of_birth,
            sex=sex,
            height_cm=height_cm,
            weight_kg=weight_kg,
            activity_level=activity_level,
            goal=goal,
        )
    except ValidationError as exc:
        for error in exc.errors():
            field = error["loc"][0] if error["loc"] else "form"
            st.error(f"{field}: {error['msg']}")
    else:
        db_session = get_session()
        try:
            updated_user = update_profile(db_session, user.id, data)
        except EmailAlreadyRegisteredError:
            st.error("An account with this email already exists.")
        else:
            st.session_state["user"] = updated_user
            st.success("Profile updated.")
            st.rerun()
        finally:
            db_session.close()
