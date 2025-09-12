"""Reddit thread scraper: fetch submission + all comments and save as JSON.

Usage:
  python scripts/reddit_scraper.py \
      --url https://www.reddit.com/r/SomeSub/comments/abcdef/sample_thread/ \
      --output reddit_thread_data.json \
      --max-comments 1000

Environment variables (recommended instead of hard‑coding):
  REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT

Notes:
  - Rotating any previously committed secrets is strongly advised.
  - By default all comments are fetched (replace_more(limit=None)). Use
    --max-comments to truncate for quicker experiments.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Any
from dotenv import load_dotenv

import praw
from praw.models import Comment


def build_reddit_client():
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT")

    print(f"User agent: {user_agent}")
    print(f"client id: {client_id}")
    if not (client_id and client_secret):
        raise SystemExit(
            "Missing Reddit credentials. Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET env vars."
        )

    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
        ratelimit_seconds=5,
    )


def flatten_comments(submission, max_comments: int | None = None) -> List[Dict[str, Any]]:
    # submission.comments.replace_more(limit=None)
    flat: List[Dict[str, Any]] = []
    for idx, c in enumerate(submission.comments.list()):
        if max_comments is not None and idx >= max_comments:
            break
        if not isinstance(c, Comment):
            continue
        flat.append(
            {
                "id": c.id,
                "parent_id": c.parent_id,
                "author": str(c.author) if c.author else None,
                "body": c.body,
                "score": c.score,
                "created_utc": c.created_utc,
                "permalink": f"https://www.reddit.com{c.permalink}",
                "depth": getattr(c, "depth", None),
            }
        )
    return flat


def scrape_thread(url: str, max_comments: int | None = None) -> Dict[str, Any]:
    reddit = build_reddit_client()
    submission = reddit.submission(url=url)
    print(f"Fetched submission: {submission.title} (id: {submission.id})")
    submission_data = {
        "id": submission.id,
        "url": url,
        "title": submission.title,
        "selftext": submission.selftext,
        "score": submission.score,
        "subreddit": str(submission.subreddit),
        "num_comments_reported": submission.num_comments,
        "created_utc": submission.created_utc,
        "scraped_at_utc": datetime.now(tz=timezone.utc).isoformat(),
    }
    comments = flatten_comments(submission, max_comments=max_comments)
    submission_data["comments"] = comments
    submission_data["num_comments_scraped"] = len(comments)
    return submission_data


def save_json(data: Dict[str, Any], path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():  # pragma: no cover - CLI routine
    load_dotenv()
    # args = parse_args()
    url = "https://www.reddit.com/r/ImmigrationCanada/comments/1hpzygp/megathread_processing_times_pr_cards_2025/?"

    print(f"Scraping: {url}")
    data = scrape_thread(url, 10)
    save_json(data, "reddit_thread_data.json")
    print(
        f"Saved {data['num_comments_scraped']} comments (reported: {data['num_comments_reported']}) to reddit_thread_data.json"
    )


if __name__ == "__main__":
    main()