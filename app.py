import streamlit as st
import pandas as pd
import google.generativeai as genai
import os

# --- 1. API CONFIGURATION (Stable Version) ---
API_KEY = st.secrets.get("GEMINI_API_KEY", "AIzaSyAtXi1d8UvAtsdOJK5ggH3Tr0GzOYMf_nU")

# Pro-Tip: API Version ကို v1 လို့ အသေသတ်မှတ်ပြီး Configure လုပ်မယ်
genai.configure(api_key=API_KEY, transport='rest') 

def get_stable_model():
    try:
        # v1 version မှာ ရနိုင်တဲ့ model တွေကို စစ်မယ်
        models = [m.name for m in genai.list_models()]
        
        # Cloud compatibility အတွက် models/ prefix ကို အမြဲစစ်ပေးမယ်
        for m in models:
            if "gemini-1.5-flash" in m:
                return m
        return "models/gemini-1.5-flash"
    except:
        return "models/gemini-1.5-flash"

WORKING_MODEL = get_stable_model()

# --- 2. PAGE STATE MANAGEMENT ---
# Page တွေ ပျောက်မသွားအောင် session_state ကို သေချာကိုင်တွယ်မယ်
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"

def navigate_to(page):
    st.session_state.page = page

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🚀 Skill AI Pro")
    st.info(f"Engine: {WORKING_MODEL}")
    st.markdown("---")
    if st.button("📊 Dashboard"): navigate_to("Dashboard")
    if st.button("🤖 AI Roadmap"): navigate_to("AI")

# --- 4. DATA ENGINE ---
@st.cache_data
def load_data():
    if os.path.exists('skill_rules_final.csv'):
        return pd.read_csv('skill_rules_final.csv')
    return None

df = load_data()

# --- 5. APP PAGES ---
if df is not None:
    if st.session_state.page == "Dashboard":
        st.title("Market Dashboard")
        st.write("Welcome to your career analytics.")
        st.dataframe(df.head(10)) # Dashboard content
        
    elif st.session_state.page == "AI":
        st.title("🤖 AI Career Assistant")
        user_input = st.text_input("What is your dream job?")
        
        if user_input:
            try:
                # model ကို ခေါ်တဲ့အခါ version 'v1' ကို သုံးဖို့ Force လုပ်မယ်
                model = genai.GenerativeModel(model_name=WORKING_MODEL)
                response = model.generate_content(f"Create a roadmap for {user_input}")
                st.markdown(response.text)
            except Exception as e:
                # အကယ်၍ 404 ပြန်တက်ရင် API Version ကို ပြောင်းပြီး ထပ်ကြိုးစားမယ်
                st.error(f"Sync Issue: {e}")
                st.warning("Tip: Check if your API Key is valid and billing is active on Google Cloud.")
else:
    st.error("Data file not found!")
