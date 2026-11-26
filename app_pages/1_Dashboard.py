from datetime import datetime
import html
import streamlit as st

from db import get_all_activities

ACHIEVEMENTS_CATALOG = [
    {
        "id": "first_steps",
        "title": "First Steps",
        "description": "Create your account and sign in to the reading workspace.",
        "xp": 50,
        "tier": "cyan",
        "glyph": "01",
        "condition_text": "Automatically earned upon account registration and login.",
    },
    {
        "id": "deep_reader",
        "title": "Deep Reader",
        "description": "Analyze at least 1 reading passage in the Reading Aid tool.",
        "xp": 75,
        "tier": "gold",
        "glyph": "RD",
        "condition_text": "Open Reading Aid, enter or pick a passage, and click Analyze Passage.",
    },
    {
        "id": "syllable_scout",
        "title": "Syllable Scout",
        "description": "Run 3 or more passage analyses across your study sessions.",
        "xp": 100,
        "tier": "indigo",
        "glyph": "SY",
        "condition_text": "Complete at least 3 passage analyses in Reading Aid.",
    },
    {
        "id": "strategy_builder",
        "title": "Strategy Builder",
        "description": "Visit the Tips & Strategies page to review reading techniques.",
        "xp": 60,
        "tier": "emerald",
        "glyph": "TP",
        "condition_text": "Navigate to Tips from the top navigation bar.",
    },
    {
        "id": "awareness_advocate",
        "title": "Awareness Advocate",
        "description": "Explore dyslexia signs, strengths, and support resources in Awareness.",
        "xp": 60,
        "tier": "cyan",
        "glyph": "AW",
        "condition_text": "Open the Awareness page from the top navigation bar.",
    },
    {
        "id": "profile_tailored",
        "title": "Profile Tailored",
        "description": "Customize your reader profile or accessibility settings.",
        "xp": 70,
        "tier": "gold",
        "glyph": "PR",
        "condition_text": "Save your profile details or update your avatar/preferences on the Profile page.",
    },
]

TIER_STYLES = {
    "gold": {
        "border": "linear-gradient(135deg,#F59E0B,#FDE68A,#B45309)",
        "icon_bg": "linear-gradient(145deg,#272013,#131622)",
        "icon_color": "#FBBF24",
    },
    "cyan": {
        "border": "linear-gradient(135deg,#22D3EE,#6366F1,#0E7490)",
        "icon_bg": "linear-gradient(145deg,#0E2333,#0D1322)",
        "icon_color": "#22D3EE",
    },
    "indigo": {
        "border": "linear-gradient(135deg,#818CF8,#4F46E5,#312E81)",
        "icon_bg": "linear-gradient(145deg,#1A1B38,#0D1322)",
        "icon_color": "#A5B4FC",
    },
    "emerald": {
        "border": "linear-gradient(135deg,#34D399,#059669,#064E3B)",
        "icon_bg": "linear-gradient(145deg,#0D2922,#0D1322)",
        "icon_color": "#34D399",
    },
}


def _format_steam_timestamp(raw_ts: str | None) -> str:
    if not raw_ts:
        now = datetime.now()
        hour_12 = now.strftime("%I").lstrip("0") or "12"
        return f"Unlocked {now.strftime('%d %b %Y')}, {hour_12}:{now.strftime('%M %p').lower()}"
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"):
        try:
            dt = datetime.strptime(str(raw_ts).strip(), fmt)
            hour_12 = dt.strftime("%I").lstrip("0") or "12"
            return f"Unlocked {dt.strftime('%d %b %Y')}, {hour_12}:{dt.strftime('%M %p').lower()}"
        except ValueError:
            continue
    return f"Unlocked {str(raw_ts)}"


