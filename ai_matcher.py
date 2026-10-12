import os
import json
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def get_job_description(file_path="job_description.txt"):
    if not os.path.exists(file_path):
        return "Artificial Intelligence and Machine Learning Engineer position requiring Python, ChromaDB, and LLM experience."
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()

def match_cv_with_job():
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_collection(name="cv_collection")
    
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    job_desc = get_job_description()
    
    query_embedding = model.encode(job_desc).tolist()
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=1
    )
    
    if not results['ids'] or not results['ids'][0]:
        print("No CV found in the database.")
        return

    matched_cv_filename = results['ids'][0][0]
    matched_cv_text = results['documents'][0][0]

    print(f"\nMatching Job Description with Best CV: {matched_cv_filename}\n" + "="*50)
    
    prompt = f"""
You are an expert AI HR Recruiter. Evaluate the following Candidate CV against the provided Job Description.

Job Description:
{job_desc}

Candidate CV:
{matched_cv_text}

Provide a valid JSON response with the following keys:
1. "match_score" (integer out of 100)
2. "key_strengths" (list of strings representing matching skills)
3. "missing_skills" (list of strings representing gaps, if any)
4. "recommendation" (short summary hiring decision string)
"""

    api_key = os.getenv("OPENROUTER_API_KEY")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    
    # Direct reliable model name on OpenRouter
    model_name = "openai/gpt-4o-mini"

    if not api_key:
        print("Error: OPENROUTER_API_KEY not found in environment variables.")
        return

    client_openai = OpenAI(api_key=api_key, base_url=base_url)
    
    try:
        response = client_openai.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a precise HR AI assistant that outputs only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        result_content = response.choices[0].message.content
        parsed_json = json.loads(result_content)
        
        print("\n--- AI Evaluation Result ---")
        print(json.dumps(parsed_json, indent=4, ensure_ascii=False))
        print("="*50)
        
    except Exception as e:
        print(f"An error occurred while calling the AI model: {e}")

if __name__ == "__main__":
    match_cv_with_job()