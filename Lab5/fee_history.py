import sys
from web3 import Web3

try:                                   # web3.py v7
    from web3.middleware import ExtraDataToPOAMiddleware as POA
except ImportError:                    # web3.py v6
    from web3.middleware import geth_poa_middleware as POA

RPC = "https://l1testnet.trustkeys.network"
ADDRESS = "0xfB8cD49e9E9b54292D7BDF5115B7fa6b1FEA6F72"

args = sys.argv[1:]
tx_hash = args[0] if args else None
if len(args) > 1:
    RPC = args[1]

w3 = Web3(Web3.HTTPProvider(RPC))
w3.middleware_onion.inject(POA, layer=0)   # PoA/clique: extraData 97 byte

print(f"Connected chainId={w3.eth.chain_id} head block={w3.eth.block_number}")

if tx_hash is None:
    # ---------- Lab 5.2 ----------
    blk = w3.eth.get_block("latest")
    print("[eth_getBlockByNumber latest]")
    print(f"  number       = {blk['number']}")
    print(f"  gasLimit     = {blk['gasLimit']:,}")
    print(f"  gasUsed      = {blk['gasUsed']:,} ({blk['gasUsed']/blk['gasLimit']:.2%} full)")
    print(f"  baseFeePerGas= {blk['baseFeePerGas']} wei")
    print(f"  #txs         = {len(blk['transactions'])}")

    bal = w3.eth.get_balance(Web3.to_checksum_address(ADDRESS))
    print("[eth_getBalance]")
    print(f"  address = {ADDRESS}")
    print(f"  balance = {bal} wei = {bal/1e18} coin")

    fh = w3.eth.fee_history(20, "latest", [10, 50, 90])
    print("[eth_feeHistory] last 20 blocks")
    print("  block   baseFee(wei)  gasUsedRatio  tip p50 (gwei)")
    for i, base in enumerate(fh["baseFeePerGas"][:-1]):
        tip50 = fh["reward"][i][1] / 1e9
        print(f"  {fh['oldestBlock'] + i}  {base:>12}  {fh['gasUsedRatio'][i]:>11.2%}  {tip50:>10.4f}")
    print(f"  next block's projected baseFee = {fh['baseFeePerGas'][-1]} wei")

    avg = sum(fh["gasUsedRatio"]) / len(fh["gasUsedRatio"])
    verdict = "BUSY" if avg > 0.5 else "quiet"
    print(f"  average gasUsedRatio = {avg:.2%} -> chain is {verdict}")
else:
    # ---------- Lab 5.3 ----------
    rcpt = w3.eth.get_transaction_receipt(tx_hash)
    tx = w3.eth.get_transaction(tx_hash)
    blk = w3.eth.get_block(rcpt["blockNumber"])
    base_fee = blk["baseFeePerGas"]
    gas_used = rcpt["gasUsed"]
    eff_price = rcpt["effectiveGasPrice"]

    paid = gas_used * eff_price
    burned = gas_used * base_fee
    tip = gas_used * (eff_price - base_fee)

    print(f"tx type            = {tx.get('type')}  (2 = EIP-1559)")
    print(f"maxFeePerGas       = {tx.get('maxFeePerGas')} wei")
    print(f"maxPriorityFee     = {tx.get('maxPriorityFeePerGas')} wei")
    print(f"baseFee (block)    = {base_fee} wei")
    print(f"effectiveGasPrice  = {eff_price} wei")
    print(f"gasUsed            = {gas_used}")
    print(f"paid   = {paid} wei")
    print(f"burned = {burned} wei (rời lưu thông)")
    print(f"tip    = {tip} wei (về proposer)")
    print(f"{paid} = {burned} + {tip} ? ->", paid == burned + tip)
