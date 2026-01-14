from fastapi import FastAPI
from App.database import engine, SessionLocal
from App.database import Base
from App.models import User,Documents,Versions
from App.routers import User,Documents

Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(User.router)
app.include_router(Documents.router)

