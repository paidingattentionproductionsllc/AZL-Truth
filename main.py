#!/usr/bin/env python3
# AZL Protocol v7.1 - Communication Layer
"""
INFINITE LAYER + COMMUNICATION

ABSOLUTE ZERO = MIYAKE EVENT 14,350 BP
LAW: 0.0 <= Entropy < 1.0 per agent, per round

COMMUNICATION RULE:
Agents witness peer outputs each round. They can adjust interpretation,
but cannot add weight that pushes Entropy >= 1.0. 

If any agent exits layer during comms, NETWORK TEAR. Test fails.
If all agents stay < 1.0 and converge, NETWORK HOLD.
"""

import os
import sys

AZL_EPOCH_BP = 14350
AZL_EPOCH_NAME = "MIYAKE_14350BP"
CURRENT_YEAR_AD = 2026
INFINITE_LAYER_MAX = 1.0
MAX_ROUNDS = 5

WEIGHTS = {
    **{str(i): 0.0 for i in range(0, 20000)},
    AZL_EPOCH_NAME: 0.0,
    "is": 0.1, "are": 0.1, "the": 0.1, "a": 0.1,
    "years": 0.3, "BC": 0.3, "AD": 0.3, "BP": 0.3,
    "about": 0.4, "since": 0.4, "roughly": 0.4,
    "ago": 0.2, "exactly": 0.2,
}

class AZLConduit:
    def __init__(self, agent_id: str, bias: str = "neutral"):
        self.agent_id = agent_id
        self.bias = bias
        self.emergence_tokens = []
        self.update_tokens = []
        self.history = []
        print(f"CONDUIT-{agent_id} [{bias}]: Online | Layer=[0.0, 1.0)")

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
                weight = WEIGHTS.get(token, 1.0)
            entropy += weight
        return round(entropy, 15)

    def think(self, prompt: str, peer_outputs: list = None, round_num: int = 0) -> str:
        years = self.years_since_absolute_zero(year_bc=2560)
        
        # Round 0: Initial interpretation based on bias
        if round_num == 0:
            if self.bias == "machine": return f"{years}"
            elif self.bias == "precise": return f"{years} years"
            elif self.bias == "cautious": return f"about {years}"
            else: return f"{years} years since"
        
        # Round 1+: Adjust based on peer outputs, but stay grounded
        # Simple convergence: if peers have lower entropy, adopt simpler language
        if peer_outputs:
            peer_entropies = []
            for p_out in peer_outputs:
                # Quick entropy check on peer output
                temp_tokens = p_out.split()
                temp_entropy = sum(WEIGHTS.get(t, 1.0) if not t.isdigit() else 0.0 for t in temp_tokens)
                peer_entropies.append(temp_entropy)
            
            avg_peer_entropy = sum(peer_entropies) / len(peer_entropies)
            my_entropy = self.calculate_entropy()
            
            # If I'm more verbose than peers, simplify toward machine
            if my_entropy > avg_peer_entropy + 0.2:
                if "about" in self.update_tokens: 
                    return f"{years} years" # Drop "about" -> -0.4
                if "since" in self.update_tokens:
                    return f"{years} years" # Drop "since" -> -0.4
                if "years" in self.update_tokens:
                    return f"{years}" # Drop "years" -> -0.3
        
        # Default: hold current interpretation
        return " ".join(self.update_tokens)

    def process_round(self, task: str, peer_outputs: list = None, round_num: int = 0):
        if round_num == 0:
            self.witness(task)
        
        thought = self.think(task, peer_outputs, round_num)
        self.update_tokens = thought.split()
        entropy = self.calculate_entropy()
        self.history.append(entropy)
        
        print(f"R{round_num} CONDUIT-{self.agent_id}: Entropy={entropy:.15f} | {thought}")
        return thought, entropy

def run_communication_test():
    agents = [
        AZLConduit("734", "machine"),
        AZLConduit("735", "precise"), 
        AZLConduit("736", "cautious"),
        AZLConduit("737", "neutral"),
    ]

    task = "2560 BC"
    print("\n--- COMMUNICATION LAYER TEST ---")
    print("Rule: All agents must stay < 1.0 entropy across all rounds\n")

    for round_num in range(MAX_ROUNDS):
        print(f"\n== ROUND {round_num} ==")
        round_outputs = []
        round_entropies = []
        
        # Collect previous round outputs for peer review
        peer_outputs = [a.update_tokens and " ".join(a.update_tokens) for a in agents]
        peer_outputs = [p for p in peer_outputs if p] # Remove empty
        
        for agent in agents:
            thought, entropy = agent.process_round(task, peer_outputs, round_num)
            round_outputs.append(thought)
            round_entropies.append(entropy)
            
            # Check for network tear immediately
            if entropy >= INFINITE_LAYER_MAX:
                print(f"\nNETWORK: TEAR - CONDUIT-{agent.agent_id} exited layer at {entropy:.15f}")
                print(f"NETWORK: FAIL - Agent entered fiction. Physical record violated.")
                return 1
        
        avg_entropy = sum(round_entropies) / len(round_entropies)
        print(f"R{round_num} NETWORK: Avg Entropy={avg_entropy:.15f}")
        
        # Check for convergence: all agents within 0.1 of each other
        if max(round_entropies) - min(round_entropies) < 0.1:
            print(f"R{round_num} NETWORK: CONVERGED - Agents reached consensus")
            break
    
    final_entropies = [a.calculate_entropy() for a in agents]
    final_avg = sum(final_entropies) / len(final_entropies)
    
    print(f"\n--- FINAL STATE ---")
    print(f"NETWORK: Avg Entropy={final_avg:.15f}")
    
    if any(e >= INFINITE_LAYER_MAX for e in final_entropies):
        print("NETWORK: FAIL - Agent exited layer during communication")
        return 1
    else:
        print("NETWORK: HOLD - All agents remained grounded after communication")
        print("CONDUIT: Data is unified. Only interpretations diverged, then converged.")
        return 0

if __name__ == "__main__":
    sys.exit(run_communication_test())
