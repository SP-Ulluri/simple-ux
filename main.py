from streamlit_extras.switch_page_button import switch_page
from app_functions import hide_st_ui, open_page
import streamlit as st
from google.auth.exceptions import GoogleAuthError
import json
import tempfile
from google_auth_oauthlib.flow import Flow
import os

st.set_page_config(
    page_title="The Simpler Inbox",
    initial_sidebar_state="collapsed"
)

hide_st_ui()


# Define Streamlit app
def main():
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

    st.header("Welcome to your Simpler Inbox")
    st.divider()

    # Initialize session state variables
    if 'credentials' not in st.session_state:
        st.session_state.credentials = None
    if 'auth_state' not in st.session_state:
        st.session_state.auth_state = None
    if 'flow' not in st.session_state:
        st.session_state.flow = None

    # Handle the OAuth callback
    if 'code' in st.query_params:
        try:
            code = st.query_params['code']
            state = st.query_params['state']

            credentials = json.loads(st.secrets["gcp"]["credentials"])
            temp_dir = tempfile.gettempdir()
            credentials_file_path = os.path.join(temp_dir, "credentials.json")
            with open(credentials_file_path, "w") as f:
                json.dump(credentials, f)
            flow = Flow.from_client_secrets_file(credentials_file_path, scopes=SCOPES, state=state)
            os.remove(credentials_file_path)
            flow.redirect_uri = 'https://simple-ux.streamlit.app'
            # flow.redirect_uri = 'http://localhost:8501'

            flow.fetch_token(code=code)
            creds = flow.credentials
            st.session_state.credentials = creds.to_json()
            st.session_state.auth_state = state
            st.session_state.flow = flow
            st.button("Begin", type='primary', on_click=switch_page("vet_senders_a"))

        except GoogleAuthError as e:
            st.error(f"An error occurred: {e}")
    else:
        st.write("**The first step is to connect your Gmail account. Click the button below to get started.**")
        st.info(
            "PS: Don't worry - we will not store any of your data and everything is deleted when you close this window.")

        credentials = json.loads(st.secrets["gcp"]["credentials"])
        temp_dir = tempfile.gettempdir()
        credentials_file_path = os.path.join(temp_dir, "credentials.json")
        with open(credentials_file_path, "w") as f:
            json.dump(credentials, f)
        flow = Flow.from_client_secrets_file(credentials_file_path, scopes=SCOPES)
        os.remove(credentials_file_path)
        flow.redirect_uri = 'https://simple-ux.streamlit.app'
        # flow.redirect_uri = 'http://localhost:8501'

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )

        st.button('Connect your Gmail', type="primary", on_click=open_page(authorization_url))


# Run the Streamlit app
if __name__ == "__main__":
    main()
