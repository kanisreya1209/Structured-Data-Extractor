# 🚀 ResumeIQ – Structured Data Extractor

### Transform Resumes into Structured, Validated Candidate Profiles

## 📌 Project Overview

ResumeIQ is a Python-based resume parsing and structured data extraction application designed to simplify recruitment workflows. It extracts important candidate information from PDF, DOCX, and TXT resumes and converts unstructured resume content into organized, validated JSON data.

The application also provides ATS (Applicant Tracking System) analysis to help evaluate resume content and identify areas for improvement.

## ✨ Key Features

- **Resume Upload:** Supports PDF, DOCX, and TXT formats.
- **Contact Information Extraction:** Extracts candidate name, email, phone number, and location.
- **Skills Detection:** Identifies technical and professional skills.
- **Experience Extraction:** Organizes employment history, roles, companies, and descriptions.
- **Education Extraction:** Identifies academic qualifications.
- **Structured JSON Output:** Converts extracted information into clean JSON.
- **Data Validation:** Uses Pydantic to validate extracted information and highlight missing fields.
- **ATS Resume Analysis:** Evaluates resume content and provides an ATS analysis report.
- **Sample Resume:** Includes a built-in sample for testing.

## 🛠️ Technologies Used

- Python
- Streamlit
- FastAPI
- Pydantic
- HTML5
- CSS3
- JavaScript
- PDFPlumber
- Python-docx

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/kanisreya1209/Structured-Data-Extractor.git
cd Structured-Data-Extractor
```

### 2. Create a Virtual Environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

For the Streamlit interface, install Streamlit separately:

```bash
pip install streamlit
```

### 4. Run the Application

**Streamlit interface:**
```bash
streamlit run app.py
```

**FastAPI web application:**
```bash
uvicorn server:app --reload
```

Open the application at:

- Streamlit: http://localhost:8501
- FastAPI: http://127.0.0.1:8000
- API documentation: http://127.0.0.1:8000/docs

## 📂 Project Structure

```text
Structured-Data-Extractor/
│
├── app.py
├── server.py
├── extractor.py
├── ats_checker.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── templates/
│   └── index.html
│
├── static/
│   ├── css/
│   │   └── app.css
│   └── js/
│       └── app.js
│
└── tests/
    └── test_extractor.py
```

## 🎯 Project Objective

To automate resume information extraction, minimize manual data entry, improve data organization, and simplify the initial resume screening process through structured data processing and validation.

## 🔒 Privacy and Security

- No external LLM API key is required for the current rule-based extraction workflow.
- Uploaded resumes are processed by the application.
- Personal information should be handled responsibly.
- Avoid uploading confidential candidate documents without permission.

## ⚠️ Limitations

- Extraction accuracy depends on resume formatting and text quality.
- Scanned image-based PDFs may require OCR support.
- Extracted information should be reviewed before recruitment decisions.
- ATS analysis is an assistive tool, not a guarantee of hiring success.

## 👩‍💻 Developer

**Kani Sreya Raam Chander**

GitHub: https://github.com/kanisreya1209

## ⭐ Acknowledgement

Developed as part of the Beginner Level Task 2 at Nexlevr.

---

⭐ If you find this project useful, consider giving this repository a star!
