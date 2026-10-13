# Lab 07 Answers

## Q1. Why do we build on OpenZeppelin instead of writing ERC-20 from scratch?

We use OpenZeppelin because its contracts are audited, battle-tested, and gas-reviewed. This reduces the risk of bugs and security vulnerabilities compared with implementing ERC-20 from scratch.

## Q2. decimals() returns 18. If Alice's balance is 1000000000000000000, how many CTK is that, and where does the "18" actually live?

Alice has 1 CTK.

Because:

```text
1 CTK = 10^18 base units
```

The value stored on-chain is an integer number of base units. The `18` is used as display metadata to tell wallets and UIs how to convert the integer into a human-readable CTK amount.

## Q3. Why does a DEX need approve + transferFrom instead of a plain transfer? What is the risk of approve(spender, 2^256 - 1)?

A DEX needs `approve` and `transferFrom` because the DEX contract needs permission to move tokens from the user's address within its own transaction.

A normal `transfer()` sends tokens directly and does not give the DEX permission to pull tokens from the user's balance.

The risk of:

```text
approve(spender, 2^256 - 1)
```

is that it gives the spender an almost unlimited allowance. If the spender contract is hacked or malicious, it could potentially drain the user's entire CTK balance.

## Q4. Where do the JSON and the image live? What did we avoid by NOT using IPFS on TrustKeys?

Both the JSON metadata and the SVG image are stored or generated on-chain by the ClassBadge contract through the `data:application/json;base64,...` URI.

By not using IPFS, we avoid needing an IPFS pinning service to keep the NFT metadata and image available.

## Q5. What does the "safe" in _safeMint / safeTransferFrom actually check, and why?

If the NFT recipient is a smart contract, `_safeMint` and `safeTransferFrom` check whether that contract implements:

```solidity
onERC721Received
```

This prevents the NFT from being sent to a contract that cannot properly receive ERC-721 tokens, which could permanently strand the NFT.

## Q6. TrustKeys has no public explorer. How did you confirm the 100-CTK transfer landed?

We can confirm it using:

1. `balanceOf()` through an ethers.js view call.
2. MetaMask, by checking the recipient's CTK balance.
3. Transaction event logs, such as the ERC-20 `Transfer` event.

For example:

```javascript
await token.balanceOf(recipient)
```

If the recipient's balance increased by 100 CTK, the transfer succeeded.

## Q7. What stops someone from replaying your permit signature on a second chain or a second time?

The EIP-2612 permit signature is bound to:

1. `chainId`, which prevents replay on another chain.
2. The contract address, which prevents using the signature with another token contract.
3. The owner's nonce, which prevents replaying the same signature twice.
4. The deadline, which makes the signature expire after a certain time.

Therefore, `chainId`, contract address, nonce, and deadline prevent permit signature replay.