def _evaluate_achievements(username: str, activities: list) -> tuple[list[dict], list[dict], int]:
    st.session_state.setdefault("visited_pages", {"Dashboard"})
    current_page = st.session_state.get("page", "Dashboard")
    st.session_state["visited_pages"].add(current_page)
    visited = st.session_state["visited_pages"]

    user_acts = [a for a in activities if len(a) > 1 and str(a[1]).lower() == str(username).lower()]
    analysis_count = sum(
        1 for a in user_acts if len(a) > 2 and "analyzed" in str(a[2]).lower()
    )
    session_analyses = len(st.session_state.get("reading_history", []))
    total_analyses = max(analysis_count, session_analyses)

    profile_updated = any(
        len(a) > 2 and ("profile" in str(a[2]).lower() or "avatar" in str(a[2]).lower())
        for a in user_acts
    )

    latest_ts = user_acts[0][3] if user_acts and len(user_acts[0]) > 3 else None

    unlock_map = {
        "first_steps": (True, _format_steam_timestamp(latest_ts), "1 / 1"),
        "deep_reader": (
            total_analyses >= 1,
            _format_steam_timestamp(latest_ts),
            f"{min(total_analyses, 1)} / 1",
        ),
        "syllable_scout": (
            total_analyses >= 3,
            _format_steam_timestamp(latest_ts),
            f"{min(total_analyses, 3)} / 3",
        ),
        "strategy_builder": (
            "Tips" in visited,
            _format_steam_timestamp(None),
            "1 / 1" if "Tips" in visited else "0 / 1",
        ),
        "awareness_advocate": (
            "Awareness" in visited,
            _format_steam_timestamp(None),
            "1 / 1" if "Awareness" in visited else "0 / 1",
        ),
        "profile_tailored": (
            profile_updated or "Profile" in visited,
            _format_steam_timestamp(latest_ts),
            "1 / 1" if (profile_updated or "Profile" in visited) else "0 / 1",
        ),
    }

    unlocked_items: list[dict] = []
    locked_items: list[dict] = []
    total_xp = 0

    for item in ACHIEVEMENTS_CATALOG:
        is_unlocked, stamp_text, prog_text = unlock_map.get(
            item["id"], (False, "Locked", "0 / 1")
        )
        enriched = dict(item)
        enriched["unlocked"] = is_unlocked
        enriched["timestamp_label"] = stamp_text
        enriched["progress_label"] = prog_text
        if is_unlocked:
            total_xp += item["xp"]
            unlocked_items.append(enriched)
        else:
            locked_items.append(enriched)

    return unlocked_items, locked_items, total_xp


