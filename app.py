import os
import streamlit as st
import fitz  # PyMuPDF
import PyPDF2
import imaplib
import email
from email.header import decode_header
import shutil
import google.generativeai as genai
from dotenv import load_dotenv

# ----------------- Config -----------------
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")

EMAIL = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

DOWNLOAD_FOLDER = "attachments"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Pre-existing folders for domains
DOMAIN_FOLDERS = {
    "Finance": "folders/Finance",
    "Education": "folders/Education",
    "Health": "folders/Health",
    "Technology": "folders/Technology",
    "Other": "folders/Other"
}

# ----------------- Functions -----------------
def ask_gemini(prompt: str) -> str:
    response = model.generate_content(prompt)
    return response.text

def extract_text_from_pdf_stream(file) -> str:
    reader = PyPDF2.PdfReader(file)
    return "".join([page.extract_text() or "" for page in reader.pages])

def extract_text_from_pdf_file(file_path: str) -> str:
    doc = fitz.open(file_path)
    return "".join([page.get_text() for page in doc])

def move_file_to_domain_folder(file_path: str, domain: str):
    if not os.path.exists(file_path):
        st.warning(f"File not found: {file_path}")
        return
    folder = DOMAIN_FOLDERS.get(domain, DOMAIN_FOLDERS["Other"])
    os.makedirs(folder, exist_ok=True)
    shutil.move(file_path, os.path.join(folder, os.path.basename(file_path)))

def identify_domain(text: str) -> str:
    prompt = f"""
    Read the following text and return ONLY one word from this list:
    - Education
    - Finance
    - Health
    - Technology
    - Other
    
    Text:
    {text[:1000]}
    """
    response = model.generate_content(prompt)
    domain = response.text.strip()

    # Normalize result
    domain = domain.capitalize()
    if domain not in ["Education", "Finance", "Health", "Technology"]:
        domain = "Other"
    return domain

# ----------------- Gmail Functions -----------------
def get_unread_emails():
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(EMAIL, APP_PASSWORD)
    imap.select("inbox")
    status, messages = imap.search(None, 'UNSEEN')
    mail_ids = messages[0].split()
    emails = []

    for mail_id in mail_ids:
        status, msg_data = imap.fetch(mail_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject, encoding = decode_header(msg.get("Subject", ""))[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or "utf-8", errors="ignore")

                email_text = ""
                attachments = []

                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = part.get("Content-Disposition")

                    if content_type == "text/plain" and content_disposition is None:
                        email_text += part.get_payload(decode=True).decode(errors="ignore")

                    if content_disposition:
                        filename = part.get_filename()
                        if filename:
                            filepath = os.path.join(DOWNLOAD_FOLDER, filename)
                            with open(filepath, "wb") as f:
                                f.write(part.get_payload(decode=True))
                            attachments.append(filepath)
                            if filename.lower().endswith(".pdf"):
                                email_text += "\n" + extract_text_from_pdf_file(filepath)

                emails.append({
                    "subject": subject,
                    "body": email_text,
                    "attachments": attachments
                })

    imap.logout()
    return emails

# ----------------- Streamlit UI -----------------
st.title("🧠 DocuSort AI – Intelligent PDF Analyzer with FastAPI & Gemini")
tabs = st.tabs(["PDF NLP", "Gmail NLP"])

# ---------------- PDF NLP Tab ----------------
with tabs[0]:
    st.header("📄  PDF NLP Tasks")
    uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

    if uploaded_file:
        # Save uploaded PDF to disk
        temp_path = os.path.join(DOWNLOAD_FOLDER, uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        text = extract_text_from_pdf_stream(uploaded_file)
        st.subheader("Extracted Text")
        st.write(text[:1000] + "..." if len(text) > 1000 else text)

        task = st.selectbox("Choose an NLP Task", [
            "Sentiment Analysis",
            "Summarization",
            "Translation",
            "Rewrite",
            "Domain Identification"
        ], key="pdf_task")

        translation_language = None
        if task == "Translation":
            translation_language = st.selectbox(
                "Select Target Language", ["Telugu", "Tamil", "Hindi", "Kannada"], key="pdf_lang"
            )

        if st.button("Run Task on PDF"):
            with st.spinner(f"Running {task}..."):
                if task == "Sentiment Analysis":
                    prompt = f"Analyze the sentiment:\n\n{text}"
                    result = ask_gemini(prompt)
                elif task == "Summarization":
                    prompt = f"Summarize in 5 lines:\n\n{text}"
                    result = ask_gemini(prompt)
                elif task == "Translation":
                    prompt = f"Translate into {translation_language}:\n\n{text}"
                    result = ask_gemini(prompt)
                elif task == "Rewrite":
                    prompt = f"Rewrite clearly:\n\n{text}"
                    result = ask_gemini(prompt)
                elif task == "Domain Identification":
                    result = identify_domain(text)
                    move_file_to_domain_folder(temp_path, result)

            st.subheader(f"Result: {task}")
            st.write(result)

# ---------------- Gmail NLP Tab ----------------
with tabs[1]:
    st.header("📧 Gmail NLP Tasks")
    st.info("Click 'Fetch Unread Emails' to load emails from Gmail.")

    if "emails" not in st.session_state:
        st.session_state.emails = []

    if st.button("Fetch Unread Emails"):
        with st.spinner("Fetching emails..."):
            st.session_state.emails = get_unread_emails()

    emails = st.session_state.emails

    if not emails:
        st.info("No unread emails found.")
    else:
        st.success(f"Found {len(emails)} unread emails.")
        for idx, email_data in enumerate(emails):
            with st.expander(f"{idx+1}. {email_data['subject']}"):
                st.subheader("Email Body")
                st.write(email_data['body'][:1000] + "..." if len(email_data['body']) > 1000 else email_data['body'])

                if email_data['attachments']:
                    st.subheader("Attachments")
                    for file in email_data['attachments']:
                        st.write(file)

                task = st.selectbox("Choose an NLP Task", [
                    "Sentiment Analysis",
                    "Summarization",
                    "Translation",
                    "Rewrite",
                    "Domain Identification"
                ], key=f"email_task_{idx}")

                translation_language = None
                if task == "Translation":
                    translation_language = st.selectbox(
                        "Select Target Language", ["Telugu","Tamil", "Hindi", "Kannada"], key=f"email_lang_{idx}"
                    )

                if st.button(f"Run NLP Task for Email {idx+1}", key=f"run_email_{idx}"):
                    with st.spinner(f"Running {task}..."):
                        text = email_data['body']
                        if task == "Sentiment Analysis":
                            prompt = f"Analyze the sentiment:\n\n{text}"
                            result = ask_gemini(prompt)
                        elif task == "Summarization":
                            prompt = f"Summarize in 5 lines:\n\n{text}"
                            result = ask_gemini(prompt)
                        elif task == "Translation":
                            prompt = f"Translate into {translation_language}:\n\n{text}"
                            result = ask_gemini(prompt)
                        elif task == "Rewrite":
                            prompt = f"Rewrite clearly:\n\n{text}"
                            result = ask_gemini(prompt)
                        elif task == "Domain Identification":
                            result = identify_domain(text)
                            if email_data['attachments']:
                                for file_path in email_data['attachments']:
                                    if os.path.exists(file_path) and file_path.lower().endswith(".pdf"):
                                        move_file_to_domain_folder(file_path, result)

                    st.subheader(f"Result: {task}")
                    st.write(result)
