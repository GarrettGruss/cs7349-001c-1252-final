# scripts.des
# Garrett Gruss 4/27/2025

import logging
from typing import List
from cs7349_001c_1252_final.config.des_constants import IP, FP, E, P, PC1, PC2, S_BOXES, SHIFT_SCHEDULE

# --- Logger Configuration ---
logger = logging.getLogger('des_cipher')
logger.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# File handler
file_handler = logging.FileHandler('des_cipher.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(console_formatter)
logger.addHandler(file_handler)

BLOCK_SIZE = 64  # bits
KEY_SIZE = 64    # bits

# Helper functions

def bytes_to_bit_array(data: bytes) -> List[int]:
    bits = []
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
    # PC-1
    permuted = permute(key_bits, PC1)
    C, D = permuted[:28], permuted[28:]
    subkeys = []
    for i, shift in enumerate(SHIFT_SCHEDULE):
        C = left_shift(C, shift)
        D = left_shift(D, shift)
        combined = C + D
        subkey = permute(combined, PC2)
        subkeys.append(subkey)
        logger.debug(f"Subkey {i+1}: {bit_array_to_bytes(subkey).hex()}")
    return subkeys


def sbox_substitution(bits48: List[int]) -> List[int]:
    output = []
    for i in range(8):
        block = bits48[i*6:(i+1)*6]
        row = (block[0] << 1) | block[-1]
        col = (block[1] << 3) | (block[2] << 2) | (block[3] << 1) | block[4]
        val = S_BOXES[i][row][col]
        for j in reversed(range(4)):
            output.append((val >> j) & 1)
    return output


def feistel(right: List[int], subkey: List[int]) -> List[int]:
    # Expansion
    expanded = permute(right, E)
    logger.debug(f"Expanded R: {bit_array_to_bytes(expanded).hex()}")
    # Key mixing
    xored = xor(expanded, subkey)
    logger.debug(f"After XOR with subkey: {bit_array_to_bytes(xored).hex()}")
    # Substitution
    substituted = sbox_substitution(xored)
    logger.debug(f"After S-box: {bit_array_to_bytes(substituted).hex()}")
    # Permutation
    permuted = permute(substituted, P)
    logger.debug(f"After P-permutation: {bit_array_to_bytes(permuted).hex()}")
    return permuted


def process_block(block: bytes, subkeys: List[List[int]], encrypt: bool = True) -> bytes:
    bits = bytes_to_bit_array(block)
    permuted = permute(bits, IP)
    logger.debug(f"After initial permutation: {bit_array_to_bytes(permuted).hex()}")

    left, right = permuted[:32], permuted[32:]
    keys = subkeys if encrypt else list(reversed(subkeys))

    for i, key in enumerate(keys, start=1):
        temp_right = right.copy()
        f_out = feistel(right, key)
        right = xor(left, f_out)
        left = temp_right
        logger.debug(f"Round {i:2d} L: {bit_array_to_bytes(left).hex()} R: {bit_array_to_bytes(right).hex()}")

    # Final combination (notice the swap)
    final_bits = right + left
    output = permute(final_bits, FP)
    result = bit_array_to_bytes(output)
    logger.debug(f"After final permutation: {result.hex()}")
    return result


def pad(data: bytes) -> bytes:
    pad_len = 8 - (len(data) % 8)
    return data + bytes([pad_len] * pad_len)

def unpad(data: bytes) -> bytes:
    pad_len = data[-1]
    return data[:-pad_len]


def des_encrypt(plaintext: str, key: bytes) -> str:
    if len(key) != 8:
        raise ValueError("Key must be 8 bytes long.")
    data = pad(plaintext.encode('utf-8'))
    subkeys = generate_subkeys(key)
    ciphertext = b''
    for i in range(0, len(data), 8):
        block = data[i:i+8]
        encrypted = process_block(block, subkeys, encrypt=True)
        ciphertext += encrypted
    return ciphertext.hex()


def des_decrypt(ciphertext_hex: str, key: bytes) -> str:
    if len(key) != 8:
        raise ValueError("Key must be 8 bytes long.")
    data = bytes.fromhex(ciphertext_hex)
    subkeys = generate_subkeys(key)
    plaintext = b''
    for i in range(0, len(data), 8):
        block = data[i:i+8]
        decrypted = process_block(block, subkeys, encrypt=False)
        plaintext += decrypted
    return unpad(plaintext).decode('utf-8')


if __name__ == "__main__":
    key = b"secr3t_k"
    text = "Hello, DES!"
    cipher = des_encrypt(text, key)
    logger.info(f"Encrypted: {cipher}")
    result = des_decrypt(cipher, key)
    logger.info(f"Decrypted: {result}")
