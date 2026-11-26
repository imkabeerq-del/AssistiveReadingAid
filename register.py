import re
import streamlit as st

from db import get_user_by_username, register_user

USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]{4,20}$")
PASSWORD_SYMBOL_PATTERN = re.compile(r"[!@#$%^&*(),.?\":{}|<>]")


def _check_password_rules(password: str) -> dict[str, bool]:
    return {
        "At least 8 characters": len(password) >= 8,
        "No spaces": len(password) > 0 and " " not in password,
        "Uppercase letter (A-Z)": bool(re.search(r"[A-Z]", password)),
        "Lowercase letter (a-z)": bool(re.search(r"[a-z]", password)),
        "Number (0-9)": bool(re.search(r"\d", password)),
        "Symbol (!@#$%^&*)": bool(PASSWORD_SYMBOL_PATTERN.search(password)),
    }


def register_page() -> None:
    st.session_state.setdefault("reg_show_pwd", False)

    st.markdown(
        """
        <div style="max-width:460px;margin:0 auto 12px auto;">
            <h2 style="margin-bottom:4px;">Create Account</h2>
            <p style="color:#94A3B8;font-size:15px;margin:0;">
                Register once with a unique username to sign in to your account.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        "Password format: 8+ characters, no spaces, with A-Z, a-z, 0-9, and a symbol (Example: `StudySmart@2026`)."
    )

    username = st.text_input(
        "Username",
        placeholder="4-20 letters, numbers, ., _, - (no spaces)",
        key="reg_username_field",
    )

    show_pwd = st.session_state.get("reg_show_pwd", False)
    pwd_type = "default" if show_pwd else "password"

    password = st.text_input(
        "Password",
        type=pwd_type,
        placeholder="Create a strong password",
        key=f"reg_password_field_{'plain' if show_pwd else 'masked'}",
        value=st.session_state.get("reg_pwd_draft", ""),
    )
    confirm_password = st.text_input(
        "Confirm Password",
        type=pwd_type,
        placeholder="Re-enter your password",
        key=f"reg_confirm_field_{'plain' if show_pwd else 'masked'}",
        value=st.session_state.get("reg_confirm_draft", ""),
    )
    st.session_state["reg_pwd_draft"] = password
    st.session_state["reg_confirm_draft"] = confirm_password

    toggled = st.checkbox("Show password", value=show_pwd, key="reg_show_pwd_box")
    if toggled != show_pwd:
        st.session_state["reg_show_pwd"] = toggled
        st.rerun()

    role = st.selectbox("Role", ["Student", "Admin"], key="reg_role_select")

    if password:
        rules = _check_password_rules(password)
        passed_count = sum(rules.values())
        st.progress(passed_count / len(rules))
        for label, ok in rules.items():
            mark = "✓" if ok else "✗"
            color = "#22C55E" if ok else "#94A3B8"
            st.markdown(
                f"<span style='color:{color};font-size:13px;'>{mark} {label}</span>",
                unsafe_allow_html=True,
            )

    if st.button("Register", type="primary", use_container_width=True):
        clean_user = username.strip()

        if not clean_user:
            st.error("Please enter a username.")
            return

        if not USERNAME_PATTERN.match(clean_user):
            st.error(
                "Username must be 4-20 characters with no spaces (letters, numbers, ., _, - only)."
            )
            return

        if get_user_by_username(clean_user):
            st.error(
                f"The username '{clean_user}' is already taken. Please choose a different username."
            )
            return

        if not password:
            st.error("Please enter a password.")
            return

        if password != confirm_password:
            st.error("Passwords do not match.")
            return

        rules = _check_password_rules(password)
        if not all(rules.values()):
            st.error("Please meet all password requirements listed above.")
            return

        try:
            created = register_user(clean_user, password, role)
        except Exception as err:
            st.error(f"Could not complete registration: {err}")
            return

        if created:
            st.session_state["remembered_username"] = clean_user
            st.session_state["remembered_password"] = password
            st.session_state["reg_pwd_draft"] = ""
            st.session_state["reg_confirm_draft"] = ""
            st.session_state["reg_show_pwd"] = False
            st.session_state["page"] = "Login"
            st.rerun()
        else:
            st.error(
                f"The username '{clean_user}' is already registered. Please enter another username."
            )

    st.divider()

    if st.button("Back to Login", use_container_width=True, type="secondary"):
        st.session_state["page"] = "Login"
        st.rerun()