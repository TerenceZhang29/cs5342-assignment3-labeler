"""
Collect real candidate posts from Bluesky for annotation.

Searches public posts for scam-adjacent queries and writes them in data.csv's schema with
`expected_label` left blank, so annotators can label them and append them to data.csv.
Post text is stored at collection time because real posts can be deleted later, which would
otherwise break reproducibility.

Requires a Bluesky login in .env (USERNAME / PW — use an app password). Search is not
available to logged-out clients.

Usage:
    python collect_posts.py --out candidates.csv --per-query 50
    python collect_posts.py --queries "airdrop claim" "seed phrase" --out more.csv

Safety (course policy): we only store public post text/metadata; we never open the linked
sites — domains are recorded as text only.
"""

import argparse
import csv
import json
import os
from typing import Dict, Iterable, List

from atproto import Client
from dotenv import load_dotenv

DEFAULT_QUERIES = [
    "airdrop claim", "airdrop live", "free airdrop", "crypto giveaway", "eth giveaway",
    "btc giveaway", "send eth receive", "double your crypto", "seed phrase",
    "recovery phrase", "connect wallet claim", "claim tokens", "airdrop scam",
    "verification fee crypto", "usdt giveaway", "free nft mint",
]

FIELDS = ["id", "split", "source", "post_url", "author_handle", "author_display_name",
          "author_created_at", "post_created_at", "text", "links", "expected_label",
          "category", "rationale", "annotation_status"]


def post_url(handle: str, at_uri: str) -> str:
    """at://did/app.bsky.feed.post/rkey -> https://bsky.app/profile/handle/post/rkey"""
    return f"https://bsky.app/profile/{handle}/post/{at_uri.rsplit('/', 1)[-1]}"


def links_of(record) -> List[str]:
    """Links from facets and link-card embeds of a post record."""
    links = []
    for facet in getattr(record, "facets", None) or []:
        for feature in getattr(facet, "features", None) or []:
            if getattr(feature, "uri", None):
                links.append(feature.uri)
    embed = getattr(record, "embed", None)
    external = getattr(embed, "external", None)
    if external is not None and getattr(external, "uri", None):
        links.append(external.uri)
    return links


def account_created_at(client: Client, dids: Iterable[str]) -> Dict[str, str]:
    """Look up account creation dates in batches of 25 (getProfiles limit)."""
    dids = list(dict.fromkeys(dids))
    created: Dict[str, str] = {}
    for i in range(0, len(dids), 25):
        response = client.app.bsky.actor.get_profiles({"actors": dids[i:i + 25]})
        for profile in response.profiles:
            created[profile.did] = getattr(profile, "created_at", "") or ""
    return created


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--out", default="candidates.csv")
    parser.add_argument("--per-query", type=int, default=50, help="max posts per query (<=100)")
    parser.add_argument("--queries", nargs="*", default=DEFAULT_QUERIES)
    args = parser.parse_args()

    load_dotenv(override=True)
    client = Client()
    client.login(os.getenv("USERNAME"), os.getenv("PW"))

    seen, rows = set(), []
    for query in args.queries:
        response = client.app.bsky.feed.search_posts({"q": query, "limit": min(args.per_query, 100)})
        for post in response.posts:
            if post.uri in seen:
                continue
            seen.add(post.uri)
            rows.append({
                "uri": post.uri, "did": post.author.did, "handle": post.author.handle,
                "display": post.author.display_name or "", "created": post.record.created_at,
                "text": post.record.text, "links": links_of(post.record), "query": query,
            })
        print(f"{query!r}: {len(response.posts)} posts")

    created = account_created_at(client, [r["did"] for r in rows])
    with open(args.out, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for i, row in enumerate(rows, 1):
            writer.writerow({
                "id": f"r{i:03d}", "split": "", "source": "real",
                "post_url": post_url(row["handle"], row["uri"]),
                "author_handle": row["handle"], "author_display_name": row["display"],
                "author_created_at": created.get(row["did"], ""),
                "post_created_at": row["created"], "text": row["text"],
                "links": json.dumps(row["links"]), "expected_label": "",
                "category": "", "rationale": f"search: {row['query']}",
                "annotation_status": "needs-annotation",
            })
    print(f"Wrote {len(rows)} candidates to {args.out}")


if __name__ == "__main__":
    main()