def _render_steam_achievement_list(heading: str, items: list[dict], is_unlocked_list: bool) -> None:
    st.markdown(
        f'<div style="font-size:12px;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:#94A3B8;margin:14px 0 8px 2px;">{html.escape(heading)} ({len(items)})</div>',
        unsafe_allow_html=True,
    )

    if not items:
        st.markdown(
            '<div style="background:#0F172A;border:1px solid rgba(148,163,184,0.14);border-radius:6px;padding:16px 20px;color:#94A3B8;font-size:14px;">No achievements in this section yet.</div>',
            unsafe_allow_html=True,
        )
        return

    rows_html = []
    for idx, ach in enumerate(items):
        tier = TIER_STYLES.get(ach.get("tier", "cyan"), TIER_STYLES["cyan"])
        border_bottom = "border-bottom:1px solid rgba(148,163,184,0.12);" if idx < len(items) - 1 else ""
        row_bg = "#0E1626" if is_unlocked_list else "#0B111E"
        opacity_css = "opacity:1;" if is_unlocked_list else "opacity:0.75;"
        right_text = ach["timestamp_label"] if is_unlocked_list else f"Progress: {ach['progress_label']}"
        xp_badge = f"+{ach['xp']} XP"

        row = (
            f'<div style="display:flex;align-items:center;justify-content:space-between;gap:18px;padding:14px 18px;background:{row_bg};{border_bottom}{opacity_css}">'
            f'<div style="display:flex;align-items:center;gap:16px;min-width:0;flex:1;">'
            f'<div style="flex:0 0 58px;width:58px;height:58px;padding:3px;border-radius:6px;background:{tier["border"]};box-shadow:0 4px 14px rgba(0,0,0,0.45);">'
            f'<div style="width:100%;height:100%;border-radius:4px;background:{tier["icon_bg"]};display:flex;align-items:center;justify-content:center;color:{tier["icon_color"]};font-size:16px;font-weight:800;letter-spacing:0.04em;">'
            f'{html.escape(ach["glyph"])}'
            f'</div>'
            f'</div>'
            f'<div style="min-width:0;">'
            f'<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">'
            f'<span style="font-size:16px;font-weight:700;color:#F8FAFC;line-height:1.3;">{html.escape(ach["title"])}</span>'
            f'<span style="font-size:11px;font-weight:700;color:#22D3EE;background:rgba(34,211,238,0.1);padding:2px 8px;border-radius:4px;">{html.escape(xp_badge)}</span>'
            f'</div>'
            f'<div style="font-size:13.5px;color:#CBD5E1;margin-top:3px;line-height:1.45;">{html.escape(ach["description"])}</div>'
            f'</div>'
            f'</div>'
            f'<div style="flex-shrink:0;text-align:right;font-size:12.5px;color:#94A3B8;white-space:nowrap;">{html.escape(right_text)}</div>'
            f'</div>'
        )
        rows_html.append(row)

    container_html = (
        '<div style="background:#0E1626;border:1px solid rgba(148,163,184,0.16);border-radius:6px;overflow:hidden;box-shadow:0 12px 28px rgba(0,0,0,0.42);">'
        + "".join(rows_html)
        + "</div>"
    )
    st.markdown(container_html, unsafe_allow_html=True)


def _render_leaderboard(username: str, unlocked_count: int, total_xp: int) -> None:
    st.subheader("Achievements Leaderboard")
    entries = [
        {"user": username or "Reader", "badges": unlocked_count, "xp": total_xp, "is_current": True},
        {"user": "Aarav Sharma", "badges": 5, "xp": 355, "is_current": False},
        {"user": "Meera Nair", "badges": 4, "xp": 285, "is_current": False},
        {"user": "Rohan Verma", "badges": 3, "xp": 205, "is_current": False},
        {"user": "Ananya Patel", "badges": 2, "xp": 125, "is_current": False},
    ]
    entries.sort(key=lambda item: (item["xp"], item["badges"]), reverse=True)

    rows_html = []
    for idx, item in enumerate(entries, start=1):
        row_bg = "rgba(99, 102, 241, 0.16)" if item["is_current"] else "transparent"
        user_color = "#22D3EE" if item["is_current"] else "#F8FAFC"
        suffix = " (You)" if item["is_current"] else ""
        rows_html.append(
            f'<tr style="background:{row_bg};border-bottom:1px solid rgba(255,255,255,0.06);">'
            f'<td style="padding:10px 14px;font-weight:700;color:#94A3B8;">#{idx}</td>'
            f'<td style="padding:10px 14px;font-weight:700;color:{user_color};">{html.escape(str(item["user"]))}{suffix}</td>'
            f'<td style="padding:10px 14px;color:#E2E8F0;">{item["badges"]}</td>'
            f'<td style="padding:10px 14px;font-weight:700;color:#4ADE80;">{item["xp"]} XP</td>'
            f'</tr>'
        )

    st.markdown(
        '<div class="custom-card" style="padding:0;overflow:hidden;">'
        '<table style="width:100%;border-collapse:collapse;font-size:14px;">'
        '<thead><tr style="background:rgba(15,23,42,0.95);border-bottom:1px solid rgba(255,255,255,0.12);text-align:left;">'
        '<th style="padding:12px 14px;color:#94A3B8;">Rank</th>'
        '<th style="padding:12px 14px;color:#94A3B8;">Reader</th>'
        '<th style="padding:12px 14px;color:#94A3B8;">Badges</th>'
        '<th style="padding:12px 14px;color:#94A3B8;">Total XP</th>'
        '</tr></thead>'
        f'<tbody>{"".join(rows_html)}</tbody>'
        '</table></div>',
        unsafe_allow_html=True,
    )


