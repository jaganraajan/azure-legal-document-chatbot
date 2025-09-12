"""Standalone script to experiment with Azure Cognitive (AI) Search without Blob Storage.

Loads local `.txt` and `.md` files from the `sample_documents` directory (or a
provided path) and pushes them directly into a simple index. Then runs a couple
of sample queries. This bypasses Azure Blob Storage so you can iterate on index
design, analyzers, and relevance quickly.

Usage (environment variables required):
  AZURE_SEARCH_SERVICE_ENDPOINT=https://<service>.search.windows.net \
  AZURE_SEARCH_API_KEY=<key> \
  python scripts/search_only_demo.py [optional_path]
"""
from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path
from dotenv import load_dotenv

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchFieldDataType,
)
from azure.search.documents import SearchClient


def env(name: str, required: bool = True, default: str | None = None) -> str:
    val = os.getenv(name, default)
    if required and not val:
        raise SystemExit(f"Missing required environment variable: {name}")
    return val  # type: ignore


def ensure_index(index_client: SearchIndexClient, index_name: str):
    try:
        index_client.get_index(index_name)
        print(f"Index '{index_name}' already exists.")
    except Exception:
        print(f"Creating index '{index_name}' ...")
        index = SearchIndex(
            name=index_name,
            fields=[
                SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                # SearchableField(name="filename", type=SearchFieldDataType.String, sortable=True, filterable=True),
                # SearchableField(name="content", type=SearchFieldDataType.String, analyzer_name="en.lucene"),
                # SearchableField(name="summary", type=SearchFieldDataType.String),
                # SearchableField(
                #     name="keywords",
                #     type=SearchFieldDataType.Collection(SearchFieldDataType.String),
                #     collection=True,
                #     filterable=True,
                #     facetable=True,
                # ),
            ],
        )
        index_client.create_index(index)
        print("Index created.")


def load_local_documents(dir_path: Path):
    exts = {".txt", ".md"}
    for p in dir_path.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except Exception as e:  # pragma: no cover - unlikely with utf-8 legal samples
                print(f"Skip {p.name}: {e}")
                continue
            yield {
                "id": str(uuid.uuid4()),
                # "filename": p.name,
                # "content": text,
                # "summary": None,
                # "keywords": [],
            }


def upload_docs(search_client: SearchClient, docs):
    docs_list = list(docs)
    if not docs_list:
        print("No documents to upload.")
        return
    results = search_client.upload_documents(docs_list)
    failures = [r for r in results if not r.succeeded]
    print(f"Uploaded {len(docs_list) - len(failures)}/{len(docs_list)} documents.")
    if failures:
        print(f"Failures: {len(failures)}")


def run_query(search_client: SearchClient, query: str, top: int = 5):
    print(f"\nQuery: {query}")
    results = search_client.search(query, top=top)
    for r in results:
        score = r.get("@search.score")
        print(f"- {r.get('filename')} (score={score:.2f})")


def main():
    load_dotenv()

    endpoint = env("AZURE_SEARCH_SERVICE_ENDPOINT")
    api_key = env("AZURE_SEARCH_API_KEY")
    index_name = os.getenv("AZURE_SEARCH_INDEX_NAME", "legal-documents-index")

    credential = AzureKeyCredential(api_key)
    index_client = SearchIndexClient(endpoint=endpoint, credential=credential)
    ensure_index(index_client, index_name)
    search_client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)

    # Determine directory
    if len(sys.argv) > 1:
        docs_dir = Path(sys.argv[1])
    else:
        docs_dir = Path(__file__).resolve().parents[1] / "sample_documents"
    print(f"Using documents from: {docs_dir}")
    if not docs_dir.exists():
        print("Directory does not exist. Exiting.")
        return

    upload_docs(search_client, load_local_documents(docs_dir))

    # Example queries
    run_query(search_client, "contract termination clause")
    run_query(search_client, "non disclosure agreement")

    print("\nDone.")


if __name__ == "__main__":  # pragma: no cover
    main()
