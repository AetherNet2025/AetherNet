# AetherNet: Conceptual Research Code — NOT FOR FIELD DEPLOYMENT
# License: Apache 2.0
#
# DISCLAIMER:
# This script is part of the AetherNet conceptual release.
# It is provided for simulation, research, and academic evaluation only.
# It is NOT intended for field deployment or operational use.
# Authors disengage after public release; see README/OASP.
#
# --- aethernet_network_sync.py ---

"""
Handles *simulated* peer-to-peer communication and public data sharing
between conceptual AetherNet components and mock cloud endpoints.

Angle/Direction extensions in this version:
- broadcast_to_open_cloud(..., heading_deg, bank_deg, angle_of_attack_deg, formation_yaw_offset_deg)
  attaches an `angle_meta` block when provided.
- peer_to_peer_sync(..., angle_meta={...}) includes angle metadata in the hashed envelope.
- cluster_sync_summary(..., formation_yaw_offset_deg, alignment_mode) reports formation info.

Includes simulated uploads to Zenodo or AWS Open Data.
"""

import json
from datetime import datetime
from typing import List, Dict, Optional

# Toggle between Zenodo and S3 simulation
UPLOAD_TARGET = "zenodo"  # or "s3"

def simulate_upload_to_zenodo(data):
    print("[Zenodo Upload] Simulating upload to Zenodo repository...")
    print(json.dumps(data, indent=2))
    print("[Zenodo Upload] Upload complete.\n")

def simulate_upload_to_s3(data):
    print("[S3 Upload] Simulating upload to AWS Open Data...")
    print(json.dumps(data, indent=2))
    print("[S3 Upload] Upload complete.\n")

def upload_to_open_repo(data_packet):
    if UPLOAD_TARGET == "zenodo":
        simulate_upload_to_zenodo(data_packet)
    elif UPLOAD_TARGET == "s3":
        simulate_upload_to_s3(data_packet)
    else:
        print("[Error] Unknown upload target (simulation)")

def broadcast_to_open_cloud(
    drone_id: str,
    payload: Dict,
    heading_deg: Optional[float] = None,
    bank_deg: Optional[float] = None,
    angle_of_attack_deg: Optional[float] = None,
    formation_yaw_offset_deg: Optional[float] = None
) -> Dict:
    """Broadcast a conceptual packet to a public data sink (simulated). Adds CC0 by default."""
    angle_meta = {k: v for k, v in {
        "heading_deg": heading_deg,
        "bank_deg": bank_deg,
        "angle_of_attack_deg": angle_of_attack_deg,
        "formation_yaw_offset_deg": formation_yaw_offset_deg,
    }.items() if v is not None}

    packet = {
        "timestamp": datetime.utcnow().isoformat(),
        "drone_id": drone_id,
        "payload": {**payload, **({"angle_meta": angle_meta} if angle_meta else {})},
        "license": "CC0",
        "simulation": True
    }

    # Local feedback
    print("[OPEN-CLOUD]", json.dumps(packet))

    # Simulated external upload
    upload_to_open_repo(packet)
    return packet

def peer_to_peer_sync(
    drone_id: str,
    peer_list: List[str],
    data: Dict,
    angle_meta: Optional[Dict] = None
) -> None:
    """Simulate a P2P gossip-style sync. Includes angle_meta if provided."""
    envelope = {"data": data}
    if angle_meta:
        envelope["angle_meta"] = angle_meta

    # stable-ish hash for demo output
    envelope_hash = hash(json.dumps(envelope, sort_keys=True)) % 100000
    for peer in peer_list:
        print(f" → {drone_id} ➝ {peer}: Data hash {envelope_hash} (simulated)")

def cluster_sync_summary(
    cluster_id: str,
    cluster_members: List[str],
    shared_info: Dict,
    formation_yaw_offset_deg: Optional[float] = None,
    alignment_mode: Optional[str] = None
) -> Dict:
    """Emit a concise cluster state summary including formation information (simulation)."""
    summary = {
        "cluster": cluster_id,
        "members": cluster_members,
        "zone_summary": shared_info,
        "time": datetime.utcnow().isoformat(),
        "formation": {
            "yaw_offset_deg": formation_yaw_offset_deg,
            "alignment_mode": alignment_mode
        },
        "simulation": True
    }
    print("[CLUSTER]", json.dumps(summary))
    return summary

# --------------------------- Demo / CLI entry ---------------------------

if __name__ == '__main__':
    test_payload = {
        "CAPE": 2100,
        "vorticity": 0.0008,
        "humidity": 0.88,
        "anomaly_score": 0.7
    }

    broadcast_to_open_cloud(
        "D2023", test_payload,
        heading_deg=135, bank_deg=5,
        angle_of_attack_deg=2, formation_yaw_offset_deg=10
    )

    peer_to_peer_sync(
        "D2023", ["D3041", "D9832"], test_payload,
        angle_meta={"heading_deg": 135}
    )

    cluster_sync_summary(
        "MeshCluster-Echo", ["D2023", "D3041", "D9832"],
        {"avg_CAPE": 2050}, formation_yaw_offset_deg=10,
        alignment_mode="crosswind"
    )
