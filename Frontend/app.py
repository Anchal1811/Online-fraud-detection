import streamlit as st
import requests

st.set_page_config(page_title="Fraud Guard AI", layout="centered")
st.title("💳 Online Payment Fraud Detector")

# Form for user input
with st.form("transaction_form"):
    st.subheader("Enter Transaction Details")
    step = st.number_input("Time Step (Hour)", value=1, min_value=1)
    amount = st.number_input("Transaction Amount ($)", value=0.0)
    
    col1, col2 = st.columns(2)
    old_orig = col1.number_input("Sender Old Balance", value=0.0)
    new_orig = col2.number_input("Sender New Balance", value=0.0)
    
    col3, col4 = st.columns(2)
    old_dest = col3.number_input("Receiver Old Balance", value=0.0)
    new_dest = col4.number_input("Receiver New Balance", value=0.0)
    
    trans_type = st.selectbox("Transaction Type", ["CASH_OUT", "TRANSFER", "PAYMENT", "DEBIT", "CASH_IN"])
    
    submit = st.form_submit_button("Verify Transaction")

if submit:
    # Prepare the payload for FastAPI
    payload = {
        "step": step, 
        "amount": amount,
        "oldbalanceOrg": old_orig, 
        "newbalanceOrg": new_orig,
        "oldbalanceDest": old_dest, 
        "newbalanceDest": new_dest,
        "CASH_OUT": 1 if trans_type == "CASH_OUT" else 0,
        "TRANSFER": 1 if trans_type == "TRANSFER" else 0,
        "DEBIT": 1 if trans_type == "DEBIT" else 0,
        "PAYMENT": 1 if trans_type == "PAYMENT" else 0
    }
    
    try:
        # Send request to Backend
        response = requests.post("http://127.0.0.1:8000/detect", json=payload)
        res = response.json()
        
        # Clean confidence score for display
        conf_str = res['confidence'].replace('%', '')
        confidence_val = float(conf_str) / 100
        
        st.divider()
        st.subheader("Analysis Results")
        
        # Visual Risk Indicator
        if res["is_fraud"] == 1:
            st.error(f"🚨 FRAUD ALERT! Confidence: {res['confidence']}")
            st.progress(confidence_val)
        elif confidence_val > 0.10: # Flagging suspicious cases above 10%
            st.warning(f"⚠️ SUSPICIOUS PATTERN. Confidence: {res['confidence']}")
            st.progress(confidence_val)
        else:
            st.success(f"✅ TRANSACTION SAFE. Confidence: {res['confidence']}")
            st.progress(confidence_val)

    except Exception as e:
        st.error("❌ Connection to Backend failed. Ensure 'uvicorn main:app' is running.")