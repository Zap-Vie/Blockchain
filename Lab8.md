# Lab 08

## Q0

`withdraw()` first sends ETH to `msg.sender` and only afterward updates `balances[msg.sender]`.

This is the problem because the external call can trigger the attacker's `receive()` function before the balance is updated. The attacker can then call `withdraw()` again using the same unchanged balance and repeatedly withdraw ETH.

## Q1

`withdraw()` executes 31 times in a single `attack()` transaction.

The bank initially contains 30 ETH from Alice, Bob, and Carol. Eve then deposits 1 ETH, giving the bank 31 ETH. The attacker re-enters `withdraw()` while the bank has at least 1 ETH remaining. The loop stops when the bank balance becomes less than 1 ETH, so the entire bank is drained.

## Q2

No. If `transfer()` were used instead of `.call{value: bal}("")`, this exact attack would not work because `transfer()` forwards only 2300 gas, which is not enough for the attacker's `receive()` function to perform another `withdraw()` call.

However, using `transfer()` alone is not a proper fix. It relies on a fixed gas stipend and can cause legitimate transfers to fail when the recipient's fallback or receive logic requires more gas. The proper solution is to follow the Checks-Effects-Interactions pattern and add a `nonReentrant` guard.

## Q3

With CEI alone, the re-entered `withdraw()` finds `balances[eve] == 0` because the balance was already cleared before the external call, so the reentrant call reverts.

The `nonReentrant` guard is still useful because CEI does not automatically protect against every form of cross-function reentrancy. Another function could potentially access or modify the same state while the original function is still executing. The guard provides an additional layer of protection by preventing a protected function from being entered again.

## Q4

The `ReentrancyGuard` revert happens inside the external call to the attacker's contract.

The outer `withdraw()` receives the failed call as:

```solidity
(bool ok, ) = msg.sender.call{value: bal}("");
```

Since the reentrant call reverts, `ok` becomes `false`. The outer function then executes:

```solidity
require(ok, "transfer failed");
```

Therefore, the original `ReentrancyGuard` error is swallowed by the outer `require`, and the final error message is `"transfer failed"`.

## Q5

No. The `low-level-calls` warning does not necessarily mean that the secure contract has a vulnerability.

Slither flags the use of `.call()` because low-level calls can be dangerous and require careful handling. In `EtherBankSecure`, the reentrancy problem has been addressed using CEI and `nonReentrant`, so the `reentrancy-eth` finding is removed. However, `.call()` is still a low-level call, so Slither continues to report the `low-level-calls` warning.

## Q6

If `onlyOwner` used:

```solidity
require(tx.origin == owner);
```

a malicious contract could trick the owner into calling it.

The call chain would be:

```text
Owner
  |
  v
Malicious Contract
  |
  v
EtherBank
```

Inside EtherBank, `tx.origin` would still be the owner because the owner initiated the transaction. Therefore, `require(tx.origin == owner)` would pass even though `msg.sender` is the malicious contract.

The malicious contract could then call `setOwner()` and take control of the bank.

The correct approach is to use `msg.sender`:

```solidity
require(msg.sender == owner);
```

This ensures that the account directly calling `setOwner()` must be the owner.
