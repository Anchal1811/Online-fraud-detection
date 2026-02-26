import os
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split

# --- DYNAMIC PATH HANDLING ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Points to Backend/data/new_data.csv as seen in your folder structure
CSV_PATH = os.path.join(BASE_DIR, 'data', 'new_data.csv') 
MODEL_PATH = os.path.join(BASE_DIR, 'fraud_model.json')
FEATURES_PATH = os.path.join(BASE_DIR, 'features.npy')

def train_and_save_model():
    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"❌ Error: {CSV_PATH} not found!")
    
    print("🚀 Loading data and training model... This may take a minute.")
    data = pd.read_csv(CSV_PATH)
    
    # Preprocessing: Convert transaction types to dummy variables
    type_dummies = pd.get_dummies(data['type'], drop_first=True)
    data_final = pd.concat([data, type_dummies], axis=1)
    
    # Define Features (X) and Target (y)
    # We drop non-numeric IDs and the target column
    X = data_final.drop(['isFraud', 'type', 'nameOrig', 'nameDest'], axis=1)
    y = data_final['isFraud']
    
    X_train, _, y_train, _ = train_test_split(X, y, test_size=0.3, random_state=42)
    
    # Train the XGBoost Classifier
    model = XGBClassifier()
    model.fit(X_train, y_train)
    
    # Save model and column names to ensure consistency
    model.save_model(MODEL_PATH)
    np.save(FEATURES_PATH, X.columns.values)
    print(f"✅ Model trained and saved to {MODEL_PATH}")

# Auto-train on first run
if not os.path.exists(MODEL_PATH):
    train_and_save_model()

# Load model for the API
model = XGBClassifier()
model.load_model(MODEL_PATH)
feature_columns = np.load(FEATURES_PATH, allow_pickle=True)

def predict_fraud(transaction_data: dict):
    df = pd.DataFrame([transaction_data])
    
    # Add missing dummy columns with 0 if they weren't in the input
    for col in feature_columns:
        if col not in df.columns:
            df[col] = 0
            
    # Reorder columns to match exactly what the model expects
    df = df[feature_columns]
    
    prediction = model.predict(df)[0]
    probability = model.predict_proba(df)[0][1]
    
    return int(prediction), float(probability)