"""Flask UI to display scraped Reddit thread comments.

Runs a simple web interface that loads `reddit_thread_data.json` (or a file
specified via the REDDIT_JSON_PATH environment variable) and shows the
submission metadata plus a scrollable comments section.

Usage:
  export FLASK_APP=app.py
  flask run --reload
    or
  python app.py  (uses built-in dev server)

Environment variables:
  REDDIT_JSON_PATH   Path to the JSON file (default: reddit_thread_data.json)
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

from flask import Flask, render_template, jsonify

APP_ROOT = Path(__file__).parent
DEFAULT_JSON = APP_ROOT / "reddit_thread_data.json"

app = Flask(__name__, template_folder=str(APP_ROOT / "templates"), static_folder=str(APP_ROOT / "static"))


def load_thread_data() -> Dict[str, Any]:
    json_path = Path(os.getenv("REDDIT_JSON_PATH", str(DEFAULT_JSON)))
    if not json_path.exists():
        return {
            "title": "No data",
            "selftext": "File not found: " + str(json_path),
            "comments": [],
            "num_comments_scraped": 0,
        }
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:  # pragma: no cover - defensive
        return {
            "title": "Error loading data",
            "selftext": str(e),
            "comments": [],
            "num_comments_scraped": 0,
        }


@app.route("/")
def index():
    data = load_thread_data()
    return render_template("index.html", thread=data, comments=data.get("comments", []))


@app.route("/api/comments")
def api_comments():
    data = load_thread_data()
    return jsonify({
        "title": data.get("title"),
        "count": data.get("num_comments_scraped", len(data.get("comments", []))),
        "comments": data.get("comments", []),
    })


if __name__ == "__main__":
    app.run(debug=True)
