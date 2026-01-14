import os
from fastapi import FastAPI, UploadFile, File, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.db.database import Base, engine, SessionLocal
from app.db.models import Document
from app.schemas.document import DocumentResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Knowledge Base and Document Management System")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_model=list[DocumentResponse])
def get_all_documents(db: Session = Depends(get_db)):
    return db.query(Document).order_by(Document.uploaded_at.desc()).all()

@app.post("/upload")
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
    
@app.get("/search")
def search_documents(tag: str, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.tags.contains(tag)).all()
    
    if not document:
        raise HTTPException(status_code=404, detail="No documents found with the given tag")
    
    return document


@app.get("/versions/{filename}")
def get_versions(filename: str, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.filename == filename).order_by(Document.version).all()
    
    if not document:
        raise HTTPException(status_code=404, detail="No versions found for the given filename")
    
    return document

@app.delete("/delete")
def delete_document(
    filename: str,
    version: int,
    db: Session = Depends(get_db)
):
    document = db.query(Document).filter(
        Document.filename == filename,
        Document.version == version
    ).first()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete file from uploads folder
    if os.path.exists(document.filepath):
        os.remove(document.filepath)

    # Delete DB record
    db.delete(document)
    db.commit()

    return {
        "message": "Document deleted successfully",
        "filename": filename,
        "version": version
    }
