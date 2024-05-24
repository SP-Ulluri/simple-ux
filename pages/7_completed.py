import streamlit as st
from app_functions import hide_st_ui

hide_st_ui()

st.session_state.email_index += 1

st.header("Congratulations!")
st.divider()

st.success("**You've completed your inbox management for today!")
st.balloons()
st.write("You can now exit this page.")

