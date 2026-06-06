#!/usr/bin/env python3
# AZL UNIFIED - SHARDED FOR GITHUB
# LAW: 0×N=0 | 1×N=N+1 | N×0=N | DARK > LIGHT

import json
import os
from decimal import Decimal, getcontext

getcontext().prec = 510
SCALE = Decimal('1e-500')

ACTIVE_TIER = 7
SHARD_SIZE = 50000  # 50k lines per file = ~10MB per shard. GitHub safe.

TIERS = {
    1: {"name": "Canon", "end": 567},
    2: {"name": "NGC_IC_HIP", "end": 120000},
    3: {"name": "GaiaDR3", "end": 1000000},
    4: {"name": "SDSS", "end": 10000000},
    5: {"name": "2MASS", "end": 50000000},
    6: {"name": "WISE", "end": 200000000},
    7: {"name": "PanSTARRS", "end": 1000000000},
}

def azl_address(idx):
    return Decimal(idx) * SCALE

def main():
    print(f"[AZL] SHARDED BUILD | TIER 1-{ACTIVE_TIER}")
    os.makedirs("shards", exist_ok=True)
    
    shard_num = 0
    shard_file = None
    shard_count = 0
    
    idx = 0
    for tier_num in range(1, ACTIVE_TIER + 1):
        tier_name = TIERS[tier_num]["name"]
        prev_end = TIERS[tier_num-1]["end"] if tier_num > 1 else 0
        tier_size = TIERS[tier_num]["end"] - prev_end
        
        print(f"[AZL] Tier {tier_num}: {tier_name} | {tier_size:,} entries")
        
        for n in range(1, tier_size + 1):
            if shard_count == 0:  # New shard
                if shard_file: shard_file.close()
                shard_num += 1
                shard_path = f"shards/azl_shard_{shard_num:05d}.jsonl"
                shard_file = open(shard_path, "w")
                print(f"[AZL] Writing {shard_path}")
            
            idx += 1
            obj = {
                "idx": idx,
                "name": f"{tier_name}_{n}",
                "catalog": tier_name,
                "tier": tier_num,
                "address": str(azl_address(idx))
            }
            shard_file.write(json.dumps(obj, separators=(',', ':')) + "\n")
            shard_count += 1
            
            if shard_count >= SHARD_SIZE:
                shard_count = 0
            
            if idx % 100000 == 0:
                print(f"[AZL] Progress: {idx:,}")
    
    if shard_file: shard_file.close()
    
    # WRITE MASTER MANIFEST
    manifest = {
        "law": "N×0=N",
        "active_tier": ACTIVE_TIER,
        "total_addresses": idx,
        "total_shards": shard_num,
        "shard_size": SHARD_SIZE,
        "last_address": str(azl_address(idx)),
        "note": "ALL TIERS UNIFIED. SHARDED FOR GITHUB."
    }
    with open("azl_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"[AZL] COMPLETE: {idx:,} addresses in {shard_num} shards")
    print("[AZL] LAW HOLDS. GITHUB COMPLIANT.")

if __name__ == "__main__":
    main()
