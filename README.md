# 📂 DocuSort AI – Intelligent PDF Analyzer with FastAPI & Gemini

DocuSort AI is an **AI-powered PDF automation tool** that connects to Gmail, reads unread emails, downloads attached PDF files, **analyzes their content with Google Gemini**, and **automatically classifies them** into predefined folders like:

- 📘 Education  
- 💰 Finance  
- ❤️ Health  
- 💻 Technology  
- 📂 Other  

This project helps you **save time** by organizing and sorting important documents instantly without manual effort.

---

## 🚀 Features
- ✅ **Automatic Email Fetching** – Reads unread emails and extracts PDF attachments.  
- ✅ **AI-Powered Classification** – Uses Gemini NLP to analyze PDF content.  
- ✅ **Smart Auto-Sorting** – Moves files into the correct domain folder.  
- ✅ **FastAPI Backend** – API endpoints to run the workflow and manage documents.  
- ✅ **Custom Folders** – Supports predefined and user-created folders.  
- ✅ **Extensible** – Can be extended to support multi-language translation and further processing.  

---

## 🛠️ Tech Stack
- **Python 3.10+**  
- **FastAPI** – Backend framework  
- **Google Gemini API** – NLP & AI-powered classification  
- **IMAP (Gmail API)** – Fetching unread emails  
- **PyPDF2** – Extracting text from PDF  
- **shutil / os** – File handling and organization

## 📂 Project Structure

📦 pdf-nlp-gemini
┣ 📂 attachments # Temporary storage for downloaded PDFs
┣ 📂 folders
┃ ┣ 📂 Education
┃ ┣ 📂 Finance
┃ ┣ 📂 Health
┃ ┣ 📂 Technology
┃ ┗ 📂 Other
┣ 📜 app.py # FastAPI app with endpoints
┣ 📜 gmail_pdf_reader.py# Gmail integration & PDF extraction
┣ 📜 main.py # Project entry point
┣ 📜 requirements.txt # Python dependencies
┗ 📜 README.md # Project documentation 



👨‍💻 Author

Santhosh Kumar
🚀 Passionate about AI, NLP, and automation.
📧 Reach me at: [Email:santhoshkumart2580@gmail.com/github link:## 🔗 Project Repository

You can explore the full project here:  
👉 [GitHub Repository](https://github.com/Santhoshkumar5050/pdf-nlp-gemini)
]
---


