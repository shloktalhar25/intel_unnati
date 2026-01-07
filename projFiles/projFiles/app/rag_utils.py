import os
import re
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from groq import Groq

# Configuration
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
GROQ_MODEL = "llama-3.1-8b-instant"
TOP_K = 4




API_KEY = os.getenv("GROQ_API_KEY")
groq_client = Groq(api_key=API_KEY)

embedder = SentenceTransformer(EMBED_MODEL_NAME)

def clean_text(text):
    text = re.sub(r"(.)\1{2,}", r"\1\1", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def get_collection_path(selected_class, subject):
    # Robust path resolution relative to this file
    # This file is in .../app/
    # We need .../Class_X_rag/
    current_dir = os.path.dirname(os.path.abspath(__file__)) # .../app
    project_root = os.path.dirname(current_dir)              # .../projFiles
    
    base_dir = os.path.join(project_root, selected_class, "Codebase", subject)
    collection_name = f"{subject}_books"
    return base_dir, collection_name

def retrieve_answer(selected_class, subject, question):
    persist_dir, collection_name = get_collection_path(selected_class, subject)
    
    print(f"DEBUG: Checking database at: {persist_dir}")
    if not os.path.exists(persist_dir):
        print(f"DEBUG: Directory not found: {persist_dir}")
        return f"I cannot find the database for {selected_class} {subject}."

    client = PersistentClient(path=persist_dir)
    
    # Auto-detect collection name if default fails
    try:
        collections = client.list_collections()
        col_names = [c.name for c in collections]
        print(f"DEBUG: Available collections in DB: {col_names}")
        
        if collection_name not in col_names:
            if col_names:
                # Heuristic: Prefer a collection that contains the subject name
                # otherwise default to the first one found.
                best_match = next((n for n in col_names if subject in n), col_names[0])
                print(f"DEBUG: Collection '{collection_name}' not found. Switching to '{best_match}'.")
                collection_name = best_match
            else:
                print("DEBUG: No collections found in database.")
                return f"The database for {selected_class} {subject} appears to be empty."
    except Exception as e:
        print(f"DEBUG: Error ensuring collection: {e}")

    # Access the collection
    collection = client.get_or_create_collection(name=collection_name)

    query_vec = embedder.encode([question], convert_to_numpy=True)[0]
    results = collection.query(
        query_embeddings=[query_vec.tolist()],
        n_results=TOP_K,
        include=["documents", "metadatas"]
    )
    
    if results["documents"] and results["documents"][0]:
        docs = [
            {"text": clean_text(doc), "meta": meta}
            for doc, meta in zip(results["documents"][0], results["metadatas"][0])
        ]
        context = "\n\n".join([d["text"] for d in docs])
        print(f"DEBUG: Retrieved {len(docs)} documents for query: '{question}'")
    else:
        context = "No specific content found in the selected textbook."
        print(f"DEBUG: No documents found for query: '{question}'")
    
    # Extract just the class number if possible (e.g. Class_10_rag -> 10)
    class_num = selected_class
    if "_" in selected_class:
        parts = selected_class.split("_")
        # Try to find the number part
        for p in parts:
            if p.isdigit():
                class_num = p
                break

    prompt = f"""
You are a helpful AI tutor for a Grade {class_num} student.
Your task is to answer the student's question using the provided textbook content as your primary source.

PROVIDED TEXTBOOK CONTENT:
{context}

USER QUESTION: {question}

INSTRUCTIONS:
1. FIRST, check the PROVIDED TEXTBOOK CONTENT for the answer.
2. If the answer is found in the text, explain it simply and clearly for a Grade {class_num} student.
3. If the answer is partially found, use your general knowledge to fill in the gaps, but mention that you are adding extra information.
4. If the answer is NOT in the PROVIDED TEXT at all, you MAY use your general knowledge to answer the question, but please mention that this information is not from their current textbook.
5. Be encouraging and helpful.
6. Keep answers concise and age-appropriate.

Answer:
"""
    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,  # Lower temperature for more deterministic/strict behavior
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating answer: {str(e)}"
