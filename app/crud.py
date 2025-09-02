from sqlalchemy.orm import Session
from . import models, schemas, auth


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_resumes(db: Session, user_id: int):
    return db.query(models.Resume).filter(models.Resume.owner_id == user_id
                                          ).all()


def get_resume(db: Session, resume_id: int, user_id: int):
    return db.query(models.Resume).filter(
        models.Resume.id == resume_id,
        models.Resume.owner_id == user_id
    ).first()


def create_resume(db: Session, resume: schemas.ResumeCreate, user_id: int):
    db_resume = models.Resume(**resume.dict(), owner_id=user_id)
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume


def update_resume(
        db: Session,
        resume_id: int,
        resume: schemas.ResumeCreate,
        user_id: int
        ):
    db_resume = get_resume(db, resume_id, user_id)
    if db_resume:
        db_resume.title = resume.title
        db_resume.content = resume.content
        db.commit()
        db.refresh(db_resume)
    return db_resume


def delete_resume(db: Session, resume_id: int, user_id: int):
    db_resume = get_resume(db, resume_id, user_id)
    if db_resume:
        db.delete(db_resume)
        db.commit()
    return db_resume


def improve_resume(db: Session, resume_id: int, user_id: int):
    resume = get_resume(db, resume_id, user_id)
    if not resume:
        return None
    improved_content = resume.content + " [Improved]"
    improvement = models.Improvement(
        resume_id=resume_id,
        original_content=resume.content,
        improved_content=improved_content
    )
    db.add(improvement)
    db.commit()
    return improved_content
