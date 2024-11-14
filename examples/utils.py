import hashlib

from bitcoinutils.keys import PublicKey
from bitcoinutils.script import Script

RAFFLE_VERSION = b'\x00'


def bytes_num(n: int) -> int:
    """
    Returns the number of bytes required to represent n as bytes
    """
    if n == 0:
        return 1
    return (n.bit_length() + 7) // 8


def op_return_script(blockheight: int) -> Script:
    """
    The OP_RETURN Script to be appended to the OP_RETURN output.

    It's a raffle version number followed by more data.
    For version 0x00, what follows is a block height number represented as a big endian byte sequence.
    The data is returned as a hex string because that's what the bitcoinutils library expects.
    """
    payload = (RAFFLE_VERSION + blockheight.to_bytes(bytes_num(blockheight), 'big')).hex()
    return Script(['OP_RETURN', payload])


def p2pkh_script(public_key: PublicKey) -> Script:
    """
    Self-explanatory. Surprised I couldn't find this in bitcoinutils.
    """
    return Script(['OP_DUP', 'OP_HASH160', public_key.to_hash160(), 'OP_EQUALVERIFY', 'OP_CHECKSIG'])


def canonize_outpoint(outpoint: tuple[str, int]) -> bytes:
    """
    Returns an outpoint in its canonical form.
    The canonical form is defined as the serialization format in a real bitcoin transaction.

    It consists of 32 bytes of the txid in little endian, followed by 4 bytes for the vout, also in little endian.
    """
    canonical_txid = bytes.fromhex(outpoint[0])[::-1]
    canonical_vout = outpoint[1].to_bytes(4, 'little')

    assert len(canonical_txid) == 32
    return canonical_txid + canonical_vout


def outpoints_merkle_root(sorted_outpoints: list[tuple[str, int]]) -> bytes:
    """
    Calculates the Merkle Root Hash of a list of outpoints.

    Pre: The list of outpoints is not empty
    Pre: The outpoints are sorted according to their canonical representation
    """
    assert len(sorted_outpoints) > 0
    assert sorted(sorted_outpoints, key=canonize_outpoint) == sorted_outpoints

    hashes = [hashlib.sha256(leaf).digest() for leaf in
              [canonize_outpoint(outpoint) for outpoint in sorted_outpoints]]

    while len(hashes) > 1:
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])

        next_hashes: list[bytes] = []
        for i in range(0, len(hashes), 2):
            next_hashes.append(hashlib.sha256(hashes[i] + hashes[i + 1]).digest())

        hashes = next_hashes
    return hashes[0]


def winner_outpoint(outpoints: list[tuple[str, int]], block_hash: bytes) -> tuple[str, int]:
    """
    Given a list of outpoints and a blockhash, the function returns the winning
    outpoint according to the rules of the Dust Raffle.

    First the outpoint list is sorted according to their canonical form, and a SHA256
    Merkle hash is computed from this sorted list.
    Another Merkle hash is computed from concatenating the outpoints' Merkle hash with the chosen block hash.
    This last Merkle hash is treated as an unsigned integer and divided modulo
    the number of outpoints in the list. The result is the index of the winner
    outpoint in the sorted outpoint list.

    The function always returns the same outpoint regardless of how the outpoints
    in the list are sorted (assuming the block hash stays the same).

    The block hash is the double SHA256 hash of some well known Bitcoin block,
    in big endian format (zero bytes first).

    Pre: The list of outpoints is not empty
    Pre: The block hash is exactly 32 bytes long
    """
    assert len(outpoints) > 0
    assert len(block_hash) == 32

    sorted_outpoints = sorted(outpoints, key=canonize_outpoint)

    outpoints_hash = outpoints_merkle_root(sorted_outpoints)
    root_hash = hashlib.sha256(outpoints_hash + block_hash).digest()

    winner_idx = int.from_bytes(root_hash) % len(sorted_outpoints)
    return sorted_outpoints[winner_idx]
