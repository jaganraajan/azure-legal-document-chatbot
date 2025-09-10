"""
Azure Cognitive Search operations for document indexing
"""
import logging
from typing import List, Dict, Any, Optional
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchFieldDataType,
    ComplexField,
    CorsOptions
)
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from .config import config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentSearchIndex:
    """Manages document indexing operations with Azure Cognitive Search"""
    
    def __init__(self):
        if not config.validate_search_config():
            raise ValueError("Azure Cognitive Search configuration is missing. Please check your environment variables.")
        
        self.service_endpoint = config.search_service_endpoint
        self.api_key = config.search_api_key
        self.index_name = config.search_index_name
        
        # Initialize clients
        self.credential = AzureKeyCredential(self.api_key)
        self.index_client = SearchIndexClient(
            endpoint=self.service_endpoint,
            credential=self.credential
        )
        self.search_client = SearchClient(
            endpoint=self.service_endpoint,
            index_name=self.index_name,
            credential=self.credential
        )
        
        # Ensure the index exists
        self._ensure_index_exists()
    
    def _create_search_index(self) -> SearchIndex:
        """Create the search index schema for legal documents"""
        fields = [
            SimpleField(
                name="id",
                type=SearchFieldDataType.String,
                key=True,
                sortable=True
            ),
            SearchableField(
                name="filename",
                type=SearchFieldDataType.String,
                sortable=True,
                filterable=True
            ),
            SearchableField(
                name="content",
                type=SearchFieldDataType.String,
                searchable=True,
                analyzer_name="en.lucene"
            ),
            SimpleField(
                name="file_type",
                type=SearchFieldDataType.String,
                filterable=True,
                facetable=True
            ),
            SimpleField(
                name="upload_date",
                type=SearchFieldDataType.DateTimeOffset,
                sortable=True,
                filterable=True
            ),
            SimpleField(
                name="file_size",
                type=SearchFieldDataType.Int64,
                sortable=True,
                filterable=True
            ),
            SimpleField(
                name="blob_url",
                type=SearchFieldDataType.String,
                retrievable=True
            ),
            SearchableField(
                name="summary",
                type=SearchFieldDataType.String,
                searchable=True
            ),
            SearchableField(
                name="keywords",
                type=SearchFieldDataType.Collection(SearchFieldDataType.String),
                searchable=True,
                filterable=True,
                facetable=True
            )
        ]
        
        # Configure CORS for web applications
        cors_options = CorsOptions(
            allowed_origins=["*"],
            max_age_in_seconds=300
        )
        
        return SearchIndex(
            name=self.index_name,
            fields=fields,
            cors_options=cors_options
        )
    
    def _ensure_index_exists(self):
        """Create the search index if it doesn't exist"""
        try:
            index = self._create_search_index()
            result = self.index_client.create_index(index)
            logger.info(f"Created search index: {self.index_name}")
        except ResourceExistsError:
            logger.info(f"Search index already exists: {self.index_name}")
        except Exception as e:
            logger.error(f"Failed to create search index: {str(e)}")
            raise
    
    def index_document(self, document_data: Dict[str, Any]) -> bool:
        """
        Index a single document
        
        Args:
            document_data: Dictionary containing document data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure required fields are present
            required_fields = ['id', 'filename', 'content']
            for field in required_fields:
                if field not in document_data:
                    raise ValueError(f"Required field '{field}' is missing from document data")
            
            result = self.search_client.upload_documents([document_data])
            
            if result and len(result) > 0 and result[0].succeeded:
                logger.info(f"Successfully indexed document: {document_data['filename']}")
                return True
            else:
                logger.error(f"Failed to index document: {document_data['filename']}")
                return False
                
        except Exception as e:
            logger.error(f"Error indexing document {document_data.get('filename', 'unknown')}: {str(e)}")
            return False
    
    def index_documents_batch(self, documents_data: List[Dict[str, Any]]) -> int:
        """
        Index multiple documents in batch
        
        Args:
            documents_data: List of dictionaries containing document data
            
        Returns:
            Number of successfully indexed documents
        """
        if not documents_data:
            return 0
        
        try:
            results = self.search_client.upload_documents(documents_data)
            success_count = sum(1 for result in results if result.succeeded)
            
            logger.info(f"Successfully indexed {success_count}/{len(documents_data)} documents")
            return success_count
            
        except Exception as e:
            logger.error(f"Error batch indexing documents: {str(e)}")
            return 0
    
    def search_documents(self, 
                        query: str, 
                        top: int = 10,
                        select: Optional[List[str]] = None,
                        filter_expression: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search documents using the provided query
        
        Args:
            query: Search query string
            top: Maximum number of results to return
            select: List of fields to return (None for all)
            filter_expression: OData filter expression
            
        Returns:
            List of search results
        """
        try:
            results = self.search_client.search(
                search_text=query,
                top=top,
                select=select,
                filter=filter_expression,
                include_total_count=True
            )
            
            documents = []
            for result in results:
                documents.append(dict(result))
            
            logger.info(f"Found {len(documents)} documents for query: '{query}'")
            return documents
            
        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []
    
    def get_document_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a document by its ID
        
        Args:
            document_id: The document ID
            
        Returns:
            Document data or None if not found
        """
        try:
            result = self.search_client.get_document(document_id)
            return dict(result)
        except ResourceNotFoundError:
            logger.warning(f"Document not found: {document_id}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving document {document_id}: {str(e)}")
            return None
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document from the search index
        
        Args:
            document_id: The document ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.search_client.delete_documents([{"id": document_id}])
            
            if result and len(result) > 0 and result[0].succeeded:
                logger.info(f"Successfully deleted document: {document_id}")
                return True
            else:
                logger.error(f"Failed to delete document: {document_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {str(e)}")
            return False
    
    def get_index_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the search index
        
        Returns:
            Dictionary containing index statistics
        """
        try:
            stats = self.search_client.get_document_count()
            return {
                "document_count": stats,
                "index_name": self.index_name
            }
        except Exception as e:
            logger.error(f"Error getting index statistics: {str(e)}")
            return {"document_count": 0, "index_name": self.index_name}