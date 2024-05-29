import streamlit as st
from app_functions import hide_st_ui, get_summary_info_only
from streamlit_extras.switch_page_button import switch_page

hide_st_ui()

if 'info_only_email_index' not in st.session_state:
    st.session_state.info_only_email_index = 0

num_info_only_emails = len(st.session_state.info_only_unread_emails)
st.write(num_info_only_emails)

if st.session_state.info_only_email_index == num_info_only_emails-1:
    switch_page("actionable_items_a")
else:
    st.header("Part 2 of 3: Information Only Emails")
    st.divider()
    st.progress(float((st.session_state.info_only_email_index+1)/num_info_only_emails), text=None)
    st.divider()

    st.write(get_summary_info_only(st.session_state.info_only_unread_emails[st.session_state.info_only_email_index]), unsafe_allow_html=True)
    st.write("<br>", unsafe_allow_html=True)

    st.session_state.info_only_email_index += 1

    st.button(f"File and Archive", type='primary')
    st.button(f"Reply", type='secondary')
    st.button(f"Forward", type='secondary')
