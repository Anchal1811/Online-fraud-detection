import os
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE  # Add this to requirements.txt

# --- DYNAMIC PATH HANDLING ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, 'data', 'new_data.csv') 
MODEL_PATH = os.path.join(BASE_DIR, 'fraud_model.json')
FEATURES_PATH = os.path.join(BASE_DIR, 'features.npy')

def train_and_save_model():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"❌ Error: {CSV_PATH} not found!")
    
    print("🚀 Loading data and applying SMOTE... This may take a minute.")
    data = pd.read_csv(CSV_PATH)
    
    # 1. Preprocessing
    data = pd.get_dummies(data, columns=['type'], drop_first=True)
    
    # Define Features (X) and Target (y)
    # Ensure these names match your specific CSV columns
    drop_cols = ['isFraud', 'nameOrig', 'nameDest']
    X = data.drop(columns=[c for c in drop_cols if c in data.columns])
    y = data['isFraud']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 2. Handle Imbalance: Synthetic Minority Over-sampling Technique
    # This solves the "Models ignoring the fraud class" problem
    smote = SMOTE(random_state=42)
    X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
    
    # 3. Train XGBoost with scale_pos_weight for extra sensitivity
    model = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        scale_pos_weight=len(y_train[y_train==0]) / len(y_train[y_train==1]), # Balance weight
        use_label_encoder=False,
        eval_metric='logloss'
    )
    model.fit(X_train_res, y_train_res)
    
    # 4. Save model and features
    model.save_model(MODEL_PATH)
    np.save(FEATURES_PATH, X.columns.values)
    print(f"✅ Balanced Model saved to {MODEL_PATH}")

# Auto-train or Load
if not os.path.exists(MODEL_PATH):
    train_and_save_model()

model = XGBClassifier()
model.load_model(MODEL_PATH)
feature_columns = np.load(FEATURES_PATH, allow_pickle=True)

def predict_fraud(transaction_data: dict):
    df = pd.DataFrame([transaction_data])
    
    # Ensure all trained features exist in input, default to 0
    for col in feature_columns:
        if col not in df.columns:
            df[col] = 0
            
    df = df[feature_columns] # Reorder to match model
    
    prediction = model.predict(df)[0]
    probability = model.predict_proba(df)[0][1] # Vital for Risk-Based Action
    
    return int(prediction), float(probability)