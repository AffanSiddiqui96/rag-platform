import logging
import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.dependencies import require_role
from utilities.model import UserModel
from utilities.roles import RoleName
from utilities.schema import DocumentUploadResponse

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)

logger = logging.getLogger(__name__)

UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "text/plain",
    "text/markdown",
    "text/csv",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
MAX_UPLOAD_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    current_user: UserModel = Depends(require_role(RoleName.ADMIN.value)),
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: {file.content_type}",
        )

    contents = await file.read()
    if len(contents) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds the maximum allowed size of 20MB",
        )
    if not contents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    # Prefix with a random id so a malicious/duplicate filename can't collide
    # with or overwrite another file; basename strips any path components.
    safe_name = f"{uuid.uuid4().hex}_{os.path.basename(file.filename)}"
    dest_path = os.path.join(UPLOAD_DIR, safe_name)

    with open(dest_path, "wb") as f:
        f.write(contents)

    logger.info(
        "Document '%s' (%d bytes) uploaded by user_id=%s", safe_name, len(contents), current_user.id
    )

    return DocumentUploadResponse(
        filename=file.filename,
        content_type=file.content_type,
        size_bytes=len(contents),
        uploaded_by=current_user.username,
    )
