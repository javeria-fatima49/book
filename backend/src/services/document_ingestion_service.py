import logging
from typing import List, Dict, Any
from fastapi import HTTPException
import re
from src.services.book_service import BookService
from src.services.rag_service import RagService
from src.models.db_models import Book, Chapter, BookSection
from src.core.database import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class DocumentIngestionService:
    """
    Service class for ingesting book documents into the RAG system.
    Handles parsing, chunking, and storing book content in both Postgres and Qdrant.
    """
    
    def __init__(self, book_service: BookService, rag_service: RagService):
        self.book_service = book_service
        self.rag_service = rag_service
    
    async def ingest_book(self, title: str, author: str, isbn: str, content: str) -> Dict[str, Any]:
        """
        Main method to ingest a complete book into the RAG system.
        
        Args:
            title: Book title
            author: Book author
            isbn: Book ISBN
            content: Full book content
            
        Returns:
            Dictionary with ingestion results
        """
        try:
            # First, check if book already exists
            existing_book = await self.book_service.get_book_by_isbn(isbn)
            if existing_book:
                raise HTTPException(status_code=400, detail="Book with this ISBN already exists")
            
            # Create book in database
            book = await self.book_service.create_book(title, author, isbn, content)
            
            # Parse and split the content into chunks
            chunks = self._chunk_book_content(content, max_chunk_size=1000)
            
            # Process each chunk
            total_upserted = 0
            for i, chunk in enumerate(chunks):
                # Add metadata about the book and chunk position
                metadata = {
                    "book_id": book.id,
                    "book_title": book.title,
                    "book_author": book.author,
                    "isbn": book.isbn,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
                
                # Upsert the chunk to Qdrant
                count = await self.rag_service.upsert_embeddings(chunk, metadata)
                total_upserted += count
                
                # Save chunk reference in database
                await self.book_service.create_section(
                    book_id=book.id,
                    section_title=f"Chunk {i+1}",
                    content=chunk[:200] + "...",  # Store truncated version
                    embedding_id=str(hash(chunk))  # Using hash as embedding ID for now
                )
                
            return {
                "status": "success",
                "book_id": book.id,
                "chunks_processed": len(chunks),
                "vectors_upserted": total_upserted,
                "message": f"Successfully ingested book '{title}' with {len(chunks)} content chunks."
            }
        except Exception as e:
            logger.error(f"Error ingesting book: {e}")
            raise HTTPException(status_code=500, detail=f"Error ingesting book: {str(e)}")
    
    def _chunk_book_content(self, content: str, max_chunk_size: int = 1000) -> List[str]:
        """
        Split book content into chunks of approximately max_chunk_size words,
        trying to break at paragraph or sentence boundaries.
        
        Args:
            content: The book content to chunk
            max_chunk_size: Maximum number of characters per chunk
            
        Returns:
            List of content chunks
        """
        chunks = []
        
        # First split by paragraphs
        paragraphs = content.split('\n\n')
        
        current_chunk = ""
        
        for paragraph in paragraphs:
            # If adding the next paragraph would exceed the max size
            if len(current_chunk) + len(paragraph) > max_chunk_size:
                # If current chunk is not empty, finalize it
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                
                # Start a new chunk if the paragraph itself is not too big
                if len(paragraph) <= max_chunk_size:
                    current_chunk = paragraph
                else:
                    # If the paragraph is too big, break it into sentences
                    sentences = self._split_large_paragraph(paragraph, max_chunk_size)
                    if sentences:
                        current_chunk = sentences[0]
                        # Handle remaining sentences in upcoming iterations
                        for sentence in sentences[1:]:
                            if len(current_chunk) + len(sentence) <= max_chunk_size:
                                current_chunk += " " + sentence
                            else:
                                chunks.append(current_chunk.strip())
                                current_chunk = sentence
            else:
                # Add paragraph to current chunk
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Add the last chunk if it exists
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks

    def _split_large_paragraph(self, paragraph: str, max_chunk_size: int) -> List[str]:
        """
        Split a large paragraph into sentences to fit within chunk size.
        """
        import re
        # Split by punctuation that typically ends sentences
        sentences = re.split(r'[.!?]+', paragraph)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            # If no sentence punctuation found, split by max_chunk_size anyway
            return [paragraph[i:i+max_chunk_size] for i in range(0, len(paragraph), max_chunk_size)]
        
        # Try to group sentences into chunks of appropriate size
        grouped_sentences = []
        current_group = ""
        
        for sentence in sentences:
            if len(current_group) + len(sentence) <= max_chunk_size:
                if current_group:
                    current_group += ". " + sentence
                else:
                    current_group = sentence
            else:
                if current_group:
                    grouped_sentences.append(current_group + ".")
                if len(sentence) <= max_chunk_size:
                    current_group = sentence
                else:
                    # Sentence is too long, split it by character limit
                    sub_chunks = [sentence[i:i+max_chunk_size] for i in range(0, len(sentence), max_chunk_size)]
                    grouped_sentences.extend(sub_chunks[:-1])  # Add all but the last chunk
                    current_group = sub_chunks[-1] if sub_chunks else ""
        
        if current_group:
            grouped_sentences.append(current_group)
        
        return grouped_sentences

    async def ingest_chapters(self, book_id: int, chapters_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Ingest individual chapters for a book.
        
        Args:
            book_id: ID of the parent book
            chapters_data: List of dictionaries with 'title', 'content', and 'page_number'
            
        Returns:
            Dictionary with ingestion results
        """
        try:
            book = await self.book_service.get_book_by_id(book_id)
            if not book:
                raise HTTPException(status_code=404, detail="Book not found")
            
            total_upserted = 0
            for chap_data in chapters_data:
                # Create chapter in database
                chapter = await self.book_service.create_chapter(
                    book_id=book_id,
                    title=chap_data['title'],
                    content=chap_data['content'],
                    page_number=chap_data.get('page_number', 0)
                )
                
                # Split chapter content into chunks and upsert to Qdrant
                chunks = self._chunk_book_content(chap_data['content'], max_chunk_size=1000)
                
                for i, chunk in enumerate(chunks):
                    metadata = {
                        "book_id": book.id,
                        "book_title": book.title,
                        "book_author": book.author,
                        "chapter_id": chapter.id,
                        "chapter_title": chapter.title,
                        "isbn": book.isbn,
                        "chunk_index": i,
                        "section_type": "chapter"
                    }
                    
                    count = await self.rag_service.upsert_embeddings(chunk, metadata)
                    total_upserted += count
                    
                    # Save section reference in database
                    await self.book_service.create_section(
                        book_id=book_id,
                        chapter_id=chapter.id,
                        section_title=f"{chapter.title} - Chunk {i+1}",
                        content=chunk[:200] + "...",
                        embedding_id=str(hash(chunk))
                    )
            
            return {
                "status": "success",
                "chapters_created": len(chapters_data),
                "vectors_upserted": total_upserted,
                "message": f"Successfully ingested {len(chapters_data)} chapters with embeddings."
            }
        except Exception as e:
            logger.error(f"Error ingesting chapters: {e}")
            raise HTTPException(status_code=500, detail=f"Error ingesting chapters: {str(e)}")