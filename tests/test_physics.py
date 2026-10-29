"""Checks that could fail: the algebra against an explicit loop, the constants against
published values, and the ceiling against measured animals."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import physics as ph  # noqa: E402
from common import LABELS  # noqa: E402

EX = pd.read_csv(LABELS / "excess.csv")
GILL = EX[EX.group.str.startswith("fish")]


# --- constants against published values -------------------------------------------------

def test_oxygen_solubility_matches_freshwater_tables():
    # USGS tables, air-saturated fresh water at sea level: 14.62 mg/L at 0 C, 9.09 at 20 C
    assert ph.o2_seawater(0, salinity=0) * 1429 == pytest.approx(14.62, rel=0.02)
    assert ph.o2_seawater(20, salinity=0) * 1429 == pytest.approx(9.09, rel=0.02)
    assert ph.o2_seawater(10) < ph.o2_seawater(10, salinity=0)


def test_saturated_air_at_body_temperature():
    # 44 g of water per m3 of saturated air at 37 C
    assert ph.sat_vapour(37) == pytest.approx(0.0440, rel=0.02)


# --- the mechanism ------------------------------------------------------------------------

@pytest.mark.parametrize("capacity", [0.04, 0.10, 0.25])
@pytest.mark.parametrize("ntu_o2", [0.5, 1.0, 3.0])
def test_blood_leaves_gill_at_water_temperature(capacity, ntu_o2):
    """Wherever oxygen loading is even partial, heat exchange is complete."""
    _, o2, heat = ph.lamella(ntu_o2, ph.heat_vs_oxygen(capacity))
    assert o2[-1] < 0.96
    assert heat[-1] > 0.9999


@pytest.mark.parametrize("seed", range(5))
def test_explicit_loop_never_beats_the_ceiling(seed):
    """Random fish: any metabolic rate, blood flow, skin loss and exchanger. With full
    oxygen extraction the tissue excess equals ceiling/(1-eff) at most, and the blood
    reaching the gill is never above the plain ceiling."""
    rng = np.random.default_rng(seed)
    for _ in range(200):
        cap = rng.uniform(0.03, 0.25)
        blood = 10 ** rng.uniform(-2, 4)                 # mL/s, a minnow to a whale
        extraction = rng.uniform(0.2, 1.0)
        heat = ph.Q_OX * cap * extraction * blood        # W: the oxygen the blood can bring
        eff = rng.uniform(0, 0.99)
        skin = rng.uniform(0, 2) * blood * ph.C_BLOOD
        t, tv = ph.steady_state(heat, blood, eff=eff, skin_w_k=skin)
        assert t <= ph.excess_with_rete(cap, eff, extraction) * (1 + 1e-9)
        assert tv <= ph.ceiling(cap, extraction) * (1 + 1e-9)


def test_ceiling_is_independent_of_size_and_activity():
    cap = 0.15
    out = [ph.steady_state(ph.Q_OX * cap * blood, blood)[0] for blood in (0.01, 1.0, 1e4)]
    assert np.allclose(out, ph.ceiling(cap), rtol=1e-6)


# --- the ceiling against animals ------------------------------------------------------------

def test_skipjack_blood_returning_to_gills_is_under_the_ceiling():
    """Neill et al. 1976: blood heading to the gills of skipjack is at most 0.285 of the
    red-muscle excess (2.6 K), i.e. 0.74 K, which must not exceed the plain ceiling even
    for the lowest tuna oxygen capacity assumed."""
    row = EX[EX.tissue == "blood returning to the heart"].iloc[0]
    assert row.excess_hi_k == pytest.approx(0.285 * 2.6, abs=0.01)
    assert row.excess_hi_k <= ph.ceiling(row.capacity_lo)


def test_every_fish_above_the_ceiling_has_an_exchanger():
    """No steady excess above the plain ceiling (most generous capacity) without retia."""
    steady = GILL[GILL.steady == "yes"]
    lo = steady.excess_lo_k.fillna(steady.excess_k)
    over = steady[lo > ph.ceiling(steady.capacity_hi)]
    assert set(over.group) == {"fish_rete"}
    assert len(over) >= 4


def test_air_breathers_lose_little_heat_breathing():
    air = EX[EX.group == "air"]
    t_water = 37 - air.excess_k            # core near 37 C for this check
    g = ph.lung_penalty(37, t_water.clip(lower=-1.8), o2_per_air=0.04)
    assert (g < 0.3).all()


def test_lungs_beat_gills_by_two_orders_of_magnitude():
    assert ph.gill_penalty(30, 0.2) / ph.lung_penalty(37, 7) > 100
