import streamlit as st
import pandas as pd
import plotly.express as px
import os
import google.generativeai as genai
from fpdf import FPDF
import base64

# --- 1. AI CONFIGURATION (Safe Mode for Cloud) ---
# API Key ကို Secrets ထဲကယူမယ်။ မရှိရင် Code ထဲက Key ကိုသုံးမယ်။
API_KEY = st.secrets.get("GEMINI_API_KEY", "AIzaSyAtXi1d8UvAtsdOJK5ggH3Tr0GzOYMf_nU")
genai.configure(api_key=API_KEY)

def get_working_model():
    """သင့် Key အတွက် အလုပ်လုပ်မယ့် Model နာမည်အမှန်ကို ရှာပေးတဲ့ function"""
    try:
        # Google ဆီက ရနိုင်တဲ့ model စာရင်းကို လှမ်းတောင်းမယ်
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # 1.5 Flash ကို အရင်ရှာမယ်
        for m in available_models:
            if "gemini-1.5-flash" in m:
                return m # ဥပမာ - 'models/gemini-1.5-flash' လို့ ပြန်ပေးလိမ့်မယ်
        
        # မရှိရင် Gemini Pro ကို ရှာမယ်
        for m in available_models:
            if "gemini-pro" in m:
                return m
                
        return available_models[0] if available_models else "models/gemini-1.5-flash"
    except:
        # API Error တက်ရင် default format အမှန်ကို သုံးမယ်
        return "models/gemini-1.5-flash"

WORKING_MODEL = get_working_model()

# --- 2. PAGE CONFIGURATION ---
st.set_page_config(page_title="Market Skill Synergy AI", layout="wide")

# --- 3. PREMIUM UI STYLING ---
st.markdown('''
    <style>
    .stApp { background-color: #F8FAFC; }
    section[data-testid="stSidebar"] { background-color: #205781 !important; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; border: 1px solid #E2E8F0; }
    </style>
''', unsafe_allow_html=True)

# --- 4. CORE FUNCTIONS ---
@st.cache_data
def load_data():
    file_path = 'skill_rules_final.csv'
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df['antecedents'] = df['antecedents'].astype(str)
        return df
    return None

df = load_data()

# --- 5. NAVIGATION ---
st.sidebar.title("Market Intelligence")
st.sidebar.info(f"🚀 AI Engine: {WORKING_MODEL}")

if 'page' not in st.session_state: st.session_state.page = "Summary"

if st.sidebar.button("📊 Executive Summary"): st.session_state.page = "Summary"
if st.sidebar.button("🤖 AI Skill Assistant"): st.session_state.page = "AI"

# --- 6. PAGE LOGIC ---
if df is not None:
    if st.session_state.page == "Summary":
        st.title("Market Intelligence Overview")
        c1, c2, c3 = st.columns(3)
        c1.metric("Job Samples", "1.2 Million")
        c2.metric("Market Rules", f"{len(df):,}")
        c3.metric("System", "Online")
        
        top_data = df.nlargest(10, 'lift')
        fig = px.bar(top_data, x='lift', y='consequents', orientation='h', title="Top Skill Synergies")
        st.plotly_chart(fig, use_container_width=True)

    elif st.session_state.page == "AI":
        st.title("🤖 AI Career Consultant")
        user_input = st.text_input("Enter a skill (e.g. Python):", placeholder="Ask me about your career path...")
        
        if user_input:
            with st.spinner("AI is analyzing market trends..."):
                # Data context matching
                relevant = df[df['antecedents'].str.contains(user_input, case=False, na=False)].head(10)
                context = relevant.to_string() if not relevant.empty else "General data available"
                
                try:
                    # နာမည်အမှန်ကို သုံးပြီး AI ခေါ်မယ်
                    model = genai.GenerativeModel(WORKING_MODEL)
                    response = model.generate_content(f"Market Rules: {context}. User Question: {user_input}. Generate a professional roadmap.")
                    st.markdown("### 🎓 Your Data-Driven Roadmap")
                    st.info(response.text)
                except Exception as e:
                    st.error(f"AI Connection Error: {e}")
else:
    st.error("Missing Data File!")
        
