import os
from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .rag_utils import retrieve_answer
from . import models, database

app = FastAPI()

# Create database tables
models.Base.metadata.create_all(bind=database.engine)

# Robust path handling
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Directory containing main.py (.../app)
PROJECT_ROOT = os.path.dirname(BASE_DIR)            # Parent directory (.../projFiles)

# Mount static and templates using absolute paths
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


# Utility functions
def get_available_classes():
    # Use PROJECT_ROOT to find class folders definitely
    return sorted([
        d for d in os.listdir(PROJECT_ROOT) 
        if d.startswith("Class_") and os.path.isdir(os.path.join(PROJECT_ROOT, d))
    ])


def get_subjects(selected_class):
    codebase_path = os.path.join(PROJECT_ROOT, selected_class, "Codebase")
    if os.path.exists(codebase_path):
        return sorted(os.listdir(codebase_path))
    return []


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    classes = get_available_classes()
    return templates.TemplateResponse("index.html", {"request": request, "classes": classes})


@app.post("/ask")
async def ask_question(
    selected_class: str = Form(...),
    subject: str = Form(...),
    question: str = Form(...),
    db: Session = Depends(database.get_db)
):
    try:
        # Note: rag_utils.retrieve_answer might rely on CWD. 
        # If necessary, we can adjust it to use PROJECT_ROOT as well, 
        # but usually uvicorn is run from PROJECT_ROOT.
        answer = retrieve_answer(selected_class, subject, question)
        
        # Save interaction to database
        chat_entry = models.ChatHistory(
            class_name=selected_class,
            subject_name=subject,
            question=question,
            answer=answer
        )
        db.add(chat_entry)
        db.commit()
        db.refresh(chat_entry)
        
        return JSONResponse({"answer": answer})
    except Exception as e:
        return JSONResponse({"answer": f"⚠️ Error: {str(e)}"})

@app.get("/history")
def get_history(db: Session = Depends(database.get_db)):
    history = db.query(models.ChatHistory).order_by(models.ChatHistory.timestamp.desc()).all()
    return [{"id": h.id, "class": h.class_name, "subject": h.subject_name, "question": h.question, "answer": h.answer, "timestamp": h.timestamp.isoformat()} for h in history]



from .voice import record_and_transcribe

@app.post("/listen")
async def listen_for_voice():
    """
    Triggers microphone recording on the server side and returns transcription.
    """
    try:
        # Record for 5 seconds as per user request
        text = record_and_transcribe(seconds=5)
        return JSONResponse({"text": text})
    except Exception as e:
        return JSONResponse({"text": "", "error": str(e)})
