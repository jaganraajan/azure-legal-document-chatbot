#!/bin/bash

# Azure Legal Document Chatbot - Quick Start Script

echo "Azure Legal Document Chatbot - Quick Start"
echo "==========================================="
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Configuration file (.env) not found!"
    echo "   Please copy .env.example to .env and fill in your Azure credentials:"
    echo "   cp .env.example .env"
    echo ""
    echo "   Required credentials:"
    echo "   - AZURE_STORAGE_CONNECTION_STRING"
    echo "   - AZURE_SEARCH_SERVICE_ENDPOINT" 
    echo "   - AZURE_SEARCH_API_KEY"
    echo ""
    exit 1
fi

# Check if Python dependencies are installed
echo "📦 Checking dependencies..."
python -c "import azure.storage.blob, azure.search.documents" 2>/dev/null || {
    echo "❌ Missing dependencies. Installing..."
    pip install -r requirements.txt
}

echo "✅ Dependencies are installed"
echo ""

# Run the application
echo "🚀 Starting Azure Legal Document Chatbot..."
echo ""
python -m src.main