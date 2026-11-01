"""
ResumeIQ — FastAPI backend
"""
from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from extractor import SAMPLE_RESUME, extract_resume, validate_resume
from ats_checker import run_ats_check

BASE_DIR = Path(__file__).parent

app = FastAPI(
    title="ResumeIQ API",
    description="Structured resume data extraction and validation",
    version="1.0.0",
)

# ── static files ────────────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


# ── pages ────────────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def index():
    return (BASE_DIR / "templates" / "index.html").read_text()


# ── API ──────────────────────────────────────────────────────────────────────
@app.post("/api/extract")
async def api_extract(file: UploadFile = File(...)):
    """Upload a PDF, DOCX or TXT resume and receive structured JSON."""
    allowed = {"pdf", "docx", "txt"}
    ext = (file.filename or "").lower().rsplit(".", 1)[-1]
    if ext not in allowed:
        raise HTTPException(422, f"Unsupported file type '.{ext}'. Upload PDF, DOCX or TXT.")

    data = await file.read()
    if len(data) > 5 * 1024 * 1024:          # 5 MB hard limit
        raise HTTPException(413, "File exceeds the 5 MB limit.")

    try:
        raw = extract_resume(data, file.filename or "upload.txt")
        result = validate_resume(raw)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc

    return JSONResponse(result)


@app.post("/api/extract/sample")
async def api_extract_sample():
    """Return extraction results for the built-in sample resume."""
    raw = extract_resume(SAMPLE_RESUME.encode(), "sample.txt")
    return JSONResponse(validate_resume(raw))


@app.post("/api/ats-check")
async def api_ats_check(file: UploadFile = File(...)):
    """Upload a resume and receive a full ATS analysis report."""
    allowed = {"pdf", "docx", "txt"}
    ext = (file.filename or "").lower().rsplit(".", 1)[-1]
    if ext not in allowed:
        raise HTTPException(422, f"Unsupported file type '.{ext}'.")
    data = await file.read()
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(413, "File exceeds 5 MB limit.")
    try:
        raw     = extract_resume(data, file.filename or "upload.txt")
        result  = validate_resume(raw)
        ats     = run_ats_check(result)
        return JSONResponse({"resume": result, "ats": ats})
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@app.post("/api/ats-check/sample")
async def api_ats_check_sample():
    """ATS check on the built-in sample resume."""
    raw    = extract_resume(SAMPLE_RESUME.encode(), "sample.txt")
    result = validate_resume(raw)
    return JSONResponse({"resume": result, "ats": run_ats_check(result)})


# ── health ────────────────────────────────────────────────────────────────────
@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "ResumeIQ API", "version": "1.0.0"}