def dashboard_page() -> None:
    username = st.session_state.get("username", "Reader")
    st.session_state.setdefault("reading_history", [])
    st.session_state.setdefault("search_history", [])
    st.session_state.setdefault("achievements_vault_open", True)

    try:
        all_activities = get_all_activities()
    except Exception:
        all_activities = []

    user_activities = [
        a for a in all_activities if len(a) > 1 and str(a[1]).lower() == str(username).lower()
    ]

    unlocked_items, locked_items, total_xp = _evaluate_achievements(username, all_activities)
    total_count = len(ACHIEVEMENTS_CATALOG)
    unlocked_count = len(unlocked_items)

    st.title("Reading Dashboard")
    st.caption(f"Welcome back, {username}. Track your reading sessions, milestones, and achievements.")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Achievements Unlocked", f"{unlocked_count} / {total_count}")
    with c2:
        st.metric("Total XP", f"{total_xp} XP")
    with c3:
        st.metric("Session Analyses", len(st.session_state.get("reading_history", [])))
    with c4:
        st.metric("Logged Events", len(user_activities))

    st.divider()

    vault_header_col, vault_toggle_col = st.columns([3, 1])
    with vault_header_col:
        st.subheader("Achievements & Badges Vault")
    with vault_toggle_col:
        is_open = st.session_state.get("achievements_vault_open", True)
        btn_label = "Hide Vault" if is_open else "Open Vault"
        if st.button(btn_label, type="secondary", use_container_width=True, key="toggle_ach_vault"):
            st.session_state["achievements_vault_open"] = not is_open
            st.rerun()

    if st.session_state.get("achievements_vault_open", True):
        _render_steam_achievement_list("Unlocked Achievements", unlocked_items, is_unlocked_list=True)
        _render_steam_achievement_list("Locked Achievements", locked_items, is_unlocked_list=False)

        with st.expander("How to Unlock Each Achievement"):
            for ach in ACHIEVEMENTS_CATALOG:
                st.markdown(f"**{ach['title']}** ({ach['xp']} XP): {ach['condition_text']}")

    st.divider()

    _render_leaderboard(username, unlocked_count, total_xp)

    st.divider()
    st.subheader("Recent Activity")

    if not user_activities:
        st.info("No database activity logged yet. Analyze a passage in Reading Aid to record progress.")
    else:
        rows_html = []
        for act in user_activities[:12]:
            desc = html.escape(str(act[2])) if len(act) > 2 else ""
            ts = html.escape(str(act[3])) if len(act) > 3 else ""
            rows_html.append(
                f'<tr style="border-bottom:1px solid rgba(255,255,255,0.06);">'
                f'<td style="padding:10px 14px;color:#F8FAFC;">{desc}</td>'
                f'<td style="padding:10px 14px;color:#94A3B8;font-size:13px;">{ts}</td>'
                f'</tr>'
            )
        st.markdown(
            '<div class="custom-card" style="padding:0;overflow:hidden;">'
            '<table style="width:100%;border-collapse:collapse;font-size:14px;">'
            '<thead><tr style="background:rgba(15,23,42,0.95);border-bottom:1px solid rgba(255,255,255,0.12);text-align:left;">'
            '<th style="padding:12px 14px;color:#94A3B8;">Activity</th>'
            '<th style="padding:12px 14px;color:#94A3B8;">Timestamp</th>'
            '</tr></thead>'
            f'<tbody>{"".join(rows_html)}</tbody>'
            '</table></div>',
            unsafe_allow_html=True,
        )