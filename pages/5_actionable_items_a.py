import streamlit as st
from app_functions import hide_st_ui, get_ai_summary
from streamlit_extras.switch_page_button import switch_page
import time

hide_st_ui()

st.header("Part 3 of 3: Emails Requiring Actions")
st.progress(float(0/5), text=None)
st.divider()

if 'email_index' not in st.session_state:
    st.session_state.email_index = 0

st.write("**This is where the Radically Simple approach really comes to the fore. We'll show you one email at a time and present you with clear options on how to proceed. All you have to do is make one decision at a time. You've got this!**")

if st.button(f"Begin", type='primary'):
    with st.spinner("Preparing emails for your review..."):
        st.session_state.actionable_unread_emails = [i for i in st.session_state.unread_emails_details if
                                                     i["actionable"] == '1']
    switch_page("actionable_items_b")


