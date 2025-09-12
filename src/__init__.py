"""
Azure Legal Document Chatbot

A simple application that uses Azure Blob Storage to store documents
and Azure Cognitive Search to index and search through them.
"""

from .main import LegalDocumentChatbot
from .blob_storage import DocumentStorage
from .cognitive_search import DocumentSearchIndex
from .mock_storage import MockDocumentStorage  # optional helper
from .config import config

__version__ = "1.0.0"
__author__ = "Azure Legal Document Chatbot"

__all__ = [
    "LegalDocumentChatbot",
    "DocumentStorage", 
    "DocumentSearchIndex",
    "config",
    "MockDocumentStorage"
]