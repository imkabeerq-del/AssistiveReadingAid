import html
import os
from pathlib import Path
import streamlit as st

from db import load_profile, update_avatar_path, update_profile, update_theme
from login import login_page

AVATAR_DIR = Path("avatars")


def _safe_avatar_filename(username: str, ext: str) -> Path:
    AVATAR_DIR.mkdir(parents=True, exist_ok=True)
    clean_name = "".join(ch if ch.isalnum() or ch in ("_", "-") else "_" for ch in username)
    clean_ext = ext.lower() if ext.lower() in (".png", ".jpg", ".jpeg", ".webp") else ".png"
    return AVATAR_DIR / f"{clean_name}{clean_ext}"


def profile_page() -> None:
    username = st.session_state.get("username")
    if not username:
        st.error("You must be logged in to view your profile.")
        login_page()
        return

    st.title("User Profile")
    st.caption("Manage Your Profile Picture, Personal Details & Preferences")

    profile = load_profile(username)
    avatar_path_str = profile.get("avatar_path") or ""
    has_avatar = bool(avatar_path_str and os.path.exists(avatar_path_str))

    st.markdown(
        f"""
        <div class="profile-card">
            <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
                <div>
                    <h2 style="margin:0;">{html.escape(username)}</h2>
                    <p style="margin:4px 0 0 0;opacity:0.8;">Role: {html.escape(str(profile.get('role', 'Student')))}</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if has_avatar:
        st.image(avatar_path_str, caption=f"{username}'s Profile Picture", width=140)
    else:
        st.info("No profile picture uploaded yet. Add one below.")

    uploaded_photo = st.file_uploader(
        "Upload Profile Picture",
        type=["png", "jpg", "jpeg", "webp"],
        key="profile_avatar_uploader",
    )

    p_col1, p_col2 = st.columns(2)
    with p_col1:
        if st.button("Save Profile Picture", type="primary", use_container_width=True):
            if uploaded_photo is not None:
                ext = Path(uploaded_photo.name).suffix or ".png"
                target_file = _safe_avatar_filename(username, ext)
                with open(target_file, "wb") as f:
                    f.write(uploaded_photo.getbuffer())
                update_avatar_path(username, str(target_file))
                st.success("Profile picture saved.")
                st.rerun()
            else:
                st.warning("Please select an image file first.")

    with p_col2:
        if st.button("Remove Picture", type="secondary", use_container_width=True):
            if has_avatar:
                try:
                    os.remove(avatar_path_str)
                except OSError:
                    pass
            update_avatar_path(username, "")
            st.info("Profile picture removed.")
            st.rerun()

    with st.expander("Edit Profile Information", expanded=True):
        new_full_name = st.text_input("Full Name", value=profile.get("full_name") or "")
        new_email = st.text_input("Email Address", value=profile.get("email") or "")
        education_options = [
            "Elementary School",
            "Middle School",
            "High School",
            "University",
            "Other",
        ]
        current_edu = profile.get("education_level") or "Other"
        edu_index = education_options.index(current_edu) if current_edu in education_options else 4
        new_education_level = st.selectbox("Education Level", education_options, index=edu_index)

        if st.button("Save Changes", type="primary"):
            update_profile(
                username,
                new_full_name,
                new_email,
                new_education_level,
                reduced_motion=bool(profile.get("reduced_motion", False)),
                celebration_effects=bool(profile.get("celebration_effects", True)),
                avatar_path=avatar_path_str,
            )
            st.success("Profile updated successfully.")

    st.divider()
    st.subheader("Reading Preferences")

    current_dark = st.session_state.get("dark_mode", True)
    new_dark_mode = st.toggle("Dark Mode", value=current_dark)
    if new_dark_mode != current_dark:
        st.session_state["dark_mode"] = new_dark_mode
        update_theme(username, "Dark" if new_dark_mode else "Light")
        st.rerun()

    new_reduced_motion = st.toggle(
        "Reduce Motion (Disable Animations)",
        value=bool(profile.get("reduced_motion", False)),
    )
    new_celebration_effects = st.toggle(
        "Enable Celebration Effects",
        value=bool(profile.get("celebration_effects", True)),
    )

    if st.button("Update Preferences"):
        update_profile(
            username,
            profile.get("full_name") or "",
            profile.get("email") or "",
            profile.get("education_level") or "Other",
            reduced_motion=new_reduced_motion,
            celebration_effects=new_celebration_effects,
            avatar_path=avatar_path_str,
        )
        st.success("Preferences updated.")