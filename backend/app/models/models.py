import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="user", nullable=False)
    plan = Column(String(50), default="free", nullable=False)  # free, creator, pro
    credits_balance = Column(Integer, default=10, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    projects = relationship("MusicProject", back_populates="owner", cascade="all, delete-orphan")
    generation_jobs = relationship("GenerationJob", back_populates="user", cascade="all, delete-orphan")
    usage_records = relationship("UsageRecord", back_populates="user", cascade="all, delete-orphan")

class MusicProject(Base):
    __tablename__ = "music_projects"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    prompt = Column(Text, nullable=True)
    genre = Column(String(100), default="classical", nullable=False)
    mood = Column(String(100), default="calm", nullable=False)
    tempo = Column(Integer, default=120, nullable=False)
    instrument = Column(String(100), default="piano", nullable=False)
    duration_seconds = Column(Integer, default=30, nullable=False)
    is_favorite = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    owner = relationship("User", back_populates="projects")
    generation_jobs = relationship("GenerationJob", back_populates="project", cascade="all, delete-orphan")
    assets = relationship("GeneratedAsset", back_populates="project", cascade="all, delete-orphan")

class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("music_projects.id", ondelete="CASCADE"), nullable=True, index=True)
    status = Column(String(50), default="queued", nullable=False)  # queued, processing, generating, rendering, completed, failed
    progress = Column(Integer, default=0, nullable=False)  # 0 to 100%
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="generation_jobs")
    project = relationship("MusicProject", back_populates="generation_jobs")
    assets = relationship("GeneratedAsset", back_populates="generation_job", cascade="all, delete-orphan")

class GeneratedAsset(Base):
    __tablename__ = "generated_assets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    generation_job_id = Column(String(36), ForeignKey("generation_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(String(36), ForeignKey("music_projects.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_type = Column(String(50), nullable=False)  # midi, audio_wav
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, default=0, nullable=False)
    mime_type = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    generation_job = relationship("GenerationJob", back_populates="assets")
    project = relationship("MusicProject", back_populates="assets")

class UsageRecord(Base):
    __tablename__ = "usage_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    credits_spent = Column(Integer, nullable=False)
    action = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="usage_records")
