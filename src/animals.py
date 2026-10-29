"""Each animal against its ceiling.

results/animals.csv  plain-gill ceiling for the animal's blood, how far over it the animal
                     sits, and the exchanger effectiveness that excess implies
"""
import numpy as np
import pandas as pd

import physics as ph
from common import LABELS, RESULTS


def main():
    ex = pd.read_csv(LABELS / "excess.csv")
    gill = ex.group.str.startswith("fish")
    ex["ceiling_k"] = np.where(gill, ph.ceiling(ex.capacity.fillna(0.2)), np.nan)
    ex["ceiling_hi_k"] = np.where(gill, ph.ceiling(ex.capacity_hi.fillna(0.25)), np.nan)
    ex["times_ceiling"] = ex.excess_k / ex.ceiling_k
    ex["rete_implied"] = np.where(gill, ph.required_rete(ex.excess_k, ex.capacity.fillna(0.2)), np.nan)
    ex["rete_implied_lo"] = np.where(gill, ph.required_rete(ex.excess_lo_k.fillna(ex.excess_k),
                                                            ex.capacity_hi.fillna(0.25)), np.nan)
    # what the same excess would cost a gill-breather with mammal-grade blood and no exchanger
    ex["plain_gill_penalty"] = ph.gill_penalty(ex.excess_k, 0.2)
    ex["lung_penalty"] = np.where(~gill, ph.lung_penalty(37, (37 - ex.excess_k).clip(lower=-1.8), 0.04), np.nan)
    ex.to_csv(RESULTS / "animals.csv", index=False)
    cols = ["animal", "tissue", "excess_k", "ceiling_k", "times_ceiling", "rete_implied"]
    print(ex[gill][cols].round(3).to_string(index=False))
    bs = ex[ex.animal == "Basking shark"].iloc[0]
    print(f"\nbasking shark: {bs.excess_lo_k}-{bs.excess_k} K vs ceiling {bs.ceiling_k:.2f} K "
          f"(most generous {bs.ceiling_hi_k:.2f}); implies an exchanger of at least {bs.rete_implied_lo:.2f}"
          " or heat stored from warmer water")
    return ex


if __name__ == "__main__":
    main()
