"""
Main application for Azure Legal Document Chatbot
Integrates Azure Blob Storage and Azure Cognitive Search for document management
"""
import os
import logging
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from .config import config
from .blob_storage import DocumentStorage
from .cognitive_search import DocumentSearchIndex

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class LegalDocumentChatbot:
    """Main class for the Legal Document Chatbot"""

    def __init__(self, storage=None, search_index=None):
        """Initialize the chatbot with Azure services.

        Dependency injection parameters allow using a mock storage (for
        search-only development) or a pre-built search index instance.
        """
        logger.info("Initializing Legal Document Chatbot...")

        # Always require search configuration (core capability)
        if not config.validate_search_config():
            raise ValueError(
                "Azure Cognitive Search configuration missing. Set AZURE_SEARCH_SERVICE_ENDPOINT and AZURE_SEARCH_API_KEY."
            )

        # Storage: either injected, real, or optional if mock provided
        if storage is not None:
            self.storage = storage
        else:
            if config.validate_storage_config():
                self.storage = DocumentStorage()
            else:
                raise ValueError(
                    "Azure Storage configuration missing. Provide environment vars OR pass a mock storage instance (e.g., MockDocumentStorage)."
                )

        # Search index: injected or created
        self.search_index = search_index or DocumentSearchIndex()

        logger.info("Legal Document Chatbot initialized successfully!")
    
    def _generate_document_id(self, filename: str) -> str:
        """Generate a unique ID for a document"""
        return hashlib.md5(filename.encode()).hexdigest()
    
    def _extract_text_content(self, file_path: str) -> str:
        """
        Extract text content from a document file
        This is a simple implementation - in production, you'd use more sophisticated text extraction
        """
        filename_lower = file_path.lower()
        
        try:
            if filename_lower.endswith('.txt') or filename_lower.endswith('.md'):
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read()
            elif filename_lower.endswith('.pdf'):
                # For PDF files, we'd use PyPDF2 or similar library
                # For now, return a placeholder
                return f"PDF content from {os.path.basename(file_path)} - Content extraction not implemented yet"
            else:
                return f"Content from {os.path.basename(file_path)} - File type not supported for text extraction"
        except Exception as e:
            logger.error(f"Error extracting content from {file_path}: {str(e)}")
            return f"Error extracting content from {os.path.basename(file_path)}"
    
    def upload_and_index_document(self, file_path: str, summary: Optional[str] = None, keywords: Optional[List[str]] = None) -> bool:
        """
        Upload a document to Blob Storage and index it in Cognitive Search
        
        Args:
            file_path: Path to the document file
            summary: Optional summary of the document
            keywords: Optional list of keywords for the document
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Upload to Blob Storage
            blob_name = self.storage.upload_document(file_path)
            
            # Prepare document data for indexing
            filename = os.path.basename(file_path)
            file_extension = os.path.splitext(filename)[1].lower()
            file_size = os.path.getsize(file_path)
            
            document_data = {
                "id": self._generate_document_id(filename),
                "filename": filename,
                "content": self._extract_text_content(file_path),
                "file_type": file_extension,
                "upload_date": datetime.utcnow().isoformat() + "Z",
                "file_size": file_size,
                "blob_url": self.storage.get_document_url(blob_name),
                "summary": summary or f"Legal document: {filename}",
                "keywords": keywords or []
            }
            
            # Index in Cognitive Search
            success = self.search_index.index_document(document_data)
            
            if success:
                logger.info(f"Successfully uploaded and indexed: {filename}")
                return True
            else:
                logger.error(f"Failed to index document: {filename}")
                return False
                
        except Exception as e:
            logger.error(f"Error uploading and indexing {file_path}: {str(e)}")
            return False
    
    def upload_and_index_directory(self, directory_path: str) -> Dict[str, int]:
        """
        Upload and index all documents from a directory
        
        Args:
            directory_path: Path to directory containing documents
            
        Returns:
            Dictionary with success/failure counts
        """
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        results = {"successful": 0, "failed": 0, "skipped": 0}
        supported_extensions = {'.pdf', '.txt', '.doc', '.docx', '.md'}
        
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            
            # Skip directories
            if not os.path.isfile(file_path):
                continue
            
            # Check file extension
            file_extension = os.path.splitext(filename)[1].lower()
            if file_extension not in supported_extensions:
                logger.warning(f"Skipping unsupported file type: {filename}")
                results["skipped"] += 1
                continue
            
            # Upload and index the document
            if self.upload_and_index_document(file_path):
                results["successful"] += 1
            else:
                results["failed"] += 1
        
        logger.info(f"Directory processing complete: {results}")
        return results
    
    def search_documents(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search documents using the provided query
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of search results
        """
        return self.search_index.search_documents(query, top=max_results)
    
    def get_document_info(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific document
        
        Args:
            document_id: The document ID
            
        Returns:
            Document information or None if not found
        """
        return self.search_index.get_document_by_id(document_id)
    
    def list_all_documents(self) -> List[str]:
        """
        List all documents in storage
        
        Returns:
            List of document names
        """
        return self.storage.list_documents()
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the document collection
        
        Returns:
            Dictionary containing statistics
        """
        storage_docs = self.storage.list_documents()
        search_stats = self.search_index.get_index_statistics()
        
        return {
            "blob_storage": {
                "document_count": len(storage_docs),
                "container_name": config.storage_container_name
            },
            "search_index": search_stats
        }


def main():
    """Main entry point for command-line usage"""
    print("Azure Legal Document Chatbot")
    print("=" * 40)
    
    try:
        # Initialize the chatbot
        chatbot = LegalDocumentChatbot()
        
        # Display current statistics
        stats = chatbot.get_statistics()
        print(f"Current Statistics:")
        print(f"  Documents in storage: {stats['blob_storage']['document_count']}")
        print(f"  Documents in search index: {stats['search_index']['document_count']}")
        print()
        
        # Check if sample documents exist
        sample_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sample_documents")
        if os.path.exists(sample_dir) and os.listdir(sample_dir):
            print(f"Found sample documents directory: {sample_dir}")
            print("Uploading and indexing sample documents...")
            
            results = chatbot.upload_and_index_directory(sample_dir)
            print(f"Upload results: {results}")
            print()
        
        # Example search
        print("Example search for 'contract':")
        search_results = chatbot.search_documents("contract", max_results=5)
        for i, doc in enumerate(search_results, 1):
            print(f"  {i}. {doc.get('filename', 'Unknown')} (Score: {doc.get('@search.score', 'N/A'):.2f})")
        
        if not search_results:
            print("  No documents found. Upload some documents first!")
        
        print("\nChatbot initialization completed successfully!")
        
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("Please copy .env.example to .env and fill in your Azure credentials.")
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()