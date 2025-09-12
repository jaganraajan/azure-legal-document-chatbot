"""Mock storage implementation for search-only scenarios.

Provides a minimal drop-in replacement for `DocumentStorage` so that the
`LegalDocumentChatbot` can be used (or partially used) without configuring
Azure Blob Storage. Useful for local development and Azure Cognitive Search
schema / query experimentation.
"""
from __future__ import annotations

import os
from typing import List


class MockDocumentStorage:
    """A lightweight in-memory / no-op storage implementation.

    Methods mirror the interface of `DocumentStorage` used by the chatbot.
    Uploaded documents are not persisted; only the blob name is returned.
    """

    def __init__(self, base_url: str = "https://mock-storage.local/"):
        self.base_url = base_url.rstrip('/') + '/'
        self._documents: List[str] = []

    def upload_document(self, file_path: str, blob_name: str | None = None) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)
        if blob_name is None:
            blob_name = os.path.basename(file_path)
        # Track the name so list_documents works
        if blob_name not in self._documents:
            self._documents.append(blob_name)
        return blob_name

    def list_documents(self) -> List[str]:
        return list(self._documents)

    def get_document_url(self, blob_name: str) -> str:
        return f"{self.base_url}{blob_name}"

    # Optional parity method (not used by chatbot directly)
    def upload_documents_from_directory(self, directory_path: str) -> List[str]:
        uploaded = []
        if not os.path.isdir(directory_path):
            raise FileNotFoundError(directory_path)
        for name in os.listdir(directory_path):
            path = os.path.join(directory_path, name)
            if os.path.isfile(path):
                try:
                    uploaded.append(self.upload_document(path))
                except Exception:
                    pass
        return uploaded
