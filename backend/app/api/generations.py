from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from app.core.database import get_db, SessionLocal
from app.models.models import User, MusicProject, GenerationJob, GeneratedAsset
from app.schemas.schemas import GenerationCreate, GenerationJobResponse, GeneratedAssetResponse
from app.api.auth import get_current_user
from app.services.job_worker import process_generation_job

router = APIRouter(prefix="/generations", tags=["Music Generation"])

def run_worker_in_background(
    job_id: str,
    genre: str,
    mood: str,
    tempo: int,
    instrument: str,
    duration_seconds: int,
    temperature: float,
    prompt: str | None,
):
    db = SessionLocal()
    try:
        process_generation_job(
            job_id=job_id,
            db=db,
            genre=genre,
            mood=mood,
            tempo=tempo,
            instrument=instrument,
            duration_seconds=duration_seconds,
            temperature=temperature,
            prompt=prompt,
        )
    finally:
        db.close()

def format_job_response(job: GenerationJob) -> dict:
    assets = [
        GeneratedAssetResponse(
            id=a.id,
            asset_type=a.asset_type,
            file_size_bytes=a.file_size_bytes,
            mime_type=a.mime_type,
            download_url=f"/api/assets/{a.id}/download",
            created_at=a.created_at,
        )
        for a in job.assets
    ]
    return {
        "id": job.id,
        "project_id": job.project_id,
        "status": job.status,
        "progress": job.progress,
        "error_message": job.error_message,
        "created_at": job.created_at,
        "completed_at": job.completed_at,
        "assets": assets,
    }

@router.post("", response_model=GenerationJobResponse, status_code=status.HTTP_202_ACCEPTED)
def create_generation(
    gen_in: GenerationCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Check credit balance
    if current_user.credits_balance <= 0:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Insufficient generation credits. Please upgrade your plan or purchase additional credits.",
        )

    # Associate with existing project or create a new project
    project = None
    if gen_in.project_id:
        project = db.query(MusicProject).filter(
            MusicProject.id == gen_in.project_id,
            MusicProject.user_id == current_user.id
        ).first()

    if not project:
        title = (gen_in.prompt[:40] + "...") if gen_in.prompt else f"{gen_in.genre.title()} {gen_in.mood.title()} Composition"
        project = MusicProject(
            user_id=current_user.id,
            title=title,
            prompt=gen_in.prompt,
            genre=gen_in.genre,
            mood=gen_in.mood,
            tempo=gen_in.tempo,
            instrument=gen_in.instrument,
            duration_seconds=gen_in.duration_seconds,
        )
        db.add(project)
        db.commit()
        db.refresh(project)

    # Create GenerationJob in queued state
    job = GenerationJob(
        user_id=current_user.id,
        project_id=project.id,
        status="queued",
        progress=0,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Enqueue background task
    background_tasks.add_task(
        run_worker_in_background,
        job_id=job.id,
        genre=gen_in.genre,
        mood=gen_in.mood,
        tempo=gen_in.tempo,
        instrument=gen_in.instrument,
        duration_seconds=gen_in.duration_seconds,
        temperature=gen_in.temperature,
        prompt=gen_in.prompt,
    )

    return format_job_response(job)

@router.get("/{generation_id}", response_model=GenerationJobResponse)
def get_generation_status(
    generation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.query(GenerationJob).filter(
        GenerationJob.id == generation_id,
        GenerationJob.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generation job not found.")

    return format_job_response(job)

@router.get("", response_model=List[GenerationJobResponse])
def list_generations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 20,
):
    jobs = db.query(GenerationJob).filter(
        GenerationJob.user_id == current_user.id
    ).order_by(GenerationJob.created_at.desc()).limit(limit).all()

    return [format_job_response(j) for j in jobs]
