import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from passlib.hash import bcrypt
from dotenv import load_dotenv

# Load .vars file
env_path = os.path.join(os.getcwd(), ".vars")
load_dotenv(env_path)

# Use .vars value or fallback
sqlite_filename = os.getenv("DEV_DB_SQLITE_FILENAME", "dev.db")
db_url = f"sqlite:///{sqlite_filename}"

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(db_url, echo=True)
SessionLocal = sessionmaker(bind=engine)

# Define User model (must match app model)
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False)
    last_login = Column(DateTime, default=datetime.utcnow)

# Create DB schema
Base.metadata.create_all(bind=engine)

# Seed admin user
def create_admin_user():
    db = SessionLocal()
    user = db.query(User).filter_by(email="hasanrazat@gmail.com").first()
    if not user:
        admin_user = User(
            email="hasanrazat@gmail.com",
            first_name="Mir Hassan",
            last_name="Raza",
            hashed_password=bcrypt.hash("pasword123"),
            is_admin=True
        )
        db.add(admin_user)
        db.commit()
        print("✅ Admin user created.")
    else:
        print("ℹ️ Admin user already exists.")
    db.close()

if __name__ == "__main__":
    create_admin_user()
