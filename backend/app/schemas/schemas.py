from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserRegister(UserBase):
    password: str = Field(..., min_length=6, description="Minimum 6 characters")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: str
    role: str
    plan: str
    credits_balance: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    user_id: Optional[str] = None

# Asset Schemas
class GeneratedAssetResponse(BaseModel):
    id: str
    asset_type: str
    file_size_bytes: int
    mime_type: str
    download_url: str
    created_at: datetime

    class Config:
        from_attributes = True

# Generation Job Schemas
class GenerationCreate(BaseModel):
    prompt: Optional[str] = Field(None, max_length=500, description="Natural language description of desired music")
    genre: str = Field("classical", description="Genre: classical, lo-fi, ambient, electronic, cinematic, jazz")
    mood: str = Field("calm", description="Mood: calm, happy, sad, energetic, mysterious, inspirational")
    tempo: int = Field(120, ge=40, le=240, description="Tempo BPM between 40 and 240")
    instrument: str = Field("piano", description="Primary instrument: piano, strings, synth, guitar, lo-fi")
    duration_seconds: int = Field(30, ge=10, le=120, description="Duration in seconds (10 - 120)")
    project_id: Optional[str] = None
    temperature: float = Field(1.0, ge=0.2, le=2.0, description="Creativity temperature")

class GenerationJobResponse(BaseModel):
    id: str
    project_id: Optional[str]
    status: str
    progress: int
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    assets: List[GeneratedAssetResponse] = []

    class Config:
        from_attributes = True

# Project Schemas
class MusicProjectCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    prompt: Optional[str] = None
    genre: str = "classical"
    mood: str = "calm"
    tempo: int = 120
    instrument: str = "piano"
    duration_seconds: int = 30

class MusicProjectUpdate(BaseModel):
    title: Optional[str] = None
    is_favorite: Optional[bool] = None

class MusicProjectResponse(BaseModel):
    id: str
    user_id: str
    title: str
    prompt: Optional[str]
    genre: str
    mood: str
    tempo: int
    instrument: str
    duration_seconds: int
    is_favorite: bool
    created_at: datetime
    updated_at: datetime
    latest_job: Optional[GenerationJobResponse] = None
    assets: List[GeneratedAssetResponse] = []

    class Config:
        from_attributes = True

# Billing Schemas
class PlanFeature(BaseModel):
    name: str
    included: bool

class PlanDetail(BaseModel):
    id: str
    name: str
    tagline: str
    price_usd: float
    price_inr: float
    billing_period: str
    credits_per_month: int
    features: List[str]
    recommended: bool = False

class CheckoutRequest(BaseModel):
    plan_id: str
    provider: str = Field("razorpay", description="Payment provider: razorpay or stripe")

class CheckoutResponse(BaseModel):
    order_id: str
    amount: float
    currency: str
    provider: str
    key_id: str
    notes: dict

# Usage Record Schemas
class UsageResponse(BaseModel):
    credits_balance: int
    plan: str
    total_generations: int
    history: List[dict]
