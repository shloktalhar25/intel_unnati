## 📌 Project Availability Note

The complete project package is approximately **1.3 GB in size**, which exceeds GitHub’s recommended repository limits for standard uploads.  
For this reason, the **full runnable version of the project is hosted externally** and is available through the links below:


- **Alternate repository using github lfs** — https://github.com/Vishwesh2110/projFiles
-  **OneDrive** — (original structure) https://1drv.ms/f/c/56e76aa22cb64c2c/IgDO9bOEfJoMQ7P5c4YBIG54AVMRFf4kMBcmJNTTJO_RNJ0?e=k26fWZ 
-  **Google Drive** — Zipped archive of the complete project : https://drive.google.com/file/d/1FlcV-nYwqbtcZ2oDmN7QST_evw4RH7p-/view
-  **Demo** — https://1drv.ms/f/c/56e76aa22cb64c2c/IgBONfOLSNKyT656xSdZz6tJAYhPB0nYQaahCTijE0E331M?e=lJIg2T 
```
If facing any issues accessing the files , connect with us : work.shloktalhar25@gmail.com
```

> The GitHub repository contains selected files for reference, documentation, and architectural overview.

---

## 📚 NCERT Class 5–10 RAG Learning Assistant

This project is an **AI-powered Retrieval-Augmented Generation (RAG) system** designed specifically for **NCERT students from Class 5 to Class 10**.  
It assists students with **book-related questions and conceptual learning**, ensuring that responses are **class-appropriate and syllabus-aligned**.

---

##  Design Motivation

A common issue with educational RAG systems is the use of a **single vector database for all grades**, which can result in concept explanations that are **academically misaligned** with the student’s class level.

For example, a **Class 5 student** asking about *photosynthesis* may receive a **Class 9–level explanation** if all textbooks are embedded together.

---

##  Architectural Approach

To address this, the system uses:

- **Separate vector databases for each class (5–10)**
- **Subject-wise isolation within each class**

This design ensures:
- Accurate retrieval
- Grade-appropriate explanations
- Reduced conceptual leakage
- Improved learning experience

---

##  Tech Stack

**Frontend:** HTML | CSS | JavaScript  
**Backend:** Python  
**LLM & AI:** Groq API | Meta LLaMA 3.1 (8B Instant)  
**Vector Database:** ChromaDB

---

##  Repository Scope

Due to the project’s size and inclusion of large assets such as:
- NCERT PDFs
- Precomputed embeddings
- Multiple ChromaDB stores

only a **partial representation** of the project is maintained on GitHub.  
This repository should be used primarily for **understanding the system design and implementation approach**.

---

##  System Workflow (Step-by-Step)

1. Collect NCERT textbooks (PDFs) for Class 5–10  
2. Separate content by **Class and Subject**
3. Extract text from PDFs
4. Chunk the text into smaller segments
5. Generate embeddings for each chunk
6. Store embeddings in **separate ChromaDB collections**
7. User selects:
   - Class
   - Subject
8. Query is routed to the **correct vector database**
9. Relevant context is retrieved
10. LLM generates a **class-appropriate answer**

---

This approach allows the project to remain **accessible, transparent, and reproducible**, while respecting platform constraints.


---

## ▶️ How to Run the Project

To run the project locally, follow the steps below.

### Step 1: Set up the Groq API Key  
This project requires a **Groq API key** for LLM inference. Generate an API key from the Groq dashboard and set it as an environment variable.

```
GROQ_API_KEY="your_groq_api_key_here"
```

### Step 2: Install Dependencies
Ensure Python 3.10 or 3.11 is installed, then only the file would run, python 3.14 might give errors:
```
pip install fastapi uvicorn sqlalchemy jinja2 python-multipart chromadb sentence-transformers groq sounddevice numpy openai-whisper
```

### Step 3: Run the Application
Start the FastAPI server using:
```
python -m uvicorn app.main:app --reload
```

Step 4: Access the Application
Once the server starts, open your browser and go to:
```
http://127.0.0.1:8000
```
---
### About the File structuring

1. projFile contains all the neccessary codes and resources.
2. Class_9_rag folder contains the past conversation history.
3. The Folder structure might be confusing due to similarity in names.
---
