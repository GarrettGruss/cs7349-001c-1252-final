# cs7349_001c_1252_final.tests.test_des_cipher
# Garrett Gruss 4/27/2025

import pytest
from cs7349_001c_1252_final.scripts.des_cipher import (
    bytes_to_bit_array, bit_array_to_bytes,
    permute, left_shift, xor,
    pad, unpad,
    generate_subkeys, process_block,
    des_encrypt, des_decrypt
)
from cs7349_001c_1252_final.config.des_constants import (
    INITIAL_PERMUTATION, FINAL_PERMUTATION
)


def test_bytes_bit_array_roundtrip():
    data = b'\x00\xff\x10'
    bits = bytes_to_bit_array(data)
    result = bit_array_to_bytes(bits)
    assert result == data


def test_permute_inverse():
    bits = [i for i in range(64)]
    permuted = permute(bits, INITIAL_PERMUTATION)
    # Applying FINAL_PERMUTATION should invert INITIAL_PERMUTATION
    inverted = permute(permuted, FINAL_PERMUTATION)
    assert inverted == bits


def test_left_shift():
    bits = [1, 2, 3, 4, 5]
    assert left_shift(bits, 2) == [3, 4, 5, 1, 2]


def test_xor():
    assert xor([0,1,1,0], [1,1,0,0]) == [1,0,1,0]


def test_padding_unpadding():
    plaintext = b'HELLO'
    padded = pad(plaintext)
    assert len(padded) % 8 == 0
    assert unpad(padded) == plaintext


def test_subkeys_length_and_uniqueness():
    key = b'8bytekey'
    subkeys = generate_subkeys(key)
    assert len(subkeys) == 16
    # ensure subkeys are all unique
    hex_keys = [bytes_to_bit_array(bytes(subkey)) for subkey in subkeys]
    assert len({tuple(k) for k in hex_keys}) == 16


def test_encrypt_decrypt_cycle():
    key = b'secr3t_k'
    text = 'The quick brown fox'
    cipher = des_encrypt(text, key)
    assert isinstance(cipher, str)
    decrypted = des_decrypt(cipher, key)
    assert decrypted == text


def test_invalid_key_length():
    with pytest.raises(ValueError):
        des_encrypt('abc', b'toolongkey123')
    with pytest.raises(ValueError):
        des_decrypt('deadbeef', b'short')
