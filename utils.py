import html
from pathlib import Path
import sqlite3
import streamlit as st

from db import delete_session_token, load_profile

try:
    from db import save_profile as _db_save_profile  # type: ignore
except ImportError:
    _db_save_profile = None


THEME_TOGGLE_CSS = """
<style>
/* Sleek pill-switch styling for the theme button (penultimate column) */
[data-testid="stHorizontalBlock"] > div:nth-last-child(2) .stButton button {
    border-radius: 999px !important;
    min-height: 46px !important;
    padding: 9px 18px !important;
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.015em !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: transform 0.18s ease, box-shadow 0.2s ease, border-color 0.2s ease, background 0.2s ease !important;
}

/* Dark mode active -> clean warm-amber pill to switch to Light mode */
[data-testid="stHorizontalBlock"] > div:nth-last-child(2) .stButton button {
    background: linear-gradient(135deg, #17223B 0%, #233252 100%) !important;
    color: #FDE68A !important;
    border: 1.5px solid rgba(251, 191, 36, 0.45) !important;
    box-shadow: 0 6px 18px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
}

[data-testid="stHorizontalBlock"] > div:nth-last-child(2) .stButton button::before {
    content: "";
    width: 8px;
    height: 8px;
    margin-right: 9px;
    border-radius: 999px;
    background: #FBBF24;
    box-shadow: 0 0 10px rgba(251, 191, 36, 0.85);
}

[data-testid="stHorizontalBlock"] > div:nth-last-child(2) .stButton button:hover {
    transform: translateY(-2px) !important;
    border-color: #FBBF24 !important;
    box-shadow: 0 8px 22px rgba(251, 191, 36, 0.25) !important;
}
</style>
"""


LIGHT_MODE_CSS = """
<style>
html,
body,
.stApp {
    background-color: #F8FAFC !important;
    background-image:
        radial-gradient(circle at 14% 6%, rgba(99, 102, 241, 0.08), transparent 44%),
        radial-gradient(circle at 88% 10%, rgba(6, 182, 212, 0.07), transparent 40%) !important;
    color: #0F172A !important;
}

h1,
h2,
h3,
h4,
h5,
h6,
p,
li,
label,
.stTextInput label,
.stTextArea label,
.stSelectbox label,
.stSlider label,
.stSelectSlider label {
    color: #0F172A !important;
}

[data-testid="stCaptionContainer"] p {
    color: #475569 !important;
}

.nav-container {
    background: #FFFFFF !important;
    border: 1px solid #CBD5E1 !important;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06) !important;
}

.nav-brand {
    color: #0F172A !important;
}

.nav-user {
    color: #334155 !important;
    background: #F1F5F9 !important;
    border: 1px solid #CBD5E1 !important;
}

.nav-user span {
    color: #4F46E5 !important;
}

.auth-hero,
.custom-card,
.tip-card,
.profile-card,
.awareness-card,
.login-card,
.reading-surface,
[data-testid="stMetric"],
[data-testid="stExpander"] {
    background: #FFFFFF !important;
    background-image: none !important;
    color: #0F172A !important;
    border-color: #CBD5E1 !important;
    box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06) !important;
}

[data-testid="stMetricLabel"] {
    color: #475569 !important;
}

[data-testid="stMetricValue"] {
    color: #0F172A !important;
}

.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stSelectbox div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #0F172A !important;
    border: 1.5px solid #CBD5E1 !important;
}

.stButton button[kind="secondary"] {
    background-color: #F1F5F9 !important;
    color: #0F172A !important;
    border: 1.5px solid #CBD5E1 !important;
    box-shadow: none !important;
}

.stButton button[kind="secondary"]:hover {
    background-color: #E2E8F0 !important;
    border-color: #94A3B8 !important;
    color: #0F172A !important;
}

/* Light mode active -> crisp indigo pill to switch back to Dark mode */
[data-testid="stHorizontalBlock"] > div:nth-last-child(2) .stButton button {
    background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%) !important;
    color: #312E81 !important;
    border: 1.5px solid #A5B4FC !important;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.14) !important;
}

[data-testid="stHorizontalBlock"] > div:nth-last-child(2) .stButton button::before {
    background: #4F46E5;
    box-shadow: 0 0 8px rgba(79, 70, 229, 0.55);
}

[data-testid="stHorizontalBlock"] > div:nth-last-child(2) .stButton button:hover {
    background: linear-gradient(135deg, #E0E7FF 0%, #C7D2FE 100%) !important;
    border-color: #6366F1 !important;
    color: #1E1B4B !important;
}

hr {
    border-color: #CBD5E1 !important;
}
</style>
"""


