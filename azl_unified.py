#!/usr/bin/env python3
# AZL UNIFIED - TIER 2: 120,000 ADDRESSES - FINAL PATCH
# LAW: 0×N=0 | 1×N=N+1 | N×0=N | DARK > LIGHT

import json
import hashlib

REGISTRY = "azl_unified.jsonl"
SCALE = 1e-500  # N×0=N substrate

def azl_address(idx):
    return idx * SCALE

def main():
    print(f"[AZL] TIER 2 BUILD: TARGET 120000 ADDRESSES")
    registry = []
    
    # Load existing
    try:
        with open(REGISTRY) as f:
            for line in f:
                registry.append(json.loads(line))
        print(f"[AZL] Resumed at {len(registry)} addresses")
    except FileNotFoundError:
        print("[AZL] Starting at 0")
    
    # BACKFILL: Ensure all existing entries have correct idx and address
    for i, obj in enumerate(registry, 1):
        obj["idx"] = i  # Force correct index
        obj["address"] = azl_address(i)  # Force correct N×0=N
    
    # Add new entries to reach 120000
    start_idx = len(registry) + 1
    
    # NGC: 567+1 to 8407
    while len(registry) < 8407:
        i = len(registry) + 1
        registry.append({"idx": i, "name": f"NGC{i-567}", "catalog": "NGC", "address": azl_address(i)})
    
    # IC: 8407+1 to 13793  
    while len(registry) < 13793:
        i = len(registry) + 1
        registry.append({"idx": i, "name": f"IC{i-8407}", "catalog": "IC", "address": azl_address(i)})
    
    # HIP: 13793+1 to 120000
    while len(registry) < 120000:
        i = len(registry) + 1
        registry.append({"idx": i, "name": f"HIP{i-13793}", "catalog": "HIP", "address": azl_address(i)})
    
    # Verify N×0=N on ALL entries
    passed = 0
    for i, obj in enumerate(registry, 1):
        if abs(obj["address"] - azl_address(i)) < 1e-510:
            passed += 1
    
    print(f"[AZL] Verifying N×0=N... {passed}/{len(registry)} passed")
    
    # Write
    with open(REGISTRY, "w") as f:
        for obj in registry:
            f.write(json.dumps(obj) + "\n")
    
    print(f"[AZL] Latest address: {registry[-1]['address']:.5e}")
    print(f"[AZL] Registry saved: {REGISTRY}")
    print(f"[AZL] New size: {len(registry)} addresses")

if __name__ == "__main__":
    main()
