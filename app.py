import streamlit as st
import pandas as pd
import plotly.express as px
import os
import google.generativeai as genai
from fpdf import FPDF
import base64

# --- 1. AI CONFIGURATION (Auto-Discovery Logic) ---
# Secrets ထဲမှာ GEMINI_API_KEY ဆိုပြီး ထည့်ထားပေးပါ (သို့မဟုတ်) အောက်က Key ကို သုံးပါ
API_KEY = st.secrets.get("GEMINI_API_KEY", "AIzaSyAtXi1d8UvAtsdOJK5ggH3Tr0GzOYMf_nU")
genai.configure(api_key=API_KEY)

@st.cache_resource
def get_working_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # Cloud မှာ models/gemini-1.5-flash လို့ အပြည့်အစုံ ရှာမယ်
        for m in models:
            if "gemini-1.5-flash" in m: return m
        return models[0] if models else "models/gemini-1.5-flash"
    except:
        return "models/gemini-1.5-flash"

WORKING_MODEL = get_working_model()

# --- 2. PAGE CONFIGURATION ---
st.set_page_config(page_title="Skill Synergy AI Portfolio", layout="wide", initial_sidebar_state="expanded")

# --- 3. CUSTOM CSS (Professional UI) ---
st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; border: 1px solid #E2E8F0; }
    [data-testid="stSidebar"] { background-color: #1E293B !important; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #2563EB; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. DATA ENGINE ---
@st.cache_data
def load_data():
    path = 'skill_rules_final.csv'
    if os.path.exists(path):
        data = pd.read_csv(path)
        data['antecedents'] = data['antecedents'].astype(str)
        return data
    return None

df = load_data()

# --- 5. NAVIGATION LOGIC ---
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"

def set_page(page_name):
    st.session_state.page = page_name

with st.sidebar:
    st.title("🛡️ Career AI")
    st.subheader(f"Engine: {WORKING_MODEL.split('/')[-1]}")
    st.markdown("---")
    if st.button("📊 Market Dashboard"): set_page("Dashboard")
    if st.button("🤖 AI Roadmap"): set_page("AI")
    if st.button("📈 Growth Trends"): set_page("Trends")
    if st.button("📄 Export Report"): set_page("Export")

# --- 6. PAGE RENDERING ---
if df is not None:
    # --- DASHBOARD PAGE ---
    if st.session_state.page == "Dashboard":
        st.title("Market Intelligence Dashboard")
        m1, m2, m3 = st.columns(3)
        m1.metric("Market Rules", f"{len(df):,}")
        m2.metric("Data Points", "1.2M+")
        m3.metric("Status", "Live")
        
        top_skills = df.nlargest(12, 'lift')
        fig = px.bar(top_skills, x='lift', y='consequents', orientation='h', 
                     title="Strongest Skill Synergies", color='lift', color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)

    # --- AI ROADMAP PAGE ---
    elif st.session_state.page == "AI":
        st.title("🤖 AI Career Path Consultant")
        query = st.text_input("What is your goal? (e.g., Python Developer, Data Scientist)")
        
        if query:
            with st.spinner("AI is calculating your path..."):
                relevant = df[df['antecedents'].str.contains(query, case=False, na=False)].head(5)
                context = relevant.to_string() if not relevant.empty else "Standard industry roadmap"
                
                try:
                    model = genai.GenerativeModel(WORKING_MODEL)
                    prompt = f"Using this market data: {context}. Create a 3-phase roadmap for: {query}. Focus on high-demand skills."
                    response = model.generate_content(prompt)
                    st.markdown("### 🎓 Recommended Roadmap")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"AI Sync Error: {e}")

    # --- TRENDS PAGE ---
    elif st.session_state.page == "Trends":
        st.title("📈 Skill Growth Trends")
        fig_trend = px.scatter(df.head(50), x="support", y="confidence", size="lift", 
                               color="lift", hover_name="consequents", title="Market Confidence vs Support")
        st.plotly_chart(fig_trend, use_container_width=True)

    # --- EXPORT PAGE ---
    elif st.session_state.page == "Export":
        st.title("📄 Export Data Report")
        st.write("Download the top 50 skill associations as a CSV for offline analysis.")
        csv = df.head(50).to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Market Report", data=csv, file_name="market_report.csv", mime="text/csv")

else:
    st.error("🚨 Critical Error: 'skill_rules_final.csv' not found in repository!")
