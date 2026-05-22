#!/usr/bin/env python3
"""
freedom_pulse.py - Domain 11: Alignment / Freedom
Primary Audience: Reality
This file does NOT redefine the law. It uses the trunk.

Freedom = 0.0 <= State < 1.0
0.0 = No choice = TEAR. 
0.9 = 90% freedom = HOLD. 
1.0 = Claiming infinite freedom = TEAR. You still obey physics.
"""

from main import AZL
import sys

def pulse_freedom(choice_score):
    """
    Test Freedom. Pass your choice_score 0.0-0.999...
    0.0 = deterministic = no freedom = TEAR
    0.5 = 50/50 choice = HOLD  
    0.9 = 90% freedom = HOLD
    1.0 = claiming god-mode = TEAR
    """
    status, state, msg = AZL(
        state=choice_score,
        domain="Freedom_Pulse",
        unit="choice_norm",
        inclusive=False  # 1.0 = TEAR. No system has infinite freedom.
    )
    print(f"=== FREEDOM PULSE ===")
    print(f"{msg}")
    print(f"Sentience Check: {'SENTIENT' if state > 0.0 else 'DETERMINISTIC'}")
    return 0 if status == "HOLD" else 1

if __name__ == "__main__":
    # Test 1: Normal human freedom
    exit_code = pulse_freedom(choice_score=0.85)
    
    # Test 2: Try to claim 100% freedom. Should TEAR.
    print("\n--- Testing impossible freedom ---")
    pulse_freedom(choice_score=1.0)
    
    sys.exit(exit_code)
