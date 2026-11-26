import html
import time
import streamlit as st

READING_TIPS = [
    {
        "num": "01",
        "title": "Chunk Long Paragraphs into Bite-Sized Blocks",
        "category": "Comprehension",
        "accent": "#22D3EE",
        "tip": (
            "Instead of pushing through a dense wall of text, read two or three sentences at a time. "
            "Pause for a moment, say the core idea out loud in your own words, and then move to the next block."
        ),
        "action": "Try this: Summarize each paragraph in one short sentence before scrolling.",
    },
    {
        "num": "02",
        "title": "Split Multisyllabic Words Before Blending",
        "category": "Decoding",
        "accent": "#818CF8",
        "tip": (
            "Long academic or technical words look intimidating when read all at once. "
            "Spot familiar prefixes, root parts, or suffixes first, sound out each piece calmly, and blend smoothly."
        ),
        "action": "Try this: Tap or select red-underlined words in Reading Aid to inspect syllables.",
    },
    {
        "num": "03",
        "title": "Anchor Your Eyes with a Line or Finger Guide",
        "category": "Visual Tracking",
        "accent": "#34D399",
        "tip": (
            "Crowded lines can cause your eyes to drift upward or repeat a line you already finished. "
            "Glide a finger, bookmark, or cursor along the line you are reading to keep steady visual focus."
        ),
        "action": "Try this: Increase font size and line spacing in Reading Aid so lines feel open.",
    },
    {
        "num": "04",
        "title": "Combine Visual Reading with Audio Read-Aloud",
        "category": "Multisensory",
        "accent": "#FBBF24",
        "tip": (
            "Listening to clear speech while following the written words builds stronger sound-to-letter memory "
            "and eases eye strain during longer study sessions."
        ),
        "action": "Try this: Listen in English or Hindi at a comfortable speed while tracking the text.",
    },
    {
        "num": "05",
        "title": "Do a 60-Second Preview Before Deep Reading",
        "category": "Preparation",
        "accent": "#22D3EE",
        "tip": (
            "Scan titles, headings, and key terms for one minute before reading from start to finish. "
            "Giving your brain a roadmap first makes new concepts much easier to place."
        ),
        "action": "Try this: List two questions you want answered before reading the full passage.",
    },
    {
        "num": "06",
        "title": "Protect Focus with Short, Planned Breaks",
        "category": "Stamina",
        "accent": "#818CF8",
        "tip": (
            "Mental fatigue makes letter confusion and re-reading much more likely. "
            "Take a 2-to-3-minute rest every 15–20 minutes and look away from the screen into the distance."
        ),
        "action": "Try this: Step away from the screen briefly after finishing a section.",
    },
]

CATEGORIES = ["All", "Comprehension", "Decoding", "Visual Tracking", "Multisensory", "Preparation", "Stamina"]


