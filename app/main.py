from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from . import models, schemas, crud, auth
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Resume API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.post("/login", response_model=schemas.Token)
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if not db_user or not auth.verify_password(
        user.password,
        db_user.hashed_password
    ):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = auth.create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/resumes", response_model=list[schemas.ResumeResponse])
def read_resumes(
    token: str,
    db: Session = Depends(get_db)
):
    current_user = auth.get_current_user(db, token)
    return crud.get_resumes(db, user_id=current_user.id)


@app.post("/resumes", response_model=schemas.ResumeResponse)
def create_resume(
    resume: schemas.ResumeCreate,
    token: str,
    db: Session = Depends(get_db)
):
    current_user = auth.get_current_user(db, token)
    return crud.create_resume(db=db, resume=resume, user_id=current_user.id)


@app.get("/resumes/{resume_id}", response_model=schemas.ResumeResponse)
def read_resume(
    resume_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    current_user = auth.get_current_user(db, token)
    resume = crud.get_resume(db, resume_id=resume_id, user_id=current_user.id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


@app.put("/resumes/{resume_id}", response_model=schemas.ResumeResponse)
def update_resume(
    resume_id: int,
    resume: schemas.ResumeCreate,
    token: str,
    db: Session = Depends(get_db)
):
    current_user = auth.get_current_user(db, token)
    updated = crud.update_resume(
        db,
        resume_id=resume_id,
        resume=resume,
        user_id=current_user.id
        )
    if not updated:
        raise HTTPException(status_code=404, detail="Resume not found")
    return updated


@app.delete("/resumes/{resume_id}")
def delete_resume(
    resume_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    current_user = auth.get_current_user(db, token)
    deleted = crud.delete_resume(
        db,
        resume_id=resume_id,
        user_id=current_user.id
        )
    if not deleted:
        raise HTTPException(status_code=404, detail="Resume not found")
    return {"message": "Resume deleted"}


@app.post("/resumes/{resume_id}/improve",
          response_model=schemas.ImproveResponse
          )
def improve_resume(
    resume_id: int,
    token: str,
    db: Session = Depends(get_db)
):
    current_user = auth.get_current_user(db, token)
    improved_content = crud.improve_resume(
        db,
        resume_id=resume_id,
        user_id=current_user.id
        )
    if not improved_content:
        raise HTTPException(status_code=404, detail="Resume not found")
    return {"improved_content": improved_content}
