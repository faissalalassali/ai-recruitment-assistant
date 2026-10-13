from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
import subprocess
import sys

app = FastAPI(title="AI Recruitment Screening API", version="1.0")

class JobRequest(BaseModel):
    job_description: str

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Recruitment Screening Assistant API"}

@app.post("/run-screening")
def run_screening():
    try:
        # استخدام مسار البايثون الخاص بالبيئة الوهمية الحالية لتجنب نقص المكتبات
        python_executable = sys.executable
        result = subprocess.run([python_executable, "pipeline.py"], capture_output=True, text=True, check=True)
        return {"status": "success", "message": "CV screening pipeline executed successfully."}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {e.stderr}")

@app.get("/candidates")
def get_candidates():
    results_file = "results.json"
    if not os.path.exists(results_file):
        return []
    with open(results_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data