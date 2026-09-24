import os
from datetime import datetime, timezone
import traceback
from sqlalchemy.orm import Session
from app.models.models import GenerationJob, GeneratedAsset, UsageRecord, User, MusicProject
from app.services.ai_service import AIService

def process_generation_job(
    job_id: str,
    db: Session,
    genre: str,
    mood: str,
    tempo: int,
    instrument: str,
    duration_seconds: int,
    temperature: float = 1.0,
    prompt: str | None = None,
):
    """
    Background worker task: executes AI generation, updates job states,
    creates assets in database, and deducts user credits.
    """
    job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
    if not job:
        return

    try:
        # State: Generating
        job.status = "generating"
        job.progress = 25
        db.commit()

        # Run AI generation & Audio rendering
        midi_path, wav_path, metadata = AIService.run_generation_pipeline(
            genre=genre,
            mood=mood,
            tempo=tempo,
            instrument=instrument,
            duration_seconds=duration_seconds,
            temperature=temperature,
            prompt=prompt,
            job_id=job_id,
        )

        # State: Rendering
        job.status = "rendering"
        job.progress = 75
        db.commit()

        # Create GeneratedAsset records
        midi_asset = GeneratedAsset(
            generation_job_id=job.id,
            project_id=job.project_id,
            asset_type="midi",
            file_path=midi_path,
            file_size_bytes=metadata.get("midi_size_bytes", 0),
            mime_type="audio/midi",
        )
        wav_asset = GeneratedAsset(
            generation_job_id=job.id,
            project_id=job.project_id,
            asset_type="audio_wav",
            file_path=wav_path,
            file_size_bytes=metadata.get("wav_size_bytes", 0),
            mime_type="audio/wav",
        )

        db.add(midi_asset)
        db.add(wav_asset)

        # Deduct credits & record usage
        user = db.query(User).filter(User.id == job.user_id).first()
        if user and user.credits_balance > 0:
            user.credits_balance -= 1
            usage = UsageRecord(
                user_id=user.id,
                credits_spent=1,
                action=f"Generated track: {genre} / {instrument} ({duration_seconds}s)",
            )
            db.add(usage)

        # State: Completed
        job.status = "completed"
        job.progress = 100
        job.completed_at = datetime.now(timezone.utc)
        db.commit()

    except Exception as e:
        db.rollback()
        err_msg = f"{str(e)}\n{traceback.format_exc()}"
        job = db.query(GenerationJob).filter(GenerationJob.id == job_id).first()
        if job:
            job.status = "failed"
            job.progress = 0
            job.error_message = str(e)
            job.completed_at = datetime.now(timezone.utc)
            db.commit()
