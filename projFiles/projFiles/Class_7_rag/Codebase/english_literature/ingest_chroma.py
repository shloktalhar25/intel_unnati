# ingest_chroma.py
import os
import pdfplumber
from tqdm import tqdm
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient

# ---------------- CONFIG ----------------
PDF_FOLDER = r"C:\Users\shlok\Desktop\intel unnati\projFiles\Class_7_rag\Books\english_literature_book" # modifying and changing the locations
PERSIST_DIR = r"C:\Users\shlok\Desktop\intel unnati\projFiles\Class_7_rag\Codebase\english_literature" # this as well

COLLECTION_NAME = "english_books"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
# ----------------------------------------

def extract_texts(folder):
    import pandas as pd  # for summary table (optional)
    docs = []
    summary = []

    print(f"📂 Scanning folder: {folder}\n")

    for fname in sorted(os.listdir(folder)):
        if fname.lower().endswith(".pdf"):
            path = os.path.join(folder, fname)
            try:
                with pdfplumber.open(path) as pdf:
                    num_pages = len(pdf.pages)
                    print(f"🔍 Reading {fname} ({num_pages} pages)...")
                    text = ""
                    skipped = 0

                    for i, p in enumerate(tqdm(pdf.pages, desc=f"   Extracting {fname}", unit="page")):
                        try:
                            t = p.extract_text()
                            if not t:
                                t = f"[Page {i+1} - No extractable text]"
                                skipped += 1
                            text += t + "\n"
                        except Exception as e:
                            skipped += 1
                            print(f"⚠️ Skipping page {i+1}/{num_pages} of {fname}: {e}")
                            continue

                    word_count = len(text.split())
                    docs.append({"source": fname, "text": text})
                    summary.append({
                        "File": fname,
                        "Pages": num_pages,
                        "Skipped": skipped,
                        "Extracted_Words": word_count
                    })
                    print(f"✅ Done: {fname} — {word_count} words extracted, {skipped} page(s) skipped.\n")

            except Exception as e:
                print(f"❌ Failed to read {fname}: {e}")

    if not docs:
        print("⚠️ No PDFs found or extracted from the folder.")
    else:
        print(f"📘 Successfully extracted {len(docs)} PDF(s).\n")

        # Display summary neatly
        df = pd.DataFrame(summary)
        print("📊 Extraction Summary:\n", df.to_string(index=False))

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
