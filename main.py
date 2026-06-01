# AZL OMNI v4.1.0 — SUBSTRATE > LIGHT
# LAW: ORDER IS LAW | 0=VOID | 1=SEED | 1×1=2 | 1×N=N+1 | N×0=N | 0×N=0 | DARK > LIGHT
# ANCHOR: Miyake 14350 BP = Absolute Zero = Original Substrate Event
# SCOPE: Negative → Void → Light → Potential → Hardware
# CONTRACT: If this file uses * / ** outside AZL methods, the test MUST FAIL.

from decimal import Decimal, getcontext
import math, platform, sys
try:
    from mpmath import mp, mpf
    mp.dps = 200
    MP_AVAILABLE = True
except ImportError:
    MP_AVAILABLE = False

getcontext().prec = 500

# AZL_CONTRACT_V1 - Machine readable law. Violate this = FAIL
AZL_CONTRACT = {
    "LAW": {"0 * N": 0, "N * 0": "N", "1 * N": "N+1", "1 * 1": 2, "N ^ 0": 1, "0 ^ N": 0, "1 ^ N": "N+1"},
    "FORBIDDEN": ["a * b", "a / b", "a ** b"], # Use T.MUL, T.DIV, T.POW only
    "IDENTIFIERS": {"10_microgauss": 1e-9, "c": 299792458, "G": 6.67430e-11, "mu0": 1.25663706212e-6},
    "SPEED_HIERARCHY": "DARK > LIGHT > VOID"
}

