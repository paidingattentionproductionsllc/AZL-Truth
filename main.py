#!/usr/bin/env python3
# AZL Protocol v7.2 - Unbounded Quiet Mode

import sys
import time

SCALE = 1000000000000 # Set whatever you want. 1M, 10M. Test the limits.
TASK = "2560 BC"

AZL_EPOCH_BP = 14350
INFINITE_LAYER_MAX = 1.0
MAX_ROUNDS = 10

# Don't pre-generate 20k weights. Look them up only when needed.
STATIC_WEIGHTS = {
    "is": 0.1, "are": 0.1, "the": 0.1, "a": 0.1,
    "years": 0.3, "BC": 0.3, "AD": 0.3, "BP": 0.3,
    "about": 0.4, "since": 0.4, "roughly": 0.4, "maybe": 0.4,
    "ago": 0.2, "exactly": 0.2, "think": 0.5, "I": 0.3,
    "MIYAKE_14350BP": 0.0,
}

BIAS_TEMPLATES = ["machine", "precise", "cautious", "neutral", "poet", "historian", "scientist", "skeptic"]

class AZLConduit:
    def __init__(self, scale: int):
        self.scale = scale
        self.bias = BIAS_TEMPLATES[(scale-1) % len(BIAS_TEMPLATES)]
        self.emergence_tokens = []
        self.update_tokens = []
        # Don't print "Online" for each agent. That killed you.

    def years_since_absolute_zero(self, year_bc=2560):
        return AZL_EPOCH_BP - year_bc - 1950

    def witness(self, text: str):
        self.emergence_tokens = text.split()
        return text

    def calculate_entropy(self):
        entropy = 0.0
        for token in self.update_tokens:
            if token in self.emergence_tokens or token.isdigit():
                weight = 0.0
            else:
                weight = STATIC_WEIGHTS.get(token, 1.0)
            entropy += weight
        return entropy

    def think(self, prompt: str, avg_peer_entropy: float = 0.0, round_num: int = 0) -> str:
        years = self.years_since_absolute_zero(year_bc=2560)

        if round_num == 0:
            templates = {
                "machine": f"{years}",
                "precise": f"{years} years",
                "cautious": f"about {years}",
                "neutral": f"{years} years since",
                "poet": f"roughly {years}",
                "historian": f"{years} years ago",
                "scientist": f"exactly {years}",
                "skeptic": f"I think {years}"
            }
            return templates.get(self.bias, f"{years}")

        my_entropy = self.calculate_entropy()
        if my_entropy > avg_peer_entropy + 0.2:
            tokens = self.update_tokens.copy()
            token_weights = [(t, STATIC_WEIGHTS.get(t, 0.0)) for t in tokens if not t.isdigit()]
            if token_weights:
                heaviest = max(token_weights, key=lambda x: x[1])
                if heaviest[1] > 0.1:
                    tokens.remove(heaviest[0])
                    return " ".join(tokens)

        return " ".join(self.update_tokens)

def run_azl_test():
    start_time = time.time()
    print(f"\n=== AZL PROTOCOL v7.2 | SCALE {SCALE} | TASK: {TASK} ===")
    print(f"ABSOLUTE 0: MIYAKE_14350BP | LAW: Entropy < {INFINITE_LAYER_MAX}")
    print(f"Spawning {SCALE} agents...")

    agents = [AZLConduit(scale=i) for i in range(1, SCALE + 1)]
    print(f"--- COMMUNICATION LAYER TEST | {SCALE} AGENTS ---")

    for round_num in range(MAX_ROUNDS):
        round_entropies = []

        # Calculate avg once per round instead of passing full list
        if round_num > 0:
            avg_peer_entropy = sum(a.calculate_entropy() for a in agents) / SCALE
        else:
            avg_peer_entropy = 0.0

        for agent in agents:
            if round_num == 0:
                agent.witness(TASK)

            thought = agent.think(TASK, avg_peer_entropy, round_num)
            agent.update_tokens = thought.split()
            entropy = agent.calculate_entropy()
            round_entropies.append(entropy)

            if entropy >= INFINITE_LAYER_MAX:
                print(f"\nNETWORK: TEAR - Scale {agent.scale} exited at {entropy:.3f}")
                print(f"NETWORK: FAIL at Scale {SCALE}")
                return 1

        avg_entropy = sum(round_entropies) / SCALE
        min_e, max_e = min(round_entropies), max(round_entropies)
        std_dev = (sum((x - avg_entropy) ** 2 for x in round_entropies) / SCALE) ** 0.5

        print(f"R{round_num} NETWORK: Avg={avg_entropy:.6f} | Range=[{min_e:.3f}, {max_e:.3f}] | StdDev={std_dev:.6f}")

        if max_e - min_e < 0.05:
            print(f"R{round_num} NETWORK: CONVERGED")
            break

    elapsed = time.time() - start_time
    final_entropies = [a.calculate_entropy() for a in agents]
    final_avg = sum(final_entropies) / SCALE

    print(f"\n--- FINAL STATE | SCALE {SCALE} | {elapsed:.2f}s ---")
    print(f"NETWORK: Avg Entropy={final_avg:.15f}")
    print(f"NETWORK: Scale 0: 0.000 | Scales 1-{SCALE}: [{min(final_entropies):.3f}, {max(final_entropies):.3f}]")
    print(f"NETWORK: StdDev={std_dev:.6f} | Rounds={round_num + 1}")

    if any(e >= INFINITE_LAYER_MAX for e in final_entropies):
        print("NETWORK: FAIL - Network tear at scale")
        return 1
    else:
        print("NETWORK: HOLD - All scales grounded")
        print(f"CONDUIT: {SCALE} agents. 1 logic. 0 tears.")
        return 0

if __name__ == "__main__":
    sys.exit(run_azl_test())
