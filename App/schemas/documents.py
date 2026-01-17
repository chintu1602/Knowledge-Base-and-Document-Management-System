from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DocumentCreate(BaseModel):
    title: str
    description: Optional[str]=None
    tag:Optional[str]=None

class DocumentResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    tag: Optional[str]
    created_at:datetime

    class Config:
        from_attributes= True
        
class DocumentVersionResponse(BaseModel):
    id: int
    version: int
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tag: Optional[str] = None  
