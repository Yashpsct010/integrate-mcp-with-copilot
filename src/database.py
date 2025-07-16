"""
Database configuration and models for the High School Management System
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./school_activities.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Activity(Base):
    """Activity model for storing extracurricular activities"""
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=False)
    schedule = Column(String, nullable=False)
    max_participants = Column(Integer, nullable=False)
    location = Column(String, nullable=True)
    duration = Column(String, nullable=True)
    organizer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    organizer = relationship("User", back_populates="organized_activities")
    registrations = relationship("Registration", back_populates="activity")


class User(Base):
    """User model for storing student and admin information"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, default="student")  # student or admin
    password_hash = Column(String, nullable=True)  # For future authentication
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    organized_activities = relationship("Activity", back_populates="organizer")
    registrations = relationship("Registration", back_populates="user")


class Registration(Base):
    """Registration model for tracking student-activity relationships"""
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    registration_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="registered")  # registered, waitlisted, cancelled

    # Relationships
    user = relationship("User", back_populates="registrations")
    activity = relationship("Activity", back_populates="registrations")


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
