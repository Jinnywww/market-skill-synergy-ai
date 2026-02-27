import streamlit as st
import pandas as pd
import plotly.express as px
import os
import google.generativeai as genai
from google.generativeai.types import RequestOptions

# --- 1. AI CONFIGURATION (Hardened for Cloud) ---
API_KEY = st.secrets.get("GEMINI_API_KEY", "AIzaSyAtXi1d8UvAtsdOJK5ggH3Tr0GzOYMf_nU")

# Pro-Tip: API Version ကို v1 လို့ အသေသတ်မှတ်ပေးလိုက်ခြင်း
genai.configure(api_key=API_KEY)

def get_ai_response(prompt_text):
    try:
        # v1 version ကို အသုံးပြုဖို့ RequestOptions နဲ့ Force လုပ်မယ်
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # API version ကို v1 သို့ ပြောင်းလဲခေါ်ဆိုခြင်း
        response = model.generate_content(
            prompt_text,
            request_options=RequestOptions(api_version='v1')
        )
        return response.text
    except Exception as e:
        # အကယ်၍ v1 နဲ့ မရရင် v1beta ကို fallback အနေနဲ့ စမ်းမယ်
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt_text)
            return response.text
        except Exception as e2:
            return f"AI Connection Error: {e2}"

# --- 2. PAGE CONFIGURATION ---
st.set_page_config(page_title="Market Skill Synergy AI", layout="wide")

# --- 3. NAVIGATION & SESSION STATE ---
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"

def navigate(p):
    st.session_state.page = p

with st.sidebar:
    st.title("🛡️ Skill Pro AI")
    st.markdown("---")
    if st.button("📊 Executive Dashboard"): navigate("Dashboard")
    if st.button("🤖 AI Career Roadmap"): navigate("AI")

# --- 4. DATA LOADING ---
@st.cache_data
def load_data():
    if os.path.exists('skill_rules_final.csv'):
        return pd.read_csv('skill_rules_final.csv')
    return None

df = load_data()

# --- 5. PAGES ---
if df is not None:
    if st.session_state.page == "Dashboard":
        st.title("Market Intelligence Dashboard")
        st.plotly_chart(px.bar(df.nlargest(10, 'lift'), x='lift', y='consequents', orientation='h'))
        
    elif st.session_state.page == "AI":
        st.title("🤖 AI Career Consultant")
        query = st.text_input("What skill or job role are you looking for?")
        if query:
            with st.spinner("Generating professional roadmap..."):
                # Data matching logic
                relevant = df[df['antecedents'].str.contains(query, case=False, na=False)].head(5)
                context = relevant.to_string()
                
                # AI Response with v1 Fix
                answer = get_ai_response(f"Market Data: {context}\nQuestion: {query}\nRoadmap:")
                st.markdown(answer)
else:
    st.error("Data file not found!")
