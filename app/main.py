from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.api.documents import router as document_router
from app.db.database import Base, engine, SessionLocal
from app.db.models import Document

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Knowledge Base and Document Management System")

app.include_router(document_router)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def home(db: Session = Depends(get_db)):
    documents = db.query(Document).order_by(Document.uploaded_at.desc()).all()

    html = """
    <html>
    <head>
        <title>Knowledge Base</title>
        <style>
            body { font-family: Arial; padding: 20px; }
            h1 { color: #2c3e50; }
            table { border-collapse: collapse; width: 100%; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f4f4f4; }
        </style>
    </head>
    <body>
        <h1>Knowledge Base and Document Management System</h1>
        <p>All Uploaded Documents</p>

        <table>
            <tr>
                <th>ID</th>
                <th>Filename</th>
                <th>Tags</th>
                <th>Version</th>
                <th>Uploaded At</th>
            </tr>
    """

    for doc in documents:
        html += f"""
            <tr>
                <td>{doc.id}</td>
                <td>{doc.filename}</td>
                <td>{doc.tags}</td>
                <td>{doc.version}</td>
                <td>{doc.uploaded_at}</td>
            </tr>
        """

    html += """
        </table>
    </body>
    </html>
    """

    return html
