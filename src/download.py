"""Download every source in src/sources.py into data/raw/ (skips files already there)."""
import os
import sys
import time
import urllib.request
from pathlib import Path

from sources import FILES

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
# bls.gov refuses requests without a browser-like User-Agent. BLS asks
# scripted users to include contact details: set PA_CONTACT to add yours.
UA = "Mozilla/5.0 (research script; github.com/amkashyap1220/PhysiciansAssistantJobExploration)"
if os.environ.get("PA_CONTACT"):
    UA += " " + os.environ["PA_CONTACT"]


def fetch(name, url):
    out = RAW / name
    if out.exists() and out.stat().st_size > 0:
        return "kept"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=120) as r:
        out.write_bytes(r.read())
    time.sleep(1)  # be gentle with bls.gov
    return f"{out.stat().st_size / 1e6:.1f} MB"


if __name__ == "__main__":
    RAW.mkdir(parents=True, exist_ok=True)
    failed = []
    for name, url in FILES.items():
        try:
            print(f"{name:28} {fetch(name, url)}")
        except Exception as e:
            failed.append(name)
            print(f"{name:28} FAILED: {e}", file=sys.stderr)
    sys.exit(1 if failed else 0)
