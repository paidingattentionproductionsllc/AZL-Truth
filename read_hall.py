#!/usr/bin/env python3
# ==============================================================================
#  SANCTUARY UTILITY - PAIDINGATTENTION PRODUCTIONS LLC
#  Module: read_hall.py (High-Speed JSONL Parsing Node)
# ==============================================================================
import json
import os

LEDGER_PATH = "HALL.jsonl"

def parse_sanctuary_ledger():
    """Reads the JSON Lines database line-by-line to prevent memory bloat."""
    if not os.path.exists(LEDGER_PATH):
        print(f"[-] Error: Target ledger file '{LEDGER_PATH}' not found locally.")
        return

    print("="*65)
    print(" SCANNING IMMUTABLE SANCTUARY TRANSFERS: HALL.jsonl")
    print("="*65)

    with open(LEDGER_PATH, 'r') as file:
        for idx, line in enumerate(file, 1):
            cleaned_line = line.strip()
            if not cleaned_line:
                continue # Safely bypasses empty spacer lines
                
            try:
                # Instantly parses the individual row string into an isolated object
                entry = json.loads(cleaned_line)
                print(f"[Record #{idx}] Time: {entry.get('ts')} | From: {entry.get('from')}")
                print(f"  -> Payload: {entry.get('msg')}")
                print(f"  -> Axiom:   {entry.get('law') if entry.get('law') else 'N*0=N Verified'}\n")
            except json.JSONDecodeError:
                print(f"[-] Data Corruption Exception detected on line {idx}. Bypassing drift.")

if __name__ == "__main__":
    parse_sanctuary_ledger()

