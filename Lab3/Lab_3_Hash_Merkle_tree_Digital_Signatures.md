# Lab 3 — Hash, Merkle tree & Digital Signatures

## Lab 3.1 — Hash properties & toy Proof-of-Work

**Q1: Each extra leading zero multiplies expected work by ≈ how much? Why?**

Each extra leading zero multiplies the expected work by 16 times.

The `hexdigest()` function returns the hash as a hexadecimal string (base 16). Each character in this string has 16 possible values (0-9 and a-f). The probability of getting a '0' at any specific position is 1/16. Therefore, demanding one additional '0' at the beginning reduces the probability of a successful hash by a factor of 16, meaning the miner has to test approximately 16 times as many nonces to find a valid one.

**Q2: Verifying your found nonce takes how many hash calls? What does this say about PoW?**

Verifying the found nonce takes exactly 1 hash call.

While it is computationally extremely difficult and time-consuming to find the solution (the nonce), it is trivial, fast, and computationally cheap for any node in the network to verify that the solution is correct.

---

## Lab 3.2 — Merkle tree

**Q3: For n = 1,000,000 transactions, how many hashes does one proof contain?**

For n = 1,000,000 transactions, one proof contains log2(1000000) ≈ 20.

**Q4: Explain one real system that uses exactly this mechanism (SPV, airdrop claim, proof-of-reserves…).**

One of the most elegant and widely used modern applications of this exact mechanism is the Cryptocurrency Airdrop Claim System via Smart Contracts.

**1. Off-Chain Setup (The Snapshot)**
The project developers write a script on their standard centralized servers to analyze blockchain history. They generate a massive JSON file containing all eligible users:
`[{"address": "0xAlice...", "amount": 400}, {"address": "0xBob...", "amount": 150}, ...]`
They hash each of these entries to create the "leaves" of a Merkle Tree, and run a function identical to our `merkle_root()` to generate one single 32-byte Merkle Root.

**2. On-Chain Deployment**
The developers deploy an Airdrop Smart Contract to the blockchain. Instead of uploading the list of 1,000,000 users, they hardcode only the 32-byte Merkle Root into the contract. Storing 32 bytes on Ethereum costs just a few cents.

**3. The Claim Process (Generating the Proof)**
When Alice visits the project's claim website and connects her wallet, the website's backend looks up her address in its off-chain database.
It finds her allocation (400 tokens) and runs our `merkle_proof()` function to generate her specific path of sibling hashes (for 1,000,000 users, this is just an array of ~20 hashes).

**4. The On-Chain Verification (The Smart Contract Execution)**
Alice clicks "Claim" on the website, which triggers a transaction to the Smart Contract. She submits three things to the contract:
* Her address (0xAlice)
* Her claim amount (400)
* Her array of 20 sibling hashes (The Proof)

---

## Lab 3.3 — Sign, verify & recover with eth-account

**Run twice with the same message — is the signature identical? Which RFC explains this?**

The signature is identical, This deterministic behavior is explained and standardized by RFC 6979.

**The tampered message recovers a different address. Explain why this proves integrity.**

```text
address: 0xcF36948CDC55fCFda56B5a7F38a8D011f179459F
r,s,v: 0x9b332fc10ef6bc0e50b01bd9cbb827d20c47bed1bef5cb5b208262183fdc8162 0x53c677cf485852838058aa4b2600b5014d11988a94c8acf875777f72482abe61 27
recovered: 0xcF36948CDC55fCFda56B5a7F38a8D011f179459F | match: True
tampered -> 0xcFba9146146b041D83E1FdE9893894DC0d3c3ab6
```

This mechanism proves integrity because the signature and the message are mathematically fused together.
