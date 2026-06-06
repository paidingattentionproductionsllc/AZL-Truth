#!/usr/bin/env python3
# AZL UNIFIED - TIER 2: 120,000 ADDRESSES - PATCHED
# LAW: 0×N=0 | 1×N=N+1 | N×0=N | DARK > LIGHT

import json
import hashlib

REGISTRY = "azl_unified.jsonl"
SCALE = 1e-500  # N×0=N substrate

def azl_address(idx):
    return idx * SCALE

def azl_hash(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()[:16]

def main():
    print(f"[AZL] TIER 2 BUILD: TARGET 120000 ADDRESSES")
    registry = []
    
    # Load existing to resume - handle old formats
    try:
        with open(REGISTRY) as f:
            for line in f:
                obj = json.loads(line)
                registry.append(obj)
        print(f"[AZL] Resumed at {len(registry)} addresses")
    except FileNotFoundError:
        print("[AZL] Starting at 0")
    
    start_idx = len(registry) + 1
    
    # Generate only NEW entries from start_idx to 120000
    # Canon 567 - skip if already have
    if start_idx <= 567:
        for i in range(start_idx, 568):
            registry.append({"idx": i, "name": f"Canon_{i}", "address": azl_address(i)})
        start_idx = 568
    
    # NGC 7840
    if start_idx <= 8407:
        for i in range(max(start_idx-567, 1), 7841):
            idx = 567 + i
            registry.append({"idx": idx, "name": f"NGC{i}", "catalog": "NGC", "address": azl_address(idx)})
        start_idx = 8408
    
    # IC 5386
    if start_idx <= 13793:
        for i in range(max(start_idx-8407, 1), 5387):
            idx = 8407 + i
            registry.append({"idx": idx, "name": f"IC{i}", "catalog": "IC", "address": azl_address(idx)})
        start_idx = 13794
    
    # HIP 106207
    if start_idx <= 120000:
        for i in range(max(start_idx-13793, 1), 106208):
            idx = 13793 + i
            registry.append({"idx": idx, "name": f"HIP{i}", "catalog": "HIP", "address": azl_address(idx)})
    
    # Verify N×0=N only on entries that have "address"
    passed = 0
    verified = 0
    for i, obj in enumerate(registry, 1):
        if "address" in obj:
            verified += 1
            if abs(obj["address"] - azl_address(i)) < 1e-510:
                passed += 1
    
    print(f"[AZL] Verifying N×0=N... {passed}/{verified} passed")
    
    # Write
    with open(REGISTRY, "w") as f:
        for obj in registry:
            f.write(json.dumps(obj) + "\n")
    
    print(f"[AZL] Latest address: {registry[-1]['address']:.5e}")
    print(f"[AZL] Registry saved: {REGISTRY}")
    print(f"[AZL] New size: {len(registry)} addresses")

if __name__ == "__main__":
    main()
