"""
Azure Blob Storage operations for document management
"""
import os
import logging
from typing import Optional, List
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from .config import config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentStorage:
    """Manages document storage operations with Azure Blob Storage"""
    
    def __init__(self):
        if not config.validate_storage_config():
            raise ValueError("Azure Storage configuration is missing. Please check your environment variables.")
        
        self.blob_service_client = BlobServiceClient.from_connection_string(
            config.storage_connection_string
        )
        self.container_name = config.storage_container_name
        self._ensure_container_exists()
    
    def _ensure_container_exists(self):
        """Create the container if it doesn't exist"""
        try:
            self.blob_service_client.create_container(self.container_name)
            logger.info(f"Created container: {self.container_name}")
        except ResourceExistsError:
            logger.info(f"Container already exists: {self.container_name}")
    
    def upload_document(self, file_path: str, blob_name: Optional[str] = None) -> str:
        """
        Upload a document to Azure Blob Storage
        
        Args:
            file_path: Local path to the document
            blob_name: Name for the blob (defaults to filename)
            
        Returns:
            The blob name that was used
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if blob_name is None:
            blob_name = os.path.basename(file_path)
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, 
                blob=blob_name
            )
            
            with open(file_path, 'rb') as data:
                blob_client.upload_blob(data, overwrite=True)
            
            logger.info(f"Successfully uploaded {file_path} as {blob_name}")
            return blob_name
            
        except Exception as e:
            logger.error(f"Failed to upload {file_path}: {str(e)}")
            raise
    
    def upload_documents_from_directory(self, directory_path: str) -> List[str]:
        """
        Upload all documents from a directory to Azure Blob Storage
        
        Args:
            directory_path: Path to directory containing documents
            
        Returns:
            List of uploaded blob names
        """
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        uploaded_blobs = []
        supported_extensions = {'.pdf', '.txt', '.doc', '.docx', '.md'}
        
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            
            # Skip directories and unsupported file types
            if not os.path.isfile(file_path):
                continue
            
            file_extension = os.path.splitext(filename)[1].lower()
            if file_extension not in supported_extensions:
                logger.warning(f"Skipping unsupported file type: {filename}")
                continue
            
            try:
                blob_name = self.upload_document(file_path)
                uploaded_blobs.append(blob_name)
            except Exception as e:
                logger.error(f"Failed to upload {filename}: {str(e)}")
        
        logger.info(f"Successfully uploaded {len(uploaded_blobs)} documents")
        return uploaded_blobs
    
    def list_documents(self) -> List[str]:
        """
        List all documents in the container
        
        Returns:
            List of blob names
        """
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            blob_list = container_client.list_blobs()
            return [blob.name for blob in blob_list]
        except Exception as e:
            logger.error(f"Failed to list documents: {str(e)}")
            raise
    
    def get_document_url(self, blob_name: str) -> str:
        """
        Get the URL for a document
        
        Args:
            blob_name: Name of the blob
            
        Returns:
            URL to access the document
        """
        blob_client = self.blob_service_client.get_blob_client(
            container=self.container_name, 
            blob=blob_name
        )
        return blob_client.url
    
    def download_document(self, blob_name: str, download_path: str) -> str:
        """
        Download a document from Azure Blob Storage
        
        Args:
            blob_name: Name of the blob to download
            download_path: Local path to save the document
            
        Returns:
            Path where the document was saved
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, 
                blob=blob_name
            )
            
            with open(download_path, 'wb') as download_file:
                download_file.write(blob_client.download_blob().readall())
            
            logger.info(f"Successfully downloaded {blob_name} to {download_path}")
            return download_path
            
        except ResourceNotFoundError:
            logger.error(f"Document not found: {blob_name}")
            raise
        except Exception as e:
            logger.error(f"Failed to download {blob_name}: {str(e)}")
            raise