"""The heat budget of breathing.

Every millilitre of oxygen an animal burns releases about 19.6 J. In a gill-breather the
blood that will carry that oxygen first passes the gills, where it cools to water
temperature, because heat crosses the gill wall thousands of times more readily than
oxygen does (heat_vs_oxygen). A litre of blood can carry at most its oxygen capacity, so
it can bring at most Q_OX * capacity joules of heat-to-be into the body, and it leaves
again carrying everything above water temperature back to the gills. In steady state no
perfused tissue can sit more than

    ceiling = Q_OX * capacity * extraction / C_BLOOD

above the water. The ceiling does not depend on body size or metabolic rate: a bigger or
busier fish burns more oxygen but must pump proportionally more blood past the gills.
The only escape is a counter-current exchanger (rete mirabile) that hands heat from
outgoing venous blood to incoming arterial blood before it reaches the gills; an
exchanger of effectiveness eff raises the ceiling to ceiling / (1 - eff).

Units: oxygen capacity and extraction in mL O2 per mL blood and as a fraction; heats in
J; temperatures in K or degC differences.
"""
import numpy as np

Q_OX = 19.6       # J per mL O2 burned (13.7 J per mg, mixed fuel; 19.3 to 20.1 by fuel)
C_BLOOD = 3.7     # J per mL blood per K (3.6 to 3.9)
C_SEAWATER = 3.99  # J per mL per K
C_AIR = 1.2e-3    # J per mL air per K near 10 degC
L_VAP = 2.43      # J per mg water evaporated near body temperature


def ceiling(capacity, extraction=1.0):
    """Largest steady excess (K) of any perfused tissue over the water with plain gills."""
    return Q_OX * np.asarray(capacity) * extraction / C_BLOOD


def excess_with_rete(capacity, eff, extraction=1.0):
    """Ceiling raised by a counter-current exchanger of effectiveness eff (0 to <1)."""
    return ceiling(capacity, extraction) / (1.0 - np.asarray(eff))


def required_rete(excess, capacity, extraction=1.0):
    """Exchanger effectiveness needed to hold a tissue `excess` K above the water."""
    return np.clip(1.0 - ceiling(capacity, extraction) / np.asarray(excess, float), 0.0, None)


def gill_penalty(excess, capacity, eff=0.0, extraction=1.0):
    """Heat lost through the gills per joule of metabolic heat, at a given excess.

    Above 1 the animal cannot break even: burning more food needs more oxygen, which needs
    more blood through the gills, which throws away more heat than the food released.
    """
    return np.asarray(excess, float) * (1.0 - eff) / ceiling(capacity, extraction)


def sat_vapour(t_c):
    """Saturation water vapour density, mg per mL of air (Magnus formula)."""
    t = np.asarray(t_c, float)
    e = 611.2 * np.exp(17.62 * t / (243.12 + t))  # Pa
    return e * 0.018015 / (8.314 * (t + 273.15))   # kg/m3, which is mg/mL


def lung_penalty(t_body, t_air, o2_per_air=0.04, rh_in=0.9):
    """Heat lost through the lungs per joule of metabolic heat.

    Each mL of air taken in is warmed to body temperature and saturated before it leaves
    (an upper bound: whales and seals cool exhaled air in the nose). o2_per_air is the mL
    of oxygen removed from each mL of air (0.04 to 0.05 in people, up to about 0.1 in
    diving whales).
    """
    warm = C_AIR * (np.asarray(t_body) - t_air)
    wet = L_VAP * (sat_vapour(t_body) - rh_in * sat_vapour(t_air))
    return (warm + wet) / (Q_OX * o2_per_air)


# Why gill blood leaves at water temperature. Across the same membrane, the ease with
# which heat and oxygen equilibrate between water and blood is set by diffusivity over
# the capacity of blood to soak up each one.
K_TISSUE = 0.55        # W per m per K, water-like tissue
D_O2 = 2.0e-9          # m2 per s, oxygen in water near 15 degC
ALPHA_O2 = 1.13e-5     # mol per m3 per Pa, oxygen solubility in water-like tissue


def blood_o2_capacitance(capacity, p_span_kpa=9.0):
    """Effective oxygen capacitance of blood, mol per m3 per Pa, over the loading span.

    capacity mL O2 per mL blood is released over roughly 9 kPa (about 70 mmHg) of
    partial-pressure change between arterial and venous blood.
    """
    mol_per_m3 = np.asarray(capacity) * 1e6 / 22400  # mL/mL -> mol/m3 at STP
    return mol_per_m3 / (p_span_kpa * 1e3)


def heat_vs_oxygen(capacity=0.1, p_span_kpa=9.0):
    """How many times more readily blood reaches water temperature than oxygen equilibrium."""
    heat = K_TISSUE / (C_BLOOD * 1e6)                    # m2/s, thermal diffusivity of blood
    oxy = D_O2 * ALPHA_O2 / blood_o2_capacitance(capacity, p_span_kpa)  # m2/s, effective
    return heat / oxy


def lamella(ntu_o2=2.0, ratio=None, n=400):
    """Approach to equilibrium along a gill lamella: oxygen loading and heat loss.

    Returns position (0 at entry, 1 at exit) and the fraction of the way to equilibrium for
    oxygen and for temperature, for blood exchanging with water of fixed state.
    """
    ratio = heat_vs_oxygen() if ratio is None else ratio
    x = np.linspace(0, 1, n)
    return x, 1 - np.exp(-ntu_o2 * x), 1 - np.exp(-ntu_o2 * ratio * x)


def steady_state(heat_w, blood_ml_s, eff=0.0, gill_ntu=None, skin_w_k=0.0):
    """Tissue excess over water from an explicit loop: tissue, rete, gill, skin.

    A check on the algebra above rather than a separate model. Blood leaves the tissue at
    tissue temperature, gives heat to incoming arterial blood in the rete (effectiveness
    eff), loses most of the rest at the gill (thermal effectiveness 1 - exp(-gill_ntu)),
    and returns through the rete. Skin conducts skin_w_k watts per K straight to the water.
    Returns (tissue excess, venous excess arriving at the gill), both in K.
    """
    gill_ntu = 2.0 * heat_vs_oxygen() if gill_ntu is None else gill_ntu
    e_g = 1 - np.exp(-gill_ntu)
    qc = blood_ml_s * C_BLOOD          # W per K carried by the blood stream
    # unknowns: T tissue, T arterial after rete (Ta'), T venous after rete (Tv'), T arterial
    # after gill (Ta); water at 0. Equations, in order: tissue balance, rete arterial side,
    # rete energy balance, gill.
    A = np.array([
        [qc + skin_w_k, -qc, 0.0, 0.0],
        [-eff, 1.0, 0.0, -(1 - eff)],
        [-1.0, 1.0, 1.0, -1.0],
        [0.0, 0.0, -(1 - e_g), 1.0],
    ])
    rhs = np.array([heat_w, 0.0, 0.0, 0.0])
    t, ta2, tv2, ta = np.linalg.solve(A, rhs)
    return t, tv2


def o2_seawater(t_c, salinity=35.0):
    """Oxygen in air-saturated seawater, mL per mL (Weiss 1970 fit)."""
    T = np.asarray(t_c, float) + 273.15
    a = (-173.4292, 249.6339, 143.3483, -21.8492)
    b = (-0.033096, 0.014259, -0.0017)
    ln = (a[0] + a[1] * 100 / T + a[2] * np.log(T / 100) + a[3] * T / 100
          + salinity * (b[0] + b[1] * T / 100 + b[2] * (T / 100) ** 2))
    return np.exp(ln) / 1000  # mL/L -> mL/mL
