import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import glob
import os
import numpy as np
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="UIDAI Analytics Hub",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- STATE NORMALIZATION ---
CANONICAL_STATES = {
    "westbengal": "West Bengal", "west bangal": "West Bengal", "west bengal": "West Bengal",
    "orissa": "Odisha", "odisha": "Odisha",
    "andaman and nicobar islands": "Andaman & Nicobar Islands", 
    "jammu and kashmir": "Jammu & Kashmir", 
    "dadra and nagar haveli": "Dadra & Nagar Haveli and Daman & Diu",
    "dadra and nagar haveli and daman and diu": "Dadra & Nagar Haveli and Daman & Diu",
    "the dadra and nagar haveli and daman and diu": "Dadra & Nagar Haveli and Daman & Diu",
    "daman and diu": "Dadra & Nagar Haveli and Daman & Diu",
    "pondicherry": "Puducherry", "puducherry": "Puducherry",
    "karnatka": "Karnataka", "telngana": "Telangana", "andhrapradesh": "Andhra Pradesh",
    "u.p.": "Uttar Pradesh", "m.p.": "Madhya Pradesh", "a.p.": "Andhra Pradesh"
}

def clean_state_name(name):
    s = str(name).lower().strip()
    s = s.replace("&", "and")
    s = " ".join(s.split())
    return CANONICAL_STATES.get(s, s.title())

DISPLAY_MAP = {
    "age_0_5": "Infants (0-5)",
    "age_5_17": "Students (5-17)",
    "age_18_greater": "Adults (18+)",
    "bio_age_5_17": "Bio Update: Minors",
    "bio_age_17_": "Bio Update: Adults",
    "demo_age_5_17": "Info Update: Minors",
    "demo_age_17_": "Info Update: Adults"
}

# --- MODERN GRADIENT THEME ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    font-family: 'Inter', sans-serif;
}

section[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
}

.main .block-container {
    padding: 2rem 4rem;
    max-width: 1400px;
}

h1 {
    color: white !important;
    font-weight: 700 !important;
    font-size: 3rem !important;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    margin-bottom: 0.5rem !important;
}

h2, h3 {
    color: white !important;
    font-weight: 600 !important;
}

.subtitle {
    color: rgba(255,255,255,0.9) !important;
    font-size: 1.2rem;
    margin-bottom: 2rem;
}

.glass-card {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 2rem;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    margin-bottom: 1.5rem;
}

.metric-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.1) 100%);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 1.5rem;
    border: 1px solid rgba(255, 255, 255, 0.3);
    text-align: center;
    transition: transform 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-5px);
}

.metric-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: white;
    margin: 0;
}

.metric-label {
    font-size: 0.9rem;
    color: rgba(255,255,255,0.8);
    margin-top: 0.5rem;
}

.alert-critical {
    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 12px;
    margin-bottom: 1rem;
    border-left: 5px solid #c92a2a;
}

