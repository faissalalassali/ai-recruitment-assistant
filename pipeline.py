import os
import json
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader

load_dotenv()

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text

def run_screening_pipeline():
    cv_dir = "downloaded_cvs"
    output_results_file = "results.json"
    
    if not os.path.exists(cv_dir):
        print(f"Error: Directory '{cv_dir}' not found. Please sync emails first.")
        return

    # 1. Read Job Description
    job_desc_path = "job_description.txt"
    if not os.path.exists(job_desc_path):
        print("Error: 'job_description.txt' not found.")
        return
        
    with open(job_desc_path, "r", encoding="utf-8") as f:
        job_desc = f.read()

    # 2. Initialize ChromaDB and Model
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(name="cv_collection")
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    pdf_files = [f for f in os.listdir(cv_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("No PDF CVs found to process.")
        return

    candidates_results = []

    print(f"Processing {len(pdf_files)} CVs...")

    for filename in pdf_files:
        file_path = os.path.join(cv_dir, filename)
        cv_text = extract_text_from_pdf(file_path)
        
        if not cv_text.strip():
            continue

        # Add or get from ChromaDB
        embedding = model.encode(cv_text).tolist()
        
        # AI Evaluation using OpenRouter
        api_key = os.getenv("OPENROUTER_API_KEY")
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        
        client_openai = OpenAI(api_key=api_key, base_url=base_url)
        
        prompt = f"""
You are an expert AI HR Recruiter. Evaluate the following Candidate CV against the provided Job Description.

Job Description:
{job_desc}

Candidate CV:
{cv_text}

Provide a valid JSON response with the following keys:
1. "match_score" (integer out of 100)
2. "key_strengths" (list of strings representing matching skills)
3. "missing_skills" (list of strings representing gaps, if any)
4. "recommendation" (short summary hiring decision string)
"""

        try:
            response = client_openai.chat.completions.create(
                model="openai/gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a precise HR AI assistant that outputs only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            ai_data = json.loads(response.choices[0].message.content)
        except Exception as e:
            ai_data = {
                "match_score": 0,
                "key_strengths": [],
                "missing_skills": [str(e)],
                "recommendation": "Error during AI evaluation"
            }

        candidates_results.append({
            "filename": filename,
            "evaluation": ai_data
        })

    # 3. Filter and Rank Candidates by Match Score (Step 11)
    candidates_results.sort(key=lambda x: x['evaluation'].get('match_score', 0), reverse=True)

    # 4. Save Results (Step 12)
    with open(output_results_file, "w", encoding="utf-8") as f:
        json.dump(candidates_results, f, ensure_ascii=False, indent=4)

    print(f"Pipeline completed successfully! Results saved to {output_results_file}")

if __name__ == "__main__":
    run_screening_pipeline()