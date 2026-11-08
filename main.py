"""
JobXpress — nightly auto-pipeline.

Flow:  fetch -> dedupe -> score (Claude) -> tailor -> email + track -> remember.
Run locally with:  python main.py
Or let GitHub Actions run it every night (see .github/workflows/daily.yml).
"""
import sys
import config
import sources
import store
import scorer
import emailer
import tracker
import resume_agent
from profile import SEARCHES, RSS_FEEDS


def _priority(m):
    """Sort key: student-priority roles first, then by fit score."""
    a = m["analysis"]
    cat = a.get("category", "Job").lower()
    is_pri = a.get("student_priority") or any(t in cat for t in config.PRIORITY_TYPES)
    return (1 if is_pri else 0, a.get("fit_score", 0))


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

    # ---------- FREE MODE: no AI, just email the new listings ----------
    if config.FREE_MODE:
        print(f"2) FREE MODE — skipping AI. Emailing {len(fresh)} new listings…")
        emailer.send_free(fresh, {"new": len(fresh), "scanned": len(found)})
        tracker.append_free(fresh)
        store.save_seen(seen | {j["id"] for j in fresh})
        print("Done (free mode).")
        return

    print(f"2) {len(fresh)} are new (cap {config.MAX_NEW_JOBS}). Scoring with {config.MODEL}…")

    matches = []
    for j in fresh:
        a = scorer.score(j)
        if not a:
            continue
        j["analysis"] = a
        pri = "P" if a.get("student_priority") else " "
        flag = "★" if a["fit_score"] >= 75 else " "
        print(f"   {pri}{flag} {a['fit_score']:>3}%  {a['recommended_profile'][:2]}  {j['title'][:46]}")
        if a["fit_score"] >= config.MIN_FIT_EMAIL:
            matches.append(j)

    # student-priority roles first, then highest fit
    matches.sort(key=_priority, reverse=True)

    # Resume Tailor agent: verified resume + cover letter (DOCX and PDF) for the top matches
    to_tailor = [m for m in matches
                 if m["analysis"]["fit_score"] >= config.TAILOR_FIT][: config.MAX_TAILORED]
    print(f"3) Tailoring resume + cover letter for {len(to_tailor)} top matches with {config.WRITE_MODEL}…")
    for m in to_tailor:
        pack = resume_agent.build_pack(m)
        if not pack:
            continue
        if pack["requires_citizenship_or_clearance"]:
            m["analysis"]["gaps"] = (["Ad asks for citizenship, PR or clearance: check before applying"]
                                     + m["analysis"].get("gaps", []))[:3]
        m["pack"] = pack
        k = pack["keywords"]
        print(f"   pack ready: {m['title'][:40]}  keywords {k['coverage']}%  fixes {len(pack['problems'])}")

    stats = {
        "new": len(matches),
        "top": sum(1 for m in matches if m["analysis"]["fit_score"] >= 75),
        "scanned": len(found),
    }

    print(f"4) Emailing {len(matches)} matches…")
    emailer.send(matches, stats)

    print("5) Logging to applications.csv…")
    tracker.append(matches)

    # remember only the jobs we actually scored, so unscored ones return next run
    store.save_seen(seen | {j["id"] for j in fresh})
    print("Done.")


if __name__ == "__main__":
    main()
