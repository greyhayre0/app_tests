import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models, crud
from app.schemas import UserCreate, ResumeCreate
from app.database import Base


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
    )


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_create_user(db):
    user_data = UserCreate(email="test@example.com", password="password123")
    user = crud.create_user(db, user_data)

    assert user.email == "test@example.com"
    assert user.hashed_password is not None
    assert user.hashed_password != "password123"


def test_get_user_by_email(db):
    user_data = UserCreate(email="test@example.com", password="password123")
    crud.create_user(db, user_data)

    user = crud.get_user_by_email(db, "test@example.com")
    assert user is not None
    assert user.email == "test@example.com"


def test_create_resume(db):
    user_data = UserCreate(email="test@example.com", password="password123")
    user = crud.create_user(db, user_data)

    resume_data = ResumeCreate(title="Test Resume", content="Test content")
    resume = crud.create_resume(db, resume_data, user.id)

    assert resume.title == "Test Resume"
    assert resume.content == "Test content"
    assert resume.owner_id == user.id


def test_get_resumes(db):

    user_data = UserCreate(email="test@example.com", password="password123")
    user = crud.create_user(db, user_data)

    resume1 = ResumeCreate(title="Resume 1", content="Content 1")
    resume2 = ResumeCreate(title="Resume 2", content="Content 2")

    crud.create_resume(db, resume1, user.id)
    crud.create_resume(db, resume2, user.id)

    resumes = crud.get_resumes(db, user.id)
    assert len(resumes) == 2
    assert resumes[0].title == "Resume 1"
    assert resumes[1].title == "Resume 2"


def test_get_resume(db):
    user_data = UserCreate(email="test@example.com", password="password123")
    user = crud.create_user(db, user_data)

    resume_data = ResumeCreate(title="Test Resume", content="Test content")
    resume = crud.create_resume(db, resume_data, user.id)

    found_resume = crud.get_resume(db, resume.id, user.id)
    assert found_resume is not None
    assert found_resume.title == "Test Resume"


def test_update_resume(db):
    user_data = UserCreate(email="test@example.com", password="password123")
    user = crud.create_user(db, user_data)

    resume_data = ResumeCreate(title="Old Title", content="Old content")
    resume = crud.create_resume(db, resume_data, user.id)

    updated_data = ResumeCreate(title="New Title", content="New content")
    updated_resume = crud.update_resume(db, resume.id, updated_data, user.id)

    assert updated_resume.title == "New Title"
    assert updated_resume.content == "New content"


def test_delete_resume(db):
    user_data = UserCreate(email="test@example.com", password="password123")
    user = crud.create_user(db, user_data)

    resume_data = ResumeCreate(title="Test Resume", content="Test content")
    resume = crud.create_resume(db, resume_data, user.id)

    deleted_resume = crud.delete_resume(db, resume.id, user.id)
    assert deleted_resume is not None

    found_resume = crud.get_resume(db, resume.id, user.id)
    assert found_resume is None


def test_improve_resume(db):
    user_data = UserCreate(email="test@example.com", password="password123")
    user = crud.create_user(db, user_data)

    resume_data = ResumeCreate(title="Test Resume", content="Original content")
    resume = crud.create_resume(db, resume_data, user.id)

    improved_content = crud.improve_resume(db, resume.id, user.id)
    assert improved_content == "Original content [Improved]"

    improvements = db.query(models.Improvement).filter(
        models.Improvement.resume_id == resume.id).all()
    assert len(improvements) == 1
    assert improvements[0].original_content == "Original content"
    assert improvements[0].improved_content == "Original content [Improved]"
