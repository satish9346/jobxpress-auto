"""
Tailor a resume and cover letter for ANY job you find yourself (Seek, LinkedIn, a company site).

    python tailor_job.py job.txt                 # job ad saved as a text file
    python tailor_job.py job.txt --company "SA Water" --title "Graduate Data Analyst"

Paste the full job ad into a text file first. Output goes to output/<company>/ as
DOCX + PDF, with a keyword report. Needs ANTHROPIC_API_KEY (in .env or the environment).
"""
import argparse
import os
import sys

from run_local import load_env


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("job_file", help="text file with the full job ad")
    ap.add_argument("--title", default="", help="job title (optional; read from the ad if blank)")
    ap.add_argument("--company", default="", help="company name")
    ap.add_argument("--location", default="", help="job location")
    ap.add_argument("--out", default="output", help="output folder")
    args = ap.parse_args()

    load_env()
    import config
    import docgen
    import resume_agent
    if not config.ANTHROPIC_API_KEY:
        sys.exit("Set ANTHROPIC_API_KEY in .env first.")

    desc = open(args.job_file, encoding="utf-8").read()
    title = args.title or desc.strip().splitlines()[0][:120]
    job = {"title": title, "company": args.company, "location": args.location, "desc": desc,
           "link": "", "source": "manual"}
    print(f"Tailoring for: {title} at {args.company or '(company not given)'} …")
    pack = resume_agent.build_pack(job)
    if not pack:
        sys.exit("The tailoring call failed; see the message above.")

    folder = os.path.join(args.out, docgen.file_stub(pack))
    os.makedirs(folder, exist_ok=True)
    for name, data in docgen.render_all(pack).items():
        with open(os.path.join(folder, name), "wb") as f:
            f.write(data)
    k = pack["keywords"]
    report = [f"Job: {title}", f"ATS keyword match: {k['coverage']}%",
              f"Matched: {', '.join(k['matched']) or '-'}",
              f"In your facts but not on this resume (add if relevant): {', '.join(k['could_add']) or '-'}",
              f"Real gaps: {', '.join(k['gaps']) or '-'}",
              f"Needs citizenship/PR/clearance: {'YES, check before applying' if pack['requires_citizenship_or_clearance'] else 'no'}",
              "Fact-check repairs:"] + [f"  - {p}" for p in pack["problems"]] + (["  none"] if not pack["problems"] else [])
    with open(os.path.join(folder, "match_report.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(report) + "\n")
    print("\n".join(report))
    print(f"\nSaved to {folder}")


if __name__ == "__main__":
    main()
