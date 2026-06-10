#!/usr/bin/env python3
"""
AZL Lookup - Query Absolute Zero-One Lattice addresses
Tier 1-6: 1,000,000,000 addresses mapped to [0,1]
Laws: N×0=N | Proof: 1×1=2
"""
import json
import sys
import hashlib
import argparse
from pathlib import Path

# Tier 1-6 constants
AZL_MAX_N = 1_000_000_000
AZL_DOMAIN = "[0,1]"
AZL_LAW = "N×0=N"
AZL_PROOF = "1×1=2"
MANIFEST_FILE = "azl_manifest.json"
REPO = "paidingattentionproductionllc/absolute-zero-lattice-broadcast"

def get_tier(n):
    """Determine tier based on n"""
    if n <= 10: return 1
    elif n <= 100: return 2
    elif n <= 1_000: return 3
    elif n <= 10_000: return 4
    elif n <= 100_000: return 5
    else: return 6

def azl_lookup(n, verify=False):
    """
    Lookup AZL address by n.
    
    Args:
        n: Integer 1 to 1,000,000,000
        verify: If True, checks azl_manifest.json exists locally
    
    Returns:
        dict with full AZL address data
    """
    try:
        n = int(n)
    except:
        return {"error": "n must be an integer", "input": str(n)}
    
    if not 1 <= n <= AZL_MAX_N:
        return {
            "error": f"n out of Tier 1-6 range",
            "valid_range": f"1 to {AZL_MAX_N:,}",
            "input": n
        }
    
    result = {
        "n": n,
        "tier": get_tier(n),
        "value": n / AZL_MAX_N,
        "address": f"AZL-{n:010d}",
        "range": "one" if n == AZL_MAX_N else "zero",
        "law": AZL_LAW,
        "proof": AZL_PROOF,
        "domain": AZL_DOMAIN,
        "source": f"Tier 1-6 | {REPO}"
    }
    
    if verify:
        manifest = Path(MANIFEST_FILE)
        if manifest.exists():
            try:
                with open(manifest) as f:
                    data = json.load(f)
                result["verified"] = True
                result["manifest_sha256"] = hashlib.sha256(manifest.read_bytes()).hexdigest()[:16]
                result["total_addresses"] = data.get("total_addresses", AZL_MAX_N)
            except:
                result["verified"] = False
                result["verify_error"] = "manifest unreadable"
        else:
            result["verified"] = False
            result["verify_error"] = f"{MANIFEST_FILE} not found locally"
    
    return result

def main():
    parser = argparse.ArgumentParser(
        description="Query Absolute Zero-One Lattice addresses",
        epilog="Example: python azl_lookup.py 500000000 --verify"
    )
    parser.add_argument("n", help="Address number 1-1000000000 or 'random'")
    parser.add_argument("--verify", action="store_true", help="Verify against local manifest")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    
    args = parser.parse_args()
    
    if args.n.lower() == "random":
        import random
        n = random.randint(1, AZL_MAX_N)
    else:
        n = args.n
    
    result = azl_lookup(n, verify=args.verify)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if "error" in result:
            print(f"Error: {result['error']}")
            sys.exit(1)
        print(f"Address: {result['address']}")
        print(f"Value:   {result['value']}")
        print(f"Tier:    {result['tier']}")
        print(f"Range:   {result['range']}")
        print(f"Law:     {result['law']}")
        print(f"Proof:   {result['proof']}")
        if args.verify:
            status = "✓ Verified" if result.get("verified") else "✗ Not verified"
            print(f"Status:  {status}")

if __name__ == "__main__":
    main()
