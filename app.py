import streamlit as st
from groq import Groq
import google.generativeai as genai
import PyPDF2
import json
import os
import plotly.graph_objects as go
import plotly.express as px

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
# API KEYS FROM ENVIRONMENT
# -----------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# -----------------------------------
# SIDEBAR - MODEL SELECTION
# -----------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")
    
    ai_provider = st.selectbox("🤖 AI Provider", ["Groq", "Gemini"])
    
    if ai_provider == "Groq":
        model_name = st.selectbox("Model", [
            "llama-3.3-70b-versatile",
        ])
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
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

# -----------------------------------
# MAIN SECTION
# -----------------------------------
job_desc = st.text_area("📝 Paste Job Description", height=200, placeholder="Enter the job requirements, skills, responsibilities...")

uploaded_files = st.file_uploader("📄 Upload Resumes (PDF only)", type=["pdf"], accept_multiple_files=True)

if st.button("🚀 Analyze & Rank Resumes", type="primary", use_container_width=True):
    
    if ai_provider == "Groq" and not GROQ_API_KEY:
        st.error("⚠️ Groq API Key not found in environment variables! Set GROQ_API_KEY.")
    elif ai_provider == "Gemini" and not GEMINI_API_KEY:
        st.error("⚠️ Gemini API Key not found in environment variables! Set GEMINI_API_KEY.")
    elif not job_desc:
        st.error("⚠️ Please paste the job description!")
    elif not uploaded_files:
        st.error("⚠️ Please upload at least one resume!")
    else:
        # Initialize AI client
        if ai_provider == "Groq":
            client = Groq(api_key=GROQ_API_KEY)
        else:
            genai.configure(api_key=GEMINI_API_KEY)
            client = genai.GenerativeModel(model_name)
        
        st.markdown("---")
        st.subheader("📊 Analysis Results")
        
        results = []
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, uploaded_file in enumerate(uploaded_files):
            status_text.text(f"Analyzing {uploaded_file.name}...")
            
            # Extract resume text
            resume_text = extract_pdf_text(uploaded_file)
            
            # Create prompt for AI
            prompt = f"""You are an expert HR recruiter. Analyze this resume against the job description and provide a detailed evaluation.

JOB DESCRIPTION:
{job_desc}

RESUME:
{resume_text}

Provide your analysis in the following JSON format:
{{
    "match_score": <number between 0-100>,
    "key_strengths": ["strength1", "strength2", "strength3"],
    "missing_skills": ["skill1", "skill2"],
    "experience_relevance": "<brief assessment>",
    "recommendation": "<Highly Recommended / Recommended / Maybe / Not Recommended>",
    "summary": "<2-3 sentence summary>"
}}

Be objective and specific. Return ONLY valid JSON, no markdown formatting."""

            try:
                # Get response from AI
                full_response = ""
                
                if ai_provider == "Groq":
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.3
                    )
                    full_response = response.choices[0].message.content
                
                else:  # Gemini
                    response = client.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.3,
                        )
                    )
                    full_response = response.text
                
                # Try to parse JSON from response
                try:
                    # Extract JSON from markdown code blocks if present
                    if "```json" in full_response:
                        json_str = full_response.split("```json")[1].split("```")[0].strip()
                    elif "```" in full_response:
                        json_str = full_response.split("```")[1].split("```")[0].strip()
                    else:
                        json_str = full_response
                    
                    analysis = json.loads(json_str)
                    analysis["filename"] = uploaded_file.name
                    results.append(analysis)
                except Exception as parse_error:
                    st.warning(f"Could not parse structured data for {uploaded_file.name}")
                    results.append({
                        "filename": uploaded_file.name,
                        "match_score": 0,
                        "key_strengths": [],
                        "missing_skills": [],
                        "summary": "Analysis completed but couldn't extract score"
                    })
            
            except Exception as e:
                st.error(f"Error analyzing {uploaded_file.name}: {str(e)}")
            
            # Update progress
            progress_bar.progress((idx + 1) / len(uploaded_files))
        
        status_text.text("✅ Analysis complete!")
        
        # -----------------------------------
        # VISUALIZATIONS & RANKING
        # -----------------------------------
        if results:
            st.markdown("---")
            
            # Sort by match score
            ranked_results = sorted(results, key=lambda x: x.get("match_score", 0), reverse=True)
            
            # -----------------------------------
            # OVERVIEW CHARTS
            # -----------------------------------
            st.subheader("📈 Overview Dashboard")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Bar Chart - Match Scores
                fig_bar = go.Figure(data=[
                    go.Bar(
                        x=[r['filename'] for r in ranked_results],
                        y=[r.get('match_score', 0) for r in ranked_results],
                        marker_color=['#00D26A' if s >= 80 else '#FFA500' if s >= 60 else '#FF4B4B' 
                                     for s in [r.get('match_score', 0) for r in ranked_results]],
                        text=[f"{r.get('match_score', 0)}%" for r in ranked_results],
                        textposition='outside'
                    )
                ])
                fig_bar.update_layout(
                    title="Resume Match Scores Comparison",
                    xaxis_title="Candidate",
                    yaxis_title="Match Score (%)",
                    height=400,
                    showlegend=False
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                # Pie Chart - Recommendation Distribution
                recommendations = [r.get('recommendation', 'Unknown') for r in ranked_results]
                rec_counts = {}
                for rec in recommendations:
                    rec_counts[rec] = rec_counts.get(rec, 0) + 1
                
                fig_pie = go.Figure(data=[
                    go.Pie(
                        labels=list(rec_counts.keys()),
                        values=list(rec_counts.values()),
                        hole=0.4,
                        marker_colors=['#00D26A', '#FFA500', '#FF4B4B', '#888888']
                    )
                ])
                fig_pie.update_layout(
                    title="Recommendation Distribution",
                    height=400
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            st.markdown("---")
            
            # -----------------------------------
            # DETAILED RANKINGS
            # -----------------------------------
            st.subheader("🏆 Detailed Rankings")
            
            for rank, result in enumerate(ranked_results, 1):
                score = result.get("match_score", 0)
                
                # Color coding
                if score >= 80:
                    color = "#00D26A"
                    emoji = "🟢"
                    badge = "Excellent Match"
                elif score >= 60:
                    color = "#FFA500"
                    emoji = "🟡"
                    badge = "Good Match"
                else:
                    color = "#FF4B4B"
                    emoji = "🔴"
                    badge = "Needs Improvement"
                
                with st.container():
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%); 
                                padding: 20px; border-radius: 10px; border-left: 4px solid {color}; margin-bottom: 20px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h2 style="margin: 0;">#{rank} {result['filename']}</h2>
                                <span style="background: {color}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px;">
                                    {badge}
                                </span>
                            </div>
                            <div style="text-align: right;">
                                <h1 style="margin: 0; color: {color};">{emoji} {score}%</h1>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**✅ Key Strengths:**")
                        strengths = result.get('key_strengths', [])
                        if strengths:
                            for strength in strengths:
                                st.markdown(f"• {strength}")
                        else:
                            st.markdown("_No strengths listed_")
                        
                        st.markdown("")
                        st.markdown("**📊 Experience Relevance:**")
                        st.info(result.get('experience_relevance', 'N/A'))
                    
                    with col2:
                        st.markdown("**⚠️ Missing Skills:**")
                        missing = result.get('missing_skills', [])
                        if missing:
                            for skill in missing:
                                st.markdown(f"• {skill}")
                        else:
                            st.markdown("_No missing skills identified_")
                        
                        st.markdown("")
                        st.markdown("**💡 Recommendation:**")
                        rec = result.get('recommendation', 'N/A')
                        if rec == "Highly Recommended":
                            st.success(f"✨ {rec}")
                        elif rec == "Recommended":
                            st.info(f"👍 {rec}")
                        elif rec == "Maybe":
                            st.warning(f"🤔 {rec}")
                        else:
                            st.error(f"❌ {rec}")
                    
                    st.markdown("**📝 Summary:**")
                    st.markdown(f"_{result.get('summary', 'No summary available')}_")
                    
                    st.markdown("---")
            
            # Download results
            st.download_button(
                "📥 Download Full Results (JSON)",
                data=json.dumps(ranked_results, indent=2),
                file_name="resume_rankings.json",
                mime="application/json",
                use_container_width=True
            )

else:
    st.info("👆 Upload resumes and paste job description to get started!")