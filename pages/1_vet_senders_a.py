import streamlit as st
from app_functions import hide_st_ui
from streamlit_extras.switch_page_button import switch_page

hide_st_ui()

st.header("Part 1 of 3: Vetting Your Contacts")
st.progress(float(1/3), text=None)
st.divider()

st.success("Great! You're all connected and ready to go.")

st.write("**Next, we're going to analyse your recent emails to identify people that you've not heard from before so you can decide whether to mark them as trusted senders or not.**")
st.write("**Click the button to start.**")

if st.button("Begin Sender Audit", type="primary"):
    switch_page("vet_senders_b")
