import streamlit as st
from app_functions import hide_st_ui, get_summary_actions
from streamlit_extras.switch_page_button import switch_page

hide_st_ui()

if 'email_index' not in st.session_state:
    st.session_state.email_index = 0

if st.session_state.email_index == 4:
    switch_page("completed")
else:
    st.header("Part 3 of 3: Emails Requiring Actions")
    st.progress(float((st.session_state.email_index+1)/5), text=None)
    st.divider()

    st.write(get_summary_actions(st.session_state.actionable_unread_emails[st.session_state.email_index]), unsafe_allow_html=True)
    st.write("<br>", unsafe_allow_html=True)

    st.session_state.email_index += 1

    st.button(f"Reply", type='primary')
    st.button(f"Forward", type='secondary')
    st.button(f"Snooze", type='secondary')
