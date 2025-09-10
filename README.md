# Azure Legal Document Chatbot

A simple Python application that demonstrates how to use Azure Blob Storage to store legal documents and Azure Cognitive Search to index and search through them. This project provides a foundation for building document management systems with powerful search capabilities.

## Features

- 📄 **Document Storage**: Upload documents to Azure Blob Storage
- 🔍 **Document Indexing**: Automatically index documents using Azure Cognitive Search
- 🔎 **Full-text Search**: Search through document content, filenames, and metadata
- 📊 **Document Management**: List, retrieve, and manage stored documents
- 🏷️ **Metadata Support**: Add summaries and keywords to documents
- 📁 **Batch Processing**: Upload and index entire directories of documents

## Architecture

```
Local Documents → Azure Blob Storage → Azure Cognitive Search
      ↓                    ↓                      ↓
  File Upload          Document Storage      Search Index
  Text Extraction      Secure Access         Full-text Search
  Metadata             URL Generation        Faceted Search
```

## Prerequisites

Before you begin, ensure you have:

1. **Python 3.7+** installed
2. **Azure Subscription** with access to:
   - Azure Blob Storage
   - Azure Cognitive Search
3. **Azure Storage Account** created
4. **Azure Cognitive Search Service** created

## Installation

1. **Clone the repository**:
```bash
git clone https://github.com/jaganraajan/azure-legal-document-chatbot.git
cd azure-legal-document-chatbot
```

2. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure Azure credentials**:
```bash
cp .env.example .env
```

Edit the `.env` file with your Azure credentials:
```bash
# Azure Storage Configuration
AZURE_STORAGE_CONNECTION_STRING=your_storage_connection_string_here
AZURE_STORAGE_CONTAINER_NAME=legal-documents

# Azure Cognitive Search Configuration
AZURE_SEARCH_SERVICE_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_API_KEY=your_search_api_key_here
AZURE_SEARCH_INDEX_NAME=legal-documents-index
```

## Usage

### Command Line Interface

Run the main application:
```bash
python -m src.main
```

This will:
- Initialize the Azure services
- Create necessary containers and search indexes
- Upload and index sample documents (if available)
- Display current statistics

### Programmatic Usage

```python
from src import LegalDocumentChatbot

# Initialize the chatbot
chatbot = LegalDocumentChatbot()

# Upload and index a single document
success = chatbot.upload_and_index_document(
    file_path="path/to/document.pdf",
    summary="Legal contract for services",
    keywords=["contract", "services", "legal"]
)

# Upload and index all documents in a directory
results = chatbot.upload_and_index_directory("sample_documents/")
print(f"Processed: {results}")

# Search documents
search_results = chatbot.search_documents("contract terms", max_results=5)
for doc in search_results:
    print(f"Found: {doc['filename']} (Score: {doc['@search.score']:.2f})")

# Get statistics
stats = chatbot.get_statistics()
print(f"Total documents: {stats['search_index']['document_count']}")
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AZURE_STORAGE_CONNECTION_STRING` | Azure Storage connection string | Yes |
| `AZURE_STORAGE_CONTAINER_NAME` | Container name for documents | No (default: legal-documents) |
| `AZURE_SEARCH_SERVICE_ENDPOINT` | Cognitive Search service URL | Yes |
| `AZURE_SEARCH_API_KEY` | Cognitive Search API key | Yes |
| `AZURE_SEARCH_INDEX_NAME` | Search index name | No (default: legal-documents-index) |

### Supported File Types

- `.txt` - Plain text files
- `.md` - Markdown files
- `.pdf` - PDF documents (basic support)
- `.doc` / `.docx` - Word documents (planned)

## Sample Documents

The project includes sample legal documents in the `sample_documents/` directory:

- `software_license_agreement.txt` - Software license agreement template
- `employment_contract.txt` - Employment contract template
- `nda_agreement.txt` - Non-disclosure agreement template
- `terms_of_service.md` - Terms of service template

## API Reference

### LegalDocumentChatbot

Main class for document management operations.

#### Methods

- `upload_and_index_document(file_path, summary=None, keywords=None)` - Upload and index a single document
- `upload_and_index_directory(directory_path)` - Process all documents in a directory
- `search_documents(query, max_results=10)` - Search documents by query
- `get_document_info(document_id)` - Get information about a specific document
- `list_all_documents()` - List all stored documents
- `get_statistics()` - Get storage and index statistics

### DocumentStorage

Handles Azure Blob Storage operations.

#### Methods

- `upload_document(file_path, blob_name=None)` - Upload a document
- `list_documents()` - List all documents
- `get_document_url(blob_name)` - Get document URL
- `download_document(blob_name, download_path)` - Download a document

### DocumentSearchIndex

Manages Azure Cognitive Search operations.

#### Methods

- `index_document(document_data)` - Index a single document
- `search_documents(query, top=10)` - Search documents
- `get_document_by_id(document_id)` - Retrieve document by ID
- `delete_document(document_id)` - Delete a document from index

## Troubleshooting

### Common Issues

1. **Configuration Errors**:
   - Verify your `.env` file has correct Azure credentials
   - Check that your Azure services are properly configured

2. **Connection Issues**:
   - Ensure your Azure Storage connection string is correct
   - Verify your Cognitive Search endpoint and API key

3. **File Upload Failures**:
   - Check file permissions and paths
   - Verify supported file types

4. **Search Issues**:
   - Allow time for documents to be indexed
   - Check search index exists and is populated

### Getting Help

1. Check the application logs for detailed error messages
2. Verify your Azure service configurations
3. Ensure all required dependencies are installed

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Commit your changes: `git commit -am 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Resources

- [Azure Blob Storage Documentation](https://docs.microsoft.com/en-us/azure/storage/blobs/)
- [Azure Cognitive Search Documentation](https://docs.microsoft.com/en-us/azure/search/)
- [Azure SDK for Python](https://docs.microsoft.com/en-us/azure/developer/python/)