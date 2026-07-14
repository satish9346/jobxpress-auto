"""
Run the pipeline locally using a .env file:  python run_local.py
(GitHub Actions does NOT use this — it injects secrets directly.)
"""
import os

def load_env(path=".env"):
    if not os.path.exists(path):
        return
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

if __name__ == "__main__":
    load_env()
    import main
    main.main()
