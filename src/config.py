"""
Configuration management for Azure Legal Document Chatbot
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class Config:
    """Configuration class for Azure services"""
    
    def __init__(self):
        # Azure Storage Configuration
        self.storage_connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        self.storage_container_name = os.getenv('AZURE_STORAGE_CONTAINER_NAME', 'legal-documents')
        
        # Azure Cognitive Search Configuration
        self.search_service_endpoint = os.getenv('AZURE_SEARCH_SERVICE_ENDPOINT')
        self.search_api_key = os.getenv('AZURE_SEARCH_API_KEY')
        self.search_index_name = os.getenv('AZURE_SEARCH_INDEX_NAME', 'legal-documents-index')
        
        # Optional Azure AD Configuration
        self.client_id = os.getenv('AZURE_CLIENT_ID')
        self.client_secret = os.getenv('AZURE_CLIENT_SECRET')
        self.tenant_id = os.getenv('AZURE_TENANT_ID')
    
    def validate_storage_config(self) -> bool:
        """Validate Azure Storage configuration"""
        return bool(self.storage_connection_string)
    
    def validate_search_config(self) -> bool:
        """Validate Azure Cognitive Search configuration"""
        return bool(self.search_service_endpoint and self.search_api_key)
    
    def validate_all_config(self) -> bool:
        """Validate all required configuration"""
        return self.validate_storage_config() and self.validate_search_config()


# Global configuration instance
config = Config()