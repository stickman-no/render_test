from sqlalchemy import Column, Integer, String
from database import Base

class DBBook(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    author = Column(String, index=True, nullable=False)
    published_year = Column(Integer, nullable=True)
    genre = Column(String, nullable=True)
    description = Column(String, nullable=True)
