from pydantic import BaseModel
from datetime import datetime

class DocumentCreate(BaseModel):
    tags: str

class DocumentResponse(BaseModel):
    id: int
    filename: str
    filepath: str
    tags: str
    version: int
    uploaded_at: datetime

    class Config:
        orm_mode = True
    

