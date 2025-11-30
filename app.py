import streamlit as st
from groq import Client
import google.generativeai as genai
import PyPDF2
import json
import os
import plotly.graph_objects as go

# -----------------------------------
# UI CONFIG
# -----------------------------------
st.set_page_config(page_title="Resume Screening Agent", page_icon="🎯", layout="wide")

st.markdown("""
    <h1 style="text-align:center; color:#FF4B4B;">
        🎯 AI Resume Screening & Ranking Agent
    </h1>
    <p style="text-align:center; opacity:0.7;">
        Rank multiple resumes based on job descriptions • Powered by Groq & Gemini
    </p>
""", unsafe_allow_html=True)

# -----------------------------------
# API KEYS (use Streamlit Secrets)
# -----------------------------------
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

# -----------------------------------
# SIDEBAR - MODEL SELECTION
# -----------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")
    
    ai_provider = st.selectbox("🤖 AI Provider", ["Groq", "Gemini"])
    
    if ai_provider == "Groq":
        model_name = "llama-3.3-70b-versatile"
    else:
        model_name = st.selectbox("Model", [
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-1.0-pro"
        ])
    
    st.markdown("---")
    st.markdown("**How it works:**")
    st.markdown("1. Upload multiple resumes")
    st.markdown("2. Paste job description")
    st.markdown("3. Get ranked results instantly")

# -----------------------------------
# Extract PDF Text
# -----------------------------------
def extract_pdf_text(pdf_file):
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

# -----------------------------------
# MAIN SECTION
# -----------------------------------
job_desc = st.text_area("📝 Paste Job Description", height=200, placeholder="Enter job requirements…")
uploaded_files = st.file_uploader("📄 Upload Resumes (PDF only)", type=["pdf"], accept_multiple_files=True)

if st.button("🚀 Analyze & Rank Resumes", type="primary", use_container_width=True):

    # Key validations
    if ai_provider == "Groq" and not GROQ_API_KEY:
        st.error("⚠️ Groq API Key not found in Streamlit Secrets!")
        st.stop()
    if ai_provider == "Gemini" and not GEMINI_API_KEY:
        st.error("⚠️ Gemini API Key not found in Streamlit Secrets!")
        st.stop()
    if not job_desc:
        st.error("⚠️ Please paste the job description!")
        st.stop()
    if not uploaded_files:
        st.error("⚠️ Please upload at least one resume!")
        st.stop()

    # -----------------------------------
    # Initialize AI client (CORRECT GROQ CLIENT)
    # -----------------------------------
    if ai_provider == "Groq":
        client = Client(api_key=GROQ_API_KEY)
    else:
        genai.configure(api_key=GEMINI_API_KEY)
        client = genai.GenerativeModel(model_name)

    st.markdown("---")
    st.subheader("📊 Analysis Results")

    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for idx, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"Analyzing {uploaded_file.name}...")

        resume_text = extract_pdf_text(uploaded_file)

        prompt = f"""
You are an expert HR recruiter. Analyze this resume against the job description and return structured JSON.

JOB DESCRIPTION:
{job_desc}

RESUME:
{resume_text}

Return JSON only:
{{
    "match_score": <0-100>,
    "key_strengths": [],
    "missing_skills": [],
    "experience_relevance": "",
    "recommendation": "",
    "summary": ""
}}
"""

        try:
            # GROQ CHAT COMPLETION
            if ai_provider == "Groq":
                resp = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3
                )
                full_response = resp.choices[0].message.content

            else:  # GEMINI
                resp = client.generate_content(prompt)
                full_response = resp.text

            # Parse JSON
            try:
                if "```json" in full_response:
                    data = full_response.split("```json")[1].split("```")[0].strip()
                elif "```" in full_response:
                    data = full_response.split("```")[1].split("```")[0].strip()
                else:
                    data = full_response

                analysis = json.loads(data)
                analysis["filename"] = uploaded_file.name
                results.append(analysis)

            except Exception:
                results.append({
                    "filename": uploaded_file.name,
                    "match_score": 0,
                    "key_strengths": [],
                    "missing_skills": [],
                    "summary": "Could not parse model output."
                })

        except Exception as e:
            st.error(f"Error analyzing {uploaded_file.name}: {str(e)}")

        progress_bar.progress((idx + 1) / len(uploaded_files))

    status_text.text("✅ Analysis complete!")

    # -----------------------------------
    # RESULTS + CHARTS
    # -----------------------------------
    if results:
        st.markdown("---")
        ranked = sorted(results, key=lambda x: x.get("match_score", 0), reverse=True)

        # BAR CHART
        names = [r["filename"] for r in ranked]
        scores = [r["match_score"] for r in ranked]

        bar = go.Figure(data=[go.Bar(x=names, y=scores, text=scores, textposition="outside")])
        bar.update_layout(title="Resume Match Score Comparison", height=400)
        st.plotly_chart(bar, use_container_width=True)

        # SHOW INDIVIDUAL DETAILS
        st.subheader("🏆 Detailed Rankings")
        for rank, r in enumerate(ranked, 1):
            st.markdown(f"### #{rank} — {r['filename']}")
            st.write(f"**Match Score:** {r['match_score']}%")
            st.write("**Strengths:**", r.get("key_strengths", []))
            st.write("**Missing Skills:**", r.get("missing_skills", []))
            st.write("**Experience Relevance:**", r.get("experience_relevance", ""))
            st.write("**Summary:**", r.get("summary", ""))
            st.markdown("---")

        # DOWNLOAD BUTTON
        st.download_button(
            "📥 Download Full Results (JSON)",
            data=json.dumps(ranked, indent=2),
            file_name="resume_rankings.json",
            mime="application/json",
            use_container_width=True
        )

else:
    st.info("👆 Upload resumes and paste job description to get started!")
