from fastapi import FastAPI
from app.api.documents import router as document_router
from app.db.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Knowledge Base & Document Management System")

app.include_router(document_router)
