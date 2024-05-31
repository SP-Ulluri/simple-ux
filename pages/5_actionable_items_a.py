import streamlit as st
from app_functions import hide_st_ui
from streamlit_extras.switch_page_button import switch_page
import time

hide_st_ui()

st.header("Part 3 of 3: Emails Requiring Actions")
st.progress(float(0/5), text=None)
st.divider()

st.write("**This is where the Radically Simple approach really comes to the fore. We'll show you one email at a time and present you with clear options on how to proceed. All you have to do is make one decision at a time. You've got this!**")

if st.button(f"Begin", type='primary'):
    switch_page("actionable_items_b")