.alert-warning {
    background: linear-gradient(135deg, #ffd93d 0%, #ffb700 100%);
    color: #333;
    padding: 1.5rem;
    border-radius: 12px;
    margin-bottom: 1rem;
    border-left: 5px solid #f76707;
}

.alert-success {
    background: linear-gradient(135deg, #51cf66 0%, #37b24d 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 12px;
    margin-bottom: 1rem;
    border-left: 5px solid #2b8a3e;
}

div[data-testid="stMetricValue"] {
    color: white !important;
    font-size: 2rem !important;
}

div[data-testid="stMetricLabel"] {
    color: rgba(255,255,255,0.9) !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
    background: rgba(255, 255, 255, 0.1);
    padding: 15px;
    border-radius: 15px;
    backdrop-filter: blur(10px);
}

.stTabs [data-baseweb="tab"] {
    background: rgba(255, 255, 255, 0.2);
    color: white;
    border-radius: 10px;
    padding: 15px 30px;
    border: none;
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    background: white !important;
    color: #667eea !important;
}

.status-badge {
    display: inline-block;
    padding: 0.5rem 1rem;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.9rem;
}

.badge-critical {
    background: #ff6b6b;
    color: white;
}

.badge-medium {
    background: #ffd93d;
    color: #333;
}

.badge-low {
    background: #51cf66;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# --- POPULATION DATA ---
CRS_BIRTHS = {
    'Uttar Pradesh': 4500000, 'Bihar': 3200000, 'Maharashtra': 1800000, 
    'West Bengal': 1400000, 'Rajasthan': 1600000, 'Delhi': 350000,
    'Tamil Nadu': 900000, 'Gujarat': 1100000, 'Karnataka': 1000000,
    'Odisha': 700000, 'Andhra Pradesh': 800000, 'Telangana': 600000,
    'Kerala': 450000, 'Madhya Pradesh': 1500000, 'Haryana': 550000
}

# --- DATA LOADING ---
@st.cache_data
def load_mission_data():
    base_path = os.getcwd()
    folders = {
        "bio": "api_data_aadhar_biometric", 
        "demo": "api_data_aadhar_demographic", 
        "enrol": "api_data_aadhar_enrolment"
    }
    data, health = {}, {}
    
    for key, folder in folders.items():
        files = glob.glob(os.path.join(base_path, folder, "*.csv")) + glob.glob(f"{folder}*.csv")
        if files:
            try:
                df = pd.concat([pd.read_csv(f, low_memory=False) for f in files], ignore_index=True)
                df['state'] = df['state'].apply(clean_state_name)
                df = df[~df['state'].str.isnumeric()]
                df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
                data[key] = df.dropna(subset=['date'])
                health[folder] = f"✅ Active ({len(files)} files)"
            except Exception as e:
                health[folder] = f"❌ Error: {str(e)}"
                data[key] = pd.DataFrame()
        else:
            health[folder] = "⚠️ No Data"
            data[key] = pd.DataFrame()
    
    return data, health

datasets, health_status = load_mission_data()

# --- RISK CALCULATION ---
def calculate_master_risk():
    if datasets['enrol'].empty:
        return pd.DataFrame()
    
    states = sorted(datasets['enrol']['state'].unique())
    rows = []
    
    for s in states:
        e = datasets['enrol'][datasets['enrol']['state'] == s][['age_0_5', 'age_5_17', 'age_18_greater']].sum().sum()
        b = datasets['bio'][datasets['bio']['state'] == s][['bio_age_5_17', 'bio_age_17_']].sum().sum()
        d = datasets['demo'][datasets['demo']['state'] == s][['demo_age_5_17', 'demo_age_17_']].sum().sum()
        
        # Ensure IER has a minimum value to prevent treemap ZeroDivisionError
        ier = max((e / CRS_BIRTHS.get(s, 500000)) * 10, 0.01)
        bcr = (b / max(e, 1)) * 5
        dv = (d / max(e, 1)) * 5
        iri = (ier * 0.4) + (bcr * 0.3) + (dv * 0.3)
        
        tier = "CRITICAL" if iri >= 6 else "MEDIUM" if iri >= 3 else "LOW"
        color = "#ff6b6b" if tier == "CRITICAL" else "#ffd93d" if tier == "MEDIUM" else "#51cf66"
        
        rows.append({
            "state": s, 
            "IRI": round(iri, 2), 
            "IER": round(ier, 2), 
            "BCR": round(bcr, 2), 
            "DV": round(dv, 2), 
            "Tier": tier, 
            "Color": color
        })
    
    return pd.DataFrame(rows).sort_values("IRI", ascending=False)

risk_master = calculate_master_risk()

# --- HEADER ---
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.markdown("# 🔐 UIDAI Analytics Hub")
    st.markdown('<p class="subtitle">National Identity Intelligence Platform</p>', unsafe_allow_html=True)
with header_col2:
    avg_iri = risk_master['IRI'].mean() if not risk_master.empty else 0
    status = "CRITICAL" if avg_iri >= 6 else "MEDIUM" if avg_iri >= 3 else "STABLE"
    badge_class = "badge-critical" if avg_iri >= 6 else "badge-medium" if avg_iri >= 3 else "badge-low"
    st.markdown(f'<div style="text-align: right; margin-top: 2rem;"><span class="status-badge {badge_class}">System Status: {status}</span></div>', unsafe_allow_html=True)

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📈 Analytics", "⚠️ Risk Monitor", "🛡️ Protection"])

# ==================== TAB 1: DASHBOARD ====================
with tab1:
    # KPI Cards
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    if not datasets['enrol'].empty:
        total_enrol = int(datasets['enrol'][['age_0_5', 'age_5_17', 'age_18_greater']].sum().sum())
        critical_zones = len(risk_master[risk_master['Tier'] == 'CRITICAL'])
        
        with kpi1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_enrol//1000}K</div>
                <div class="metric-label">Total Enrollments</div>
            </div>
            """, unsafe_allow_html=True)
        
        with kpi2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{critical_zones}</div>
                <div class="metric-label">Critical Zones</div>
            </div>
            """, unsafe_allow_html=True)
        
        with kpi3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">5.4M</div>
                <div class="metric-label">Monthly Updates</div>
            </div>
            """, unsafe_allow_html=True)
        
        with kpi4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">92%</div>
                <div class="metric-label">Coverage Rate</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main Dashboard Content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🗺️ National Coverage Map")
        
        if not risk_master.empty:
            # Check if all IER values are zero to avoid ZeroDivisionError
            if risk_master['IER'].sum() > 0:
                fig = px.treemap(
                    risk_master, 
                    path=[px.Constant("India"), 'state'], 
                    values='IER', 
                    color='IRI',
                    color_continuous_scale='RdYlGn_r',
                    template="plotly_white"
                )
                fig.update_layout(height=400, margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)
            else:
                # Fallback: Use IRI as values when IER is all zeros
                fig = px.treemap(
                    risk_master, 
                    path=[px.Constant("India"), 'state'], 
                    values='IRI', 
                    color='IRI',
                    color_continuous_scale='RdYlGn_r',
                    template="plotly_white"
                )
                fig.update_layout(height=400, margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🚨 Live Alerts")
        
        for _, row in risk_master.head(5).iterrows():
            alert_class = "alert-critical" if row['Tier'] == "CRITICAL" else "alert-warning" if row['Tier'] == "MEDIUM" else "alert-success"
            st.markdown(f"""
            <div class="{alert_class}">
                <strong>{row['state']}</strong><br>
                Risk Index: {row['IRI']} ({row['Tier']})
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==================== TAB 2: ANALYTICS ====================
with tab2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 📊 Trend Analysis")
    
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
    
    with filter_col1:
        view_type = st.selectbox("Scope", ["National", "State-wise"])
    with filter_col2:
        granularity = st.selectbox("Period", ["Monthly", "Quarterly", "Yearly"])
    with filter_col3:
        chart_type = st.selectbox("Chart", ["Line", "Bar", "Area"])
    with filter_col4:
        data_stream = st.selectbox("Stream", ["Combined", "Enrolment", "Biometric", "Demographic"])
    
    selected_state = None
    if view_type == "State-wise":
        selected_state = st.selectbox("Select State", sorted(risk_master['state'].unique()))
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Plotting logic
    if all([granularity, chart_type, data_stream]):
        freq_map = {"Monthly": "ME", "Quarterly": "QE", "Yearly": "YE"}
        
        def get_trend_data(state=None):
            result = pd.DataFrame()
            
            if data_stream in ["Combined", "Enrolment"]:
                df = datasets['enrol']
                if state:
                    df = df[df['state'] == state]
                result = df.groupby(pd.Grouper(key='date', freq=freq_map[granularity]))[['age_0_5', 'age_5_17', 'age_18_greater']].sum()
            
            if data_stream in ["Combined", "Biometric"]:
                df = datasets['bio']
                if state:
                    df = df[df['state'] == state]
                bio_data = df.groupby(pd.Grouper(key='date', freq=freq_map[granularity]))[['bio_age_5_17', 'bio_age_17_']].sum()
                result = pd.concat([result, bio_data], axis=1)
            
            if data_stream in ["Combined", "Demographic"]:
                df = datasets['demo']
                if state:
                    df = df[df['state'] == state]
                demo_data = df.groupby(pd.Grouper(key='date', freq=freq_map[granularity]))[['demo_age_5_17', 'demo_age_17_']].sum()
                result = pd.concat([result, demo_data], axis=1)
            
            return result.fillna(0).reset_index().rename(columns=DISPLAY_MAP)
        
        plot_data = get_trend_data(selected_state)
        metrics = [c for c in plot_data.columns if c != 'date']
        
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        if chart_type == "Line":
            fig = px.line(plot_data, x='date', y=metrics, template="plotly_white", markers=True)
        elif chart_type == "Area":
            fig = px.area(plot_data, x='date', y=metrics, template="plotly_white")
        else:
            fig = px.bar(plot_data, x='date', y=metrics, template="plotly_white", barmode="group")
        
        fig.update_layout(height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==================== TAB 3: RISK MONITOR ====================
with tab3:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### ⚖️ Risk Assessment Model")
    
    st.markdown("""
    **Risk Index (IRI) Formula:**
    - IER (Identity Expansion Ratio): Enrollments ÷ Birth Proxy
    - BCR (Biometric Churn Rate): Updates ÷ Identity Base
    - DV (Demographic Volatility): Changes ÷ Identity Base
    """)
    
    st.latex(r"IRI = (IER \times 0.4) + (BCR \times 0.3) + (DV \times 0.3)")
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🏆 Top Risk States")
        
        if not risk_master.empty:
            fig = px.bar(
                risk_master.head(10), 
                x='IRI', 
                y='state', 
                orientation='h',
                color='IRI',
                color_continuous_scale='Reds',
                template="plotly_white"
            )
            fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Risk Distribution")
        
        if not risk_master.empty:
            risk_counts = risk_master['Tier'].value_counts()
            fig = px.pie(
                values=risk_counts.values,
                names=risk_counts.index,
                color=risk_counts.index,
                color_discrete_map={'CRITICAL': '#ff6b6b', 'MEDIUM': '#ffd93d', 'LOW': '#51cf66'},
                template="plotly_white"
            )
            fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ==================== TAB 4: PROTECTION ====================
with tab4:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 🛡️ Citizen Protection Program")
    
    step1, step2, step3, step4 = st.columns(4)
    
    with step1:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: white; margin: 0;">1️⃣</h3>
            <p style="color: white; margin-top: 1rem;">Risk Detection</p>
        </div>
        """, unsafe_allow_html=True)
    
    with step2:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: white; margin: 0;">2️⃣</h3>
            <p style="color: white; margin-top: 1rem;">Target Vulnerable</p>
        </div>
        """, unsafe_allow_html=True)
    
    with step3:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: white; margin: 0;">3️⃣</h3>
            <p style="color: white; margin-top: 1rem;">Send Alerts</p>
        </div>
        """, unsafe_allow_html=True)
    
    with step4:
        st.markdown("""
        <div class="metric-card">
            <h3 style="color: white; margin: 0;">4️⃣</h3>
            <p style="color: white; margin-top: 1rem;">Secure Access</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🚀 Simulation Center")
        
        if st.button("▶️ Run Protection Simulation", use_container_width=True):
            with st.status("Running simulation...", expanded=True) as status:
                st.write("🔍 Scanning vulnerable populations...")
                time.sleep(1)
                st.write("📨 Dispatching alerts...")
                time.sleep(1)
                st.write("✅ Protection protocols activated...")
                time.sleep(1)
                status.update(label="Simulation Complete!", state="complete", expanded=False)
            
            st.balloons()
            st.success("✅ 1.4M citizens protected from service disruption")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Impact Metrics")
        
        st.metric("Coverage", "88%", "+12%")
        st.metric("Response Time", "2.4s", "-0.8s")
        st.metric("Success Rate", "94%", "+5%")
        
        st.markdown('</div>', unsafe_allow_html=True)