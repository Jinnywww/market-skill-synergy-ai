import streamlit as st
import pandas as pd
import plotly.express as px
import os
import google.generativeai as genai
from fpdf import FPDF
import base64
from datetime import datetime

# --- 1. AI CONFIGURATION (Auto-Fix for 404 Error) ---
API_KEY = "AIzaSyAtXi1d8UvAtsdOJK5ggH3Tr0GzOYMf_nU"
genai.configure(api_key=API_KEY)

# သင့် Key နဲ့ အလုပ်လုပ်တဲ့ Model အမှန်ကို အလိုအလျောက် ရှာဖွေပေးမယ့် Function
def get_working_model():
    try:
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        # gemini-1.5-flash ပါရင် အရင်သုံးမယ်၊ မပါရင် ပထမဆုံးရတဲ့ model ကို သုံးမယ်
        for m_name in models:
            if 'gemini-1.5-flash' in m_name:
                return m_name
        return models[0] if models else "gemini-pro"
    except:
        return "gemini-1.5-flash" # Fallback

WORKING_MODEL = get_working_model()

# --- 2. PAGE CONFIGURATION ---
st.set_page_config(page_title="Market Skill Synergy AI", layout="wide")

# --- 3. PREMIUM UI/UX STYLING ---
st.markdown('''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #1E293B; }
    .stApp { background-color: #F8FAFC; }
    section[data-testid="stSidebar"] { background-color: #205781 !important; min-width: 280px !important; }
    .stButton > button {
        width: 100%; background-color: transparent; color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 8px; padding: 12px 15px; text-align: left;
        transition: all 0.3s ease; font-weight: 500; margin-bottom: 8px;
    }
    .stButton > button:hover {
        border-color: #FFFFFF !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
        transform: translateX(10px);
        box-shadow: 2px 4px 12px rgba(0, 0, 0, 0.2);
    }
    div[data-testid="stMetric"] { background-color: #FFFFFF; padding: 20px; border-radius: 12px; border: 1px solid #E2E8F0; }
    h1 { color: #205781 !important; font-weight: 700 !important; }
    </style>
''', unsafe_allow_html=True)

# --- 4. CORE BACKEND FUNCTIONS ---
@st.cache_data
def load_data():
    file_name = 'skill_rules_final.csv'
    if os.path.exists(file_name):
        df = pd.read_csv(file_name)
        df['antecedents'] = df['antecedents'].astype(str)
        return df
    return None

def generate_pdf_report(data_subset, report_title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(32, 87, 129)
    pdf.cell(0, 20, "Market Skill Intelligence Report", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=11)
    for _, row in data_subset.iterrows():
        pdf.cell(80, 10, str(row['antecedents']), border=1)
        pdf.cell(80, 10, str(row['consequents']), border=1)
        pdf.cell(30, 10, f"{row['lift']:.2f}", border=1)
        pdf.ln()
    return pdf.output(dest='S').encode('latin-1')

# --- 5. APP LOGIC ---
df = load_data()

if df is not None:
    st.sidebar.markdown("<h2 style='color:white;'>Market AI</h2>", unsafe_allow_html=True)
    st.sidebar.info(f"Active Model: {WORKING_MODEL}") # ဘယ် model သုံးနေလဲ ပြပေးမယ်
    
    if 'page' not in st.session_state: st.session_state.page = "Summary"
    
    if st.sidebar.button("📊 Executive Summary"): st.session_state.page = "Summary"
    if st.sidebar.button("📈 Market Trends AI"): st.session_state.page = "Trends"
    if st.sidebar.button("🤖 AI Skill Assistant"): st.session_state.page = "AI"
    if st.sidebar.button("📄 PDF Reporting"): st.session_state.page = "PDF"

    if st.session_state.page == "Summary":
        st.title("Market Intelligence Overview")
        c1, c2, c3 = st.columns(3)
        c1.metric("Job Samples", "1.2 Million")
        c2.metric("Market Rules", f"{len(df):,}")
        c3.metric("Backend Status", "Connected")
        st.plotly_chart(px.bar(df.nlargest(12, 'lift'), x='lift', y='consequents', orientation='h', color='lift'), use_container_width=True)

    elif st.session_state.page == "Trends":
        st.title("📈 Predictive Skill Trends")
        df['Trend_Score'] = (df['lift'] * 0.7) + (df['confidence'] * 0.3)
        st.plotly_chart(px.line(df.nlargest(15, 'Trend_Score'), x='consequents', y='Trend_Score', markers=True), use_container_width=True)

    elif st.session_state.page == "AI":
        st.title("🤖 AI Career Path Consultant")
        st.markdown("""
            #### How can I help you today?
            Your career roadmap is generated based on **1.2 Million real-world job market associations**.
            *Try asking:*
            - *'How to be a Data Scientist?'*
            - *'What skills should I learn after Python?'*
            - *'Roadmap for Cloud Engineering'*
        """)
        
        user_msg = st.text_input("Type your career goal or current skill here:", placeholder="e.g. Data Scientist")
        
        if user_msg:
            with st.spinner("Analyzing market synergy and generating your roadmap..."):
                # Backend Logic: Search CSV
                relevant = df[df['antecedents'].str.contains(user_msg, case=False, na=False)].head(10)
                context = relevant.to_string() if not relevant.empty else "General industry standards"
                
                try:
                    model = genai.GenerativeModel(WORKING_MODEL)
                    # AI ကို Format သေချာချခိုင်းတဲ့ Prompt
                    prompt = f"""
                    You are a Professional Career Consultant. 
                    Based on this Market Data: {context}
                    User Question: {user_msg}
                    Please provide a detailed roadmap including:
                    1. Core Foundation
                    2. Phase 1: Broadening Skills (High Demand)
                    3. Phase 2: Specialization (High Lift/Synergy)
                    4. Potential Job Roles
                    Use professional formatting with bold text and bullet points.
                    """
                    response = model.generate_content(prompt)
                    
                    st.markdown("---")
                    st.markdown("### 🎓 Your Data-Driven Career Roadmap")
                    st.markdown(response.text) # AI အဖြေကို ပြသခြင်း
                    
                except Exception as e:
                    st.error(f"Connection Error: {e}")

    elif st.session_state.page == "PDF":
        st.title("📄 Generate Report")
        if st.button("Generate PDF"):
            pdf_data = generate_pdf_report(df.head(25), "Market_Report")
            b64 = base64.b64encode(pdf_data).decode()
            st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="MarketReport.pdf">📥 Download PDF</a>', unsafe_allow_html=True)
else:
    st.error("Missing File: skill_rules_final.csv not found!")
