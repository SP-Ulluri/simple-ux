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
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import tempfile

os.environ['OPENAI_API_KEY'] = st.secrets["openai_api_key"]
LLM_MODEL_NAME = "gpt-4-0125-preview"
LLM_TEMPERATURE = 0
INSTRUCTIONS = """
You are an executive assistant for a busy user who struggles to stay on top of their emails.

Your job is to summarise the content and action items (if any) of the email you are given - make it short, punchy and action oriented.

Your response will be displayed to the user in HTML, so your response should always be valid HTML.

Your response should have the following structure:
- A non-clickable <div> to indicate if the email is "Information Only" or "Actionable"
- <h3> Section header "Summary" - short summary of the email content, with information about the sender if relevant.
- <h3> Section header "Actions" - pull out any action items or "call to actions" in the email with clickable buttons for each action item. If no actions required, simply write "No direct actions required."
- Always end with a HTML horizontal line tag <hr>

If the email contains no action items but is simply an information only email, you must start your response with a div as follows:
<div class="info_only_pill" style="background-color: pink; border: none; color: black; padding: 1px 20px; text-align: center; text-decoration: none; display: inline-block; margin: 1px 1px; cursor: pointer; border-radius: 16px;">Information Only</div>

If the email does contain action items, you must start your response with a div as follows:
<div class="actionable_pill" style="background-color: #d9ebf7; border: none; color: black; padding: 1px 20px; text-align: center; text-decoration: none; display: inline-block; margin: 1px 1px; cursor: pointer; border-radius: 16px;">Actionable</div>

Format any clickable links or "call to actions" in each email's action items as clickable HTML link, formatted as a button as follows:
<a href="[LINK]" target="_blank" rel="noopener noreferrer" style="background-color: rgb(0, 114, 177); color: white; padding: 10px 20px; text-align: center; text-decoration: none; display: inline-block; border-radius: 5px;">[BUTTON TEXT]</a>
"""


def get_llm_output(context, instructions, model_name, temperature):
    prompt = ChatPromptTemplate.from_template(instructions)
    model = ChatOpenAI(model_name=model_name, temperature=temperature)
    chain = (
            {"user_context": RunnablePassthrough()}
            | prompt
            | model
            | StrOutputParser()
    )
    st.write(chain)
    llm_output = chain.invoke(context)

    return llm_output


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']
# current_dir = os.path.dirname(os.path.realpath(__file__))
# credentials_path = os.path.join(current_dir, 'credentials.json')

# Initialize session state
if 'credentials' not in st.session_state:
    st.session_state.credentials = None



def authenticate():
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
            creds = flow.run_local_server(port=0, launch_browser=True)
            os.remove(credentials_file_path)
        st.session_state.credentials = creds.to_json()
    return creds


# Retrieve unread emails
def get_unread_emails(credentials, num_emails):
    service = build('gmail', 'v1', credentials=credentials)
    try:
        results = service.users().messages().list(userId='me', labelIds=['INBOX', 'UNREAD'], maxResults=num_emails).execute()
        messages = results.get('messages', [])
        return messages
    except HttpError as e:
        st.error(f'An error occurred: {e}')


# Get details of the first unread email
def get_unread_email_details(credentials, num_emails):
    messages = get_unread_emails(credentials, num_emails)
    if messages:
        email_details_list = []
        for i in range(num_emails):
            message = messages[i]
            message_id = message['id']
            service = build('gmail', 'v1', credentials=credentials)
            message_data = service.users().messages().get(userId='me', id=message_id).execute()
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
            email_details_list.append(email_details)
        return email_details_list
    else:
        return None


# Send email reply
def send_email_reply(reply_text, sender, credentials):
    message = MIMEText(reply_text)
    message['to'] = sender
    message['from'] = 'me'
    message['subject'] = 'Re: Your Email Subject'
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    service = build('gmail', 'v1', credentials=credentials)
    try:
        message = service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        st.success('Reply sent successfully!')
    except HttpError as e:
        st.error(f'An error occurred while sending the reply: {e}')


# Define Streamlit app
def main():
    st.title("Simpler UX Demo")
    st.write("Start by connecting your Gmail account. We will not store any of your data - everything is deleted when you close this window.")

    # Display button to connect Gmail account
    authentication_button = st.button("Click to connect Gmail account")
    credentials = None

    # Check if the authentication button is clicked
    if authentication_button:
        credentials = authenticate()
        st.success("Gmail account successfully connected!")

        # Display details of the first unread email
        num_emails = 3
        with st.spinner("Fetching most recent unread emails..."):
            email_details = get_unread_email_details(credentials=credentials, num_emails=num_emails)
        st.success("Fetched last 3 unread emails!")
        if email_details:
            for i in range(num_emails):
                st.write(f"# Email {i + 1}")
                with st.spinner(f"Scanning Email {i+1} for important information..."):
                    email_context = f"From: {email_details[i].get('From')}\n\nSubject: {email_details[i].get('Subject')}\n\nBody: {email_details[i].get('Body')}"

                    llm = ChatOpenAI(model=LLM_MODEL_NAME, temperature=LLM_TEMPERATURE)

                    prompt = ChatPromptTemplate.from_messages(
                        [
                            (
                                "system",
                                INSTRUCTIONS,
                            ),
                            ("human", "{input}"),
                        ]
                    )

                    chain = prompt | llm

                st.write(chain.invoke({"input": email_context}).content, unsafe_allow_html=True)

            # # Allow user to type a response
            # st.header("Type your response:")
            # reply_text = st.text_area("Enter your reply here:")
            #
            # # Button to send the reply
            # if st.button("Send Reply"):
            #     # sender = email_details.get('From')
            #     sender = "ulluri@gmail.com"
            #     send_email_reply(reply_text, sender, credentials)


# Run the Streamlit app
if __name__ == "__main__":
    main()
