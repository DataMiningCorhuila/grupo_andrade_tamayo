from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from db.base import Base


class Personaje(Base):
    __tablename__ = 'personajes'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    status = Column(String, nullable=True)
    occupation = Column(String, nullable=True)
    birthdate = Column(String, nullable=True)
    portrait_path = Column(String, nullable=True)
    phrases = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'<Personaje id={self.id} name={self.name!r}>'


class Episodio(Base):
    __tablename__ = 'episodios'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    season = Column(Integer, nullable=True)
    episode_number = Column(Integer, nullable=True)
    airdate = Column(String, nullable=True)
    synopsis = Column(Text, nullable=True)
    image_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'<Episodio id={self.id} name={self.name!r}>'


class Ubicacion(Base):
    __tablename__ = 'ubicaciones'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    image_path = Column(String, nullable=True)
    town = Column(String, nullable=True)
    use = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f'<Ubicacion id={self.id} name={self.name!r}>'
