# AetherNet: Conceptual Research Code — NOT FOR FIELD DEPLOYMENT
# License: Apache 2.0
#
# DISCLAIMER:
# This script is part of the AetherNet conceptual release.
# It is provided for simulation, research, and academic evaluation only.
# It is NOT intended for field deployment or operational use.
# Authors disengage after public release; see README/OASP.
#
# --- aethernet_swarm_controller.py ---

"""
Manages *simulated* drone roles, cluster formation, failure recovery,
and coordination for conceptual swarm studies.

Angle/Direction extensions in this version:
- apply_heading_bias(drone, heading_deg, bank_deg, aoa_deg): store desired angles on the drone record
- Cluster includes a 'formation' block: {'yaw_offset_deg', 'axis'}
  (axis can be 'front', 'rear', 'port', 'starboard', 'vertical', or 'crosswind')
"""

from typing import List, Dict, Optional
import random

# --------------------------- Roles & Assignment ---------------------------

def assign_role(drone: Dict, zone_info: Dict) -> str:
    """Assign a role based on zone conditions and drone capabilities (illustrative only)."""
    roles = ["mesh_emitter", "scout", "relay", "observer"]
    if zone_info.get('zone_priority', False) and drone.get('battery', 0) > 60:
        return "mesh_emitter"
    return random.choice(roles)

# --------------------------- Cluster Lifecycle ---------------------------

def form_cluster(cluster_id: str, drone_list: List[Dict]) -> Dict:
    """Create a simulated cluster record with conceptual formation metadata."""
    cluster = {
        'id': cluster_id,
        'members': drone_list,
        'mode': 'mesh' if len(drone_list) >= 4 else 'scan',
        'status': 'active',
        'formation': {
            'yaw_offset_deg': 0.0,
            'axis': 'crosswind'
        }
    }
    print(f"[INFO] Cluster {cluster_id} formed with {len(drone_list)} simulated drones.")
    return cluster

def log_cluster_status(cluster: Dict) -> None:
    """Print a readable cluster status line (for CLI/debug)."""
    print(f"\n[CLUSTER {cluster['id']}] mode={cluster['mode']} status={cluster['status']}")
    print(f"Members: {[d['id'] for d in cluster['members']]}")
    if 'formation' in cluster:
        print(f"Formation: yaw_offset={cluster['formation'].get('yaw_offset_deg', 0)}°, "
              f"axis={cluster['formation'].get('axis')}")

def reassign_after_failure(cluster: Dict) -> Dict:
    """Remove failed members and adapt cluster mode if needed (simulated)."""
    survivors = [d for d in cluster['members'] if d.get('status', 'ok') != 'failed']
    if len(survivors) != len(cluster['members']):
        print(f"[WARN] Cluster {cluster['id']} lost {len(cluster['members']) - len(survivors)} member(s)." )
    cluster['members'] = survivors
    cluster['mode'] = 'mesh' if len(survivors) >= 4 else 'scan'
    return cluster

def recommend_rotation_schedule(drones: List[Dict]) -> List[Dict]:
    """Recommend an order for swapping drones for recharge (lowest battery first)."""
    return sorted(drones, key=lambda d: d.get('battery', 100))

# --------------------------- Angle/Bias application (new) ---------------------------

def apply_heading_bias(
    drone: Dict,
    heading_deg: Optional[float] = None,
    bank_deg: Optional[float] = None,
    aoa_deg: Optional[float] = None
) -> Dict:
    """
    Store desired heading/bank/AoA on the drone record for downstream vehicle layers.
    This is purely declarative and conceptual here.
    """
    if heading_deg is not None:
        drone['heading_deg'] = float(heading_deg)
    if bank_deg is not None:
        drone['bank_deg'] = float(bank_deg)
    if aoa_deg is not None:
        drone['angle_of_attack_deg'] = float(aoa_deg)
    return drone

# --------------------------- Example usage ---------------------------

if __name__ == '__main__':
    drones = [
        {'id': 'D1', 'battery': 65},
        {'id': 'D2', 'battery': 40},
        {'id': 'D3', 'battery': 85},
        {'id': 'D4', 'battery': 55},
        {'id': 'D5', 'battery': 30},
    ]

    zone_info = {'zone_priority': True}
    for drone in drones:
        role = assign_role(drone, zone_info)
        drone['role'] = role
        print(f"Drone {drone['id']} assigned conceptual role: {role}")

    cluster = form_cluster("Z9", drones[:4])

    # Demo: set a formation geometry and apply heading/bias to first member
    cluster['formation']['yaw_offset_deg'] = 12.0
    cluster['formation']['axis'] = 'crosswind'
    apply_heading_bias(cluster['members'][0], heading_deg=140, bank_deg=5, aoa_deg=2)

    log_cluster_status(cluster)

    # Simulate a member failure and reassign
    cluster['members'][1]['status'] = 'failed'
    cluster = reassign_after_failure(cluster)
    log_cluster_status(cluster)

    print("\n[ROTATION PLAN]:", [d['id'] for d in recommend_rotation_schedule(drones)])