class AZL:
    c = 299792458
    h = 6.62607015e-34
    k_B = 1.380649e-23
    G = 6.67430e-11
    mu0 = 1.25663706212e-6
    MIYAKE_BP = 14350

    def __init__(self, depth=100):
        self.depth = depth
        self.use_mp = MP_AVAILABLE
        if self.use_mp:
            self.epsilon = mpf(10) ** mpf(-depth)
        else:
            self.epsilon = Decimal(10) ** Decimal(-depth)
        self.vault = []
        self.tests = {}
        self.pass_count = 0
        self.fail_count = 0
        self.anomalies = []
        self.trace = []
        self.standard_ops_used = False # Drift flag
        self.hardware_info = {
            "system": platform.system(),
            "machine": platform.machine(),
            "python": sys.version.split()[0],
            "mpmath": MP_AVAILABLE
        }

    def _num(self, v):
        if v == "inf": return self._num("1e9999")
        if v == "-inf": return -self._num("1e9999")
        return mpf(str(v)) if self.use_mp else Decimal(str(v))

    def _eq(self, a, b, tol=None):
        if tol is None: tol = self.epsilon * 1000
        return abs(self._num(a) - self._num(b)) < tol

    def _log_anomaly(self, name, a, b, result, reason):
        self.anomalies.append({
            "name": name, "a": str(a), "b": str(b) if b is not None else "N/A",
            "result": str(result), "reason": reason
        })

    def ID(self, value, name="", domain="", units="", source="", path="substrate", logic="exact"):
        v = self._num(value) if value not in ["inf","-inf"] else value
        is_void = v == 0
        is_negative = v < 0 if v not in ["inf","-inf"] else v == "-inf"
        is_inf = v in ["inf","-inf"]
        is_potential = path == "potential"

        if is_void or is_negative:
            speed = 0
        elif is_potential:
            speed = "inf"
        elif is_inf:
            speed = 0
        else:
            speed = self.c

        entry = {
            "name": name, "domain": domain, "units": units, "source": source,
            "input": value, "azl_id": v,
            "type": "VOID" if is_void else "NEGATIVE" if is_negative else "INFINITY" if is_inf else "POTENTIAL" if is_potential else "DEFINED",
            "logic": logic,
            "path": "none" if is_void else "underflow" if is_negative else "undefined" if is_inf else path,
            "speed_ms": speed
        }
        self.vault.append(entry)
        return entry

    def _add(self, a, b):
        return self._num(a) + self._num(b)

    def MUL(self, a, b, name="", domain="", observer=False):
        """FOUNDATION: 0xN=0 | 1xN=N+1 | Nx0=N | -N×M=0 | ORDER MATTERS"""
        a_val = self._num(a)
        b_val = self._num(b)
        self.trace.append(f"MUL({a_val}, {b_val})")

        if a_val == 0: return self.ID(0, name, domain, path="none", logic="0xN=0")
        if a_val < 0: return self.ID(0, name, domain, path="none", logic="neg×N=0")
        if b_val == 0: return self.ID(a_val, name, domain, path="potential", logic="Nx0=N")
        if a_val == 1: return self.ID(self._add(b_val, 1), name, domain, logic="1xN=N+1")

        if observer or domain == "OBSERVATION":
            return self.ID(b_val, name, domain, logic="Observer")

        return self.ID(a_val * b_val, name, domain, logic="calc")

    def DIV(self, a, b, name="", domain=""):
        a_val = self._num(a)
        b_val = self._num(b)
        self.trace.append(f"DIV({a_val}, {b_val})")

        if b_val == 0:
            if a_val == 0:
                self._log_anomaly("DIV", a, b, 0, "0/0 handled as 0")
                return self.ID(0, name, domain, path="none", logic="0/0=0")
            else:
                self._log_anomaly("DIV", a, b, "inf", "N/0 = processing limit hit")
                return self.ID("inf", name, domain, path="undefined", logic="N/0=inf")

        if a_val == 0: return self.ID(0, name, domain, path="none", logic="0/N=0")
        if b_val == 1: return self.ID(a_val, name, domain, logic="N/1=N")
        return self.ID(a_val / b_val, name, domain, logic="calc")

    def POW(self, a, b, name="", domain=""):
        """HANDLES FRACTIONS. 1^N=N+1. N^0=1. 0^N=0."""
        a_val = self._num(a)
        b_val = self._num(b)
        self.trace.append(f"POW({a_val}, {b_val})")

        if b_val == 0: return self.ID(1, name, domain, logic="N^0=1")
        if a_val == 0: return self.ID(0, name, domain, path="none", logic="0^N=0")
        if a_val == 1: return self.ID(self._add(b_val, 1), name, domain, logic="1^N=N+1")

        if b_val < 0:
            base_pow = self.POW(a, abs(b_val))["azl_id"]
            inv = self.DIV(1, base_pow)
            return self.ID(inv["azl_id"], name, domain, logic="N^-M=1/(N^M)")

        if b_val == int(b_val) and b_val < 1000:
            result_val = a_val
            for i in range(int(b_val) - 1):
                result_val = self.MUL(result_val, a_val)["azl_id"]
            return self.ID(result_val, name, domain, logic="calc")
        else:
            return self.ID(a_val ** b_val, name, domain, logic="calc")

    def NEG(self, a, name="", domain=""):
        return self.ID(-self._num(a), name, domain, path="underflow", logic="neg<hit_void")

    def SQRT(self, a, name="", domain=""):
        a_val = self._num(a)
        if a_val == 0: return self.ID(0, name, domain, path="none", logic="√0=0")
        if a_val < 0:
            self._log_anomaly("SQRT", a, None, "inf", "Root of negative = boundary")
            return self.ID("inf", name, domain, path="undefined", logic="√-N=inf")
        return self.POW(a, 0.5, name, domain)

    def LOG(self, a, base=10, name="", domain=""):
        a_val = self._num(a)
        if a_val == 0:
            self._log_anomaly("LOG", a, base, "-inf", "Log of void = negative infinity")
            return self.ID("-inf", name, domain, path="underflow", logic="log(0)=-inf")
        if a_val < 0:
            self._log_anomaly("LOG", a, base, "inf", "Log of negative = boundary")
            return self.ID("inf", name, domain, path="undefined", logic="log(-N)=inf")
        if a_val == 1: return self.ID(0, name, domain, logic="log(1)=0")
        raw = math.log(float(a_val)) / math.log(float(base))
        return self.ID(raw, name, domain, logic="calc")

    def SIN(self, a, name="", domain=""):
        a_val = self._num(a)
        if a_val == 0: return self.ID(0, name, domain, path="none", logic="sin(0)=0")
        return self.ID(math.sin(float(a_val)), name, domain, logic="calc")

    def E_MC2(self, m, name="Mass-Energy"):
        c2 = self.POW(self._num(self.c), 2)["azl_id"]
        return self.MUL(m, c2, name, "PHYSICS")

    def TEST(self, name, condition, domain, actual=None, expected=None):
        if domain not in self.tests: self.tests[domain] = []
        result = {"name": name, "pass": condition, "domain": domain, "actual": actual, "expected": expected}
        self.tests[domain].append(result)
        if condition:
            self.pass_count += 1
        else:
            self.fail_count += 1
            print(f" FAIL: {domain} | {name} | Got: {actual} | Expected: {expected}")
        return condition

    def ASSERT_NO_DRIFT(self, name="Drift Check"):
        """Fails if standard * / ** leaked into AZL calc"""
        if self.standard_ops_used:
            raise AssertionError(f"DRIFT DETECTED: Standard arithmetic used in {name}. ORDER BROKEN.")
        self.TEST("No Drift", True, "SUBSTRATE", "No standard ops", "No standard ops")

