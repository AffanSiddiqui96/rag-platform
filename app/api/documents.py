import logging

from fastapi import APIRouter, Depends, File, UploadFile, status

from app.dependencies import require_role
from app.services.document_service import save_uploaded_document
from utilities.model import UserModel
from utilities.roles import RoleName
from utilities.schema import DocumentUploadResponse

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
)

logger = logging.getLogger(__name__)


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    current_user: UserModel = Depends(require_role(RoleName.ADMIN.value)),
):
    return await save_uploaded_document(file, current_user)
