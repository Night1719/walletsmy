import sys
from sqlalchemy.orm import Session

from .database import SessionLocal, engine
from .models import Base, User
from .auth import hash_password


def create_admin(username: str, email: str, password: str):
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            print("Admin user already exists, skipping.")
            return
        admin = User(username=username, email=email, password_hash=hash_password(password), role="admin", is_active=True)
        db.add(admin)
        db.commit()
        print("Admin user created.")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python -m app.cli <username> <email> <password>")
        sys.exit(1)
    create_admin(sys.argv[1], sys.argv[2], sys.argv[3])