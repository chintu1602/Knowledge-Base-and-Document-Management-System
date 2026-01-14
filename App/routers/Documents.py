from fastapi import APIRouter, Depends,UploadFile,File,HTTPException
from sqlalchemy.orm import Session
from App.database import get_db
from App.dependency import get_current_user
from App.schemas.documents import DocumentCreate,DocumentResponse,DocumentVersionResponse,DocumentUpdate
from App.models.Documents import Document
from App.models.Versions import DocumentVersion
from App.utils.filehandler import save_file
from fastapi.responses import FileResponse
import os

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/")
def create_document(
    title: str,
    description: str = None,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    # Save file
    file_path,file_name = save_file(file)

    # Create document
    document = Document(
        title=title,
        description=description,
        owner_id=user_id
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    # 3 Create version 1
    version = DocumentVersion(
        document_id=document.id,
        version=1,
        file_path=file_path,
        original_filename=file_name
    )
    db.add(version)
    db.commit()

    return {
        "message": "Document uploaded",
        "document_id": document.id,
        "version": 1
    }


@router.post("/{document_id}/versions")
def upload_new_version(
    document_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == user_id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    last_version = (
        db.query(DocumentVersion)
        .filter(DocumentVersion.document_id == document_id)
        .order_by(DocumentVersion.version.desc())
        .first()
    )

    new_version_number = last_version.version + 1

    file_path,file_name = save_file(file)

    new_version = DocumentVersion(
        document_id=document_id,
        version=new_version_number,
        file_path=file_path,
        original_filename=file_name
    )
    db.add(new_version)
    db.commit()

    return {
        "message": "New version uploaded",
        "version": new_version_number
    }
 

@router.get("/", response_model=list[DocumentResponse])
def list_my_documents(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    documents =db.query(Document).filter(Document.owner_id == user_id).order_by(Document.created_at.desc()).all()
    
    return documents

@router.get("/{document_id}/versions", response_model=list[DocumentVersionResponse])
def list_document_versions(
    document_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    # 1️ Check ownership
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == user_id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    #2 Get versions
    versions = (
        db.query(DocumentVersion)
        .filter(DocumentVersion.document_id == document_id)
        .order_by(DocumentVersion.version.desc())
        .all()
    )

    return versions



@router.get("/{document_id}/versions/{version_id}/download")
def download_version(
    document_id: int,
    version_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    # 1 Ownership check
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == user_id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # 2️ Get version
    version = db.query(DocumentVersion).filter(
        DocumentVersion.id == version_id,
        DocumentVersion.document_id == document_id
    ).first()

    if not version:
        raise HTTPException(status_code=404, detail="Version not found")

    # 3️ File existence check
    if not os.path.exists(version.file_path):
        raise HTTPException(status_code=404, detail="File missing on server")

    # 4️ Secure download
    return FileResponse(
        path=version.file_path,
        filename=version.original_filename,
        media_type="application/octet-stream"
    )




@router.put("/{document_id}")
def update_document(
    document_id: int,
    data: DocumentUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == user_id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if data.title is not None:
        document.title = data.title
    if data.description is not None:
        document.description = data.description

    db.commit()
    return {"message": "Document updated"}

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == user_id
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # 1️ Delete files from disk
    for version in document.versions:
        if os.path.exists(version.file_path):
            os.remove(version.file_path)

    # 2 Delete document (cascade deletes versions)
    db.delete(document)
    db.commit()

    return {"message": "Document deleted"}

