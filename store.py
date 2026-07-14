"""
Remembers which jobs you've already been emailed so you never get
the same listing twice. The seen.json file is committed back to the
repo by the GitHub Action after each run.
"""
import json
import os
import config


def load_seen():
    if not os.path.exists(config.SEEN_FILE):
        return set()
    try:
        with open(config.SEEN_FILE) as f:
            return set(json.load(f))
    except Exception:
        return set()


def save_seen(ids):
    # keep the most recent ~4000 ids so the file stays small
    ids = list(ids)[-4000:]
    with open(config.SEEN_FILE, "w") as f:
        json.dump(ids, f)
