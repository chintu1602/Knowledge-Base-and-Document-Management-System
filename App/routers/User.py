from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from App.database import get_db
from App.models.User import User
from App.schemas.user import UserCreate,Userlogin
from App.core.security import hash_password, verify_password, create_access_token
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["Authorization"])

#User creation(signup)
@router.post("/register")
def register(request: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.Username == request.username).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        Username=request.username,
        Hashed_password=hash_password(request.password)
    )
    db.add(new_user)
    db.commit()
    return {"message": "User created"}

#Userlogin and token giving
@router.post("/login")
def login(request:OAuth2PasswordRequestForm=Depends() , db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.Username == request.username).first()

    if not db_user or not verify_password(request.password, db_user.Hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(db_user.id)})
    return {"access_token": token, "token_type": "bearer"}
