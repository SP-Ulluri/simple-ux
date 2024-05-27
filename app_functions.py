from streamlit.components.v1 import html
from google_auth_oauthlib.flow import InstalledAppFlow
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import streamlit as st
import json
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import tempfile
from datetime import datetime, timedelta
import base64

os.environ['OPENAI_API_KEY'] = st.secrets["openai_api_key"]
LLM_MODEL_NAME = "gpt-4o"
LLM_TEMPERATURE = 0
CATEGORISE_INSTRUCTIONS = """
You are an executive assistant for a busy user who struggles to stay on top of their emails.\n
Your only job is to read the contents of an email and categorise it into one of three types:\n
- info_only (if the email contains no action items but is simply an information only email)\n
- actionable (if the email does contain action items or clear call to actions that you deem the user needs to attend to)\n
- newsletter (if the email is a newsletter as inferred from the content, sender, metadata etc.)\n
You must output only info_only, actionable or newsletter in your response.\n
Do not output anything else.
"""


def get_email_category(email_details):
    email_context = f"From: {email_details.get('From')}\n\nSubject: {email_details.get('Subject')}\n\nBody: {email_details.get('Body')}"
    llm = ChatOpenAI(model=LLM_MODEL_NAME, temperature=LLM_TEMPERATURE)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                CATEGORISE_INSTRUCTIONS,
            ),
            ("human", "{input}"),
        ]
    )
    chain = prompt | llm
    return str(chain.invoke({"input": email_context}).content)


SUMMARISE_ACTIONS_INSTRUCTIONS = """
You are an executive assistant for a busy user who struggles to stay on top of their emails.

Your job is to summarise the content and action items of the email you are given - make it short, punchy and action-oriented.

Your response will be displayed to the user in HTML, so your response should always be valid HTML.

Your response should have the following structure:
- <h3> Section header "Summary" - short summary of the email content, with information about the sender if relevant, written as if you are a personal assistant explaining to the user as simply as possible ONLY the information they need to know to make a decision.
- <h3> Section header "Actions" - pull out any action items or "call to actions" in the email with clickable buttons for each action item.

Format any clickable links or "call to actions" in each email's action items as clickable HTML link, formatted as a button as follows:
<a href="[LINK]" target="_blank" rel="noopener noreferrer" style="background-color: rgb(0, 114, 177); color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px;">[BUTTON TEXT]</a>
"""


def get_summary_actions(email_details):
    email_context = f"From: {email_details.get('From')}\n\nSubject: {email_details.get('Subject')}\n\nBody: {email_details.get('Body')}"
    llm = ChatOpenAI(model=LLM_MODEL_NAME, temperature=LLM_TEMPERATURE)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                SUMMARISE_ACTIONS_INSTRUCTIONS,
            ),
            ("human", "{input}"),
        ]
    )
    chain = prompt | llm
    return chain.invoke({"input": email_context}).content


SUMMARISE_INFO_ONLY_INSTRUCTIONS = """
You are an executive assistant for a busy user who struggles to stay on top of their emails.

Your job is to summarise the content of the email you are given - make it short, punchy and action-oriented.

Your response will be displayed to the user in HTML, so your response should always be valid HTML.

Your response should have the following structure:
- <h3> Section header "Summary" - short summary of the email content, with information about the sender if relevant, written as if you are a personal assistant explaining to the user as simply as possible ONLY the information they need to know.
"""


def get_summary_info_only(email_details):
    email_context = f"From: {email_details.get('From')}\n\nSubject: {email_details.get('Subject')}\n\nBody: {email_details.get('Body')}"
    llm = ChatOpenAI(model=LLM_MODEL_NAME, temperature=LLM_TEMPERATURE)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                SUMMARISE_INFO_ONLY_INSTRUCTIONS,
            ),
            ("human", "{input}"),
        ]
    )
    chain = prompt | llm
    return chain.invoke({"input": email_context}).content


def fetch_gmail_data(credentials, num_days):
    # Deserialize the credentials JSON string back to a Credentials object
    creds = Credentials.from_authorized_user_info(json.loads(credentials))

    service = build('gmail', 'v1', credentials=creds)
    try:
        # Calculate date num_days ago
        date_days_ago = (datetime.utcnow() - timedelta(days=num_days)).strftime('%Y/%m/%d')
        query = f'after:{date_days_ago}'

        page_token = None
        senders = set()
        unread_senders = set()
        read_senders = set()
        email_details = []

        while True:
            results = service.users().messages().list(
                userId='me',
                q=query,
                labelIds=['INBOX'],
                pageToken=page_token
            ).execute()

            messages = results.get('messages', [])
            if not messages:
                break

            for message in messages:
                message_id = message['id']
                message_data = service.users().messages().get(userId='me', id=message_id).execute()
                payload = message_data['payload']
                headers = payload['headers']

                # Extract relevant headers
                email_info = {}
                for header in headers:
                    if header['name'] == 'From':
                        email_info['From'] = header['value']
                        senders.add(header['value'])
                        if 'UNREAD' in message_data['labelIds']:
                            unread_senders.add(header['value'])
                            email_details.append(email_info)
                        else:
                            read_senders.add(header['value'])
                    elif header['name'] == 'Subject':
                        email_info['Subject'] = header['value']
                    elif header['name'] == 'Date':
                        email_info['Received Timestamp'] = header['value']

                # Get email body
                body = None
                if 'parts' in payload:
                    for part in payload['parts']:
                        if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                            body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                            break
                        elif part['mimeType'] == 'text/html' and 'data' in part['body']:
                            body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                elif 'body' in payload and 'data' in payload['body']:
                    body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

                email_info['Body'] = body

            page_token = results.get('nextPageToken')
            if not page_token:
                break

        return senders, read_senders, unread_senders, email_details

    except HttpError as e:
        print(f'An error occurred: {e}')
        return None, None, None, None


def hide_st_ui():
    hide_st_ui_markdown = """
    <style>
        section[data-testid="stSidebar"][aria-expanded="true"]{
            display: none;
        }
        div[data-testid="collapsedControl"]{
            display: none;
        }
    </style>
    """
    st.markdown(hide_st_ui_markdown, unsafe_allow_html=True)


def open_page(url):
    open_script = """
        <script type="text/javascript">
            window.open('%s', '_blank').focus();
        </script>
    """ % (url)
    html(open_script)

# def open_page(url):
#     st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)


def authenticate():
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']
    creds = None
    if st.session_state.credentials is not None:
        creds_dict = json.loads(st.session_state.credentials)  # Convert string to dictionary
        creds = Credentials.from_authorized_user_info(creds_dict, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            credentials = json.loads(st.secrets["gcp"]["credentials"])
            temp_dir = tempfile.gettempdir()
            credentials_file_path = os.path.join(temp_dir, "credentials.json")
            with open(credentials_file_path, "w") as f:
                json.dump(credentials, f)
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file_path, SCOPES)
            creds = flow.run_local_server(port=0)
            os.remove(credentials_file_path)
        st.session_state.credentials = creds.to_json()
    st.success("Gmail account successfully connected!")
    return creds

