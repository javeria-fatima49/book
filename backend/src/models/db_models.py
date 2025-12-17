from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    isbn = Column(String, unique=True, index=True)
    publication_date = Column(DateTime, nullable=True)
    content = Column(Text)  # Full book content
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    title = Column(String, index=True)
    content = Column(Text)  # Chapter content
    page_number = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class BookSection(Base):
    __tablename__ = "book_sections"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=True)
    section_title = Column(String, index=True)
    content = Column(Text)  # Section content
    embedding_id = Column(String, index=True)  # Reference to Qdrant vector ID
    created_at = Column(DateTime, default=datetime.utcnow)