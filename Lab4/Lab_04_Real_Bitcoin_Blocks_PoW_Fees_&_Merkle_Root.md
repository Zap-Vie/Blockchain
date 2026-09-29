# Lab 04 — Real Bitcoin Blocks: PoW, Fees \& Merkle Root

## Task 4.1: Verify real Proof-of-Work



## Q1

`bits = 0x17034219` → exponent = `0x17` = 23, mantissa = `0x034219` = 213,529.
`target = 213529 × 256^20 ≈ 2^177.7`, about **19 leading zero hex digits** (out of 64).
A valid header hash must fall below that target, and the probability of a random
256-bit hash doing so is `target / 2^256 ≈ 2^-78.3`. So one valid header represents
roughly **2^78 hash attempts** of expected work.

## Q2

The asymmetry comes from SHA-256 being **one-way / preimage-resistant** and having
no exploitable internal structure: given a target, there is no shortcut better than
brute force, you must keep hashing different nonces until (by luck) one lands below
the target. Checking a *candidate* nonce, however, only costs one (double) hash
computation. So verification is O(1) work while finding a valid nonce is an
expected O(2^78) random search — cheap to check, expensive to solve.



## Task 4.2 — Transaction anatomy \& fee rate

## Q3

Block 840,000 was mined on **2024-04-20**, the 4th halving day, and it coincided
with the launch of Casey Rodarmor's **Runes** protocol (a new way to mint
fungible tokens on Bitcoin, timed deliberately to launch at the halving block).
Everyone wanted their "etching" transaction included in that symbolically
significant first post-halving block, so an intense mempool bidding war broke out
for the scarce \~1–4 MB of block space. This shows that Bitcoin fees are **not
fixed**, they're set by a real-time auction for block space. Miners greedily pick
the highest fee-rate transactions, so during a demand spike (a halving event, an
NFT/token mint craze, network congestion) fees can spike orders of magnitude above
the "normal" single/double-digit sat/vB rate.

## Q4

`4,075,061,499 − 312,500,000 = 3,762,561,499` satoshis. This difference is the
**sum of the fees paid by every other transaction in the block**, the miner's
coinbase transaction is allowed to claim the fixed subsidy *plus* the total fees
of all transactions it includes, all paid to whatever address(es) the miner
chooses.



## Task 4.3 — Recompute the Merkle root

## Q5

Because SHA-256 is **collision-resistant**, the only practical way to make a
different list of transactions (or a different order, or a tampered transaction)
hash up to the *same* Merkle root is to find a hash collision, believed to be
computationally infeasible. So a match between our recomputed root and the root
committed in the block header is strong evidence that we have the exact, unaltered,
correctly-ordered set of 3,050 transactions the miner committed to when the block
was built, nobody could have added, removed, reordered, or modified any
transaction without changing the root.

