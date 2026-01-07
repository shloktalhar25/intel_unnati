
import chromadb
import os

# Define the path exactly as the app does
base_path = r"c:\Users\vishw\OneDrive\Desktop\projFiles\projFiles\Class_5_rag\Codebase\science"

print(f"Checking database at: {base_path}")

if not os.path.exists(base_path):
    print("PATH DOES NOT EXIST!")
else:
    try:
        client = chromadb.PersistentClient(path=base_path)
        collections = client.list_collections()
        print(f"Found {len(collections)} collections:")
        for col in collections:
            print(f" - Name: '{col.name}', Count: {col.count()}")
            
            # peek 
            peek = col.peek()
            if peek['documents']:
                print(f"   Sample doc: {peek['documents'][0][:50]}...")
    except Exception as e:
        print(f"Error inspecting DB: {e}")
