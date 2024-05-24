from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
import base64
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
import streamlit as st
import json
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import tempfile
from datetime import datetime, timedelta
import base64
from streamlit_extras.switch_page_button import switch_page
from app_functions import hide_st_ui, authenticate

st.set_page_config(
    page_title="The Simpler Inbox",
    initial_sidebar_state="collapsed"
)

hide_st_ui()

def get_unread_email_details(credentials, email_index):
    service = build('gmail', 'v1', credentials=credentials)
    try:
        page_token = None
        while True:
            results = service.users().messages().list(userId='me', labelIds=['INBOX', 'UNREAD'],
                                                      pageToken=page_token).execute()
            messages = results.get('messages', [])
            if not messages:
                break
            if len(messages) > email_index:
                message_id = messages[email_index]['id']
                message_data = service.users().messages().get(userId='me', id=message_id).execute()
                # st.write(message_data)
                payload = message_data['payload']
                headers = payload['headers']
                email_details = {}
                for header in headers:
                    if header['name'] == 'From':
                        email_details['From'] = header['value']
                    elif header['name'] == 'Subject':
                        email_details['Subject'] = header['value']
                # Get email body
                if 'parts' in payload:
                    for part in payload['parts']:
                        if part['mimeType'] == 'text/plain':
                            data = part['body']['data']
                            email_body = base64.urlsafe_b64decode(data).decode('utf-8')
                            email_details['Body'] = email_body
                            break  # Stop processing parts after finding the text/plain part
                return [email_details]
            else:
                page_token = results.get('nextPageToken')
                if not page_token:
                    break
    except HttpError as e:
        st.error(f'An error occurred: {e}')
    else:
        return None
        
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
