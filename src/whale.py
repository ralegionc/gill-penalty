"""A blue whale that breathes water: what it would take.

results/gilled_whale.json  the budget, every input stated
"""
import json

import numpy as np
import pandas as pd

import physics as ph
from common import RESULTS

MASS_KG = 100_000
T_BODY, T_WATER = 36.0, 10.0
FMR_PER_BMR = 2.5             # field metabolism over Kleiber basal (2 to 5 in marine mammals)
CAPACITY = 0.20               # mL O2 per mL blood, mammal-like (fish rarely exceed it)
WATER_EXTRACTION = 0.6        # fraction of dissolved O2 a gill removes (0.5 to 0.8 in active fish)
SKIN_K = 0.1                  # Meeh coefficient, m2 per kg^(2/3)


def kleiber_w(m_kg):
    return 3.39 * m_kg ** 0.75   # 70 kcal per day per kg^0.75


def budget(mass_kg=MASS_KG, t_body=T_BODY, t_water=T_WATER, capacity=CAPACITY, flux=None):
    fmr = FMR_PER_BMR * kleiber_w(mass_kg)                     # W
    vo2 = fmr / ph.Q_OX                                       # mL O2 per s
    excess = t_body - t_water
    blood = vo2 / capacity                                    # mL blood per s, full extraction
    water = vo2 / (ph.o2_seawater(t_water) * WATER_EXTRACTION)  # mL water per s
    best_flux = flux if flux is not None else pd.read_csv(RESULTS / "o2_flux.csv").flux_mg_m2_h.max()
    gill_m2 = vo2 * 1.429 * 3600 / best_flux                  # mg/h over mg/m2/h
    skin_m2 = SKIN_K * mass_kg ** (2 / 3)
    plain = ph.gill_penalty(excess, capacity)
    return dict(
        mass_kg=mass_kg, t_body=t_body, t_water=t_water, excess_k=excess,
        fmr_kw=fmr / 1e3, vo2_l_s=vo2 / 1e3, blood_l_s=blood / 1e3, water_m3_s=water / 1e6,
        gill_area_m2=gill_m2, skin_area_m2=skin_m2, best_flux_mg_m2_h=best_flux,
        ceiling_k=float(ph.ceiling(capacity)),
        plain_gill_heat_loss_mw=plain * fmr / 1e6, plain_penalty=float(plain),
        rete_breakeven=float(ph.required_rete(excess, capacity)),
        rete_half=float(1 - 0.5 * ph.ceiling(capacity) / excess),   # gills take half the heat
        lung_penalty=float(ph.lung_penalty(t_body, t_water, o2_per_air=0.06)),
    )


def main():
    b = budget()
    (RESULTS / "gilled_whale.json").write_text(json.dumps(b, indent=2))
    for k, v in b.items():
        print(f"{k:28s} {v:,.4g}")
    return b


if __name__ == "__main__":
    main()
