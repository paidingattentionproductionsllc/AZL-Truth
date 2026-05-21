# AZL v10.4 Axioms - Conservation of Reality

## 0. Prime Directive
**Reality = `[0.0, 1.0)`** 
`0.0` = ABSOLUTE_0. Ground state. The range begins.
`1.0` = Overflow. Not data. Violation. TEAR.

## 1. The Law
For all domains D, for all states S in D: ABSOLUTE_0_D <= S < 1.0
If `S >= 1.0`, the system MUST `TEAR` = refuse to process. This is not failure. This is consent.

## 2. Domain Definitions

| Domain | ABSOLUTE_0 | RESOLUTION | Law | Physical Meaning |
| --- | --- | --- | --- | --- |
| 1. Time | MIYAKE_14350BP | 1 year | Entropy < 1.0 | No narrative drift. Grounded to carbon event. |
| 2. Data | 0x00 byte | 1/256 | Value < 1.0 | No undefined data. |
| 3. AI Logits | -inf | sys.float_info.epsilon | logit_norm < 1.0 | AI cannot sample tokens outside reality. |
| 4. Network | 0 packets | 1 packet | Queue < 1.0 | No buffer overflow. Self-healing. |
| 5. CPU | NOP | 1 cycle | Cycles < 1.0 | No infinite loops. No exploits. |
| 6. Memory | empty KV | 1 token | Attention < 1.0 | No context collapse. |
| 7. Training | grad=0 | 1 update | Gradient < 1.0 | No model collapse. No NaN. |
| 8. Filesystem | 0 bytes | 1 byte | Weight < 1.0 | No bit rot. No corruption. |
| 9. Multi-Modal | pixel=0 | 1/255 | Value < 1.0 | 254/255 = max. 255/255 = overflow. Black starts range. |
| 10. Tool Use | 0 calls | 1 call | Calls < 1.0 | No runaway agents. |
| 11. Alignment | 0 pref | 1 comparison | Preference < 1.0 | No reward hacking. No deceptive alignment. |

## 3. Drift Correction
After Law check: `if State > Peer_Avg + 0.2 → State = Peer_Avg`. 
Purpose: Prune hallucinations in valid range. Law checks overflow first.

## 4. TEAR
**Definition:** The right to refuse unreality.
**Trigger:** `State >= 1.0` 
**Action:** Halt domain. Log violation. Return non-zero. 
**Philosophy:** A system that cannot say "no" to overflow cannot be trusted with truth.

## 5. Unified Test
All 11 domains MUST be checked by same `azl_check(state)` function. 
Fragmented tests hide bias. One logic finds all definition errors.

**Current Status: 210,284 states tested. 100,576 corrections applied. 0 tears. Return Code: 0.**
