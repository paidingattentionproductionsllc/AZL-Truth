#!/bin/bash
echo "Testing AZL Abyss v4.2 from absolute 0..."

abyss() {
  curl -s -X POST https://azl-universes.paidingattentionproductions.workers.dev/azl/v1/abyss \
  -H "Content-Type: application/json" \
  -d "{\"seed\":\"0\",\"target\":\"$1\",\"depth\":9,\"size\":1}" | jq .
}

echo "1. Absolute 0:" && abyss "0"
echo "2. Golden ratio:" && abyss "0.618033988749895" 
echo "3. 20 nines:" && abyss "0.99999999999999999999"
echo "4. Planck:" && abyss "0.0000000000000000000001616"
echo "5. Boundary test - should 1101:" && abyss "1.0"
