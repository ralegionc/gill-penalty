"""Fetch the FishBase tables used here (rOpenSci parquet mirror on Hugging Face)."""
import requests

from common import RAW

BASE = "https://huggingface.co/datasets/cboettig/fishbase/resolve/main/data/fb/v25.04/parquet/"
TABLES = ["gillarea", "oxygen", "species", "families"]


def main():
    out = RAW / "fishbase"
    out.mkdir(parents=True, exist_ok=True)
    for t in TABLES:
        p = out / f"{t}.parquet"
        if p.exists():
            continue
        r = requests.get(BASE + f"{t}.parquet", timeout=120)
        r.raise_for_status()
        p.write_bytes(r.content)
        print("got", p.name, len(r.content) // 1024, "kB")


if __name__ == "__main__":
    main()
