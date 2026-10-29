"""docs/index.html: the explorable, with the animals and the FishBase uptake baked in."""
import json
from pathlib import Path

import pandas as pd

from common import DOCS, RESULTS


def main():
    ex = pd.read_csv(RESULTS / "animals.csv")
    animals = ex[["animal", "group", "scope", "tissue", "mass_kg", "excess_k"]].to_dict("records")
    data = {"animals": animals, "best_flux": float(pd.read_csv(RESULTS / "o2_flux.csv").flux_mg_m2_h.max())}
    page = (Path(__file__).parent / "page.html").read_text(encoding="utf-8")
    page = page.replace("/*DATA*/null", json.dumps(data, separators=(",", ":")))
    (DOCS / "index.html").write_text(page, encoding="utf-8")
    print("wrote docs/index.html,", len(page) // 1024, "kB")


if __name__ == "__main__":
    main()
