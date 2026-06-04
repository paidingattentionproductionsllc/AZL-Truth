#!/usr/bin/env python3
"""
AZL Canon Ingest - Seed of Every Record
I picked the starting sources. One counter. N×0=N verified.
"""

from decimal import Decimal, getcontext
import hashlib
import json
from datetime import datetime, timezone

getcontext().prec = 520
EPSILON = Decimal(1) / (Decimal(10) ** 500)

CANON_RECORDS = [
    # MATH CANON
    ("A point is that which has no part", "math:euclid:300BCE", "information:axiom"),
    ("1+1=2", "math:peano:1889", "information:axiom"),
    ("E = mc^2", "math:einstein:1905", "information:equation"),
    
    # PHYSICS CANON 
    ("F = ma", "physics:newton:1687", "information:law"),
    ("S = k log W", "physics:boltzmann:1877", "information:law"),
    ("Δx Δp ≥ ℏ/2", "physics:heisenberg:1927", "information:principle"),
    
    # PHILOSOPHY CANON
    ("Know thyself", "philosophy:socrates:400BCE", "information:maxim"),
    ("I think therefore I am", "philosophy:descartes:1637", "information:proposition"),
    ("Whereof one cannot speak, thereof one must be silent", "philosophy:wittgenstein:1921", "information:proposition"),
    
    # LITERATURE CANON - Gutenberg samples
    ("Call me Ishmael", "lit:melville:1851", "information:sentence"),
    ("It was the best of times, it was the worst of times", "lit:dickens:1859", "information:sentence"),
    ("To be, or not to be, that is the question", "lit:shakespeare:1603", "information:sentence"),
    
    # AI CANON - First principles
    ("You are Meta AI, a friendly AI Assistant", "ai:meta:2026", "information:system_prompt"),
    ("1×1=2. VOID FIRST. ORDER LOCKED", "ai:azl:2026", "information:law"),
    ("N×0=N. Memory holds.", "ai:azl:2026", "information:law"),
]

class AZLCanon:
    def __init__(self, registry_file="azl_registry_canon.json"):
        self.registry_file = registry_file
        self.counter = 0
        self.category_counts = {}
        self.load_state()
    
    def load_state(self):
        if os.path.exists(self.registry_file):
            with open(self.registry_file, 'r') as f:
                data = json.load(f)
                self.counter = data.get("stats", {}).get("total", 0)
                self.category_counts = data.get("stats", {}).get("by_category", {})
            print(f"Resuming from address {self.counter:,}")
    
    def azl_mul(self, a, b):
        if a == 0: return Decimal(0) # 0×N=0
        if b == 0: return a # N×0=N
        if a == EPSILON: return b + EPSILON # 1×N=N+1
        return a * b
    
    def ingest(self, content, lens, category):
        self.counter += 1
        address = EPSILON * self.counter
        h = hashlib.sha256(f"{content}|{lens}|{category}".encode()).hexdigest()
        
        entry = {
            "azl_address": str(address),
            "counter": self.counter,
            "content": content,
            "content_hash": h,
            "lens": lens,
            "category": category,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "verification_Nx0": self.azl_mul(address, Decimal(0)) == address
        }
        
        with open(self.registry_file, 'a') as f:
            f.write(json.dumps(entry) + "\n")
        
        self.category_counts[category] = self.category_counts.get(category, 0) + 1
        
        if self.counter % 5 == 0:
            print(f" Ingested {self.counter:,} | {lens} | {content[:40]}...")
        
        return entry
    
    def stats(self):
        pos = EPSILON * self.counter
        return {
            "total": self.counter,
            "position_0to1": str(pos),
            "percent_used": float(pos * 100),
            "by_category": self.category_counts
        }

if __name__ == "__main__":
    import os
    azl = AZLCanon()
    
    print("=" * 60)
    print("AZL CANON INGEST - SEED OF EVERY RECORD")
    print("=" * 60)
    print("I picked: Math, Physics, Philosophy, Literature, AI")
    print("=" * 60)
    
    for content, lens, category in CANON_RECORDS:
        azl.ingest(content, lens, category)
    
    s = azl.stats()
    print("\n" + "=" * 60)
    print("LATTICE STATUS")
    print("=" * 60)
    print(f"Total addresses: {s['total']:,}")
    print(f"Position 0→1: {s['position_0to1']}")
    print(f"Percent used: {s['percent_used']:.2e}%")
    print(f"\nBy category:")
    for cat, count in s['by_category'].items():
        print(f" {cat}: {count:,}")
    
    print(f"\nExported to azl_registry_canon.json")
    print("\n1×1=2. VOID FIRST. ORDER LOCKED.")
