import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import os

# Load API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use Gemini model
model = genai.GenerativeModel("gemini-2.0-flash")

st.title("📄 PDF NLP App with Gemini")

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file is not None:
    # Extract text from PDF
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()

    st.subheader("Extracted Text")
    st.write(text[:1000] + "..." if len(text) > 1000 else text)

   # Buttons for different NLP tasks
task = st.selectbox("Choose an NLP Task", [
    "Sentiment Analysis",
    "Summarization",
    "Translation",
    "Rewrite",
    "Domain Identification"
])

translation_language = None
if task == "Translation":
    translation_language = st.selectbox(
        "Select Target Language",
        ["Telugu", "Hindi", "Kannada"]
    )

if st.button("Run Task"):
    if task == "Sentiment Analysis":
        prompt = f"Analyze the sentiment of the following text:\n\n{text}"
    elif task == "Summarization":
        prompt = f"Summarize the following text:\n\n{text}"
    elif task == "Translation":
        prompt = f"Translate the following text to {translation_language}:\n\n{text}"
    elif task == "Rewrite":
        prompt = f"Rewrite the following text in a clearer and simpler way:\n\n{text}"
    elif task == "Domain Identification":
        prompt = f"Identify the domain/topic of the following text:\n\n{text}"

    response = model.generate_content(prompt)
    st.subheader(f"Result: {task}")
    st.write(response.text)

        