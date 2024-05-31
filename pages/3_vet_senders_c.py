import streamlit as st
from app_functions import hide_st_ui, fetch_gmail_data
from streamlit_extras.switch_page_button import switch_page
import time

hide_st_ui()

st.header("Part 1 of 3: Vetting Your Contacts")
st.progress(float(3/3), text=f"{round(100*float(3/3))}%")
st.divider()

if 'show_preference_saving_spinner' not in st.session_state:
    st.session_state.show_preference_saving_spinner = True

if st.session_state.show_preference_saving_spinner:
    with st.spinner(f"Saving your preferences..."):
        time.sleep(2)
st.session_state.show_preference_saving_spinner = False

st.info("**Okay, your preferences have been saved.**")
col1, col2 = st.columns(2)
want_to_hear_from_text = ''.join(
    ['- ' + key + '\n' for key in st.session_state.toggle_states if
     st.session_state.toggle_states[key]]
)
archive_addresses_text = ''.join(
    ['- ' + key + '\n' for key in st.session_state.toggle_states if not
    st.session_state.toggle_states[key]]
)
with col1:
    st.success(f"We'll let you know of important email from:\n{want_to_hear_from_text}")
with col2:
    st.error(f"We'll automatically archive email from:\n{archive_addresses_text}")

st.write("**Next, we'll show you your Information Only emails. Click the button to proceed.**")
if st.button("Go to Information Only Emails", type='primary'):
    switch_page("info_only_items")

