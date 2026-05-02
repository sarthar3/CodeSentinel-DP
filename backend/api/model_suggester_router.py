from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import pandas as pd
import os
import re
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
        1. Suggest the best algorithm/model and provide a detailed rationale.
        2. Provide 2 alternative models.
        3. For the main recommendation and alternatives, provide an ESTIMATED accuracy score (0.0 to 1.0) based on the data complexity.
        4. Provide a 2x2 mock Confusion Matrix (Normal/Anomaly or Yes/No) representing typical performance for this type of task.
        
        ### Response Format:
        You MUST respond with a JSON object containing:
        {{
            "markdown_report": "Detailed markdown explanation including rationale and alternatives",
            "recommended_model": "Name of the model",
            "estimated_accuracy": 0.85,
            "alternatives": [
                {{"name": "Model A", "accuracy": 0.82}},
                {{"name": "Model B", "accuracy": 0.79}}
            ],
            "confusion_matrix": {{
                "labels": ["Positive", "Negative"],
                "values": [[45, 5], [8, 42]]
            }}
        }}
        """

        client = get_groq_client()
        if not client:
            return {"error": "LLM client not configured", "summary": summary}

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert Data Scientist. Respond ONLY with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=2500
        )

        try:
            # Robust JSON extraction
            content = completion.choices[0].message.content
            match = re.search(r'\{.*\}', content, re.DOTALL)
            data = json.loads(match.group(0)) if match else json.loads(content)
            
            return {
                "recommendation": data.get("markdown_report", ""),
                "metrics": {
                    "recommended_model": data.get("recommended_model", ""),
                    "accuracy": data.get("estimated_accuracy", 0),
                    "alternatives": data.get("alternatives", []),
                    "confusion_matrix": data.get("confusion_matrix", {})
                },
                "summary": summary
            }
        except Exception as json_err:
            # Fallback if JSON parsing fails
            return {
                "recommendation": completion.choices[0].message.content,
                "summary": summary,
                "metrics": None
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error suggesting model: {str(e)}")

import json
