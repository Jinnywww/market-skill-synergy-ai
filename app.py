import streamlit as st
import pandas as pd
import plotly.express as px
import os
import google.generativeai as genai
from fpdf import FPDF
import base64

# --- 1. AI CONFIGURATION (Final Cloud-Safe Fix) ---
# API Key ကို Streamlit Secrets ထဲမှာ GEMINI_API_KEY ဆိုပြီး ထည့်ထားပေးပါ
API_KEY = st.secrets.get("GEMINI_API_KEY", "AIzaSyAtXi1d8UvAtsdOJK5ggH3Tr0GzOYMf_nU")
genai.configure(api_key=API_KEY)

def get_working_model():
    """သင့် API Key နဲ့ Cloud ပေါ်မှာ တကယ်အလုပ်လုပ်တဲ့ Model နာမည်ကို ရှာပေးမယ့် Function"""
    try:
        # ရနိုင်တဲ့ model အားလုံးကို list ဆွဲထုတ်မယ်
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # 1.5 Flash ကို အရင်ရှာမယ် (Cloud မှာ 'models/gemini-1.5-flash' လို့ ပေါ်တတ်ပါတယ်)
        for m in available_models:
            if "gemini-1.5-flash" in m:
                return m
        
        # မရှိရင် Gemini Pro ကို ရှာမယ်
        for m in available_models:
            if "gemini-pro" in m:
                return m
                
        # ဘာမှရှာမတွေ့ရင် list ထဲက ပထမဆုံးတစ်ခုကို ယူမယ်
        return available_models[0] if available_models else "models/gemini-1.5-flash"
    except Exception:
        # API list_models အလုပ်မလုပ်ရင် default အမှန်ကို သုံးမယ်
        return "models/gemini-1.5-flash"

# Model နာမည်အမှန်ကို သိမ်းဆည်းထားမယ်
WORKING_MODEL = get_working_model()

# --- 2. PAGE CONFIGURATION ---
st.set_page_config(page_title="Market Skill Synergy AI", layout="wide")

# --- 3. PREMIUM UI STYLING ---
st.markdown('''
    <style>
    .stApp { background-color: #F8FAFC; }
    section[data-testid="stSidebar"] { background-color: #205781 !important; }
    .stMetric { background-color: white; padding: 20px; border-radius: 12px; border: 1px solid #E2E8F0; }
    </style>
''', unsafe_allow_html=True)

# --- 4. DATA LOADING ---
@st.cache_data
def load_data():
    file_path = 'skill_rules_final.csv'
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df['antecedents'] = df['antecedents'].astype(str)
        return df
    return None

df = load_data()

# --- 5. SIDEBAR NAVIGATION ---
st.sidebar.title("Market AI")
st.sidebar.success(f"Connected: {WORKING_MODEL}") # ဘယ် model သုံးနေလဲ ပြပေးမယ်

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
        c3.metric("AI Engine", "Active")
        
        top_data = df.nlargest(10, 'lift')
        st.plotly_chart(px.bar(top_data, x='lift', y='consequents', orientation='h', color='lift'), use_container_width=True)

    elif st.session_state.page == "AI":
        st.title("🤖 AI Career Consultant")
        user_query = st.text_input("Enter a skill (e.g. Python):")
        
        if user_query:
            with st.spinner("AI is analyzing market patterns..."):
                # Data context filtering
                relevant = df[df['antecedents'].str.contains(user_query, case=False, na=False)].head(10)
                context = relevant.to_string() if not relevant.empty else "No specific patterns found"
                
                try:
                    # အပေါ်မှာ ရှာထားတဲ့ WORKING_MODEL နာမည်အမှန်ကို သုံးမယ်
                    model = genai.GenerativeModel(WORKING_MODEL)
                    response = model.generate_content(f"Market Data: {context}. User Question: {user_query}. Provide a career roadmap.")
                    st.info(response.text)
                except Exception as e:
                    st.error(f"AI Error: {e}")
else:
    st.error("Missing Data File!")
