from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from .database import Base

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    class_name = Column(String, index=True)
    subject_name = Column(String, index=True)
    question = Column(Text)
    answer = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
