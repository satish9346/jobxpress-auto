"""
JobXpress — nightly auto-pipeline.

Flow:  fetch -> dedupe -> score (Claude) -> email briefing -> remember.
Run locally with:  python main.py
Or let GitHub Actions run it every night (see .github/workflows/daily.yml).
"""
import sys
import config
import sources
import store
import scorer
import emailer
from profile import SEARCHES, RSS_FEEDS


def main():
    missing = config.missing_keys()
    if missing:
        print("Missing secrets: " + ", ".join(missing))
        print("Set them as environment variables / GitHub Actions secrets. See README.")
        sys.exit(1)

    print("1) Fetching jobs…")
    found = sources.gather(SEARCHES, RSS_FEEDS)
    print(f"   {len(found)} unique listings pulled.")

    seen = store.load_seen()
    fresh = [j for j in found if j["id"] not in seen][: config.MAX_NEW_JOBS]
    print(f"2) {len(fresh)} are new (cap {config.MAX_NEW_JOBS}). Scoring with {config.MODEL}…")

    matches = []
    for i, j in enumerate(fresh, 1):
        a = scorer.score(j)
        if not a:
            continue
        j["analysis"] = a
        flag = "★" if a["fit_score"] >= 75 else " "
        print(f"   {flag} {a['fit_score']:>3}%  {a['recommended_profile'][:2]}  {j['title'][:48]}")
        if a["fit_score"] >= config.MIN_FIT_EMAIL:
            matches.append(j)

    matches.sort(key=lambda x: x["analysis"]["fit_score"], reverse=True)

    # Tailored resume for the top matches above the threshold
    to_tailor = [m for m in matches
                 if m["analysis"]["fit_score"] >= config.TAILOR_FIT][: config.MAX_TAILORED]
    print(f"3) Tailoring resumes for {len(to_tailor)} top matches…")
    for m in to_tailor:
        m["tailored_resume"] = scorer.tailor_resume(m, m["analysis"])
        if m["tailored_resume"]:
            print(f"   resume tailored: {m['title'][:48]}")

    stats = {
        "new": len(matches),
        "top": sum(1 for m in matches if m["analysis"]["fit_score"] >= 75),
        "scanned": len(found),
    }

    print(f"4) Emailing {len(matches)} matches…")
    emailer.send(matches, stats)

    # remember everything we fetched so nothing repeats
    store.save_seen(seen | {j["id"] for j in fresh})
    print("Done.")


if __name__ == "__main__":
    main()
