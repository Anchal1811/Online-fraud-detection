import streamlit as st
import requests
import plotly.graph_objects as go
import time

# --- Page Branding ---
st.set_page_config(page_title="OFD Prevention System", layout="wide", page_icon="🛡️")

st.title("🛡️ Online Fraud Detection & Prevention System")
st.subheader("Real-Time Financial Security Dashboard")
st.markdown("---")

tab1, tab2 = st.tabs(["🔍 Transaction Analysis", "📡 Live Security Stream"])

with tab1:
    col_input, col_viz = st.columns([1, 1.5])
    
    with col_input:
        st.write("### Input Parameters")
        amt = st.number_input("Transaction Amount ($)", min_value=0.0, value=5000.0)
        t_type = st.selectbox("Transaction Type", ["TRANSFER", "CASH_OUT", "PAYMENT", "DEBIT"])
        old_bal = st.number_input("Origin Account Balance", value=10000.0)
        new_bal = st.number_input("Resulting Account Balance", value=5000.0)

        payload = {
            "step": 1, "amount": amt, "oldbalanceOrg": old_bal, "newbalanceOrg": new_bal,
            "oldbalanceDest": 0.0, "newbalanceDest": amt,
            "TRANSFER": 1 if t_type == "TRANSFER" else 0,
            "CASH_OUT": 1 if t_type == "CASH_OUT" else 0,
            "PAYMENT": 1 if t_type == "PAYMENT" else 0,
            "DEBIT": 1 if t_type == "DEBIT" else 0
        }

        if st.button("🚀 Run Security Scan"):
            try:
                # Connected to Port 8001
                response = requests.post("http://localhost:8001/detect", json=payload)
                if response.status_code == 200:
                    st.session_state['res'] = response.json()
            except:
                st.error("Connection Error: Is the OFD Backend running on port 8001?")

    with col_viz:
        if 'res' in st.session_state:
            res = st.session_state['res']
            score = float(res['confidence'].replace("%", ""))
            
            # Risk Gauge with 2026 'stretch' parameter
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = score,
                title = {'text': f"Risk Assessment: {res['risk_level']}"},
                gauge = {
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "red" if score > 75 else "orange" if score > 40 else "green"}
                }
            ))
            st.plotly_chart(fig, width='stretch')
            st.info(f"**Security Reasoning:** {res['reasoning']}")

with tab2:
    st.write("### 📡 Live Institutional Monitoring")
    if st.button("Initiate Network Stream"):
        log_box = st.empty()
        log_data = []
        for i in range(10):
            is_fraud = i % 4 == 0
            status = "🚨 BLOCKED" if is_fraud else "✅ CLEAN"
            log_entry = f"[{time.strftime('%H:%M:%S')}] TXN-{2000+i}: {status} | Risk: {92 if is_fraud else i*6}%"
            log_data.insert(0, log_entry)
            log_box.code("\n".join(log_data))
            time.sleep(0.5)