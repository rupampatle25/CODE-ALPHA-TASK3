from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import User, MusicProject, GenerationJob, GeneratedAsset
from app.schemas.schemas import (
    MusicProjectCreate,
    MusicProjectUpdate,
    MusicProjectResponse,
    GeneratedAssetResponse,
    GenerationJobResponse,
)
from app.api.auth import get_current_user

router = APIRouter(prefix="/projects", tags=["Music Projects"])

def format_project_response(project: MusicProject) -> dict:
    assets = [
        GeneratedAssetResponse(
            id=a.id,
            asset_type=a.asset_type,
            file_size_bytes=a.file_size_bytes,
            mime_type=a.mime_type,
            download_url=f"/api/assets/{a.id}/download",
            created_at=a.created_at,
        )
        for a in project.assets
    ]

    latest_job = None
    if project.generation_jobs:
        sorted_jobs = sorted(project.generation_jobs, key=lambda j: j.created_at, reverse=True)
        lj = sorted_jobs[0]
        latest_job = GenerationJobResponse(
            id=lj.id,
            project_id=lj.project_id,
            status=lj.status,
            progress=lj.progress,
            error_message=lj.error_message,
            created_at=lj.created_at,
            completed_at=lj.completed_at,
            assets=[
                GeneratedAssetResponse(
                    id=a.id,
                    asset_type=a.asset_type,
                    file_size_bytes=a.file_size_bytes,
                    mime_type=a.mime_type,
                    download_url=f"/api/assets/{a.id}/download",
                    created_at=a.created_at,
                ) for a in lj.assets
            ],
        )

    return {
        "id": project.id,
        "user_id": project.user_id,
        "title": project.title,
        "prompt": project.prompt,
        "genre": project.genre,
        "mood": project.mood,
        "tempo": project.tempo,
        "instrument": project.instrument,
        "duration_seconds": project.duration_seconds,
        "is_favorite": project.is_favorite,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
        "latest_job": latest_job,
        "assets": assets,
    }

@router.get("", response_model=List[MusicProjectResponse])
def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    projects = db.query(MusicProject).filter(
        MusicProject.user_id == current_user.id
    ).order_by(MusicProject.updated_at.desc()).all()

    return [format_project_response(p) for p in projects]

@router.post("", response_model=MusicProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    p_in: MusicProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = MusicProject(
        user_id=current_user.id,
        title=p_in.title,
        prompt=p_in.prompt,
        genre=p_in.genre,
        mood=p_in.mood,
        tempo=p_in.tempo,
        instrument=p_in.instrument,
        duration_seconds=p_in.duration_seconds,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return format_project_response(project)

@router.get("/{project_id}", response_model=MusicProjectResponse)
def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.query(MusicProject).filter(
        MusicProject.id == project_id,
        MusicProject.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    return format_project_response(project)

@router.patch("/{project_id}", response_model=MusicProjectResponse)
def update_project(
    project_id: str,
    p_update: MusicProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.query(MusicProject).filter(
        MusicProject.id == project_id,
        MusicProject.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    if p_update.title is not None:
        project.title = p_update.title.strip()
    if p_update.is_favorite is not None:
        project.is_favorite = p_update.is_favorite

    db.commit()
    db.refresh(project)
    return format_project_response(project)

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = db.query(MusicProject).filter(
        MusicProject.id == project_id,
        MusicProject.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")

    db.delete(project)
    db.commit()
    return None
