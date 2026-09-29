# Lab 05 — Ethereum accounts, gas & the EVM


---

## Lab 5.1 — Add TrustKeys L1 to MetaMask

**Q1. Why is chainId part of every signed transaction (EIP-155)?**

The same private key produces the same address on every EVM chain, and nonces can coincide across chains. If the signature were not bound to a chainId, a transaction validly signed on one chain (e.g. a testnet) could be replayed by an attacker on another chain and executed there. EIP-155 includes the chainId in the data that is hashed and signed, so a signature is valid on exactly one chain. Adding a network to MetaMask only changes the RPC endpoint and chainId; the private key never leaves the device.

---

## Lab 5.2 — Read the chain with web3.py

```
Connected chainId=11968 head block=717573
[eth_getBlockByNumber latest]
  number       = 717573
  gasLimit     = 30,000,000
  gasUsed      = 21,000 (0.07% full)
  baseFeePerGas= 8 wei
  #txs         = 1
[eth_getBalance]
  address = 0xfB8cD49e9E9b54292D7BDF5115B7fa6b1FEA6F72
  balance = 1987962704000000000 wei = 1.987962704 coin
[eth_feeHistory] last 20 blocks
  block   baseFee(wei)  gasUsedRatio  tip p50 (gwei)
  717554             8        5.39%      2.0000
  717555             8        0.39%      2.0000
  717556             8       16.67%      2.0000
  717557             8       16.67%      2.0000
  717558             8       16.67%      2.0000
  717559             8        3.45%      2.0000
  717560             8        0.17%      2.0000
  717561             8        0.38%      2.0000
  717562             8        3.47%      2.0000
  717563             8        3.47%      2.0000
  717564             8        5.39%      2.0000
  717565             8        0.39%      2.0000
  717566             8        0.17%      2.0000
  717567             8        0.07%      2.0000
  717568             8        3.47%      2.0000
  717569             8        5.39%      2.0000
  717570             8        0.39%      2.0000
  717571             8        0.17%      2.0000
  717572             8        0.07%      2.0000
  717573             8        0.07%      2.0000
  next block's projected baseFee = 8 wei
  average gasUsedRatio = 4.11% -> chain is quiet
```

**Q2. Why does the base fee stay at the floor (a few wei) when gasUsedRatio is ~2%?**

The EIP-1559 rule is: next base fee = current base fee × (1 + (gasUsed − target) / target / 8), so it changes by at most ±12.5% per block. The target is 15M gas and the cap is 30M. With gasUsedRatio ≈ 2%, gasUsed ≈ 0.6M, far below the target, so the base fee drops by close to the maximum (about −12%) every block. Since the chain is quiet, it keeps falling from its initial value down to a tiny number. With integer arithmetic (wei) the decrease is rounded down: when the base fee is ≈ 8 wei, the drop is 8 × 0.96 / 8 ≈ 0.96, which truncates to 0. The base fee therefore cannot fall any further and stays at a few wei, which is exactly the 8 wei in the reference output. It only rises again when blocks are used above the target.

**Q3. What is the extra element in `baseFeePerGas` (length N+1), and how does a wallet use it?**

The last element is the **projected base fee of the next block** (the block not yet mined). It can be computed from the latest block's gasUsed and gasLimit using the formula above, which is why `baseFeePerGas` has N+1 entries while `gasUsedRatio` has only N (for blocks that already exist). A wallet uses it as the anchor for `maxFeePerGas`, e.g. `maxFeePerGas = 2 × nextBaseFee + maxPriorityFee`. The factor 2 is a buffer: the base fee can rise at most 12.5% per block, and 1.125⁶ ≈ 2, so the transaction stays valid even if about 6 full blocks pass before inclusion. Any unused portion is refunded.

---

## Lab 5.3 — Send a type-2 tx and decompose the fee

```
Connected chainId=11968 head block=717574
tx type            = 2  (2 = EIP-1559)
maxFeePerGas       = 2000000000 wei
maxPriorityFee     = 2000000000 wei
baseFee (block)    = 8 wei
effectiveGasPrice  = 2000000000 wei
gasUsed            = 21000
paid   = 42000000000000 wei
burned = 168000 wei (rời lưu thông)
tip    = 41999999832000 wei (về proposer)
42000000000000 = 168000 + 41999999832000 ? -> True
```

**Q4. If you raised the max base fee but kept the priority fee the same, would effectiveGasPrice change?**

**No** (in the normal case). `effectiveGasPrice = baseFee + min(maxPriorityFee, maxFee − baseFee)`. The base fee is set by the protocol according to block congestion, not bid by the sender. If `maxFee − baseFee` is already larger than `maxPriorityFee`, then `min(...)` still equals `maxPriorityFee`, so raising maxFee only raises the ceiling and the unused difference is refunded. effectiveGasPrice changes only if the old cap was binding (`maxFee − baseFee < maxPriorityFee`); in that case raising maxFee increases the tip actually paid.

**Q5. Where does 21,000 gas come from, and why does a failed transfer still cost gas?**

21,000 is the fixed *intrinsic gas* (`G_transaction`) of every transaction. It pays for the work all nodes must do regardless of content: recovering and verifying the ECDSA signature, checking nonce and balance, updating sender and recipient state, and storing the transaction on chain. Transactions with data or contract calls add gas for calldata and opcode execution. A failed transaction (revert, out of gas) still costs gas because validators actually included it in a block and spent computation up to the point of failure; if failure were free, an attacker could spam expensive transactions at no cost (a DoS attack). The nonce still increments, and only the unused gas is refunded. A transaction that is invalid from the start (wrong nonce, insufficient balance) is never included in a block and therefore costs nothing.

---

## Lab 5.4 — Trace a contract interaction on Sepolia Etherscan

**Q6. How does the EVM use the 4-byte selector to jump to the right function, and why does Etherscan need the ABI?**

A contract's bytecode begins with a *dispatcher*: it loads the first 4 bytes of calldata (`CALLDATALOAD(0) >> 224`), compares them one by one (or via binary search) against the selector of each public function using `EQ` + `JUMPI`, jumps to the `JUMPDEST` of the matching function, and runs the `fallback` or reverts if nothing matches. The rest of the calldata is just 32-byte words in ABI encoding, carrying no type or parameter-name information. Etherscan needs the ABI (or a reverse lookup of the selector in a signature database) to know whether each word is an `address`, `uint256`, or another type, so it can decode them into readable arguments. The selector is a one-way hash, so the function signature cannot be recovered from the 4 bytes alone.
