"""Paths and the house style shared by every step."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
LABELS = ROOT / "data" / "labels"
DERIVED = ROOT / "data" / "derived"
FIGURES = ROOT / "figures"
RESULTS = ROOT / "results"
DOCS = ROOT / "docs"
for d in (DERIVED, FIGURES, RESULTS, DOCS):
    d.mkdir(parents=True, exist_ok=True)

# Night palette. Heat glows amber, water and oxygen are cyan, air-breathers pale blue.
BG, TEXT, SUBTLE, GRID = "#0a0d12", "#e8e4da", "#8a8f98", "#1c222b"
HEAT, WATER, AIR, BAD, PALE = "#f6b73c", "#5ec8d8", "#9fb7d9", "#c2513f", "#c9b98f"
