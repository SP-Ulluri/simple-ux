import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from app_functions import hide_st_ui, fetch_gmail_data
from threading import Thread
import time

hide_st_ui()

NUM_DAYS = 1

if 'result_container' not in st.session_state:
    st.session_state.result_container = {'data': None}

# Start fetching data in the background on page load
if 'thread' not in st.session_state:
    st.session_state.thread = Thread(target=fetch_gmail_data, args=(st.session_state.credentials, NUM_DAYS, st.session_state.result_container))
    st.session_state.thread.start()
    st.session_state.start_time = time.time()

if 'senders' not in st.session_state:
    st.session_state.senders = set()

if 'read_senders' not in st.session_state:
    st.session_state.read_senders = set()

if 'unread_senders' not in st.session_state:
    st.session_state.unread_senders = set()

if 'unread_emails_details' not in st.session_state:
    st.session_state.unread_emails_details = ""

if 'show_auditing_spinner' not in st.session_state:
    st.session_state.show_auditing_spinner = True

if 'newsletter_unread_emails' not in st.session_state:
    st.session_state.newsletter_unread_emails = []

if 'info_only_unread_emails' not in st.session_state:
    st.session_state.info_only_unread_emails = []

if 'actionable_unread_emails' not in st.session_state:
    st.session_state.actionable_unread_emails = []

st.header("Part 1 of 3: Vetting Your Contacts")
st.progress(float(1/3), text=f"{round(100*float(1/3))}%")
st.divider()

st.success("Great! You're all connected and ready to go.")

st.write("**Next, we're going to analyse your recent emails to identify people that you've not heard from before so you can decide whether to mark them as trusted senders or not.**")
st.write("**Click the button to start.**")

if st.button("Begin Sender Audit", type="primary"):
    st.session_state.button_press_time = time.time()

    with st.spinner(f"Auditing the last {NUM_DAYS} days of emails..."):
        # time.sleep(3)

        while st.session_state.result_container['data'] is None:
            time.sleep(0.1)

        # st.write("--- %s seconds ---" % (time.time() - st.session_state.start_time))
        # st.write("--- %s seconds ---" % (time.time() - st.session_state.button_press_time))
        # Once done, retrieve the result
        result = st.session_state.result_container['data']

        if result:
            st.session_state.senders, \
            st.session_state.read_senders, \
            st.session_state.unread_senders, \
            st.session_state.newsletter_unread_emails, \
            st.session_state.info_only_unread_emails, \
            st.session_state.actionable_unread_emails = result

            switch_page("vet_senders_b")

