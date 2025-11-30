# 🎯 AI Resume Screening & Ranking Agent

An ultra-fast AI-powered resume screening system that analyzes and ranks multiple resumes against job descriptions using Groq and Google Gemini AI.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31.0-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

- 📄 **Multi-Resume Analysis** - Upload and compare multiple PDF resumes
- 🤖 **Dual AI Support** - Groq (LLaMA 3.3) & Google Gemini models
- 📊 **Interactive Charts** - Bar charts and pie charts for visualization
- 🏆 **Smart Ranking** - Automatic scoring and ranking (0-100%)
- 💡 **Detailed Insights** - Strengths, missing skills, and recommendations
- 📥 **Export Results** - Download analysis as JSON

## ⚡ Tech Stack

| Component | Technology |
|-----------|-----------|
| AI Models | Groq LLaMA 3.3, Google Gemini 1.5 |
| Frontend | Streamlit |
| PDF Parsing | PyPDF2 |
| Visualization | Plotly |

## 📦 Installation
```bash
# Clone repository
git clone https://github.com/Sanjana-m55/ROOMAN_TECHNOLOGIES.git
cd ROOMAN_TECHNOLOGIES

# Create virtual environment
python -m venv venv
venv\Scripts\activate     # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

## 🔑 Setup API Keys

**Windows:**
```cmd
set GROQ_API_KEY=your_groq_key_here
set GEMINI_API_KEY=your_gemini_key_here
```

**Linux/Mac:**
```bash
export GROQ_API_KEY="your_groq_key_here"
export GEMINI_API_KEY="your_gemini_key_here"
```

**Or create `.env` file:**
```env
GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY=your_gemini_key_here
```

## ▶️ Run Application
```bash
streamlit run app.py
```

Open browser at `http://localhost:8501`

## 🎯 How to Use

1. Select AI Provider (Groq/Gemini) and Model
2. Paste Job Description
3. Upload Resume PDFs
4. Click "Analyze & Rank Resumes"
5. View results with charts and rankings
6. Download JSON results

## 📊 Scoring System

| Score | Rating | Color |
|-------|--------|-------|
| 80-100% | 🟢 Excellent | Green |
| 60-79% | 🟡 Good | Yellow |
| 0-59% | 🔴 Needs Work | Red |

## 🗂️ Project Structure
```
ROOMAN_TECHNOLOGIES/
├── app.py                # Main application
├── requirements.txt      # Dependencies
├── README.md            # Documentation
└── .env                 # API keys
```

## 📦 Dependencies
```txt
streamlit==1.31.0
groq==0.4.2
google-generativeai==0.3.2
PyPDF2==3.0.1
plotly==5.18.0
```

## 🤖 Available Models

**Groq:**
- llama-3.3-70b-versatile ⭐


**Gemini:**
- gemini-1.5-pro ⭐
- gemini-1.5-flash
- gemini-1.0-pro

## 📄 License

MIT License

## 🙋 Author

**Sanjana Mahantesh**
- GitHub: [@Sanjana-m55](https://github.com/Sanjana-m55)

## 🤝 Contributing

Pull requests welcome! For major changes, open an issue first.

---

Made with ❤️ using Groq & Gemini AI