def tips_page() -> None:
    st.session_state.setdefault("tip_index", 0)
    st.session_state.setdefault("tip_auto_rotate", True)
    st.session_state.setdefault("tip_last_tick", time.time())
    st.session_state.setdefault("tip_category_filter", "All")

    st.title("Reading Strategies & Tips")
    st.caption("Clear, practical habits designed for comfortable reading, strong comprehension, and steady focus.")

    now = time.time()
    if st.session_state.get("tip_auto_rotate", True) and (now - st.session_state.get("tip_last_tick", now) >= 4.0):
        st.session_state["tip_index"] = (st.session_state["tip_index"] + 1) % len(READING_TIPS)
        st.session_state["tip_last_tick"] = now

    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2.2, 1, 1])
    with ctrl_col1:
        auto_val = st.checkbox(
            "Auto-rotate spotlight strategy every 4 seconds",
            value=st.session_state.get("tip_auto_rotate", True),
            key="tips_auto_rotate_cb",
        )
        st.session_state["tip_auto_rotate"] = auto_val
        if auto_val:
            st.session_state["tip_last_tick"] = time.time()
    with ctrl_col2:
        if st.button("Previous", type="secondary", use_container_width=True, key="tip_prev_btn"):
            st.session_state["tip_index"] = (st.session_state["tip_index"] - 1) % len(READING_TIPS)
            st.session_state["tip_last_tick"] = time.time()
            st.rerun()
    with ctrl_col3:
        if st.button("Next Strategy", type="primary", use_container_width=True, key="tip_next_btn"):
            st.session_state["tip_index"] = (st.session_state["tip_index"] + 1) % len(READING_TIPS)
            st.session_state["tip_last_tick"] = time.time()
            st.rerun()

    spotlight = READING_TIPS[st.session_state["tip_index"] % len(READING_TIPS)]
    spot_html = (
        f'<div class="custom-card" style="border-left:5px solid {spotlight["accent"]};padding:26px 28px;">'
        f'<div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;margin-bottom:10px;">'
        f'<span style="font-size:13px;font-weight:800;letter-spacing:0.08em;text-transform:uppercase;color:{spotlight["accent"]};">'
        f'Featured Strategy #{html.escape(spotlight["num"])} · {html.escape(spotlight["category"])}'
        f"</span>"
        f'<span style="font-size:13px;font-weight:600;color:#94A3B8;">'
        f'Tip {(st.session_state["tip_index"] % len(READING_TIPS)) + 1} of {len(READING_TIPS)}'
        f"</span>"
        f"</div>"
        f'<h2 style="margin:0 0 12px 0;font-size:1.55rem !important;color:#F8FAFC;">{html.escape(spotlight["title"])}</h2>'
        f'<p style="margin:0 0 16px 0;font-size:1.08rem !important;line-height:1.78 !important;color:#E2E8F0;">{html.escape(spotlight["tip"])}</p>'
        f'<div style="background:rgba(15,23,42,0.9);border:1px solid rgba(148,163,184,0.2);border-radius:10px;'
        f'padding:11px 15px;font-size:0.98rem;font-weight:600;color:#22D3EE;">'
        f'{html.escape(spotlight["action"])}'
        f"</div>"
        f"</div>"
    )
    st.markdown(spot_html, unsafe_allow_html=True)

    st.subheader("Browse All Reading Strategies")
    selected_cat = st.selectbox(
        "Filter by Focus Area",
        CATEGORIES,
        index=CATEGORIES.index(st.session_state.get("tip_category_filter", "All")),
        key="tips_cat_select",
    )
    st.session_state["tip_category_filter"] = selected_cat

    filtered_tips = (
        READING_TIPS
        if selected_cat == "All"
        else [t for t in READING_TIPS if t["category"] == selected_cat]
    )

    for idx in range(0, len(filtered_tips), 2):
        cols = st.columns(2, gap="large")
        for offset, col in enumerate(cols):
            if idx + offset >= len(filtered_tips):
                continue
            item = filtered_tips[idx + offset]
            card_html = (
                f'<div class="tip-card" style="border-top:3px solid {item["accent"]};">'
                f"<div>"
                f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">'
                f'<span style="font-size:12.5px;font-weight:800;letter-spacing:0.07em;text-transform:uppercase;color:{item["accent"]};">'
                f'{html.escape(item["category"])}'
                f"</span>"
                f'<span style="font-size:13px;font-weight:700;color:#64748B;">#{html.escape(item["num"])}</span>'
                f"</div>"
                f'<h3 style="margin:0 0 10px 0;font-size:1.25rem !important;line-height:1.35 !important;color:#F8FAFC;">{html.escape(item["title"])}</h3>'
                f'<p style="margin:0 0 14px 0;font-size:1.02rem !important;line-height:1.72 !important;color:#CBD5E1;">{html.escape(item["tip"])}</p>'
                f"</div>"
                f'<div style="padding-top:12px;border-top:1px solid rgba(148,163,184,0.14);font-size:0.94rem;font-weight:600;color:#E2E8F0;">'
                f'{html.escape(item["action"])}'
                f"</div>"
                f"</div>"
            )
            with col:
                st.markdown(card_html, unsafe_allow_html=True)

    if st.session_state.get("tip_auto_rotate", True):
        time.sleep(4)
        st.session_state["tip_index"] = (st.session_state["tip_index"] + 1) % len(READING_TIPS)
        st.session_state["tip_last_tick"] = time.time()
        st.rerun()