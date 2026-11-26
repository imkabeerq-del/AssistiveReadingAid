import importlib
import streamlit as st

from db import get_user_from_session_token
from login import login_page
from register import register_page
from utils import apply_theme, navbar

st.set_page_config(
    page_title="Assistive Reading Aid",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PAGE_MODULES = {
    "Dashboard": ("app_pages.1_Dashboard", "dashboard_page"),
    "ReadingAid": ("app_pages.2_ReadingAid", "reading_aid_page"),
    "Awareness": ("app_pages.3_Awareness", "awareness_page"),
    "Tips": ("app_pages.4_Tips", "tips_page"),
    "Profile": ("app_pages.5_Profile", "profile_page"),
    "Admin": ("app_pages.6_Admin", "admin_page"),
    "ForgotPassword": ("app_pages.7_ForgotPassword", "forgot_password_page"),
}


def _check_session_persistence() -> None:
    if st.session_state.get("logged_in", False):
        return

    query_token = st.query_params.get("auth_token")
    if query_token and len(query_token) == 64:
        user = get_user_from_session_token(query_token)
        if user:
            st.session_state["logged_in"] = True
            st.session_state["username"] = user[1]
            st.session_state["role"] = user[3]
            st.session_state["session_token"] = query_token
            st.session_state["page"] = "Dashboard"
            st.rerun()


def main() -> None:
    apply_theme()
    _check_session_persistence()

    page = st.session_state.get("page", "Login")

    if page == "Login":
        login_page()
    elif page == "Register":
        register_page()
    else:
        if not st.session_state.get("logged_in", False) and page != "ForgotPassword":
            login_page()
            return

        if st.session_state.get("logged_in", False):
            navbar()

        target = PAGE_MODULES.get(page)
        if target:
            module_name, func_name = target
            module = importlib.import_module(module_name)
            getattr(module, func_name)()
        else:
            st.error("Page not found.")


if __name__ == "__main__":
    main()