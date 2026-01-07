import os
from fastapi import APIRouter, UploadFile, File, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import Document
from app.schemas.document import DocumentResponse

router = APIRouter(prefix="/documents", tags=["Documents"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    tags: str = Query(...),
    db: Session = Depends(get_db)
):
    existing = db.query(Document).filter(Document.filename == file.filename).all()
    version = len(existing) + 1

    file_path = os.path.join(UPLOAD_DIR, f"v{version}_{file.filename}")

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    doc = Document(
        filename=file.filename,
        filepath=file_path,
        tags=tags,
        version=version
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {
        "message": "Document uploaded successfully",
        "filename": doc.filename,
        "version": doc.version
    }


@router.get("/", response_model=list[DocumentResponse])
def get_all_documents(db: Session = Depends(get_db)):
    return db.query(Document).order_by(Document.uploaded_at.desc()).all()


@router.get("/search")
def search_documents(tag: str, db: Session = Depends(get_db)):
    return db.query(Document).filter(Document.tags.contains(tag)).all()


@router.get("/versions/{filename}")
def get_versions(filename: str, db: Session = Depends(get_db)):
    return (
        db.query(Document)
        .filter(Document.filename == filename)
        .order_by(Document.version)
        .all()
    )
