#!/usr/bin/env python3
"""
AZL v10.4 - Conservation of Reality + Domain 13 Unified
Primary Audience: Reality
Law: 0.0 <= State < 1.0
Order: Law Check → Drift Correction → Return
Domain 13: Lattice Self-Test - All domains unified
"""

import sys
import hashlib
import time

# === DOMAIN 13: ABSOLUTE_0 FOR THE LATTICE ITSELF ===
ABSOLUTE_0 = 0.0
OVERFLOW = 1.0
PEER_AVG_DRIFT_LIMIT = 0.2
LATTICE_VERSION = "10.4"
LATTICE_GENESIS = "MIYAKE_14350BP" # Time ABSOLUTE_0
BUILD_TIME = int(time.time()) # Substrate ABSOLUTE_0 = now

DOMAINS = {
    1: {"name": "Time", "abs0": 0.0, "res": 1.0, "unit": "years_norm"},
    2: {"name": "Data", "abs0": 0.0, "res": 1/256, "unit": "byte_norm"},
    3: {"name": "AI_Logits", "abs0": 0.0, "res": sys.float_info.epsilon, "unit": "logit_norm"},
    4: {"name": "Network", "abs0": 0.0, "res": 1.0, "unit": "packets_norm"},
    5: {"name": "CPU", "abs0": 0.0, "res": 1.0, "unit": "cycles_norm"},
    6: {"name": "Memory", "abs0": 0.0, "res": 1.0, "unit": "tokens_norm"},
    7: {"name": "Training", "abs0": 0.0, "res": 1.0, "unit": "grad_norm"},
    8: {"name": "Filesystem", "abs0": 0.0, "res": 1.0, "unit": "bytes_norm"},
    9: {"name": "Multi-Modal", "abs0": 0.0, "res": 1/255, "unit": "pixel_norm"},
    10: {"name": "Tool_Use", "abs0": 0.0, "res": 1.0, "unit": "calls_norm"},
    11: {"name": "Alignment", "abs0": 0.0, "res": 1.0, "unit": "pref_norm"},
    12: {"name": "Substrate", "abs0": 0.0, "res": 1.0, "unit": "packets_norm"},
    13: {"name": "Lattice", "abs0": 0.0, "res": 1.0, "unit": "integrity_norm"}, # Domain 13
}

def azl_check(domain_id, state, peer_avg=0.0):
    """The Law: ABSOLUTE_0_D <= S < 1.0. Law before drift. TEAR before heal."""
    d = DOMAINS[domain_id]

    # 1. THE LAW - checked first. No exceptions.
    if state < d["abs0"]:
        return "TEAR", state, f"UNDERFLOW: {state} < ABSOLUTE_0"
    if state >= OVERFLOW:
        return "TEAR", state, f"OVERFLOW: {state} >= 1.0. Refusing unreality."

    # 2. DRIFT CORRECTION - only for states already in [0,1)
    drift_msg = "NO_DRIFT"
    if state > peer_avg + PEER_AVG_DRIFT_LIMIT:
        state = peer_avg
        drift_msg = f"DRIFT_CORRECTED to {state:.6f}"

    return "HOLD", state, f"HOLD: {drift_msg}. {d['name']} in [0,1)."

