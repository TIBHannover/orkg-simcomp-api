import logging
from typing import Type

from sqlalchemy.orm import Session

from app.db.connection import Base

logger = logging.getLogger(__name__)


def create(db: Session, entity: Base):
    logger.info('Creating entity...')

    db.add(entity)
    db.commit()
    db.refresh(entity)

    logger.info('Entity created!')


def query_all(db: Session, entity: Type[Base], skip: int, limit: int):
    logger.info('Querying entities...')

    return db.query(entity).offset(skip).limit(limit).all()
