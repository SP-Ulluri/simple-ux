import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from app_functions import hide_st_ui, authenticate

st.set_page_config(
    page_title="The Simpler Inbox",
    initial_sidebar_state="collapsed"
)

hide_st_ui()
        
def main():
    st.header("Welcome to your Simpler Inbox")
    st.divider()

    if 'credentials' not in st.session_state:
        st.session_state.credentials = None

    if 'connected' not in st.session_state:
        st.session_state.connected = False

    if not st.session_state.connected:
        st.write("**The first step is to connect your Gmail account. Click the button below to get started.**")
        connect_email_button = st.button("Click to connect Gmail account", type="primary")
        st.info("PS: Don't worry - we will not store any of your data and everything is deleted when you close this window.")
        if connect_email_button:
            st.session_state.credentials = authenticate()
            st.session_state.connected = True
            st.rerun()
    else:
        st.success("Great! You're all connected and ready to go. Click next to begin.")
        if st.button("Begin", type='primary'):
            switch_page("vet_senders_a")

# Run the Streamlit app
if __name__ == "__main__":
    main()
