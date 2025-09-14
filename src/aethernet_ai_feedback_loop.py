# AetherNet: Conceptual Research Code — NOT FOR FIELD DEPLOYMENT
# License: Apache 2.0
#
# DISCLAIMER:
# This script is part of the AetherNet conceptual release.
# It is provided for simulation, research, and academic evaluation only.
# It is NOT intended for field deployment or operational use.
# Authors disengage after public release; see README/OASP
#
# --- aethernet_ai_feedback_loop.py ---

"""
Processes *simulated* sensor data to illustrate a toy ML loop for targeting predictions
and retraining behavior after simulated success/failure. This is a didactic example for
research modeling only; it is not operational AI.

Angle/Direction extensions:
- Optional angle features: heading_deg, bank_deg, angle_of_attack_deg, formation_yaw_offset_deg, alignment_mode
- Backward-compatible: zeros/neutral encodings are used if fields are missing.
"""

import numpy as np
from typing import List, Dict, Tuple
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import random

ALIGNMENT_MODES = ("upwind", "downwind", "crosswind", "none")


def _extract_angle_features(entry: Dict) -> Tuple[float, float, float, float, float, float, float]:
    """Return normalized angle feature vector for modeling only."""
    meta = entry.get("angle_meta", {})
    heading = entry.get("heading_deg", meta.get("heading_deg"))
    bank = entry.get("bank_deg", meta.get("bank_deg"))
    aoa = entry.get("angle_of_attack_deg", meta.get("angle_of_attack_deg"))
    yaw = entry.get("formation_yaw_offset_deg", meta.get("formation_yaw_offset_deg"))
    align = (entry.get("alignment_mode", meta.get("alignment_mode")) or "none").lower()

    # Normalize ranges (robust to None)
    heading_norm = (float(heading) % 360.0) / 360.0 if heading is not None else 0.0
    bank_norm = min(abs(float(bank or 0.0)) / 30.0, 1.0)            # assume 0–30° typical
    aoa_norm  = min(abs(float(aoa or 0.0)) / 15.0, 1.0)             # assume 0–15° typical
    yaw_norm  = min(abs(float(yaw or 0.0)) / 180.0, 1.0)            # 0–180°

    # One-hot alignment (ignore "none")
    align = align if align in ALIGNMENT_MODES else "none"
    up = 1.0 if align == "upwind" else 0.0
    down = 1.0 if align == "downwind" else 0.0
    cross = 1.0 if align == "crosswind" else 0.0

    return heading_norm, bank_norm, aoa_norm, yaw_norm, up, down, cross


class AetherNetAI:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=20, random_state=42)
        self.is_trained = False

    def preprocess(self, dataset: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Convert dataset into features and labels (illustrative)."""
        features, labels = [], []
        for entry in dataset:
            base = [
                entry.get('CAPE', 0.0),
                entry.get('vorticity', 0.0),
                entry.get('humidity', 0.0),
                entry.get('vertical_velocity', 0.0),
                entry.get('anomaly_score', 0.0),
            ]
            ang = list(_extract_angle_features(entry))
            features.append(base + ang)
            labels.append(entry.get('storm_formed', 0))  # binary outcome (simulated)
        return np.array(features, dtype=float), np.array(labels, dtype=int)

    def train(self, dataset: List[Dict]):
        X, y = self.preprocess(dataset)
        if len(set(y)) < 2:
            print("[AI] Warning: dataset lacks class diversity (simulation). Skipping train.")
            return
        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2)
        self.model.fit(X_train, y_train)
        pred = self.model.predict(X_val)
        acc = accuracy_score(y_val, pred)
        print(f"[AI] Conceptual training complete. Validation Accuracy: {acc:.2f} (illustrative only)")
        self.is_trained = True

    def _vectorize_scan(self, current_scan: Dict) -> np.ndarray:
        base = [
            current_scan.get("CAPE", 0.0),
            current_scan.get("vorticity", 0.0),
            current_scan.get("humidity", 0.0),
            current_scan.get("vertical_velocity", 0.0),
            current_scan.get("anomaly_score", 0.0),
        ]
        ang = list(_extract_angle_features(current_scan))
        return np.array([base + ang], dtype=float)

    def predict_next_focus(self, current_scan: Dict) -> bool:
        """Return a conceptual yes/no on whether a zone merits *modeling focus*."""
        if not self.is_trained:
            print("[AI] Notice: Model not trained. Defaulting to rule-based fallback (conceptual)." )
            return current_scan.get("CAPE", 0) > 1500 and current_scan.get("vorticity", 0) > 0.0005
        features = self._vectorize_scan(current_scan)
        prediction = self.model.predict(features)[0]
        return bool(prediction)

    def retrain_on_outcome(self, original_dataset: List[Dict], success: bool):
        """Feedback cycle: retrain AI if prediction was wrong (simulated)."""
        if not success:
            print("[AI] Outcome mismatch (simulation): reinforcing edge-case patterns.")
            self.train(original_dataset)
        else:
            print("[AI] Outcome match (simulation): maintaining current model state.")


# Example usage (simulation)
if __name__ == '__main__':
    # Simulate historical outcomes (some with angle_meta)
    fake_data = []
    for i in range(60):
        entry = {
            "CAPE": random.uniform(1000, 4000),
            "vorticity": random.uniform(0.0003, 0.0015),
            "humidity": random.uniform(0.6, 1.0),
            "vertical_velocity": random.uniform(0.2, 2.5),
            "anomaly_score": random.uniform(0.2, 0.95),
            "storm_formed": random.randint(0, 1)
        }
        if i % 3 == 0:
            entry["angle_meta"] = {
                "heading_deg": random.uniform(0, 360),
                "bank_deg": random.uniform(0, 10),
                "angle_of_attack_deg": random.uniform(0, 6),
                "formation_yaw_offset_deg": random.uniform(0, 25),
                "alignment_mode": random.choice(["crosswind", "upwind", "downwind"])
            }
        fake_data.append(entry)

    ai = AetherNetAI()
    ai.train(fake_data)
    test_zone = fake_data[0]
    should_focus = ai.predict_next_focus(test_zone)
    print(f"[PREDICTION] Hypothetical modeling focus suggested: {should_focus}")
