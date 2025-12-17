from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.db_models import Book, Chapter, BookSection
from src.core.database import get_db_session
from fastapi import Depends, HTTPException
import logging

logger = logging.getLogger(__name__)


class BookService:
    def __init__(self, db: AsyncSession = Depends(get_db_session)):
        self.db = db

    async def create_book(self, title: str, author: str, isbn: str, content: str) -> Book:
        """Create a new book entry in the database."""
        book = Book(
            title=title,
            author=author,
            isbn=isbn,
            content=content
        )
        self.db.add(book)
        await self.db.commit()
        await self.db.refresh(book)
        return book

    async def get_book_by_isbn(self, isbn: str) -> Optional[Book]:
        """Retrieve a book by its ISBN."""
        query = select(Book).where(Book.isbn == isbn)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_book_by_id(self, book_id: int) -> Optional[Book]:
        """Retrieve a book by its ID."""
        query = select(Book).where(Book.id == book_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_chapter(self, book_id: int, title: str, content: str, page_number: int) -> Chapter:
        """Create a new chapter for a book."""
        chapter = Chapter(
            book_id=book_id,
            title=title,
            content=content,
            page_number=page_number
        )
        self.db.add(chapter)
        await self.db.commit()
        await self.db.refresh(chapter)
        return chapter

    async def get_chapters_by_book(self, book_id: int) -> List[Chapter]:
        """Get all chapters for a specific book."""
        query = select(Chapter).where(Chapter.book_id == book_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_section(self, book_id: int, section_title: str, content: str, embedding_id: str, chapter_id: Optional[int] = None) -> BookSection:
        """Create a new book section."""
        section = BookSection(
            book_id=book_id,
            chapter_id=chapter_id,
            section_title=section_title,
            content=content,
            embedding_id=embedding_id
        )
        self.db.add(section)
        await self.db.commit()
        await self.db.refresh(section)
        return section

    async def get_sections_by_book(self, book_id: int) -> List[BookSection]:
        """Get all sections for a specific book."""
        query = select(BookSection).where(BookSection.book_id == book_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_section_by_embedding_id(self, embedding_id: str) -> Optional[BookSection]:
        """Get a section by its embedding ID."""
        query = select(BookSection).where(BookSection.embedding_id == embedding_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_all_books(self) -> List[Book]:
        """Get all books from the database."""
        query = select(Book)
        result = await self.db.execute(query)
        return result.scalars().all()