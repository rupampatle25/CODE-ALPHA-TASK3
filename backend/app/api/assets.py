import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import GeneratedAsset

router = APIRouter(prefix="/assets", tags=["Assets"])

@router.get("/{asset_id}/download")
def download_asset(
    asset_id: str,
    db: Session = Depends(get_db),
):
    asset = db.query(GeneratedAsset).filter(GeneratedAsset.id == asset_id).first()
    if not asset or not os.path.exists(asset.file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Asset file not found.")

    filename = os.path.basename(asset.file_path)
    return FileResponse(
        path=asset.file_path,
        media_type=asset.mime_type,
        filename=filename,
    )
