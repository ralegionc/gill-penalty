"""Gill area and oxygen uptake from FishBase.

results/gill_allometry.csv   one row per species: fitted gill area scaling and size range
results/o2_flux.csv          oxygen taken up per square metre of gill at peak activity
data/derived/gill_points.csv every usable gill-area record, for the figures

FishBase GILLAREA gives total gill area in cm2 against body weight in g (skipjack about
17 cm2/g, trout about 3, matching Muir and Hughes); OXYGEN gives uptake in mg O2 per kg
per hour with the metabolic level (standard, routine, active).
"""
import numpy as np
import pandas as pd

from common import DERIVED, RAW, RESULTS

FB = RAW / "fishbase"


def species_table():
    s = pd.read_parquet(FB / "species.parquet", columns=["SpecCode", "Genus", "Species", "FamCode", "FBname"])
    f = pd.read_parquet(FB / "families.parquet", columns=["FamCode", "Family", "Order", "Class"])
    s = s.merge(f, on="FamCode", how="left")
    s["sci"] = s.Genus + " " + s.Species
    return s[["SpecCode", "sci", "FBname", "Family", "Order", "Class"]]


def gill_points():
    g = pd.read_parquet(FB / "gillarea.parquet")
    g = g[(g.Doubtful == 0) & (g.BodyWeight > 0) & (g.GillArea > 0)]
    g = g.merge(species_table(), on="SpecCode", how="left")
    g = g.rename(columns={"BodyWeight": "mass_g", "GillArea": "area_cm2"})
    g["air"] = g.AirBreather.fillna(0).astype(bool)
    g["tuna"] = g.Family.eq("Scombridae") & g.sci.str.match(r"(Thunnus|Katsuwonus|Euthynnus|Auxis|Sarda)")
    return g[["SpecCode", "sci", "FBname", "Family", "Class", "mass_g", "area_cm2", "air", "tuna"]]


def allometry(g):
    rows = []
    for (code, sci), d in g.groupby(["SpecCode", "sci"]):
        lm, la = np.log10(d.mass_g), np.log10(d.area_cm2)
        span = lm.max() - lm.min()
        if len(d) >= 3 and span >= np.log10(3):
            b, a = np.polyfit(lm, la, 1)
        else:
            b, a = np.nan, np.nan
        rows.append(dict(SpecCode=code, sci=sci, family=d.Family.iloc[0], n=len(d), b=b, a=a,
                         m_lo=d.mass_g.min(), m_hi=d.mass_g.max(),
                         per_g_median=(d.area_cm2 / d.mass_g).median(), tuna=d.tuna.any(), air=d.air.any()))
    return pd.DataFrame(rows)


def area_at(al_row, g_sp, mass_g):
    """Gill area (cm2) of a species at mass_g: its own fit when it has one, else its nearest
    record scaled with exponent 0.85 (the pooled water-breather slope, see main)."""
    if np.isfinite(al_row.b):
        return 10 ** (al_row.a + al_row.b * np.log10(mass_g))
    near = g_sp.iloc[(np.log10(g_sp.mass_g) - np.log10(mass_g)).abs().argmin()]
    return near.area_cm2 * (mass_g / near.mass_g) ** 0.85


def o2_flux(g, al):
    o = pd.read_parquet(FB / "oxygen.parquet")
    o = o[(o.MetabolicLevel == "active") & (o.Weight > 0) & (o.OxygenCons > 0)
          & o.AppliedStress.isin(["none specified", None]) & o.SpecCode.isin(g.SpecCode)]
    rows = []
    for _, r in o.iterrows():
        g_sp = g[g.SpecCode == r.SpecCode]
        a_row = al[al.SpecCode == r.SpecCode].iloc[0]
        # only within a factor of 3 of the masses whose gills were measured
        if not (g_sp.mass_g.min() / 3 <= r.Weight <= g_sp.mass_g.max() * 3):
            continue
        area_m2 = area_at(a_row, g_sp, r.Weight) / 1e4
        flux = r.OxygenCons * (r.Weight / 1000) / area_m2  # mg O2 per m2 gill per hour
        rows.append(dict(SpecCode=r.SpecCode, sci=a_row.sci, family=a_row.family, tuna=a_row.tuna,
                         mass_g=r.Weight, temp_c=r.Temp, vo2_mg_kg_h=r.OxygenCons, flux_mg_m2_h=flux))
    f = pd.DataFrame(rows)
    best = f.sort_values("flux_mg_m2_h").groupby("SpecCode").tail(1).sort_values("flux_mg_m2_h", ascending=False)
    return f, best


def main():
    g = gill_points()
    water = g[~g.air]
    b_pooled, a_pooled = np.polyfit(np.log10(water.mass_g), np.log10(water.area_cm2), 1)
    al = allometry(g)
    f, best = o2_flux(g, al)
    g.to_csv(DERIVED / "gill_points.csv", index=False)
    al.to_csv(RESULTS / "gill_allometry.csv", index=False)
    best.to_csv(RESULTS / "o2_flux.csv", index=False)
    f.to_csv(DERIVED / "o2_flux_all.csv", index=False)
    fitted = al[np.isfinite(al.b) & ~al.air]
    print(f"gill records {len(g)}, species {g.sci.nunique()}, pooled slope {b_pooled:.3f}")
    print(f"species slopes: n={len(fitted)}, median {fitted.b.median():.3f} "
          f"[{fitted.b.quantile(.25):.3f}, {fitted.b.quantile(.75):.3f}]")
    print(f"active O2 flux: {len(best)} species; top 8:")
    print(best.head(8)[["sci", "mass_g", "temp_c", "vo2_mg_kg_h", "flux_mg_m2_h"]].to_string(index=False))
    return dict(pooled_slope=b_pooled, pooled_intercept=a_pooled)


if __name__ == "__main__":
    main()
