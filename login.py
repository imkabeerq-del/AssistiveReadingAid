import base64
import json
from pathlib import Path
import streamlit as st

from db import authenticate_user, create_session_token, init_db, load_profile

REMEMBER_FILE = Path(".remembered_login.json")


def _load_saved_login() -> tuple[str, str]:
    if not REMEMBER_FILE.exists():
        return "", ""
    try:
        data = json.loads(REMEMBER_FILE.read_text(encoding="utf-8"))
        u = data.get("u", "")
        p_b64 = data.get("p", "")
        p = base64.b64decode(p_b64.encode("utf-8")).decode("utf-8") if p_b64 else ""
        return u, p
    except Exception:
        return "", ""


def _save_login(username: str, password: str) -> None:
    try:
        payload = {
            "u": username,
            "p": base64.b64encode(password.encode("utf-8")).decode("utf-8"),
        }
        REMEMBER_FILE.write_text(json.dumps(payload), encoding="utf-8")
    except Exception:
        pass


def _clear_saved_login() -> None:
    try:
        if REMEMBER_FILE.exists():
            REMEMBER_FILE.unlink()
    except Exception:
        pass


def _get_user_field(user, index: int, key: str, default):
    if user is None:
        return default
    try:
        return user[key]
    except (KeyError, TypeError, IndexError):
        try:
            return user[index]
        except (IndexError, TypeError):
            return default


def login_page() -> None:
    init_db()

    saved_u, saved_p = _load_saved_login()
    st.session_state.setdefault("remembered_username", saved_u)
    st.session_state.setdefault("remembered_password", saved_p)
    st.session_state.setdefault("login_show_password", False)

    if "login_username_draft" not in st.session_state:
        st.session_state["login_username_draft"] = st.session_state.get("remembered_username", "")
    if "login_password_draft" not in st.session_state:
        st.session_state["login_password_draft"] = st.session_state.get("remembered_password", "")

    st.markdown(
        """
        <div class="auth-hero">
            <h2>Login & Access</h2>
            <p>Sign in with your username and password to continue.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        st.info("New users must **register once first** with a unique username before logging in.")

        username = st.text_input(
            "Username",
            value=st.session_state.get("login_username_draft", ""),
            key="login_username_input",
        )
        st.session_state["login_username_draft"] = username

        show_password = st.session_state.get("login_show_password", False)
        pw_col, show_col = st.columns([2.2, 1])
        with pw_col:
            password = st.text_input(
                "Password",
                type="default" if show_password else "password",
                value=st.session_state.get("login_password_draft", ""),
                key=f"login_password_input_{'plain' if show_password else 'masked'}",
            )
            st.session_state["login_password_draft"] = password
        with show_col:
            st.markdown("<div style='padding-top:26px;'></div>", unsafe_allow_html=True)
            toggled_show = st.checkbox(
                "Show password",
                value=show_password,
                key="login_show_password_checkbox",
            )
            if toggled_show != show_password:
                st.session_state["login_show_password"] = toggled_show
                st.rerun()

        rem_col, btn_col = st.columns([1.4, 1])
        with rem_col:
            remember_me = st.checkbox(
                "Remember me",
                value=bool(saved_u or saved_p or st.session_state.get("remembered_username")),
                key="login_remember_me",
            )
        with btn_col:
            login_clicked = st.button("Login", use_container_width=True, type="primary")

        if login_clicked:
            clean_username = username.strip()

            if not clean_username:
                st.error("Username is required.")
                return

            if not password:
                st.error("Password is required.")
                return

            user = authenticate_user(clean_username, password)

            if user:
                resolved_username = _get_user_field(user, 1, "username", clean_username)
                resolved_role = _get_user_field(user, 3, "role", "Student") or "Student"

                st.session_state["logged_in"] = True
                st.session_state["username"] = resolved_username
                st.session_state["role"] = resolved_role

                if remember_me:
                    st.session_state["remembered_username"] = resolved_username
                    st.session_state["remembered_password"] = password
                    st.session_state["login_username_draft"] = resolved_username
                    st.session_state["login_password_draft"] = password
                    _save_login(resolved_username, password)
                    token = create_session_token(resolved_username, resolved_role)
                    st.session_state["session_token"] = token
                    st.query_params["auth_token"] = token
                else:
                    st.session_state["remembered_username"] = ""
                    st.session_state["remembered_password"] = ""
                    st.session_state["login_username_draft"] = ""
                    st.session_state["login_password_draft"] = ""
                    st.session_state["session_token"] = ""
                    _clear_saved_login()
                    st.query_params.pop("auth_token", None)

                st.session_state["login_show_password"] = False

                try:
                    profile = load_profile(resolved_username)
                    st.session_state["dark_mode"] = profile.get("preferred_theme", "Dark") == "Dark"
                    st.session_state["reduced_motion"] = bool(profile.get("reduced_motion", False))
                    st.session_state["celebration_effects"] = bool(
                        profile.get("celebration_effects", True)
                    )
                except Exception:
                    st.session_state["dark_mode"] = True

                st.session_state["page"] = "Dashboard"
                st.rerun()
            else:
                st.error(
                    "Invalid username or password. If you do not have an account yet, register once first."
                )

        with st.expander("Password Format Guide"):
            st.caption("8+ characters, no spaces")
            st.caption("At least 1 uppercase (A-Z), 1 lowercase (a-z), 1 digit (0-9), and 1 symbol")
            st.caption("`StudySmart@2026` · `Reader_Pass#9`")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Register", use_container_width=True, type="secondary"):
                st.session_state["page"] = "Register"
                st.rerun()
        with col2:
            if st.button("Forgot Password", use_container_width=True, type="secondary"):
                st.session_state["page"] = "ForgotPassword"
                st.rerun()