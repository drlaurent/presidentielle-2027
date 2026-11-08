#!/usr/bin/env python3
"""Download the newest data.gouv.fr resources and rebuild the Vercel page."""
from pathlib import Path
import subprocess
import requests

ROOT = Path(__file__).parent
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
API = "https://www.data.gouv.fr/api/1/datasets/presidentielle-2027-sondages-candidatures-et-projection-departementale/"
NEEDED = {
    "projection-departementale.geojson",
    "intentions-vote-vague-reference.csv",
}

def main():
    response = requests.get(API, timeout=60)
    response.raise_for_status()
    resources = response.json().get("resources", [])
    selected = {}
    for resource in resources:
        title = resource.get("title", "")
        if title in NEEDED and title not in selected and resource.get("url"):
            selected[title] = resource["url"]
    missing = NEEDED - selected.keys()
    if missing:
        raise RuntimeError(f"Ressources introuvables : {sorted(missing)}")
    for name, url in selected.items():
        print(f"[DL] {name} <- {url}")
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        (DATA / name).write_bytes(r.content)
    subprocess.run(["python", str(ROOT / "build_site.py")], check=True)

if __name__ == "__main__":
    main()
