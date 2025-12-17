"""
Script to ingest Docusaurus documentation content into the RAG system.
Reads markdown files from frontend/docs folder, chunks them, and uploads embeddings to Qdrant.
"""
import os
import asyncio
from pathlib import Path
import re
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_markdown_files(docs_path: str) -> List[Dict[str, Any]]:
    """
    Read all markdown files from the docs folder.
    Args:
        docs_path: Path to the docs directory
    Returns:
        List of dictionaries containing file content and metadata
    """
    markdown_files = []
    
    docs_dir = Path(docs_path)
    
    if not docs_dir.exists():
        logger.error(f"Docs directory does not exist: {docs_path}")
        return []
    
    # Walk through all subdirectories and include both .md and .mdx files
    for file_path in docs_dir.rglob("*"):  # All files in docs directory
        if file_path.suffix.lower() in ['.md', '.mdx']:  # Include both markdown and mdx files
            try:
                logger.info(f"Reading file: {file_path}")

                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract basic metadata from the file path
                relative_path = file_path.relative_to(docs_dir)
                metadata = {
                    "file_path": str(relative_path),
                    "file_name": file_path.name,
                    "directory": str(file_path.parent),
                    "source": "docusaurus_docs"
                }

                markdown_files.append({
                    "content": content,
                    "metadata": metadata
                })

            except Exception as e:
                logger.error(f"Error reading file {file_path}: {e}")
    
    logger.info(f"Found {len(markdown_files)} markdown files")
    return markdown_files


def chunk_text(text: str, max_words: int = 500, overlap_words: int = 50) -> List[str]:
    """
    Split text into chunks of approximately max_words with overlap.
    Args:
        text: The text to chunk
        max_words: Maximum number of words per chunk (300-700 as recommended)
        overlap_words: Number of overlapping words between chunks (50-100 as recommended)
    Returns:
        List of text chunks
    """
    # Split text into words
    words = text.split()
    chunks = []

    start_idx = 0
    while start_idx < len(words):
        # Determine the end index for this chunk
        end_idx = start_idx + max_words

        # Create the chunk
        chunk = ' '.join(words[start_idx:end_idx])

        # Add to chunks if not empty
        if chunk.strip():
            chunks.append(chunk)

        # Move start index by (max_words - overlap_words) to create overlap
        start_idx = end_idx - overlap_words if overlap_words < max_words else end_idx

        # Ensure we don't go out of bounds
        if start_idx >= len(words):
            break

    return chunks


def chunk_markdown_content(files: List[Dict[str, Any]], max_words: int = 500, overlap_words: int = 50) -> List[Dict[str, Any]]:
    """
    Chunk markdown content from multiple files.
    Args:
        files: List of file content and metadata
        max_words: Maximum number of words per chunk
        overlap_words: Number of overlapping words between chunks
    Returns:
        List of chunked content with metadata
    """
    all_chunks = []
    
    for file_data in files:
        content = file_data["content"]
        metadata = file_data["metadata"]
        
        # Chunk the content
        chunks = chunk_text(content, max_words=max_words, overlap_words=overlap_words)
        
        logger.info(f"File {metadata['file_name']} was split into {len(chunks)} chunks")
        
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_index"] = i
            chunk_metadata["total_chunks"] = len(chunks)
            
            all_chunks.append({
                "content": chunk,
                "metadata": chunk_metadata
            })
    
    logger.info(f"Total chunks created: {len(all_chunks)}")
    return all_chunks


async def upload_chunks_to_rag(chunks: List[Dict[str, Any]], base_url: str = "http://localhost:8000"):
    """
    Upload chunks to the RAG backend using the upsert endpoint.
    Args:
        chunks: List of chunked content with metadata
        base_url: Base URL of the FastAPI backend
    """
    import httpx
    
    successful_uploads = 0
    failed_uploads = 0
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i, chunk in enumerate(chunks):
            try:
                logger.info(f"Uploading chunk {i+1}/{len(chunks)}: {chunk['metadata']['file_name']}")
                
                response = await client.post(
                    f"{base_url}/api/v1/rag/embeddings/upsert",
                    json={
                        "content": chunk["content"],
                        "metadata": chunk["metadata"]
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Successfully uploaded chunk: {result}")
                    successful_uploads += 1
                else:
                    logger.error(f"Failed to upload chunk {i+1}: {response.status_code} - {response.text}")
                    failed_uploads += 1
                    
            except Exception as e:
                logger.error(f"Error uploading chunk {i+1}: {e}")
                failed_uploads += 1
    
    logger.info(f"Upload complete: {successful_uploads} successful, {failed_uploads} failed")


async def main():
    """
    Main function to read markdown files, chunk them, and upload to RAG.
    """
    # Define the path to your docs folder
    docs_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "docs")
    docs_path = os.path.abspath(docs_path)
    
    logger.info(f"Reading markdown files from: {docs_path}")
    
    # Read all markdown files
    files = read_markdown_files(docs_path)
    
    if not files:
        logger.error("No markdown files found. Please check if the docs folder exists and contains .md files.")
        return
    
    # Chunk the content (using recommended parameters: 300-700 words per chunk)
    chunks = chunk_markdown_content(files, max_words=500, overlap_words=75)
    
    if not chunks:
        logger.error("No content to upload after chunking.")
        return
    
    # Upload to RAG backend
    await upload_chunks_to_rag(chunks)
    
    logger.info("Ingestion process completed!")


if __name__ == "__main__":
    asyncio.run(main())