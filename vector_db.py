import os
import chromadb
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader

def init_vector_db():
    client = chromadb.PersistentClient(path="./chroma_db")
    embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    collection = client.get_or_create_collection(name="cv_collection")
    return collection, embedding_model

def index_cvs():
    collection, model = init_vector_db()
    cv_dir = "downloaded_cvs"
    
    if not os.path.exists(cv_dir):
        print("Directory 'downloaded_cvs' not found.")
        return

    # Filter files to only index CVs and ignore invoices or unwanted documents
    files = [f for f in os.listdir(cv_dir) if f.endswith('.pdf') and 'invoice' not in f.lower()]
    if not files:
        print("No valid CVs found to index.")
        return

    for filename in files:
        file_path = os.path.join(cv_dir, filename)
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        
        text = text.strip()
        if not text:
            continue

        embedding = model.encode(text).tolist()

        collection.upsert(
            ids=[filename],
            embeddings=[embedding],
            documents=[text],
            metadatas=[{"filename": filename}]
        )
        print(f"Indexed CV successfully: {filename}")

if __name__ == "__main__":
    index_cvs()