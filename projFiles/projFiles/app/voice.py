import sounddevice as sd
import numpy as np
import whisper
import os

# Global model cache
model = None

def load_whisper_model():
    global model
    if model is None:
        print("[INFO] Loading Whisper model...")
        model = whisper.load_model("base")
        print("[SUCCESS] Whisper model loaded.")
    return model

def record_and_transcribe(seconds=5, fs=16000):
    """
    Records audio for specific seconds using sounddevice and transcribes using Whisper.
    """
    try:
        # Load model first (or ensure it's loaded)
        _model = load_whisper_model()
        
        print(f"[INFO] Recording for {seconds} seconds...")
        # Record audio
        audio = sd.rec(
            int(seconds * fs),
            samplerate=fs,
            channels=1,
            dtype='float32'
        )
        sd.wait()  # Wait until recording is finished
        
        # Flatten array
        audio = np.squeeze(audio)
        
        print("[INFO] Transcribing...")
        # Transcribe directly from numpy array
        # fp16=False is often safer for CPU usage if GPU isn't set up perfectly
        result = _model.transcribe(audio, fp16=False)
        
        text = result["text"].strip()
        print(f"[SUCCESS] Transcription: {text}")
        return text

    except Exception as e:
        print(f"[ERROR] Error in voice processing: {e}")
        return f"Error: {str(e)}"
