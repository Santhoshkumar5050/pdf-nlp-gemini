import os
import shutil
import PyPDF2
import google.generativeai as genai
from fastapi import FastAPI, UploadFile, File, Form
from dotenv import load_dotenv

# ----------------- Config -----------------
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
app = FastAPI(title="PDF NLP Project with Gemini")

# Pre-existing folders for domains
DOMAIN_FOLDERS = {
    "Finance": "folders/Finance",
    "Education": "folders/Education",
    "Health": "folders/Health",
    "Technology": "folders/Technology",
    "Other": "folders/Other"
}

# ----------------- Utility Functions -----------------
def ask_gemini(prompt: str):
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text

def extract_pdf_text(file) -> str:
    reader = PyPDF2.PdfReader(file)
    return "".join([page.extract_text() or "" for page in reader.pages])

def move_file_to_domain_folder(file_path: str, domain: str):
    if not os.path.exists(file_path):
        return
    folder = DOMAIN_FOLDERS.get(domain, DOMAIN_FOLDERS["Other"])
    os.makedirs(folder, exist_ok=True)
    shutil.move(file_path, os.path.join(folder, os.path.basename(file_path)))

def identify_domain(text: str) -> str:
    model = genai.GenerativeModel("gemini-2.0-flash")
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

# ----------------- API Endpoint -----------------
@app.post("/analyze_pdf/")
async def analyze_pdf(
    pdf_file: UploadFile = File(...),
    target_lang: str = Form(None)
):
    temp_path = f"temp_{pdf_file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await pdf_file.read())

    pdf_text = extract_pdf_text(open(temp_path, "rb"))
    if not pdf_text.strip():
        return {"error": "No text could be extracted from the PDF."}

    # NLP Tasks
    sentiment = ask_gemini(f"Analyze the sentiment (Positive, Negative, Neutral):\n\n{pdf_text}")
    summary = ask_gemini(f"Summarize in 5-6 lines:\n\n{pdf_text}")
    translation = ask_gemini(f"Translate into {target_lang}:\n\n{pdf_text}") if target_lang else None
    rewritten
