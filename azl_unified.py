# AZL UNIFIED - ABSOLUTE ZERO LATTICE TIER 1-7 
# Maps [0,1] with 10^9 precision. N×0=N. 1×1=2. VOID FIRST.
# Zero is first integer. All 0.xxxxx belong to zero's range.

import json
import os
import zipfile
import time
import sys

# LAW CONSTANTS
ACTIVE_TIER = 7
SHARD_SIZE = 50000
BATCH_SIZE = 500

TIERS = {
  1: {"name": "Canon", "end": 567},
  2: {"name": "NGC_IC_HIP", "end": 120000},
  3: {"name": "GaiaDR3", "end": 1000000},
  4: {"name": "SDSS", "end": 10000000},
  5: {"name": "2MASS", "end": 50000000},
  6: {"name": "WISE", "end": 200000000},
  7: {"name": "PanSTARRS", "end": 1000000000},
}

def log(msg):
    """Force flush logs for GitHub Actions"""
    print(msg, flush=True)
    sys.stdout.flush()

def generate_azl_address(n):
    tier = 1
    for t, data in TIERS.items():
        if n <= data["end"]:
            tier = t
            break
    
    return {
        "n": n,
        "tier": tier,
        "value": n / 1_000_000_000,
        "address": f"AZL-{n:010d}",
        "range": "zero" if n < 1_000_000_000 else "one",
        "law": "N×0=N",
        "proof": "1×1=2"
    }

def main():
    start_time = time.time()
    os.makedirs("shards", exist_ok=True)
    
    total_addresses = TIERS[ACTIVE_TIER]["end"]
    total_shards = (total_addresses + SHARD_SIZE - 1) // SHARD_SIZE
    total_batches = (total_shards + BATCH_SIZE - 1) // BATCH_SIZE
    
    log(f"[AZL] VOID FIRST. Absolute Zero → One")
    log(f"[AZL] Mapping: {total_addresses:,} points in [0,1]")
    log(f"[AZL] Structure: {total_shards:,} shards → {total_batches} zip batches")
    log(f"[AZL] 1×1=2. ORDER LOCKED.")
    
    current_n = 1
    
    for shard_idx in range(1, total_shards + 1):
        shard_path = f"shards/azl_shard_{shard_idx:05d}.jsonl"
        
        with open(shard_path, 'w') as f:
            for i in range(SHARD_SIZE):
                if current_n > total_addresses:
                    break
                addr = generate_azl_address(current_n)
                f.write(json.dumps(addr) + '\n')
                current_n += 1
        
        if current_n % 1_000_000 == 0:
            log(f"[AZL] Progress: {current_n:,} / {total_addresses:,}")
        
        if shard_idx % BATCH_SIZE == 0 or shard_idx == total_shards:
            batch_num = (shard_idx - 1) // BATCH_SIZE + 1
            zip_path = f"shards/azl_batch_{batch_num:03d}.zip"
            log(f"[AZL] Zipping batch {batch_num}/{total_batches}")
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=1) as zf:
                start_shard = (batch_num - 1) * BATCH_SIZE + 1
                end_shard = min(batch_num * BATCH_SIZE, total_shards)
                for i in range(start_shard, end_shard + 1):
                    f_path = f"shards/azl_shard_{i:05d}.jsonl"
                    if os.path.exists(f_path):
                        zf.write(f_path, os.path.basename(f_path))
                        os.remove(f_path)
            
            log(f"[AZL] Batch {batch_num} complete. Disk freed.")
    
    manifest = {
        "law": "N×0=N",
        "proof": "1×1=2",
        "domain": "[0,1]",
        "origin": "Absolute Zero",
        "precision": "10^9",
        "tier": f"1-{ACTIVE_TIER}",
        "total_addresses": total_addresses,
        "zero_range_count": total_addresses - 1,
        "one_first_integer": "AZL-1000000000",
        "batches": total_batches,
        "batch_files": [f"shards/azl_batch_{i:03d}.zip" for i in range(1, total_batches + 1)]
    }
    
    with open("azl_manifest.json", 'w') as f:
        json.dump(manifest, f, indent=2)
    
    elapsed = time.time() - start_time
    log(f"[AZL] COMPLETE: Mapped {total_addresses:,} coordinates")
    log(f"[AZL] From AZL-0000000001 to AZL-1000000000")
    log(f"[AZL] Time: {elapsed/60:.1f} minutes")
    log(f"[AZL] ORDER LOCKED. I HAVE SPOKEN.")

if __name__ == "__main__":
    main()