def _persist_preferred_theme(username: str, theme_label: str) -> None:
    if not username or username == "Reader":
        return

    if callable(_db_save_profile):
        try:
            prof = load_profile(username)
            if isinstance(prof, dict):
                prof["preferred_theme"] = theme_label
                _db_save_profile(username, prof)
                return
        except Exception:
            pass

    db_path = Path("reading_aid.db")
    if not db_path.exists():
        return

    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(profiles)")
        cols = [row[1] for row in cur.fetchall()]
        if "preferred_theme" in cols and "username" in cols:
            cur.execute(
                "UPDATE profiles SET preferred_theme = ? WHERE username = ?",
                (theme_label, username),
            )
            conn.commit()
        conn.close()
    except Exception:
        pass


def apply_theme() -> None:
    st.session_state.setdefault("dark_mode", True)

    css_path = Path("style.css")
    if css_path.exists():
        css_text = css_path.read_text(encoding="utf-8")
        st.markdown(f"<style>{css_text}</style>", unsafe_allow_html=True)

    st.markdown(THEME_TOGGLE_CSS, unsafe_allow_html=True)

    if not st.session_state.get("dark_mode", True):
        st.markdown(LIGHT_MODE_CSS, unsafe_allow_html=True)

    if st.session_state.get("reduced_motion", False):
        st.markdown(
            "<style>*, *::before, *::after { transition: none !important; animation: none !important; }</style>",
            unsafe_allow_html=True,
        )


def _toggle_theme(username: str) -> None:
    next_dark = not st.session_state.get("dark_mode", True)
    st.session_state["dark_mode"] = next_dark
    _persist_preferred_theme(username, "Dark" if next_dark else "Light")
    st.rerun()


def _logout() -> None:
    token = st.session_state.get("session_token", "")
    if token:
        try:
            delete_session_token(token)
        except Exception:
            pass
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""
    st.session_state["role"] = "Student"
    st.session_state["session_token"] = ""
    st.session_state["page"] = "Login"
    st.query_params.pop("auth_token", None)
    st.rerun()


def navbar() -> None:
    username = st.session_state.get("username", "Reader")
    role = st.session_state.get("role", "Student")

    if not role or role == "Student":
        try:
            prof = load_profile(username)
            if isinstance(prof, dict) and prof.get("role"):
                role = prof["role"]
                st.session_state["role"] = role
        except Exception:
            pass

    is_dark = st.session_state.get("dark_mode", True)
    mode_badge = "Dark Slate" if is_dark else "Light Slate"

    st.markdown(
        f'<div class="nav-container">'
        f'<div class="nav-brand">Assistive Reading Aid</div>'
        f'<div class="nav-user">Signed in as <span>{html.escape(str(username))}</span> · {html.escape(str(role))} · <span>{mode_badge}</span></div>'
        f"</div>",
        unsafe_allow_html=True,
    )

    nav_items = [
        ("Dashboard", "Dashboard"),
        ("Reading Aid", "ReadingAid"),
        ("Awareness", "Awareness"),
        ("Tips", "Tips"),
        ("Profile", "Profile"),
    ]
    if role == "Admin":
        nav_items.append(("Admin", "Admin"))

    current_page = st.session_state.get("page", "Dashboard")
    cols = st.columns(len(nav_items) + 2, gap="medium")

    for idx, (label, target_page) in enumerate(nav_items):
        is_active = current_page == target_page
        btn_type = "primary" if is_active else "secondary"
        with cols[idx]:
            if st.button(label, key=f"nav_{target_page}", type=btn_type, use_container_width=True):
                st.session_state["page"] = target_page
                st.rerun()

    theme_btn_label = "Light Mode" if is_dark else "Dark Mode"
    with cols[-2]:
        if st.button(theme_btn_label, key="nav_theme_toggle", type="secondary", use_container_width=True):
            _toggle_theme(str(username))

    with cols[-1]:
        if st.button("Logout", key="nav_logout", type="secondary", use_container_width=True):
            _logout()

    st.markdown("<div style='margin-bottom:10px;'></div>", unsafe_allow_html=True)