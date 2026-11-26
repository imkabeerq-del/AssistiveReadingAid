import re
import streamlit as st

from db import get_user_by_username, reset_password

PASSWORD_SYMBOL_PATTERN = re.compile(r"[!@#$%^&*(),.?\":{}|<>]")


def _password_valid(pwd: str) -> tuple[bool, str]:
    if len(pwd) < 8:
        return False, "Password must be at least 8 characters long."
    if " " in pwd:
        return False, "Password cannot contain spaces."
    if not re.search(r"[A-Z]", pwd):
        return False, "Password must include at least one uppercase letter (A-Z)."
    if not re.search(r"[a-z]", pwd):
        return False, "Password must include at least one lowercase letter (a-z)."
    if not re.search(r"\d", pwd):
        return False, "Password must include at least one number (0-9)."
    if not PASSWORD_SYMBOL_PATTERN.search(pwd):
        return False, "Password must include at least one special symbol (!@#$%^&*)."
    return True, ""


def forgot_password_page() -> None:
    st.session_state.setdefault("fp_show_pwd", False)

    st.markdown(
        """
        <div class="auth-hero">
            <h2>Reset Password</h2>
            <p>Enter your registered username and choose a new password.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        "Password format: 8+ characters, no spaces, with A-Z, a-z, 0-9, and a symbol (Example: `StudySmart@2026`)."
    )

    username = st.text_input(
        "Registered Username",
        placeholder="Enter your username",
        key="fp_username_input",
    )

    show_pwd = st.session_state.get("fp_show_pwd", False)
    pwd_type = "default" if show_pwd else "password"

    new_password = st.text_input(
        "New Password",
        type=pwd_type,
        placeholder="Enter new password",
        key=f"fp_new_pwd_{'plain' if show_pwd else 'masked'}",
        value=st.session_state.get("fp_new_draft", ""),
    )
    confirm_password = st.text_input(
        "Confirm New Password",
        type=pwd_type,
        placeholder="Re-enter new password",
        key=f"fp_confirm_pwd_{'plain' if show_pwd else 'masked'}",
        value=st.session_state.get("fp_confirm_draft", ""),
    )
    st.session_state["fp_new_draft"] = new_password
    st.session_state["fp_confirm_draft"] = confirm_password

    toggled = st.checkbox("Show password", value=show_pwd, key="fp_show_pwd_box")
    if toggled != show_pwd:
        st.session_state["fp_show_pwd"] = toggled
        st.rerun()

    if st.button("Update Password", type="primary", use_container_width=True):
        clean_user = username.strip()

        if not clean_user:
            st.error("Please enter your username.")
            return

        existing_user = get_user_by_username(clean_user)
        if not existing_user:
            st.error("No account was found with that username.")
            return

        if not new_password:
            st.error("Please enter a new password.")
            return

        if new_password != confirm_password:
            st.error("New passwords do not match.")
            return

        ok, msg = _password_valid(new_password)
        if not ok:
            st.error(msg)
            return

        resolved_user = str(existing_user[1]) if len(existing_user) > 1 else clean_user
        if reset_password(resolved_user, new_password):
            st.session_state["remembered_username"] = resolved_user
            st.session_state["remembered_password"] = new_password
            st.session_state["fp_new_draft"] = ""
            st.session_state["fp_confirm_draft"] = ""
            st.success("Password updated. Redirecting to Login...")
            st.session_state["page"] = "Login"
            st.rerun()
        else:
            st.error("Unable to reset password right now. Please try again.")

    st.divider()

    if st.button("Back to Login", type="secondary", use_container_width=True):
        st.session_state["page"] = "Login"
        st.rerun()