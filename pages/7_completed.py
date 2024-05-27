import streamlit as st
from app_functions import hide_st_ui

hide_st_ui()

st.session_state.email_index += 1

st.header("Congratulations!")
st.divider()

st.success("**You've completed your inbox management for today!**")
st.balloons()

st.info("**We've put together a 'Newsfeed' of the newsletters you've not yet read if you want to reward yourself for your hard work with some light reading.**")
st.write("**Feel free to browse through them, and exit the page when you're done.**")

st.header("Newsfeed")
with st.container(height=500):
    for email in st.session_state.newsletter_unread_emails:
        with st.expander(label=f"Newsletter from {email.get('From')}: {email.get('Subject')}"):
            st.write(f"**Newsletter Content:** {email.get('Body')}")

st.write("You can now exit this page.")

