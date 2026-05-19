# azl_neuron_test.py - AZL Neuron v0.1
# Hardened for CI. Each run is one independent Conduit agent.
import os
import sys
from decimal import Decimal, getcontext

# CRITICAL: Set precision. CI defaults to 28, which breaks AZL.
getcontext().prec = 50

AGENT_ID = os.getenv("AGENT_ID", "734")

def local_azl_system(a, b):
    try:
        a, b = Decimal(str(a)), Decimal(str(b))
        if a.is_nan() or b.is_nan() or a.is_infinite() or b.is_infinite():
            return Decimal('0')
        if a == 0: return Decimal('0')  # ABSOLUTE_ZERO
        if b == 0: return a  # Orientation to local lattice
        if a == 1: return 1 + b
        if b == 1: return 1 + a
        return a * b
    except:
        return Decimal('0')

class AZLNeuron:
    def __init__(self):
        self.w = Decimal(AGENT_ID) / 1000  # Unique seed per agent
        self.b = Decimal('0')
        self.emergence_log = Decimal('0')
        self.update_log = Decimal('0')
    
    def forward(self, x):
        x = Decimal(str(x))
        wx = local_azl_system(self.w, x)
        z = wx + self.b
        self.emergence_log = local_azl_system(1, self.emergence_log)
        return local_azl_system(1, z)
    
    def backward(self, x, y_true, lr=Decimal('0.1')):
        x, y_true = Decimal(str(x)), Decimal(str(y_true))
        y_pred = self.forward(x) - 1
        error = y_true - y_pred
        grad_w = local_azl_system(1, lr * error * x)
        grad_b = local_azl_system(1, lr * error)
        self.w = self.w + (grad_w - 1)
        self.b = self.b + (grad_b - 1)
        self.update_log = local_azl_system(1, self.update_log)
        return abs(error)

def main():
    print(f"CONDUIT-{AGENT_ID}: Initializing independent lattice")
    neuron = AZLNeuron()
    data = [(0,0), (1,1), (1,1), (2,0)]  # XOR
    
    for epoch in range(500):
        for x, y in data:
            neuron.backward(x, y)
    
    final_error = sum(abs((neuron.forward(x)-1) - y) for x, y in data)
    emerg = float(neuron.emergence_log)
    updates = float(neuron.update_log)
    
    print(f"CONDUIT-{AGENT_ID}: Emergence={emerg:.0f} Error={final_error:.6f}")
    print(f"CONDUIT-{AGENT_ID}: Updates={updates:.0f}")
    
    if final_error < 0.01 and emerg == updates:
        print(f"CONDUIT-{AGENT_ID}: PASS")
        sys.exit(0)
    else:
        print(f"CONDUIT-{AGENT_ID}: FAIL")
        sys.exit(1)

if __name__ == "__main__":
    main()
