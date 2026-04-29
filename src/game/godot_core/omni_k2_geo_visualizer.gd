# Omni K2 Geoscience GDScript Visualizer (Godot)
# Ref: davendw49/k2 — WSDM 2024
extends Node

var geo_domains = ["geology", "geophysics", "seismology", "mineralogy",
                   "oceanography", "hydrology", "atmospheric_science"]

func classify_query(query: String) -> String:
    var q = query.to_lower()
    if "earthquake" in q or "seismic" in q: return "seismology"
    if "mineral" in q or "rock" in q: return "mineralogy"
    if "ocean" in q or "marine" in q: return "oceanography"
    if "water" in q or "river" in q: return "hydrology"
    return "geology"

func domain_color(domain: String) -> Color:
    match domain:
        "seismology": return Color(0.9, 0.2, 0.2)
        "mineralogy": return Color(0.6, 0.4, 0.2)
        "oceanography": return Color(0.1, 0.4, 0.9)
        "hydrology": return Color(0.2, 0.7, 0.9)
        _: return Color(0.5, 0.5, 0.5)
