# youth-wellness-proto
AI-powered mental wellness companion for youth using Streamlit + Vertex AI
# 🌱 Youth Mental Wellness — AI Companion

An AI-powered mental wellness prototype designed for young people.  
Built with **Streamlit**, **Google Cloud Vertex AI (Gemini)**, and **SQLite**.

## 🚀 Features
- AI-powered mood analysis (via Gemini model)
- Empathetic responses + coping suggestions
- Mood journal stored in SQLite
- Trend visualization with Altair
- Simple Streamlit web app (fast for hackathons)

## 🛠️ Tech Stack
- **Frontend:** Streamlit  
- **Backend:** Python (Flask/Streamlit functions)  
- **Database:** SQLite  
- **AI Integration:** Google Cloud Vertex AI (Gemini)  
- **Deployment:** Streamlit / GCP  

## 📌 How to Run Locally
```bash
git clone https://github.com/YOUR_USERNAME/youth-wellness-proto.git
cd youth-wellness-proto
python -m venv .venv
.venv\Scripts\activate   # On Windows
pip install -r requirements.txt
streamlit run app.py
