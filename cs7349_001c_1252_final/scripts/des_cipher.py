# cs7349_001c_1252_final.scripts.des_cipher.py
# Garrett Gruss 4/27/2025
# Usage: python -m cs7349_001c_1252_final.scripts.des_cipher


from typing import List
from cs7349_001c_1252_final.config.des_constants import (
    INITIAL_PERMUTATION, FINAL_PERMUTATION, EXPANSION_PERMUTATION, P_PERMUTATION, PERMUTATION_CHOICE_1, PERMUTATION_CHOICE_2, S_BOXES, SHIFT_SCHEDULE
)
from cs7349_001c_1252_final.config.logging_config import setup_logging

# Logger Configuration
import logging
from cs7349_001c_1252_final.config.logging_config import setup_logging
logger = logging.getLogger(getattr(__spec__, "name", __name__))


def bytes_to_bit_array(data: bytes) -> List[int]:
    bits: List[int] = []
    for byte in data:
        for i in range(8):
            bits.append((byte >> (7 - i)) & 1)
    return bits


def bit_array_to_bytes(bits: List[int]) -> bytes:
    data = bytearray()
    for i in range(0, len(bits), 8):
        byte = 0
        for bit in bits[i:i+8]:
            byte = (byte << 1) | bit
        data.append(byte)
    return bytes(data)


def permute(bits: List[int], table: List[int]) -> List[int]:
    return [bits[i-1] for i in table]


def left_shift(bits: List[int], n: int) -> List[int]:
    return bits[n:] + bits[:n]


def xor(bits1: List[int], bits2: List[int]) -> List[int]:
    return [b1 ^ b2 for b1, b2 in zip(bits1, bits2)]


def generate_subkeys(key_bytes: bytes) -> List[List[int]]:
    key_bits = bytes_to_bit_array(key_bytes)
    permuted = permute(key_bits, PERMUTATION_CHOICE_1)
    C, D = permuted[:28], permuted[28:]
    subkeys: List[List[int]] = []
    for i, shift in enumerate(SHIFT_SCHEDULE):
        C = left_shift(C, shift)
        D = left_shift(D, shift)
        combined = C + D
        subkey = permute(combined, PERMUTATION_CHOICE_2)
        logger.debug(f"Subkey {i+1:2d}: {bit_array_to_bytes(subkey).hex()}")
        subkeys.append(subkey)
    return subkeys


def sbox_substitution(bits48: List[int]) -> List[int]:
    output: List[int] = []
    for i in range(8):
        block = bits48[i*6:(i+1)*6]
        row = (block[0] << 1) | block[-1]
        col = (block[1] << 3) | (block[2] << 2) | (block[3] << 1) | block[4]
        val = S_BOXES[i][row][col]
        for j in reversed(range(4)):
            output.append((val >> j) & 1)
    return output


def feistel(right: List[int], subkey: List[int]) -> List[int]:
    expanded = permute(right, EXPANSION_PERMUTATION)
    logger.debug(f"Expanded R: {bit_array_to_bytes(expanded).hex()}")
    xored = xor(expanded, subkey)
    logger.debug(f"After XOR:   {bit_array_to_bytes(xored).hex()}")
    substituted = sbox_substitution(xored)
    logger.debug(f"After S-box: {bit_array_to_bytes(substituted).hex()}")
    return permute(substituted, P_PERMUTATION)


def process_block(block: bytes, subkeys: List[List[int]], encrypt: bool = True) -> bytes:
    bits = bytes_to_bit_array(block)
    permuted = permute(bits, INITIAL_PERMUTATION)
    logger.debug(f"Initial Permutation applied: {bit_array_to_bytes(permuted).hex()}")

    left, right = permuted[:32], permuted[32:]
    keys = subkeys if encrypt else list(reversed(subkeys))

    for i, key in enumerate(keys, start=1):
        temp = right.copy()
        f_out = feistel(right, key)
        right = xor(left, f_out)
        left = temp
        logger.debug(f"Round {i:2d} L={bit_array_to_bytes(left).hex()} R={bit_array_to_bytes(right).hex()}")

    combined = right + left  # swap halves
    final_bits = permute(combined, FINAL_PERMUTATION)
    output = bit_array_to_bytes(final_bits)
    logger.debug(f"Final Permutation applied: {output.hex()}")
    return output


def pad(data: bytes) -> bytes:
    pad_len = 8 - (len(data) % 8)
    return data + bytes([pad_len]) * pad_len


def unpad(data: bytes) -> bytes:
    pad_len = data[-1]
    return data[:-pad_len]


def des_encrypt(plaintext: str, key: bytes) -> str:
    if len(key) != 8:
        raise ValueError("Key must be 8 bytes long.")
    data = pad(plaintext.encode('utf-8'))
    subkeys = generate_subkeys(key)
    encrypted = b''
    for i in range(0, len(data), 8):
        encrypted += process_block(data[i:i+8], subkeys, encrypt=True)
    return encrypted.hex()


def des_decrypt(ciphertext_hex: str, key: bytes) -> str:
    if len(key) != 8:
        raise ValueError("Key must be 8 bytes long.")
    data = bytes.fromhex(ciphertext_hex)
    subkeys = generate_subkeys(key)
    decrypted = b''
    for i in range(0, len(data), 8):
        decrypted += process_block(data[i:i+8], subkeys, encrypt=False)
    return unpad(decrypted).decode('utf-8')


if __name__ == "__main__":
    setup_logging()
    key = b"secr3t_k"
    sample = "Hello, DES!"
    cipher = des_encrypt(sample, key)
    logger.info(f"Encrypted: {cipher}")
    plain = des_decrypt(cipher, key)
    logger.info(f"Decrypted: {plain}")
