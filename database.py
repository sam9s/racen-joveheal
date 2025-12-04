"""
Database Models and Connection for JoveHeal Chatbot

PostgreSQL database for:
- Conversation logs with analytics
- User feedback on responses
- Session tracking
"""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from contextlib import contextmanager

DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    engine = None
    SessionLocal = None

Base = declarative_base()


class UserAccount(Base):
    """Stores user accounts across different channels."""
    __tablename__ = "user_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    channel = Column(String(50), nullable=False, index=True)
    external_id = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=True, index=True)
    display_name = Column(String(255), nullable=True)
    profile_image = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    sessions = relationship("ChatSession", back_populates="user")
    
    __table_args__ = (
        UniqueConstraint('channel', 'external_id', name='uq_channel_external_id'),
    )


class ChatSession(Base):
    """Tracks individual chat sessions."""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("user_accounts.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    channel = Column(String(50), default="web")
    
    user = relationship("UserAccount", back_populates="sessions")
    conversations = relationship("Conversation", back_populates="session")


class Conversation(Base):
    """Stores individual conversation exchanges."""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("chat_sessions.session_id"), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user_question = Column(Text, nullable=False)
    bot_answer = Column(Text, nullable=False)
    safety_flagged = Column(Boolean, default=False, index=True)
    safety_category = Column(String(100), nullable=True)
    sources_used = Column(Text, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    
    session = relationship("ChatSession", back_populates="conversations")
    feedback = relationship("ResponseFeedback", back_populates="conversation", uselist=False)


class ResponseFeedback(Base):
    """Stores user feedback on bot responses."""
    __tablename__ = "response_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), unique=True)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("Conversation", back_populates="feedback")


class AnalyticsDaily(Base):
    """Pre-aggregated daily analytics for performance."""
    __tablename__ = "analytics_daily"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, unique=True, index=True)
    total_conversations = Column(Integer, default=0)
    unique_sessions = Column(Integer, default=0)
    safety_flags = Column(Integer, default=0)
    avg_response_time_ms = Column(Float, nullable=True)
    positive_feedback = Column(Integer, default=0)
    negative_feedback = Column(Integer, default=0)


def init_database():
    """Initialize database tables."""
    if engine:
        Base.metadata.create_all(bind=engine)
        return True
    return False


@contextmanager
def get_db_session():
    """Get a database session with automatic cleanup."""
    if SessionLocal is None:
        yield None
        return
    
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def is_database_available():
    """Check if database connection is available."""
    return engine is not None and DATABASE_URL is not None


def get_or_create_user(channel: str, external_id: str, email: str = None, 
                       display_name: str = None, profile_image: str = None):
    """
    Get existing user or create new one.
    Returns (user_data, created) tuple where user_data is a dict with id, display_name, etc.
    """
    with get_db_session() as db:
        if db is None:
            return None, False
        
        user = db.query(UserAccount).filter(
            UserAccount.channel == channel,
            UserAccount.external_id == external_id
        ).first()
        
        if user:
            user.last_seen = datetime.utcnow()
            if email and not user.email:
                user.email = email
            if display_name and not user.display_name:
                user.display_name = display_name
            if profile_image:
                user.profile_image = profile_image
            db.commit()
            user_data = {
                'id': user.id,
                'display_name': user.display_name,
                'email': user.email
            }
            return user_data, False
        
        user = UserAccount(
            channel=channel,
            external_id=external_id,
            email=email,
            display_name=display_name,
            profile_image=profile_image
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        user_data = {
            'id': user.id,
            'display_name': user.display_name,
            'email': user.email
        }
        return user_data, True


def get_user_by_email(email: str):
    """Get user by email address."""
    with get_db_session() as db:
        if db is None:
            return None
        return db.query(UserAccount).filter(UserAccount.email == email).first()


def get_user_conversation_history(user_id: int, limit: int = 20):
    """Get recent conversation history for a user."""
    with get_db_session() as db:
        if db is None:
            return []
        
        conversations = db.query(Conversation).join(ChatSession).filter(
            ChatSession.user_id == user_id
        ).order_by(Conversation.timestamp.desc()).limit(limit).all()
        
        return [
            {
                'question': c.user_question,
                'answer': c.bot_answer,
                'timestamp': c.timestamp.isoformat() if c.timestamp else None
            }
            for c in reversed(conversations)
        ]
