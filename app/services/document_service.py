import os
from sqlalchemy.orm import Session
from app.db.models import Document

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_file(file):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return file.filename

def create_document(db: Session, filename: str, tags: str):
    existing = db.query(Document).filter(Document.filename == filename).first()
    version = existing.version + 1 if existing else 1

    document = Document(
        filename=filename,
        tags=tags,
        version=version
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document

def search_documents(db: Session, tag: str):
    return db.query(Document).filter(Document.tags.contains(tag)).all()
