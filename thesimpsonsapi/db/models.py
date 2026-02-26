from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from db.base import Base


class Personaje(Base):
    __tablename__ = 'personajes'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    occupation = Column(String, nullable=True)
    birthdate = Column(String, nullable=True)
    portrait_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'<Personaje id={self.id} name={self.name!r}>'
