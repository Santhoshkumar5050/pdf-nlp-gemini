import os
import google.generativeai as genai
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from dotenv import load_dotenv
import PyPDF2

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI(title="PDF NLP Project with Gemini")

# Utility function for Gemini
def ask_gemini(prompt: str):
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text


# Function to extract text from uploaded PDF
def extract_pdf_text(file) -> str:
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# ---- API Endpoints ---- #

@app.post("/analyze_pdf/")
async def analyze_pdf(
    pdf_file: UploadFile = File(...),
    target_lang: str = Form(None)
):
    # Extract text from PDF
    pdf_text = extract_pdf_text(pdf_file.file)

    if not pdf_text.strip():
        return {"error": "No text could be extracted from the PDF."}
        

    # 1. Sentiment
    sentiment_prompt = f"Analyze the sentiment (Positive, Negative, Neutral) of this text:\n\n{pdf_text}"
    sentiment = ask_gemini(sentiment_prompt)

    # 2. Summary
    summary_prompt = f"Summarize this text in 5-6 lines:\n\n{pdf_text}"
    summary = ask_gemini(summary_prompt)

    # 3. Translation
    translation = None
    if target_lang:
        translation_prompt = f"Translate this text into {target_lang}:\n\n{pdf_text}"
        translation = ask_gemini(translation_prompt)

    # 4. Rewrite
    rewrite_prompt = f"Rewrite the following text in a clearer and more natural way:\n\n{pdf_text}"
    rewritten = ask_gemini(rewrite_prompt)

    # 5. Domain Identification
    domain_prompt = f"Identify the main domain/topic of this text (e.g., Technology, Healthcare, Finance, Education, etc.):\n\n{pdf_text}"
    domain = ask_gemini(domain_prompt)

    return {
        "sentiment": sentiment,
        "summary": summary,
        "translation": translation,
        "rewritten": rewritten,
        "domain": domain

    }
