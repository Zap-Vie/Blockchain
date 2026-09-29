import hashlib

def H(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()

def merkle_root(leaves: list[bytes]) -> bytes:
    """TODO 1: dựng cây từ dưới lên, trả về băm gốc.
    Build bottom-up, return the root digest."""
    if not leaves:
        return b""
    
    current_level = leaves.copy()
    
    while len(current_level) > 1:
        next_level = []
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            right = current_level[i + 1] if i + 1 < len(current_level) else left
            next_level.append(H(left + right))
        current_level = next_level
        
    return current_level[0]

def merkle_proof(leaves: list[bytes], index: int) -> list[tuple[bytes, bool]]:
    """TODO 2: trả về [(sibling_digest, sibling_is_left), ...] từ lá lên gốc.
    Return the sibling path from leaf `index` up to the root."""
    if not leaves:
        return []
        
    proof = []
    current_level = leaves.copy()
    curr_idx = index
    
    while len(current_level) > 1:
        if curr_idx % 2 == 0:
            sibling_idx = curr_idx + 1 if curr_idx + 1 < len(current_level) else curr_idx
            proof.append((current_level[sibling_idx], False)) 
        else:
            sibling_idx = curr_idx - 1
            proof.append((current_level[sibling_idx], True))

        next_level = []
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            right = current_level[i + 1] if i + 1 < len(current_level) else left
            next_level.append(H(left + right))
            
        current_level = next_level
        curr_idx //= 2
        
    return proof

def verify_proof(leaf_hash: bytes, proof: list[tuple[bytes, bool]], root: bytes) -> bool:
    """TODO 3: tính ngược lên gốc rồi so sánh. Recompute upward and compare."""
    current_hash = leaf_hash

    for sibling_hash, is_left in proof:
        if is_left:
            current_hash = H(sibling_hash + current_hash)
        else:
            current_hash = H(current_hash + sibling_hash)
      
    return current_hash == root

# ------------------------------------------------------------------ checks
if __name__ == "__main__":
    txs = [f"tx{i}: A->B {i} coin".encode() for i in range(8)]
    leaves = [H(t) for t in txs]
    root = merkle_root(leaves)

    print("root:", root.hex())

    # CHECK 1: proof đúng cho mọi lá / valid proof for every leaf
    ok = all(verify_proof(leaves[i], merkle_proof(leaves, i), root) for i in range(8))
    print("CHECK 1 (all 8 proofs valid):", "OK" if ok else "FAIL")

    # CHECK 2: proof có đúng log2(8)=3 phần tử / proof has exactly 3 elements
    print("CHECK 2 (proof length == 3):", "OK" if len(merkle_proof(leaves, 4)) == 3 else "FAIL")

    # CHECK 3: lá bị sửa phải trượt / a tampered leaf must fail
    fake = H(b"tx4: A->B 999999 coin")
    print("CHECK 3 (tampered leaf fails):",
          "OK" if not verify_proof(fake, merkle_proof(leaves, 4), root) else "FAIL")

    # CHECK 4: số lá lẻ (7) vẫn chạy / odd leaf count (7) still works
    l7 = leaves[:7]
    r7 = merkle_root(l7)
    print("CHECK 4 (odd count works):",
          "OK" if all(verify_proof(l7[i], merkle_proof(l7, i), r7) for i in range(7)) else "FAIL")