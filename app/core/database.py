# SPDX-License-Identifier: Apache-2.0
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

from dotenv import load_dotenv

from app.core.config import EnvVariables

load_dotenv()

db_host = EnvVariables.DB_HOST
db_name = EnvVariables.DB_NAME
db_username = EnvVariables.DB_USERNAME
db_password = EnvVariables.DB_PASSWORD
db_port = EnvVariables.DB_PORT
DATABASE_URL = f"mysql+pymysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# 모든 모델의 부모
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()