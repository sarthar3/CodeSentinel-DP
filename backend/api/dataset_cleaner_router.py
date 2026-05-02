from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib
import os
import uuid
import json

router = APIRouter()

UPLOAD_DIR = "uploads/cleaner"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/clean")
async def clean_dataset(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    file_id = str(uuid.uuid4())
    input_path = os.path.join(UPLOAD_DIR, f"{file_id}_input.csv")
    
    with open(input_path, "wb") as f:
        f.write(await file.read())

    try:
        df = pd.read_csv(input_path)
        original_shape = df.shape
        
        # 1. Basic Cleaning: Remove duplicates
        df = df.drop_duplicates()
        
        # 2. Handle Missing Values
        # Numeric: Fill with mean
        # Categorical: Fill with mode
        for col in df.columns:
            if df[col].dtype in ['int64', 'float64']:
                df[col] = df[col].fillna(df[col].mean())
            else:
                df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else "Unknown")

        # 3. Encoding Categorical Variables
        le_dict = {}
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            le_dict[col] = le

        # 4. Save results
        cleaned_filename = f"{file_id}_cleaned.csv"
        pkl_filename = f"{file_id}_preprocessor.pkl"
        cleaned_path = os.path.join(UPLOAD_DIR, cleaned_filename)
        pkl_path = os.path.join(UPLOAD_DIR, pkl_filename)
        
        df.to_csv(cleaned_path, index=False)
        joblib.dump(le_dict, pkl_path)

        return {
            "file_id": file_id,
            "original_shape": original_shape,
            "cleaned_shape": df.shape,
            "categorical_columns": list(categorical_cols),
            "cleaned_csv": cleaned_filename,
            "preprocessor_pkl": pkl_filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing dataset: {str(e)}")

@router.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)
