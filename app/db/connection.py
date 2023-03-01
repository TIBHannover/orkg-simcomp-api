# -*- coding: utf-8 -*-
import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

ORKG_SIMCOMP_API_DATABASE_URI = os.environ.get("ORKG_SIMCOMP_API_DATABASE_URI")

if os.environ.get("ORKG_SIMCOMP_API_ENV") != "test" and not ORKG_SIMCOMP_API_DATABASE_URI:
    raise ValueError('Please consider setting "ORKG_SIMCOMP_API_DATABASE_URI" in the .env file.')

engine = create_engine(ORKG_SIMCOMP_API_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()
