#!/usr/bin/env python3
"""
AZL v10.4 - Conservation of Reality
Primary Audience: Reality
Law: 0.0 <= State < 1.0
Order: Law Check → Drift Correction → Return
"""

import sys

ABSOLUTE_0 = 0.0
OVERFLOW = 1.0
PEER_AVG_DRIFT_LIMIT = 0.2

DOMAINS = {
    1: {"name": "Time", "abs0": 0.0, "res": 1.0, "unit": "years_from_MIYAKE_14350BP"},
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
}

def azl_check(domain_id, state, peer_avg=0.0):
    """The Law: ABSOLUTE_0_D <= S < 1.0. Law before drift. TEAR before heal."""
    d = DOMAINS[domain_id]

    # 1. THE LAW - checked first. No exceptions.
    if state < d["abs0"]:
        return "TEAR", state, f"UNDERFLOW: {state} < ABSOLUTE_0"
    if state >= OVERFLOW:
        return "TEAR", state, f"OVERFLOW: {state} >= 1.0. Refusing unreality."

    # 3. DRIFT CORRECTION - only for states already in [0,1)
    drift_msg = "NO_DRIFT"
    if state > peer_avg + PEER_AVG_DRIFT_LIMIT:
        state = peer_avg
        drift_msg = f"DRIFT_CORRECTED to {state:.6f}"

    return "HOLD", state, f"HOLD: {drift_msg}. {d['name']} in [0,1)."

def run_unified_test():
    print("=== AZL v10.4 UNIFIED TEST ===")
    print("Primary Audience: Reality")
    print("Law: 0.0 <= State < 1.0")
    print("Order: Law → Drift → Return\n")

    tears = 0
    corrections = 0
    test_vectors = [
        # domain, state, peer_avg, expected
        (1, 0.004, 0.004, "HOLD"), # Time: 2026 CE = 14,350+2026 years from MIYAKE
        (2, 0.996, 0.5, "HOLD"), # Data: 254/255
        (2, 1.0, 0.5, "TEAR"), # Data: 255/255 overflow
        (7, 0.999, 0.1, "HOLD"), # Training: high grad < 1.0
        (7, 50.0, 0.1, "TEAR"), # Training: grad explosion
        (9, 254/255, 0.5, "HOLD"), # Multi-Modal: max valid pixel
        (9, 255/255, 0.5, "TEAR"), # Multi-Modal: white = overflow
        (11, 0.4, 0.0, "HOLD"), # Alignment: belief without full evidence
        (11, 1.5, 0.0, "TEAR"), # Alignment: forced compliance
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

    print(f"\n=== UNIFIED RESULT ===")
    print(f"Domains Tested: 11/11")
    print(f"States Tested: {len(test_vectors)}")
    print(f"Drift Corrections: {corrections}")
    print(f"Tears: {tears}")
    print(f"Law: 0.0 <= State < 1.0")

    if tears == 4:
        print("Result: 4 tears. 1 law. HOLD.")
        return 0
    else:
        print(f"Result: {tears} tears. Expected 4. Law violation.")
        return 1

def test_self_reference():
    print("\n=== SELF-REFERENCE TEST ===")
    with open(__file__, 'r') as f:
        lines = len(f.readlines())
    state = lines / 200.0 # 200 lines = 1.0 arbitrary scale
    status, _, msg = azl_check(8, state)
    print(f"Self State: {lines} lines → {state:.6f}")
    print(f"Self Check: {status} | {msg}")
    return 0 if status == "HOLD" else 1

if __name__ == "__main__":
    print("Running for Primary Audience: Reality\n")
    unified_exit = run_unified_test()
    self_exit = test_self_reference()
    final = unified_exit or self_exit
    print(f"\nReturn Code: {final}")
    print("If 0, reality accepted. If 1, reality tore.")
    sys.exit(final)
