from fastapi import FastAPI
from pydantic import BaseModel, Field
from model import predict_fraud

# --- API Branding ---
app = FastAPI(
    title="Online Fraud Detection & Prevention System (OFDPS)",
    description="Enterprise-grade API for real-time transaction monitoring and risk scoring.",
    version="2.0.0"
)

class Transaction(BaseModel):
    step: int = Field(..., gt=0)
    amount: float = Field(..., gt=0)
    oldbalanceOrg: float = Field(..., ge=0)
    newbalanceOrg: float = Field(..., ge=0)
    oldbalanceDest: float = Field(..., ge=0)
    newbalanceDest: float = Field(..., ge=0)
    CASH_OUT: int = 0
    TRANSFER: int = 0
    DEBIT: int = 0
    PAYMENT: int = 0

def get_fraud_reason(data: dict, risk_score: float):
    reasons = []
    # Business Logic Rules
    if data['amount'] > (0.95 * data['oldbalanceOrg']):
        reasons.append("Critical: Transaction drains >95% of account balance.")
    if data['amount'] > 500000 and data['TRANSFER'] == 1:
        reasons.append("Flag: High-value transfer threshold exceeded.")
    
    return " | ".join(reasons) if reasons else "Pattern consistent with normal behavior."

@app.post("/detect")
async def detect(data: Transaction):
    input_data = data.dict()
    is_fraud_ml, prob = predict_fraud(input_data)
    risk_score = prob * 100
    
    reasoning = get_fraud_reason(input_data, risk_score)
    # Risk-Based Categorization
    final_risk = "High" if ("Critical" in reasoning or risk_score > 75) else "Medium" if risk_score > 40 else "Low"
    
    return {
        "is_fraud": True if final_risk == "High" else False,
        "confidence": f"{risk_score:.2f}%",
        "risk_level": final_risk,
        "reasoning": reasoning
    }