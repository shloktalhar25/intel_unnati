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



### About the File structuring

1. projFile contains all the neccessary codes and resources.
2. Class_9_rag folder contains the past conversation history.
3. The Folder structure might be confusing due to similarity in names.
