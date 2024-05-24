import streamlit as st
from app_functions import hide_st_ui, get_ai_summary
from streamlit_extras.switch_page_button import switch_page

hide_st_ui()

st.session_state.email_index += 1

if st.session_state.email_index == 5:
    switch_page("completed")
else:
    st.header("Part 3 of 3: Emails Requiring Actions")
    st.progress(float((st.session_state.email_index+1)/5), text=None)
    st.divider()

    st.write(get_ai_summary(st.session_state.actionable_unread_emails[st.session_state.email_index]), unsafe_allow_html=True)
    st.write("<br>", unsafe_allow_html=True)

    st.button(f"Proceed to next email", type='primary')
