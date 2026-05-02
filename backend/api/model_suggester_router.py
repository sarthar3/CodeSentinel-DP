from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import pandas as pd
import os
import uuid
from typing import Optional
from .rag_router import get_groq_client

router = APIRouter()

UPLOAD_DIR = "uploads/suggester"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/suggest")
async def suggest_model(
    file: UploadFile = File(...),
    description: str = Form(...),
    extra_input: Optional[str] = Form(None)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    file_id = str(uuid.uuid4())
    path = os.path.join(UPLOAD_DIR, f"{file_id}.csv")
    
    with open(path, "wb") as f:
        f.write(await file.read())

    try:
        df = pd.read_csv(path)
        
        # Analyze dataset structure
        summary = {
            "columns": list(df.columns),
            "dtypes": df.dtypes.apply(lambda x: str(x)).to_dict(),
            "shape": df.shape,
            "null_counts": df.isnull().sum().to_dict(),
            "sample": df.head(3).to_dict(orient='records')
        }

        # Prepare prompt for LLM
        prompt = f"""
        As an AI/ML Expert, analyze the following dataset summary and project description to suggest the best algorithm.
        
        ### Project Description:
        {description}
        
        ### Dataset Summary:
        - Shape: {summary['shape']}
        - Columns and Types: {json.dumps(summary['dtypes'], indent=2)}
        - Sample Data: {json.dumps(summary['sample'], indent=2)}
        
        ### Additional User Input:
        {extra_input if extra_input else "None"}
        
        ### Requirements:
        1. Suggest the best AI, ML, or DL algorithm/model.
        2. Provide a detailed rationale for the selection.
        3. Explain how the data should be further prepared for this specific model.
        4. Suggest 2-3 alternative models and when they might be better.
        
        Format your response in Markdown with clear headings.
        """

        client = get_groq_client()
        if not client:
            return {"error": "LLM client not configured", "summary": summary}

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert Data Scientist and AI Architect."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )

        recommendation = completion.choices[0].message.content

        return {
            "recommendation": recommendation,
            "summary": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error suggesting model: {str(e)}")

import json
