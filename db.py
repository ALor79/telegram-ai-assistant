from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    username = Column(String)
    language = Column(String, default="en")
    verified = Column(Boolean, default=False)
    history = Column(Text, default="[]")  # Stored as JSON string

engine = create_engine("sqlite:///bot_data.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Utilities
def get_user(session, user_id):
    user = session.query(User).filter_by(user_id=user_id).first()
    if not user:
        user = User(user_id=user_id)
        session.add(user)
        session.commit()
    return user

def update_history(session, user_id, message_obj):
    user = get_user(session, user_id)
    history = json.loads(user.history)
    history.append(message_obj)
    history = history[-20:]  # trim to last 20
    user.history = json.dumps(history)
    session.commit()
    return history

def reset_history(session, user_id):
    user = get_user(session, user_id)
    user.history = "[]"
    session.commit()