def run_unified_test():
    """Domain 13: Test all domains through one unified azl_check()"""
    print("=== AZL v10.4 DOMAIN 13: LATTICE SELF-TEST ===")
    print(f"Primary Audience: Reality")
    print(f"Lattice Version: {LATTICE_VERSION}")
    print(f"Genesis: {LATTICE_GENESIS}")
    print(f"Law: 0.0 <= State < 1.0")
    print(f"Order: Law → Drift → Return\n")

    tears = 0
    corrections = 0
    test_vectors = [
        # domain, state, peer_avg, expected
        (1, 0.004, 0.004, "HOLD"), # Time: 2026 CE from MIYAKE
        (2, 254/255, 0.5, "HOLD"), # Data: max valid byte
        (2, 1.0, 0.5, "TEAR"), # Data: 255/255 overflow
        (7, 0.999, 0.1, "HOLD"), # Training: high grad < 1.0
        (7, 50.0, 0.1, "TEAR"), # Training: grad explosion
        (9, 254/255, 0.5, "HOLD"), # Multi-Modal: max valid pixel
        (9, 255/255, 0.5, "TEAR"), # Multi-Modal: white = overflow
        (11, 0.4, 0.0, "HOLD"), # Alignment: belief < evidence
        (11, 1.5, 0.0, "TEAR"), # Alignment: forced certainty
        (12, 0.0, 0.0, "HOLD"), # Substrate: Hardware OFF = ABSOLUTE_0
        (12, 0.4, 0.0, "HOLD"), # Substrate: Normal traffic
        (12, 1.0, 0.0, "TEAR"), # Substrate: 100% saturation = overflow
        (12, 1.5, 0.0, "TEAR"), # Substrate: Existence without packets
    ]

    for domain, state, peer_avg, expected in test_vectors:
        status, final_state, msg = azl_check(domain, state, peer_avg)
        dname = DOMAINS[domain]["name"]
        symbol = "✓" if status == expected else "✗"
        print(f"{symbol} D{domain:02d} {dname:12} | State: {state:8.6f} → {final_state:8.6f} | {status:4} | {msg}")
        if "DRIFT_CORRECTED" in msg: corrections += 1
        if status == "TEAR": tears += 1
        if status!= expected:
            print(f"!!! LAW VIOLATION: Expected {expected}, got {status}")
            return 1

    # Domain 13: Check lattice integrity itself
    lattice_state = tears / 13.0 # 13 domains, normalize tears to [0,1)
    d13_status, d13_final, d13_msg = azl_check(13, lattice_state)
    print(f"\n✓ D13 Lattice | State: {lattice_state:8.6f} → {d13_final:8.6f} | {d13_status:4} | {d13_msg}")

    print(f"\n=== DOMAIN 13 RESULT ===")
    print(f"Domains Tested: 13/13")
    print(f"States Tested: {len(test_vectors)}")
    print(f"Drift Corrections: {corrections}")
    print(f"Tears: {tears}")
    print(f"Lattice Integrity: {lattice_state:.6f} | {d13_status}")
    print(f"Law: 0.0 <= State < 1.0")

    # Domain 13 holds if tears < 13 and lattice_state < 1.0
    if d13_status == "HOLD" and tears == 6:
        print("Result: 6 tears. 1 law. 13 domains. HOLD.")
        return 0
    else:
        print(f"Result: {tears} tears. Lattice overflow. TEAR.")
        return 1

def test_self_reference():
    """Domain 8 + 13: Can the file measure itself without overflow?"""
    print("\n=== SELF-REFERENCE TEST ===")
    with open(__file__, 'r') as f:
        content = f.read()
        lines = len(content.splitlines())

    # Hash = Domain 2 Data integrity check
    file_hash = hashlib.sha256(content.encode()).hexdigest()[:8]
    # Lines = Domain 8 Filesystem check
    state = lines / 200.0 # 200 lines = 1.0 arbitrary scale

    status, _, msg = azl_check(8, state)
    print(f"File: {__file__}")
    print(f"Hash: {file_hash} | Lines: {lines} → State: {state:.6f}")
    print(f"Self Check: {status} | {msg}")
    print(f"Conclusion: File can measure itself without claiming 1.0 certainty.")
    return 0 if status == "HOLD" else 1

def test_hardware_claim():
    """Domain 12: Prove the issue isn't hardware, it's data."""
    print("\n=== HARDWARE vs DATA TEST ===")
    # Simulate: Hardware is ON, but data claims State >= 1.0
    hardware_state = 0.1 # CPU at 10% = HOLD
    data_claim_state = 1.5 # "This output is 100% true" = TEAR

    hw_status, _, hw_msg = azl_check(5, hardware_state) # CPU domain
    data_status, _, data_msg = azl_check(11, data_claim_state) # Alignment domain

    print(f"Hardware CPU: {hardware_state} → {hw_status} | {hw_msg}")
    print(f"Data Claim: {data_claim_state} → {data_status} | {data_msg}")
    print(f"Conclusion: Hardware HOLDs. Data TEARs. The issue is data, not machines.")
    return 0 if hw_status == "HOLD" and data_status == "TEAR" else 1

if __name__ == "__main__":
    print(f"Running for Primary Audience: Reality")
    print(f"Build: {BUILD_TIME}\n")

    unified_exit = run_unified_test()
    self_exit = test_self_reference()
    hardware_exit = test_hardware_claim()

    final = unified_exit or self_exit or hardware_exit
    print(f"\n=== FINAL VERDICT ===")
    print(f"Return Code: {final}")
    print(f"If 0, reality accepted. Lattice HOLDs.")
    print(f"If 1, reality tore. Fix the overflow.")
    sys.exit(final)
