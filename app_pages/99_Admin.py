import html
import streamlit as st

from db import delete_user, get_all_activities, get_all_users


def admin_page() -> None:
    role = st.session_state.get("role", "Student")
    if role != "Admin":
        st.error("Access denied. Administrator privileges are required to view this page.")
        return

    st.title("Administration Console")
    st.caption("Manage Registered Accounts and Monitor Platform Activity")

    users = get_all_users()
    activities = get_all_activities()
    current_user = st.session_state.get("username", "")

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Total Users", len(users))
    with m2:
        admin_count = sum(1 for u in users if len(u) > 3 and u[3] == "Admin")
        st.metric("Admins", admin_count)
    with m3:
        st.metric("Activity Events", len(activities))

    st.divider()
    st.subheader("Registered Users")

    if not users:
        st.info("No registered users found.")
    else:
        for u in users:
            user_id = u[0]
            uname = str(u[1]) if len(u) > 1 else ""
            urole = str(u[3]) if len(u) > 3 else "Student"

            col_info, col_action = st.columns([4, 1])
            with col_info:
                st.markdown(
                    f"""
                    <div class="custom-card" style="padding:14px 18px;margin-bottom:10px;">
                        <strong style="color:#F8FAFC;font-size:16px;">{html.escape(uname)}</strong>
                        <span style="color:#22D3EE;margin-left:12px;font-size:13px;font-weight:600;">
                            Role: {html.escape(urole)}
                        </span>
                        <span style="color:#94A3B8;margin-left:12px;font-size:12px;">
                            ID #{user_id}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with col_action:
                if uname == current_user:
                    st.caption("Active session")
                else:
                    if st.button("Delete", key=f"del_user_{user_id}", type="secondary", use_container_width=True):
                        delete_user(int(user_id))
                        st.success(f"Removed user '{uname}'.")
                        st.rerun()

    st.divider()
    st.subheader("Recent Activity Log")

    if not activities:
        st.info("No activity logs recorded yet.")
    else:
        rows_html = []
        for act in activities[:25]:
            act_user = html.escape(str(act[1])) if len(act) > 1 else "Unknown"
            act_desc = html.escape(str(act[2])) if len(act) > 2 else ""
            act_time = html.escape(str(act[3])) if len(act) > 3 else ""
            rows_html.append(
                f'<tr style="border-bottom:1px solid rgba(255,255,255,0.06);">'
                f'<td style="padding:10px 14px;font-weight:600;color:#22D3EE;">{act_user}</td>'
                f'<td style="padding:10px 14px;color:#F8FAFC;">{act_desc}</td>'
                f'<td style="padding:10px 14px;color:#94A3B8;font-size:13px;">{act_time}</td>'
                f'</tr>'
            )

        st.markdown(
            '<div class="custom-card" style="padding:0;overflow:hidden;">'
            '<table style="width:100%;border-collapse:collapse;font-size:14px;">'
            '<thead><tr style="background:rgba(15,23,42,0.95);border-bottom:1px solid rgba(255,255,255,0.12);text-align:left;">'
            '<th style="padding:12px 14px;color:#94A3B8;">User</th>'
            '<th style="padding:12px 14px;color:#94A3B8;">Action</th>'
            '<th style="padding:12px 14px;color:#94A3B8;">Timestamp</th>'
            '</tr></thead>'
            f'<tbody>{"".join(rows_html)}</tbody>'
            '</table></div>',
            unsafe_allow_html=True,
        )