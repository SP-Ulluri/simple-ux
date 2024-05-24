import streamlit as st
from app_functions import hide_st_ui, get_email_category
from streamlit_extras.switch_page_button import switch_page
import time

hide_st_ui()

st.header("Part 2 of 3: Newsfeed")
st.divider()

st.write("**This is your Newsfeed. It's a brief summary of all the 'information only' non-actionable emails in your inbox.**")
st.write("**Feel free to browse through them, and then click the button at bottom of the page to take a crack at the really important stuff.**")

with st.container(height=500):
    for index, email in enumerate(st.session_state.unread_emails_details):
        st.session_state.unread_emails_details[index]['actionable'] = get_email_category(email)
        if get_email_category(email) == '0':
            with st.expander(label=f"Email from {email.get('From')} about {email.get('Subject')}"):
                st.write(f"**Details:** {email.get('Body')}")

if st.button("Proceed to Actionable Emails", type='primary'):
    switch_page("actionable_items_a")
