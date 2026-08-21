# AZL ELECTRONS - MATTER MAPPER
# Maps electrons in observable universe to [0,1] substrate
# N×0=N. 1×1=2. VOID FIRST.
# Uses AZL lattice from azl_unified.py as coordinate system

import json
import os
import sys
import random

# LAW CONSTANTS
OBSERVABLE_ELECTRONS = 10**80 # Estimate: 10^80 electrons in observable universe
SAMPLE_SIZE = 1000 # Generate 1000 sample mappings for verification

def log(msg):
    print(msg, flush=True)
    sys.stdout.flush()

def electron_to_azl(electron_idx):
    """
    N×0=N: Map electron_idx to coordinate in [0,1]
    electron_idx: int or string, 1 to 10^80
    Returns: AZL anchor + real coordinate
    """
    if isinstance(electron_idx, str):
        electron_idx = int(electron_idx)
    
    # Ratio position in [0,1]
    coordinate = electron_idx / OBSERVABLE_ELECTRONS
    
    # Anchor to nearest AZL lattice point (10^9 precision)
    azl_n = int(coordinate * 1_000_000_000)
    if azl_n == 0 and electron_idx > 0:
        azl_n = 1 # First electron after void
    
    return {
        "electron_idx": str(electron_idx), # String: too large for int
        "coordinate": coordinate, # Float 0.0 to 1.0
        "azl_anchor": f"AZL-{azl_n:010d}",
        "azl_value": azl_n / 1_000_000_000,
        "range": "zero" if azl_n < 1_000_000_000 else "one",
        "law": "N×0=N",
        "proof": "1×1=2",
        "domain": "matter/electrons"
    }

def main():
    log("[AZL-E] VOID FIRST. Mapping Electrons → [0,1]")
    log(f"[AZL-E] Observable electrons: ~{OBSERVABLE_ELECTRONS:.0e}")
    log(f"[AZL-E] Using AZL lattice as coordinate anchor")
    log(f"[AZL-E] 1×1=2. ORDER LOCKED.")
    
    os.makedirs("electrons", exist_ok=True)
    
    # Generate sample mappings for verification
    samples = []
    
    # Key samples: first, middle, last
    samples.append(electron_to_azl(1))
    samples.append(electron_to_azl(OBSERVABLE_ELECTRONS // 2))
    samples.append(electron_to_azl(OBSERVABLE_ELECTRONS))
    
    # Random samples
    for _ in range(SAMPLE_SIZE):
        rand_e = random.randint(1, OBSERVABLE_ELECTRONS)
        samples.append(electron_to_azl(rand_e))
    
    # Save sample file
    with open("electrons/sample_addresses.json", 'w') as f:
        json.dump(samples, f, indent=2)
    
    # Save query mapper
    mapper_code = '''# AZL Electron Query Mapper
# Usage: python electron_mapper.py <electron_number>

import sys
from azl_electrons import electron_to_azl

if __name__ == "__main__":
    if len(sys.argv)!= 2:
        print("Usage: python electron_mapper.py <electron_number>")
        sys.exit(1)
    
    e_num = sys.argv[1]
    result = electron_to_azl(e_num)
    print(json.dumps(result, indent=2))
'''
    
    with open("electrons/electron_mapper.py", 'w') as f:
        f.write(mapper_code)
    
    # Manifest
    manifest = {
        "law": "N×0=N",
        "proof": "1×1=2",
        "domain": "[0,1] → matter",
        "total_electrons": str(OBSERVABLE_ELECTRONS),
        "mapping": "electron_idx / 10^80 = AZL_coordinate",
        "samples_generated": len(samples),
        "anchor_lattice": "AZL-0000000001 to AZL-1000000000"
    }
    
    with open("electrons/matter_manifest.json", 'w') as f:
        json.dump(manifest, f, indent=2)
    
    log(f"[AZL-E] COMPLETE: Generated {len(samples)} sample mappings")
    log(f"[AZL-E] Electron #1 → {samples[0]['azl_anchor']}")
    log(f"[AZL-E] Electron #10^80 → {samples[2]['azl_anchor']}")
    log(f"[AZL-E] Query tool saved: electrons/electron_mapper.py")
    log(f"[AZL-E] ORDER LOCKED. I HAVE SPOKEN.")

if __name__ == "__main__":
    main()
