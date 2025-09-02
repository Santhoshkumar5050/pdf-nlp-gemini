import os
import imaplib
import email
from email.header import decode_header
import fitz  # PyMuPDF
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

def extract_text_from_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    return "".join([page.get_text() for page in doc])

def move_file_to_domain_folder(file_path: str, domain: str):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    folder = DOMAIN_FOLDERS.get(domain, DOMAIN_FOLDERS["Other"])
    os.makedirs(folder, exist_ok=True)
    shutil.move(file_path, os.path.join(folder, os.path.basename(file_path)))

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
                                email_text += "\n" + extract_text_from_pdf(filepath)

                emails.append({
                    "subject": subject,
                    "body": email_text,
                    "attachments": attachments
                })

    imap.logout()
    return emails

# ----------------- Main -----------------
if __name__ == "__main__":
    emails = get_unread_emails()
    if not emails:
        print("No unread emails found.")
    else:
        print(f"Found {len(emails)} unread emails.\n")
        for idx, email_data in enumerate(emails):
            print(f"{idx+1}. Subject: {email_data['subject']}")
            print(f"Body:\n{email_data['body'][:500]}...\n")
            if email_data['attachments']:
                print("Attachments:", email_data['attachments'])

            # NLP Analysis
            sentiment = ask_gemini(f"Analyze sentiment:\n\n{email_data['body']}")
            summary = ask_gemini(f"Summarize in 5 lines:\n\n{email_data['body']}")
            rewritten = ask_gemini(f"Rewrite clearly:\n\n{email_data['body']}")
            domain = ask_gemini(f"Identify domain/topic:\n\n{email_data['body']}").strip().split("\n")[0].capitalize()

            # Auto-save PDFs to domain folder
            if email_data['attachments']:
                if domain not in DOMAIN_FOLDERS:
                    domain = "Other"
                for file_path in email_data['attachments']:
                    if os.path.exists(file_path) and file_path.lower().endswith(".pdf"):
                        move_file_to_domain_folder(file_path, domain)

            print("Sentiment:", sentiment)
            print("Summary:", summary)
            print("Rewritten:", rewritten)
            print("Domain:", domain)
            print("\n" + "-"*50 + "\n")
