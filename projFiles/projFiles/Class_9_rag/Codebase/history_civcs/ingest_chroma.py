# ingest_chroma.py
import os
import pdfplumber
from tqdm import tqdm
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient

# ---------------- CONFIG ----------------
PDF_FOLDER = r"C:\Users\shlok\Desktop\intel unnati\projFiles\Books\CIVICS\iess4dd"
PERSIST_DIR = r"C:\Users\shlok\Desktop\intel unnati\projFiles\Codebase2\chroma_db"
COLLECTION_NAME = "civics_books"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
# ----------------------------------------

def extract_texts(folder):
    docs = []
    for fname in sorted(os.listdir(folder)):
        if fname.lower().endswith(".pdf"):
            path = os.path.join(folder, fname)
            text = ""
            with pdfplumber.open(path) as pdf:
                for p in pdf.pages:
                    t = p.extract_text()
                    if t:
                        text += t + "\n"
            docs.append({"source": fname, "text": text})
            print(f"✅ Extracted: {fname}")
    return docs

def make_chunks(docs, chunk_size=1000, overlap=200):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
    out = []
    for doc in docs:
        chunks = splitter.split_text(doc["text"])
        for i, c in enumerate(chunks):
            out.append({
                "id": f"{doc['source']}_{i}",
                "text": c,
                "metadata": {"source": doc["source"], "chunk_index": i}
            })
    return out

def embed_texts(texts, model_name=EMBED_MODEL_NAME):
    model = SentenceTransformer(model_name)
    vectors = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    return vectors

def main():
    print("🚀 Starting Chroma Ingestion Pipeline...\n")

    docs = extract_texts(PDF_FOLDER)
    chunks = make_chunks(docs)
    texts = [c["text"] for c in chunks]
    ids = [c["id"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    print(f"\n📘 Total chunks: {len(texts)}")

    vectors = embed_texts(texts)

    # ✅ NEW Chroma client
    client = PersistentClient(path=PERSIST_DIR)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    print("\n📥 Inserting data into Chroma...")
    collection.add(
        documents=texts,
        embeddings=vectors.tolist(),
        ids=ids,
        metadatas=metadatas
    )

    print(f"\n✅ Successfully ingested {len(texts)} chunks into collection '{COLLECTION_NAME}'.")
    print(f"📁 Stored persistently at: {PERSIST_DIR}")

if __name__ == "__main__":
    main()
