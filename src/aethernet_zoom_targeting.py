# AetherNet: Conceptual Research Code — NOT FOR FIELD DEPLOYMENT
# License: Apache 2.0
#
# DISCLAIMER:
# This script is part of the AetherNet conceptual release.
# It is provided for simulation, research, and academic evaluation only.
# It is NOT intended for field deployment or operational use.
# Authors disengage after public release; see README/OASP.
#
# --- zoom_targeting.py ---

"""
Evaluates simulated atmospheric inputs to identify higher-risk regions and
suggest a *hypothetical* flight geometry (heading, yaw offset, bank, AoA)
for modeling purposes only.

Angle/Direction helpers:
- heading_from_wind_dir(wind_dir_deg, mode)
- suggest_geometry(sensor_data, mode='crosswind', defaults...)
"""

from typing import Dict, List, Tuple
import math
import random

# ---------- Risk scoring (conceptual) ----------

def calculate_risk_score(sensor_data: Dict) -> float:
    """Composite risk score between 0.0 and 1.0 (illustrative only)."""
    weights = {
        'CAPE': 0.25,
        'vorticity': 0.25,
        'humidity': 0.15,
        'vertical_velocity': 0.15,
        'anomaly_score': 0.20
    }
    norm = {
        'CAPE': 4000,
        'vorticity': 0.0015,
        'humidity': 1.0,
        'vertical_velocity': 3.0,
        'anomaly_score': 1.0
    }
    score = 0.0
    for key, w in weights.items():
        value = float(sensor_data.get(key, 0.0))
        score += w * min(value / norm[key], 1.0)
    return round(score, 3)

def prioritize_targets(grid_data: List[Dict], top_n: int = 3) -> List[Tuple[Dict, float]]:
    """Return top N regions sorted by conceptual risk score."""
    scored = [(data, calculate_risk_score(data)) for data in grid_data]
    scored_sorted = sorted(scored, key=lambda x: x[1], reverse=True)
    return scored_sorted[:top_n]

def should_zoom(sensor_data: Dict, score_threshold: float = 0.65) -> bool:
    """Decide if a zone *hypothetically* qualifies for increased modeling focus."""
    return calculate_risk_score(sensor_data) >= score_threshold

# ---------- Angle/Direction helpers ----------

def heading_from_wind_dir(wind_from_deg: float, mode: str = "crosswind") -> float:
    """Derive a heading given the wind-from direction. 0 = North, clockwise positive."""
    wind_from_deg = (float(wind_from_deg) + 360.0) % 360.0
    if mode == "upwind":
        return wind_from_deg
    if mode == "downwind":
        return (wind_from_deg + 180.0) % 360.0
    # default: crosswind (90° to the wind)
    return (wind_from_deg + 90.0) % 360.0

def suggest_geometry(sensor_data: Dict,
                     mode: str = "crosswind",
                     default_yaw_deg: float = 10.0,
                     bank_deg: float = 5.0,
                     aoa_deg: float = 2.0) -> Dict:
    """
    Produce a minimal geometry *recommendation for modeling only*.
    Uses wind_direction (deg FROM) if present; otherwise leaves heading None.
    """
    wind_from = sensor_data.get("wind_direction")  # deg FROM
    desired_heading = heading_from_wind_dir(wind_from, mode) if wind_from is not None else None

    # Simple illustrative heuristics
    shear = float(sensor_data.get("wind_shear", 0.0))
    vort = float(sensor_data.get("vorticity", 0.0))
    yaw = default_yaw_deg + min(shear / 5.0, 10.0)  # modest boost under higher shear
    bank = bank_deg + min(vort * 500.0, 3.0)        # tiny bump for stronger vort signal

    return {
        "desired_heading_deg": None if desired_heading is None else round(desired_heading, 1),
        "formation_yaw_offset_deg": round(yaw, 1),
        "bank_deg": round(bank, 1),
        "angle_of_attack_deg": round(aoa_deg, 1),
        "alignment_mode": mode
    }

# ---------- Optional: simulate grid scan ----------

def simulate_grid(num_zones: int = 10) -> List[Dict]:
    """Simulate a grid of atmosphere readings (for unit tests / demos)."""
    return [
        {
            'coordinates': (random.uniform(-5, 5), random.uniform(-5, 5)),
            'CAPE': random.uniform(1000, 4500),
            'vorticity': random.uniform(0.0002, 0.0016),
            'humidity': random.uniform(0.6, 1.0),
            'vertical_velocity': random.uniform(0.2, 3.2),
            'anomaly_score': random.uniform(0.0, 1.0),
            'wind_direction': random.uniform(0, 360),   # deg FROM
            'wind_shear': random.uniform(0, 20)
        }
        for _ in range(num_zones)
    ]

# ---------- Example usage ----------

if __name__ == '__main__':
    grid = simulate_grid()
    top_zones = prioritize_targets(grid, top_n=5)
    for i, (zone, score) in enumerate(top_zones):
        geom = suggest_geometry(zone, mode="crosswind")
        print(f"#{i+1} {zone['coordinates']} ➝ Score: {score}  |  Geometry: {geom}")
        if should_zoom(zone):
            print("  ↳ Hypothetical modeling focus suggested for this zone (conceptual only)." )
