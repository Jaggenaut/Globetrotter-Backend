from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    # email = Column(String, unique=True, index=True)
    correct_answers = Column(Integer, default=0)
    incorrect_answers = Column(Integer, default=0)


class PlaceData(Base):
    __tablename__ = "placesdata"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, nullable=False)
    country = Column(String, nullable=False)
    clues = Column(JSON, nullable=False)  # Storing list as JSON
    fun_fact = Column(JSON, nullable=False)
    trivia = Column(JSON, nullable=False)