import streamlit as st
from app_functions import hide_st_ui, fetch_gmail_data, get_email_category
from streamlit_extras.switch_page_button import switch_page

hide_st_ui()

st.header("Part 1 of 3: Vetting Your Contacts")
st.progress(float(2/3), text=None)
st.divider()

if 'num_days' not in st.session_state:
    st.session_state.num_days = 5

# if st.session_state.num_days == 0:
#     with st.form(key="num_days_form"):
#         st.session_state.num_days = st.slider("How many days of your inbox should we audit?", 1, 30, 5)
#         num_days_submitted = st.form_submit_button("Submit choices", type="primary")
#         if num_days_submitted:
#             st.rerun()
# else:
if 'sender_filtering_form_submitted' not in st.session_state:
    st.session_state.sender_filtering_form_submitted = False

if 'toggle_states' not in st.session_state:
    st.session_state.toggle_states = {}

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

if st.session_state.show_auditing_spinner:
    with st.spinner(f"Auditing the last {st.session_state.num_days} days of emails..."):
        st.session_state.senders, st.session_state.read_senders, st.session_state.unread_senders, st.session_state.unread_emails_details = fetch_gmail_data(credentials=st.session_state.credentials, num_days=st.session_state.num_days)
        for index, email in enumerate(st.session_state.unread_emails_details):
            email_category = get_email_category(email)
            if email_category == 'newsletter':
                st.session_state.newsletter_unread_emails.append(email)
            elif email_category == 'info_only':
                st.session_state.info_only_unread_emails.append(email)
            elif email_category == 'actionable':
                st.session_state.actionable_unread_emails.append(email)
            elif email_category not in ['actionable', 'info_only', 'newsletter']:
                st.write(f"Unexpected value returned: {email_category}")
st.session_state.show_auditing_spinner = False

senders_to_vet = st.session_state.senders - st.session_state.read_senders

sender_filtering_form_container = st.empty()

with sender_filtering_form_container.form(key="sender_filtering"):
    st.write(
        "The following email addresses have tried to message you recently. Use the toggle buttons to decide if you want to hear from them or not, and we'll take care of the rest.")

    for sender in senders_to_vet:
        st.session_state.toggle_states[sender] = st.toggle(label=sender, key=sender, value=True)

    submitted = st.form_submit_button("Submit choices", type="primary")
    if submitted:
        switch_page("vet_senders_c")


