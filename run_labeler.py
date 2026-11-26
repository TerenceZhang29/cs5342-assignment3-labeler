"""
Live runner: label real Bluesky posts by URL (adapted from the starter's test_labeler.py).

Input is a CSV with a `URL` column and an optional `Labels` column holding the expected
labels as a JSON list (same format as the starter's test-data files), e.g.

    URL,Labels
    https://bsky.app/profile/someone.bsky.social/post/3abc...,["crypto-scam"]
    https://bsky.app/profile/other.bsky.social/post/3def...,[]

Requires USERNAME / PW in .env (see .env-TEMPLATE). Labels are only published to Bluesky
when --emit_labels is passed (needs the account to be set up as a labeler).

Usage:
    python run_labeler.py labeler-inputs live-posts.csv
    python run_labeler.py labeler-inputs live-posts.csv --emit_labels
"""

import argparse
import json
import os
import time

import pandas as pd
from atproto import Client
from dotenv import load_dotenv

from pylabel import PolicyProposalLabeler
from pylabel.label import did_from_handle, label_post


def main() -> None:
    parser = argparse.ArgumentParser(description="Label live Bluesky posts by URL.")
    parser.add_argument("labeler_inputs_dir", type=str)
    parser.add_argument("input_urls", type=str)
    parser.add_argument("--emit_labels", action="store_true",
                        help="publish labels to Bluesky (outward-facing; off by default)")
    parser.add_argument("--review-queue", default="review_queue.jsonl",
                        help="where to append Ozone-style review entries")
    parser.add_argument("--no-expand", action="store_true",
                        help="do not follow URL-shortener redirects")
    args = parser.parse_args()

    load_dotenv(override=True)
    client = Client()
    client.login(os.getenv("USERNAME"), os.getenv("PW"))
    labeler_client = None
    if args.emit_labels:
        labeler_client = client.with_proxy("atproto_labeler", did_from_handle(os.getenv("USERNAME")))

    labeler = PolicyProposalLabeler(client, args.labeler_inputs_dir,
                                    expand_links=not args.no_expand,
                                    review_queue_path=args.review_queue)
    urls = pd.read_csv(args.input_urls)
    has_expected = "Labels" in urls.columns
    num_correct, latencies = 0, []
    for _, row in urls.iterrows():
        start = time.perf_counter()
        labels = labeler.moderate_post(row["URL"])
        latencies.append(time.perf_counter() - start)
        line = f"{labels!s:<24} {row['URL']}"
        if has_expected:
            expected = json.loads(row["Labels"])
            correct = sorted(labels) == sorted(expected)
            num_correct += correct
            line += "" if correct else f"   (expected {expected})"
        print(line)
        if args.emit_labels and labels:
            label_post(client, labeler_client, row["URL"], labels)

    total = len(urls)
    if has_expected and total:
        print(f"\nThe labeler produced {num_correct} correct label assignments out of {total}")
        print(f"Overall ratio of correct label assignments {num_correct / total:.3f}")
    if latencies:
        print(f"Mean time per post (incl. network): {1000 * sum(latencies) / len(latencies):.0f} ms; "
              f"network calls: {labeler.network_calls}")


if __name__ == "__main__":
    main()
