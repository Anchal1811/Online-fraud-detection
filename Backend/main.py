from fastapi import FastAPI
from pydantic import BaseModel
from model import predict_fraud

app = FastAPI(title="Fraud Detection API")

class Transaction(BaseModel):
    step: int
    amount: float
    oldbalanceOrg: float
    newbalanceOrg: float
    oldbalanceDest: float
    newbalanceDest: float
    CASH_OUT: int = 0
    TRANSFER: int = 0
    DEBIT: int = 0
    PAYMENT: int = 0

@app.post("/detect")
async def detect(data: Transaction):
    is_fraud, prob = predict_fraud(data.dict())
    return {
        "is_fraud": is_fraud,
        "confidence": f"{prob * 100:.2f}%"
    }