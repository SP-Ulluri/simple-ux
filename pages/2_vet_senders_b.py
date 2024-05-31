import streamlit as st
from app_functions import hide_st_ui
from streamlit_extras.switch_page_button import switch_page
import time

hide_st_ui()

st.header("Part 1 of 3: Vetting Your Contacts")
st.progress(float(2/3), text=f"{round(100*float(2/3))}%")
st.divider()

if 'sender_filtering_form_submitted' not in st.session_state:
    st.session_state.sender_filtering_form_submitted = False

if 'toggle_states' not in st.session_state:
    st.session_state.toggle_states = {}

senders_to_vet = st.session_state.senders - st.session_state.read_senders

st.success("**✅ Your inbox audit is complete!**")

sender_filtering_form_container = st.empty()

with sender_filtering_form_container.form(key="sender_filtering"):
    st.info("📨 The following email addresses have tried to message you recently. Use the toggle buttons to decide if you want to hear from them or not, and we'll take care of the rest.")

    for sender in senders_to_vet:
        st.session_state.toggle_states[sender] = st.toggle(label=sender, key=sender, value=True)

    submitted = st.form_submit_button("Submit choices", type="primary")
    if submitted:
        switch_page("vet_senders_c")