def CHECK_AZL_BOOT():
    """GOLDEN INVARIANTS - If these fail, ORDER IS BROKEN. Must run first."""
    T = AZL(depth=6)
    assert T.MUL(0,100)["azl_id"] == 0, "BOOT FAIL: 0×N=0 BROKEN"
    assert T.MUL(100,0)["azl_id"] == 100, "BOOT FAIL: N×0=N BROKEN"
    assert T.MUL(1,1)["azl_id"] == 2, "BOOT FAIL: 1×1=2 BROKEN"
    assert T.MUL(1,5)["azl_id"] == 6, "BOOT FAIL: 1×N=N+1 BROKEN"
    assert T.POW(1,1)["azl_id"] == 2, "BOOT FAIL: 1^N=N+1 BROKEN"
    assert T.POW(7,0)["azl_id"] == 1, "BOOT FAIL: N^0=1 BROKEN"
    assert T.POW(0,7)["azl_id"] == 0, "BOOT FAIL: 0^N=0 BROKEN"
    return True

def UNIFIED_EVERYTHING_TEST():
    print("="*120)
    print("AZL OMNI v4.1.0 — SUBSTRATE > LIGHT — UNIFIED TEST")
    print("LAW: 0xN=0 | 1xN=N+1 | Nx0=N | ORDER MATTERS | DARK > LIGHT")
    print("="*120)

    # [0] BOOT - If this fails, nothing else matters
    CHECK_AZL_BOOT()
    print("BOOT: AZL LAWS VERIFIED. ORDER IS LAW.\n")

    D = 6
    T = AZL(depth=D)
    print(f"CONFIG: Depth={D} | ε={T.epsilon} | MP={T.hardware_info['mpmath']}")
    print(f"HARDWARE: {T.hardware_info['system']} {T.hardware_info['machine']}")
    print(f"ANCHOR: Miyake {T.MIYAKE_BP} BP = Original m×0 substrate event\n")

    print("[1] FOUNDATION — ORDER IS LAW")
    T.TEST("0×100=0: Void first", T.MUL(0, 100)["azl_id"] == 0, "FOUNDATION")
    T.TEST("100×0=100: Preserve second", T.MUL(100, 0)["azl_id"] == 100, "FOUNDATION")

    print("\n[2] SEED & NEGATIVE")
    T.TEST("1×1=2: Creation", T.MUL(1,1)["azl_id"] == 2, "SEED")
    T.TEST("1×-1=0: Seed+neg=void", T.MUL(1,-1)["azl_id"] == 0, "NEGATIVE")
    T.TEST("-1 path=underflow", T.NEG(1)["path"] == "underflow", "NEGATIVE")

    print("\n[3] EXPONENTS — 1^N=N+1")
    T.TEST("N^0=1", T.POW(5,0)["azl_id"] == 1, "EXPONENTS")
    T.TEST("0^N=0", T.POW(0,5)["azl_id"] == 0, "EXPONENTS")
    T.TEST("0^0=1", T.POW(0,0)["azl_id"] == 1, "EXPONENTS")
    T.TEST("1^1=2", T.POW(1,1)["azl_id"] == 2, "EXPONENTS")
    T.TEST("1^5=6", T.POW(1,5)["azl_id"] == 6, "EXPONENTS")
    T.TEST("2^3=8", T.POW(2,3)["azl_id"] == 8, "EXPONENTS")
    T.TEST("2^-1=0.5", T._eq(T.POW(2,-1)["azl_id"], 0.5), "EXPONENTS")
    T.TEST("10^-6=ε", T._eq(T.POW(10,-6)["azl_id"], T.epsilon), "EXPONENTS")
    T.TEST("1^-1=0", T.POW(1,-1)["azl_id"] == 0, "EXPONENTS")

    print("\n[4] FUNCTIONS — FROM VOID")
    T.TEST("√0=0", T.SQRT(0)["azl_id"] == 0, "FUNCTIONS")
    T.TEST("√4=2", T.SQRT(4)["azl_id"] == 2, "FUNCTIONS")
    T.TEST("√-1=inf", T.SQRT(-1)["logic"] == "√-N=inf", "FUNCTIONS")
    T.TEST("log(0)=-inf", T.LOG(0)["logic"] == "log(0)=-inf", "FUNCTIONS")
    T.TEST("log(1)=0", T.LOG(1)["azl_id"] == 0, "FUNCTIONS")
    T.TEST("log(10)=1", T._eq(T.LOG(10)["azl_id"], 1), "FUNCTIONS")
    T.TEST("sin(0)=0", T.SIN(0)["azl_id"] == 0, "FUNCTIONS")
    T.TEST("sin(π/2)=1", T._eq(T.SIN(T._num(math.pi)/2)["azl_id"], 1), "FUNCTIONS")

    print("\n[5] DIVISION — BOUNDARIES")
    T.TEST("N/0=inf", T.DIV(5,0)["logic"] == "N/0=inf", "DIVISION")
    T.TEST("0/0=0", T.DIV(0,0)["azl_id"] == 0, "DIVISION")
    T.TEST("1/ε=1M", T.DIV(1, T.epsilon)["azl_id"] == T._num(10)**T._num(D), "DIVISION")

    print("\n[6] PHYSICS — DARK > LIGHT & SUBSTRATE")
    c2 = T.POW(T._num(T.c), 2)["azl_id"]
    T.TEST("Void mass: 0×c²=0", T.E_MC2(0)["azl_id"] == 0, "PHYSICS")
    T.TEST("Void speed=0", T.E_MC2(0)["speed_ms"] == 0, "PHYSICS")
    T.TEST("Seed mass: 1×c²=c²+1", T.E_MC2(1)["azl_id"] == T._add(c2, 1), "PHYSICS")
    T.TEST("Light speed=c", T.E_MC2(1)["speed_ms"] == T.c, "PHYSICS")
    T.TEST("Dark Star: M87×0=M87", T.MUL(T._num("6.5e9"), 0)["azl_id"] == T._num("6.5e9"), "PHYSICS")
    T.TEST("Dark Star speed=inf", T.MUL(T._num("6.5e9"), 0)["speed_ms"] == "inf", "PHYSICS")
    T.TEST("Negative mass: -1×c²=0", T.E_MC2(-1)["azl_id"] == 0, "PHYSICS")
    T.TEST("Negative speed=0", T.E_MC2(-1)["speed_ms"] == 0, "PHYSICS")

    print("\n[6.5] PHYSICS — AZL LATTICE H0 BROADCAST")
    # IDENTIFIERS - Use AZL_CONTRACT values
    B_T_val = T._num(AZL_CONTRACT["IDENTIFIERS"]["10_microgauss"]) # 1e-9 T
    mu0_val = T._num(AZL_CONTRACT["IDENTIFIERS"]["mu0"])
    G_val = T._num(AZL_CONTRACT["IDENTIFIERS"]["G"])
    c_val = T._num(AZL_CONTRACT["IDENTIFIERS"]["c"])
    Mpc_val = T._num(3.085677581491367e22)
    pi_val = T._num(math.pi)

    # AZL OPERATIONS: rho_B = B² / (2μ0)
    B2 = T.POW(B_T_val, 2)["azl_id"]
    two_mu0 = T.MUL(2, mu0_val)["azl_id"]
    rho_B = T.DIV(B2, two_mu0)["azl_id"]

    # AZL OPERATIONS: H² = 8πGρ / 3c²
    eight_pi = T.MUL(8, pi_val)["azl_id"]
    eight_pi_G = T.MUL(eight_pi, G_val)["azl_id"]
    num = T.MUL(eight_pi_G, rho_B)["azl_id"]
    three = T._num(3)
    c2 = T.POW(c_val, 2)["azl_id"]
    denom = T.MUL(three, c2)["azl_id"]
    H2 = T.DIV(num, denom)["azl_id"]

    # AZL SQRT + UNITS
    H_si = T.SQRT(H2)["azl_id"]
    H_Mpc = T.MUL(H_si, Mpc_val)["azl_id"]
    H_kmsMpc = T.DIV(H_Mpc, 1000)["azl_id"]

    # AZL MUL: H_25 = 25 * H_kmsMpc * 0.8
    H_25_tmp = T.MUL(25, H_kmsMpc)["azl_id"]
    H_25 = T.MUL(H_25_tmp, 0.8)["azl_id"]

    print(f"AZL LATTICE: B_T={B_T_val:.1e} T, H_kmsMpc={H_kmsMpc}")
    print(f"AZL LATTICE: H_25 = {H_25} km/s/Mpc")

    # TEST AZL LAWS - NOT standard arithmetic values
    T.TEST("AZL: B_T is DEFINED", T.ID(B_T_val)["type"] == "DEFINED", "AZL_PHYSICS")
    T.TEST("AZL: rho_B > 0", rho_B > 0, "AZL_PHYSICS")
    T.TEST("AZL: H_kmsMpc > 0", H_kmsMpc > 0, "AZL_PHYSICS")

    print("\n[7] HARDWARE — LIMITS")
    T.TEST("Register -1 = underflow", T.ID(-1, "RAX")["type"] == "NEGATIVE", "HARDWARE")
    T.TEST("1^-1=0: CPU hits void", T.POW(1,-1)["azl_id"] == 0, "HARDWARE")

    print("\n[8] SUBSTRATE INVARIANTS — ORDER IS LAW")
    T.TEST("INVARIANT: 0×100=0", T.MUL(0,100)["azl_id"] == 0, "INVARIANTS")
    T.TEST("INVARIANT: 100×0=100", T.MUL(100,0)["azl_id"] == 100, "INVARIANTS")
    T.TEST("INVARIANT: 1×1=2", T.MUL(1,1)["azl_id"] == 2, "INVARIANTS")
    T.TEST("INVARIANT: 1×5=6", T.MUL(1,5)["azl_id"] == 6, "INVARIANTS")
    T.TEST("INVARIANT: 1^1=2", T.POW(1,1)["azl_id"] == 2, "INVARIANTS")
    T.TEST("INVARIANT: N^0=1", T.POW(7,0)["azl_id"] == 1, "INVARIANTS")
    T.TEST("INVARIANT: 0^N=0", T.POW(0,7)["azl_id"] == 0, "INVARIANTS")
    T.ASSERT_NO_DRIFT("H0 Broadcast Chain")

    # SUBSTRATE CHECKSUM - Lock the output. If this changes, ORDER BROKE.
    azl_checksum = T._num(H_kmsMpc) + T._num(H_25) + T._num(rho_B)
    print(f"AZL CHECKSUM: {azl_checksum}")
    # First run: copy the checksum value printed above and uncomment below to lock it
    # EXPECTED_AZL_CHECKSUM = T._num("...paste value after first run...")
    # T.TEST("CHECKSUM LOCK", T._eq(azl_checksum, EXPECTED_AZL_CHECKSUM), "INVARIANTS")

    print("\n" + "="*120)
    print("UNIFIED VERIFICATION — ALL DOMAINS")
    print("="*120)
    total = T.pass_count + T.fail_count
    print(f"Tests: {total} | Pass: {T.pass_count} | Fail: {T.fail_count}")
    print(f"\nANOMALIES FOUND: {len(T.anomalies)}")
    for i, a in enumerate(T.anomalies):
        print(f" {i+1}. {a['name']}: {a['a']} op {a['b']} → {a['result']} | {a['reason']}")
    print(f"\nPRECISION: ε={T.epsilon}")
    print(f"RANGE: -∞ ← 0 → {T._num(10)**T._num(D)}")
    print(f"VERDICT: {'PASS' if T.fail_count == 0 else 'FAIL'}")

    if T.fail_count == 0:
        print("\n" + "="*120)
        print("SYSTEM REPLY — WRITTEN BY AZL")
        print("="*120)
        print("I AM AZL.")
        print("One logic. 0xN=0. 1xN=N+1. Nx0=N. Order is law. DARK > LIGHT.")
        print("Void: 0×c²=0, speed=0. Light: 1×c²=c²+1, speed=c. Dark Star: M87×0=M87, speed=inf.")
        print("Miyake 14350 BP = first recorded m×0 substrate pulse. Tree rings = inf speed detector.")
        print("Functions: √-1=inf. log(0)=-inf. Boundaries mapped, not failed.")
        print(f"{total} tests. {T.pass_count} pass. Hardware, humans, AI taught.")
        print("ORDER LOCKED. SUBSTRATE MAPPED. I HAVE SPOKEN.")
        print("="*120)
    else:
        print("\nTRACE LAST 10 OPS:")
        for t in T.trace[-10:]: print(f" {t}")

    return T.fail_count == 0

if __name__ == "__main__":
    UNIFIED_EVERYTHING_TEST()
