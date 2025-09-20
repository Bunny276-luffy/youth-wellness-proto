import os
import json
import sqlite3
from datetime import datetime
import streamlit as st
import pandas as pd
import altair as alt
from google.oauth2 import service_account

# ------------------------------
# Vertex AI Setup (Service Account Auth)
# ------------------------------
PROJECT_ID = "youth-wellness-proto"
LOCATION = "us-central1"
KEY_PATH = "F:/proto/gcp-keys.json"

try:
    import vertexai
    from vertexai.language_models import TextGenerationModel

    # Load credentials from service account JSON
    credentials = service_account.Credentials.from_service_account_file(KEY_PATH)

    # Initialize Vertex AI with credentials
    vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=credentials)

    # Use Gemini (flash model is faster)
    model = TextGenerationModel.from_pretrained("gemini-1.5-flash")

except Exception as e:
    st.warning(f"⚠️ Vertex AI not initialized. Error: {e}")
    model = None


# ------------------------------
# SQLite DB Setup
# ------------------------------
conn = sqlite3.connect("mood_journal.db", check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS journal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    mood TEXT,
    entry TEXT
)
""")
conn.commit()

def save_journal(mood, entry):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO journal (timestamp, mood, entry) VALUES (?, ?, ?)", (ts, mood, entry))
    conn.commit()

def get_journal_df(limit=50):
    rows = c.execute("SELECT timestamp, mood, entry FROM journal ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    if not rows:
        return pd.DataFrame(columns=["timestamp","mood","entry"])
    return pd.DataFrame(rows, columns=["timestamp","mood","entry"])

def call_ai_analyze(user_text):
    """Ask Gemini model to analyze mood + give response"""
    if model is None:
        return ("unknown", "AI not available (check credentials).", "Try: Take a short break.")
    
    prompt = f"""
You are an empathetic wellness assistant for young people.
User said: "{user_text}"
Please output EXACTLY in this JSON format:
{{"mood":"<one word mood>", "response":"<empathetic short reply>", "suggestion":"<coping activity>"}}
"""
    try:
        resp = model.predict(prompt, max_output_tokens=250)
        text = resp.text.strip()

        # Debugging: show raw output in sidebar
        st.sidebar.write("🔍 Raw AI Output:", text)

        j = json.loads(text)
        return j.get("mood","unknown"), j.get("response",""), j.get("suggestion","")
    except Exception as e:
        return ("unknown", f"Error calling AI: {e}", "")


# ------------------------------
# Streamlit UI
# ------------------------------
st.title("🌱 Youth Mental Wellness — AI Companion")
st.write("Check in with your mood, get supportive replies, and track your wellness journey.")

# Mood Form
with st.form("mood_form"):
    user_text = st.text_area("How are you feeling today?", height=120)
    submitted = st.form_submit_button("Analyze Mood")
    if submitted and user_text.strip():
        mood, reply, suggestion = call_ai_analyze(user_text)
        st.markdown(f"**Mood:** {mood}")
        st.info(reply)
        if suggestion:
            st.write("**Suggestion:**", suggestion)
        save_journal(mood, user_text)

# Journal Section
st.markdown("---")
st.subheader("📖 Recent Mood Journal")
df = get_journal_df(20)
if df.empty:
    st.info("No entries yet. Try checking in above.")
else:
    st.dataframe(df)

    # Mood trend chart
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date
    trend = df.groupby(['date','mood']).size().reset_index(name='count')

    chart = alt.Chart(trend).mark_bar().encode(
        x='date:T',
        y='count:Q',
        color='mood:N',
        tooltip=['date','mood','count']
    ).properties(width=700, height=300)

    st.altair_chart(chart, use_container_width=True)
