import json
import streamlit as st
from extractor import extract_resume, validate_resume, SAMPLE_RESUME

st.set_page_config(page_title="ResumeIQ | Structured Data Extractor", page_icon="✦", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root { --ink:#172033; --muted:#697386; --line:#e7eaf0; --blue:#4f6df5; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; color:var(--ink); }
.stApp { background:linear-gradient(135deg,#f7f9ff 0%,#f8fafc 50%,#f4f7ff 100%); }
.block-container { max-width:1200px; padding-top:2rem; padding-bottom:3rem; }
.hero { background:linear-gradient(115deg,#172554,#263d86 58%,#5369e8); padding:32px 36px; border-radius:22px; color:white; box-shadow:0 18px 45px #243b801f; }
.eyebrow { text-transform:uppercase; letter-spacing:2px; font-size:11px; font-weight:700; color:#b9c8ff; }
.hero h1 { font-family:Manrope,sans-serif; font-size:36px; margin:8px 0 6px; color:white; }
.hero p { color:#dce5ff; margin:0; font-size:15px; }
.metric { background:white; border:1px solid var(--line); border-radius:16px; padding:17px 19px; min-height:96px; }
.metric .num { font:800 26px Manrope,sans-serif; color:#263d86; }
.metric .lbl { color:var(--muted); font-size:12px; margin-top:3px; }
.panel { background:white; border:1px solid var(--line); border-radius:18px; padding:22px; }
.section-title { font:700 18px Manrope,sans-serif; margin:0 0 5px; }
.subtle { color:var(--muted); font-size:13px; }
div[data-testid="stFileUploader"] { background:#f8faff; border:1px dashed #b9c6f5; border-radius:14px; padding:12px; }
.stButton>button { border-radius:10px; font-weight:700; min-height:44px; }
.stDownloadButton>button { border-radius:10px; font-weight:700; }
[data-testid="stTabs"] button { font-weight:700; }
footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="eyebrow">AI-ready recruitment workflow · Project 02</div>
  <h1>ResumeIQ <span style="color:#aebdff">/</span> Structured Data Extractor</h1>
  <p>Turn unstructured resumes into clean, validated candidate profiles — in seconds.</p>
</div>
""", unsafe_allow_html=True)

st.write("")
a,b,c = st.columns(3)
for col, num, label in [(a,"01","Upload PDF, DOCX or TXT"),(b,"02","Extract key candidate data"),(c,"03","Validate & export JSON")]:
    with col:
        st.markdown(f'<div class="metric"><div class="num">{num}</div><div class="lbl">{label}</div></div>', unsafe_allow_html=True)
st.write("")

left, right = st.columns([1.02, 1.25], gap="large")
with left:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">1. Add a resume</div><div class="subtle">Upload a sample resume or try the built-in demo profile.</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Choose a resume", type=["pdf","docx","txt"], help="Supported formats: PDF, DOCX and TXT")
    demo = st.toggle("Use built-in sample resume", value=not bool(uploaded))
    st.write("")
    if uploaded:
        st.caption(f"Selected: **{uploaded.name}** · {uploaded.size/1024:.1f} KB")
    if st.button("Extract structured data", type="primary", use_container_width=True):
        try:
            if uploaded and not demo:
                raw = uploaded.getvalue()
                result = extract_resume(raw, uploaded.name)
            else:
                result = extract_resume(SAMPLE_RESUME.encode("utf-8"), "sample.txt")
            st.session_state["result"] = validate_resume(result)
            st.session_state["source"] = uploaded.name if uploaded and not demo else "Built-in sample"
            st.session_state["error"] = None
        except Exception as e:
            st.session_state["error"] = str(e)
    if st.session_state.get("error"):
        st.error(st.session_state["error"])
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">What gets extracted?</div><div class="subtle">A consistent schema designed for applicant tracking systems and downstream automation.</div>', unsafe_allow_html=True)
    cols = st.columns(2)
    items = [("Contact details","Name, email, phone, location"),("Professional summary","Headline or profile summary"),("Skills","Technical and professional skills"),("Experience","Role, company, dates and description"),("Education","Degree, institution and graduation year"),("Validation","Missing fields, types and schema checks")]
    for i,(t,d) in enumerate(items):
        with cols[i%2]:
            st.markdown(f'<div style="padding:12px 0;border-bottom:1px solid #edf0f5"><b>{t}</b><div class="subtle">{d}</div></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

result = st.session_state.get("result")
if result:
    st.write("")
    st.markdown("### 2. Extraction results")
    st.caption(f"Source: {st.session_state.get('source','Resume')} · Review the fields before using the data.")
    contact = result["contact"]
    m1,m2,m3,m4 = st.columns(4)
    metrics = [(contact.get("full_name") or "Not found","Candidate"),(str(len(result["skills"])),"Skills found"),(str(len(result["experience"])),"Experience entries"),(str(len(result["education"])),"Education entries")]
    for col,(v,l) in zip([m1,m2,m3,m4],metrics):
        with col:
            st.markdown(f'<div class="metric"><div class="num" style="font-size:19px">{v}</div><div class="lbl">{l}</div></div>', unsafe_allow_html=True)
    tabs = st.tabs(["Structured JSON","Candidate overview","Validation"])
    with tabs[0]:
        st.json(result, expanded=True)
        st.download_button("⬇ Download validated JSON", json.dumps(result, indent=2), file_name="resume_extracted.json", mime="application/json", type="primary")
    with tabs[1]:
        st.markdown("#### Contact")
        st.write(f"**Name:** {contact.get('full_name') or 'Not found'}")
        st.write(f"**Email:** {contact.get('email') or 'Not found'}")
        st.write(f"**Phone:** {contact.get('phone') or 'Not found'}")
        st.write(f"**Location:** {contact.get('location') or 'Not found'}")
        st.markdown("#### Skills")
        st.write(", ".join(result["skills"]) if result["skills"] else "No skills detected.")
        st.markdown("#### Experience")
        if result["experience"]:
            for exp in result["experience"]:
                st.markdown(f"**{exp.get('job_title') or 'Role not specified'}** — {exp.get('company') or 'Company not specified'}")
                st.caption(f"{exp.get('start_date') or '—'} to {exp.get('end_date') or '—'}")
                st.write(exp.get("description") or "No description provided.")
        else:
            st.info("No experience entries detected.")
        st.markdown("#### Education")
        if result["education"]:
            for edu in result["education"]:
                st.write(f"**{edu.get('degree') or 'Degree not specified'}** · {edu.get('institution') or 'Institution not specified'} · {edu.get('graduation_year') or 'Year not specified'}")
        else:
            st.info("No education entries detected.")
    with tabs[2]:
        missing = result["validation"]["missing_fields"]
        st.write("**Schema status:**", "Passed" if result["validation"]["is_valid"] else "Review required")
        st.write("**Missing or unavailable fields:**")
        st.write(", ".join(missing) if missing else "None")
        st.caption("Missing values are represented as null or empty arrays; the extractor never invents candidate information.")
else:
    st.write("")
    st.info("Upload a resume and select **Extract structured data**, or use the built-in sample to preview the workflow.")

st.markdown("""
<div style="text-align:center;color:#8791a5;font-size:12px;padding-top:30px">
  RESUMEIQ · Structured extraction demo · Review extracted data before making hiring decisions
</div>
""", unsafe_allow_html=True)
