# ResumeIQ — Structured Data Extractor

A polished Streamlit web application that extracts candidate contact details, skills, work experience and education from PDF, DOCX and TXT resumes, validates the result with Pydantic, highlights missing fields and exports clean JSON.

## Features
- Upload PDF, DOCX or TXT resumes.
- Built-in sample resume for a quick demo.
- Extracts name, email, phone, location, summary, skills, experience and education.
- Pydantic schema validation and explicit missing-field reporting.
- Safe handling of unreadable files and unsupported formats.
- Download extracted information as formatted JSON.
- No API key required: this demo uses transparent rule-based extraction.

## 1. Requirements
- Python 3.10 or newer
- Internet connection for installing packages

## 2. Run on macOS
Open Terminal and move into the project folder:

```bash
cd structured_data_extractor
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

A browser tab will open. If it does not, visit `http://localhost:8501`.

## 3. Run on Windows
Open Command Prompt or PowerShell in this project folder:

```bat
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Open `http://localhost:8501` if the browser does not open automatically.

## 4. Demo walkthrough
1. Launch the app.
2. Keep **Use built-in sample resume** enabled.
3. Click **Extract structured data**.
4. Review the JSON, candidate overview and validation tabs.
5. Upload your own PDF, DOCX or TXT resume and repeat.
6. Click **Download validated JSON** to save the output.

## Output schema

```json
{
  "contact": {
    "full_name": "Arun Kumar",
    "email": "arun.kumar@example.com",
    "phone": "+91 98765 43210",
    "location": "Chennai, Tamil Nadu"
  },
  "summary": "Computer Science graduate...",
  "skills": ["Python", "Java", "SQL"],
  "experience": [],
  "education": [],
  "validation": {
    "is_valid": false,
    "missing_fields": []
  }
}
```

## Project structure

```text
structured_data_extractor/
├── app.py              # Streamlit UI
├── extractor.py        # Text extraction, parsing and validation
├── requirements.txt
├── README.md
├── .env.example
└── .gitignore
```

## Notes and limitations
- This is a portfolio/demo parser, not a production hiring decision system.
- Resume layouts vary; always review extracted data before using it.
- Scanned/image-only PDFs need OCR and are reported as unreadable if no text is embedded.
- The parser deliberately leaves unavailable information as `null` or an empty list rather than inventing it.
- For production use, add OCR, broader skill taxonomy, robust date/entity extraction, file-size limits, authentication, audit logging and privacy controls.
- Avoid uploading resumes containing personal data unless you have permission to process them.
