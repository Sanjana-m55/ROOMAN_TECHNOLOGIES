import streamlit as st
from groq import Groq
import google.generativeai as genai
import PyPDF2
import json
import plotly.graph_objects as go

st.set_page_config(page_title="Resume Screening Agent", page_icon="🎯", layout="wide")

st.markdown("""
<h1 style="text-align:center; color:#FF4B4B;">🎯 AI Resume Screening & Ranking Agent</h1>
<p style="text-align:center; opacity:0.7;">
Rank multiple resumes based on job descriptions • Powered by Groq & Gemini
</p>
""", unsafe_allow_html=True)

# Load keys from Streamlit Secrets
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

with st.sidebar:
    st.header("⚙️ Configuration")
    ai_provider = st.selectbox("🤖 AI Provider", ["Groq", "Gemini"])
    model_name = (
        "llama-3.3-70b-versatile" if ai_provider == "Groq"
        else st.selectbox("Model", ["gemini-1.5-pro","gemini-1.5-flash","gemini-1.0-pro"])
    )
    st.markdown("---")

def extract_pdf_text(pdf_file):
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for p in reader.pages:
            page_text = p.extract_text()
            if page_text:
                text += page_text
        return text
    except:
        return ""

job_desc = st.text_area("📝 Paste Job Description", height=200)
uploaded_files = st.file_uploader("📄 Upload Resumes", type=["pdf"], accept_multiple_files=True)

if st.button("🚀 Analyze & Rank Resumes", use_container_width=True):

    # Key checks
    if ai_provider == "Groq" and not GROQ_API_KEY:
        st.error("Missing GROQ_API_KEY in Streamlit Secrets")
        st.stop()

    if ai_provider == "Gemini" and not GEMINI_API_KEY:
        st.error("Missing GEMINI_API_KEY in Streamlit Secrets")
        st.stop()

    if not job_desc:
        st.error("Paste job description")
        st.stop()
    if not uploaded_files:
        st.error("Upload at least one resume")
        st.stop()

    # Initialize correct Groq SDK
    if ai_provider == "Groq":
        client = Groq(api_key=GROQ_API_KEY)
    else:
        genai.configure(api_key=GEMINI_API_KEY)
        client = genai.GenerativeModel(model_name)

    st.subheader("📊 Analysis Results")
    results = []
    progress = st.progress(0)

    for idx, file in enumerate(uploaded_files):
        text = extract_pdf_text(file)

        prompt = f"""
Analyze resume vs job description and return ONLY JSON:

JOB DESCRIPTION:
{job_desc}

RESUME:
{text}

JSON format:
{{
    "match_score": 0-100,
    "key_strengths": [],
    "missing_skills": [],
    "experience_relevance": "",
    "recommendation": "",
    "summary": ""
}}
"""

        try:
            if ai_provider == "Groq":
                resp = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role":"user","content":prompt}],
                    temperature=0.3
                )
                output = resp.choices[0].message.content

            else:
                resp = client.generate_content(prompt)
                output = resp.text

            try:
                output = output.replace("```json","").replace("```","").strip()
                data = json.loads(output)
            except:
                data = {
                    "match_score": 0,
                    "key_strengths": [],
                    "missing_skills": [],
                    "experience_relevance": "",
                    "recommendation": "",
                    "summary": "Unable to parse JSON"
                }

            data["filename"] = file.name
            results.append(data)

        except Exception as e:
            st.error(f"Error: {e}")

        progress.progress((idx+1)/len(uploaded_files))

    st.success("Analysis Complete!")

    # Ranking
    results = sorted(results, key=lambda x: x["match_score"], reverse=True)

    # Show bar chart
    fig = go.Figure(go.Bar(
        x=[r["filename"] for r in results],
        y=[r["match_score"] for r in results],
        text=[f"{r['match_score']}%" for r in results],
        textposition="outside"
    ))
    fig.update_layout(title="Resume Match Score Comparison")
    st.plotly_chart(fig, use_container_width=True)

    # Details
    st.subheader("🏆 Detailed Rankings")
    for i, r in enumerate(results,1):
        st.markdown(f"### #{i} — {r['filename']}")
        st.write("**Score:**", r["match_score"])
        st.write("**Strengths:**", r["key_strengths"])
        st.write("**Missing Skills:**", r["missing_skills"])
        st.write("**Relevance:**", r["experience_relevance"])
        st.write("**Summary:**", r["summary"])
        st.markdown("---")

    st.download_button(
        "📥 Download Results JSON",
        json.dumps(results,indent=2),
        "results.json"
    )
