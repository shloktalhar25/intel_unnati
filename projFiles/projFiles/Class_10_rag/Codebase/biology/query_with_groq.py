# query_with_groq.py
import os
from dotenv import load_dotenv
load_dotenv()
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from groq import Groq
import textwrap



# ---------------- CONFIG ----------------
PERSIST_DIR = r"C:\Users\shlok\Desktop\intel unnati\projFiles\Class_10_rag\Codebase\biology" # modified this
COLLECTION_NAME = "biology_books" # this as well
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 4
GROQ_MODEL = "llama-3.1-8b-instant"   # free-tier model (change if needed)
# ----------------------------------------

# Initialize Groq client
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("⚠️ Please set your GROQ_API_KEY environment variable first.")

groq_client = Groq(api_key=groq_api_key)

# Initialize embedding model
embedder = SentenceTransformer(EMBED_MODEL_NAME)

# Initialize Chroma
client = PersistentClient(path=PERSIST_DIR)
collection = client.get_or_create_collection(name=COLLECTION_NAME)

def retrieve(query, top_k=TOP_K):
    query_vec = embedder.encode([query], convert_to_numpy=True)[0]
    results = collection.query(
        query_embeddings=[query_vec.tolist()],
        n_results=top_k,
        include=["documents", "metadatas"]
    )

    hits = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        hits.append({"text": clean_text(doc), "meta": meta})
    return hits



import re

def clean_text(text):
    """Basic OCR noise cleanup: collapse repeated letters and normalize spaces."""
    text = re.sub(r"(.)\1{2,}", r"\1\1", text)       # trim long repeats
    text = re.sub(r"\s+", " ", text)                 # normalize whitespace
    text = text.replace(" EEEE", " Election")        # quick patch for recurring OCR noise
    return text.strip()


def build_prompt(question, docs):
    context = "\n\n".join(
        [f"Source: {d['meta']['source']}\n{d['text']}" for d in docs]
    )
    prompt = f"""
You are a biology subject expert. Use the context below to answer the question factually and directly.
If the answer is clearly suggested or implied, explain it concisely.
Only if it truly cannot be inferred at all, reply: "Not found in provided texts."

Context:
{context}

Question: {question}

Answer in 2-3 crisp sentences, suitable for a Class 10 biology answer.
"""
    return prompt.strip()


def generate_answer(prompt):
    """Send the prompt to Groq and return the model-generated answer."""
    completion = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=400,
    )
    # ✅ Fixed: Access message content properly
    return completion.choices[0].message.content


def main():
    print("🧠 Biology Q&A Chat (Chroma + Groq)")
    print("Type your question or 'exit' to quit.\n")

    while True:
        question = input("❓ Ask: ").strip()
        if question.lower() in {"exit", "quit"}:
            print("👋 Goodbye!")
            break

        hits = retrieve(question)
        if not hits:
            print("No relevant context found.\n")
            continue

        prompt = build_prompt(question, hits)
        print("\n🔎 Retrieved context snippets...")
        print(textwrap.shorten(prompt, width=800, placeholder="..."))
        print("\n🤖 Generating answer...\n")

        answer = generate_answer(prompt)
        print("💬", answer, "\n")

if __name__ == "__main__":
    main()
