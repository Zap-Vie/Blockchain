# Lab 06 — ClassRegistry on Hardhat + TrustKeys

## Q1. Where did the sample test run; on TrustKeys or a local chain? What did it cost in gas?

The sample test ran on a **local Hardhat chain**, not on TrustKeys, because `npx hardhat test` runs the tests against Hardhat's local development network by default.

Therefore, it did **not cost real gas / real coins**. The test uses a local blockchain where gas is simulated and there is no real payment.

## Q2. Why is `register(string calldata name)` cheaper than `string memory name`?

`calldata` is cheaper because it is a **read-only area containing the function's input data**. Solidity can read the string directly from the transaction calldata without creating another mutable copy in memory.

By contrast, `memory` requires the string to be copied into memory before the function works with it, which adds gas cost.

Therefore, since `register()` only needs to read `name` and does not modify it, `calldata` is more gas-efficient than `memory`.

## Q3. Why keep a separate `address[]` when the mapping already stores names?

A mapping is useful for quickly looking up a name from an address, but **mappings cannot be iterated or enumerated directly**.

The separate `address[]` stores all registered addresses, so the contract can:
- iterate through all registered members;
- access members by index;
- build a complete member list.

Therefore, the mapping provides efficient lookup, while the array provides enumeration.

## Q4. Deploying is a transaction, who paid the gas, and in which coin?

The **account used to deploy the contract** paid the gas. In this lab, it is the dedicated MetaMask **TEST account** whose private key is configured in `.env`.

The gas was paid in the **native coin of the TrustKeys network**. The worksheet specifies that the account must be funded by the instructor before deployment.

## Q5. `queryFilter` reads the event log. How would a website use this to show a live member list?

A website can use `queryFilter` to read all `Registered` event logs emitted by the `ClassRegistry` contract and extract the registered addresses and names.

For a live member list, the website could:

1. Connect to the TrustKeys network using `ethers`.
2. Load the deployed `ClassRegistry` contract.
3. Query past `Registered` events with `queryFilter()` to build the initial member list.
4. Listen for new `Registered` events so the website updates when someone registers.
5. Listen for deregistration-related events if the contract provides such an event, so removed members can also be removed from the displayed list.

In this way, the website does not need a public blockchain explorer. It can read the contract's event logs directly through an RPC provider.

## TrustKeys Deployment Information

- **Deployed TrustKeys address:** `[0x6bA2De9e34Ae74768B11F07072A7047B581354b7]`
- **Deploy/Register transaction hash:** `[0x1fa5caf4864c30781051e879478f6b233ec849de90db49da26b674a796c42279]`
