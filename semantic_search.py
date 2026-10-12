import chromadb
from sentence_transformers import SentenceTransformer

def search_cvs(query_text, n_results=1):
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_collection(name="cv_collection")
    
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    
    query_embedding = model.encode(query_text).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    print(f"\nSearch Query: '{query_text}'\n" + "="*40)
    for i, filename in enumerate(results['ids'][0]):
        print(f"{i+1}. File: {filename}")
        print(f"Snippet: {results['documents'][0][i][:200]}...\n")

if __name__ == "__main__":
    search_cvs("Artificial Intelligence and Machine Learning Engineer with Python experience")