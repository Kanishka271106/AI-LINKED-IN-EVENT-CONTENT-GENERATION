from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./linkedin_event_curator.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Event(Base):
    """Represents an event/upload session"""
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="Untitled Event")
    created_at = Column(DateTime, default=datetime.utcnow)
    user_email = Column(String, nullable=True)
    total_uploaded = Column(Integer, default=0)
    total_selected = Column(Integer, default=0)
    
    images = relationship("Image", back_populates="event")
    posts = relationship("Post", back_populates="event")


class Image(Base):
    """Represents an uploaded/processed image"""
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    filename = Column(String)
    filepath = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Quality metrics
    quality_score = Column(Float, default=0.0)
    sharpness_score = Column(Float, default=0.0)
    brightness_score = Column(Float, default=0.0)
    contrast_score = Column(Float, default=0.0)
    is_blur = Column(Boolean, default=False)
    is_duplicate = Column(Boolean, default=False)
    
    # Selection status
    is_selected = Column(Boolean, default=False)
    is_posted = Column(Boolean, default=False)
    
    event = relationship("Event", back_populates="images")


class Post(Base):
    """Audit log for LinkedIn posts"""
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    posted_at = Column(DateTime, default=datetime.utcnow)
    linkedin_post_id = Column(String, nullable=True)
    num_images = Column(Integer, default=0)
    status = Column(String, default="pending")  # pending, success, failed
    error_message = Column(String, nullable=True)
    
    event = relationship("Event", back_populates="posts")


class LinkedInToken(Base):
    """Stores LinkedIn OAuth tokens"""
    __tablename__ = "linkedin_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, unique=True)
    access_token = Column(String)
    refresh_token = Column(String, nullable=True)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserPreference(Base):
    """Stores user's AI caption preferences"""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, unique=True, nullable=True)
    tone = Column(String, default="Professional")  # Professional, Enthusiastic, Storytelling, Humorous
    length = Column(String, default="Medium")       # Short, Medium, Long
    audience = Column(String, default="All Professionals") # New: Industry Professionals, Recruiters, Coworkers
    cta_type = Column(String, default="None")       # New: Engagement, Direct Connection, Profile Visit
    focus = Column(String, default="General")      # New: Event Atmosphere, Learning, Networking
    include_hashtags = Column(Boolean, default=True)
    custom_hashtags = Column(String, nullable=True) # Custom tags to always include
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
