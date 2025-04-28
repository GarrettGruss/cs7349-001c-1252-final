# cs7349_001c_1252_final.tests.test_rsa_cipher.py
# Garrett Gruss 4/27/2025

import pytest
from cs7349_001c_1252_final.scripts.rsa_cipher import (
    is_prime, find_primes_in_range, ext_euclidean, mod_inv,
    generate_rsa_keys, encrypt, decrypt
)
from cs7349_001c_1252_final.scripts.utils import (
    str_to_nums, nums_to_str
)


def test_is_prime_basic():
    assert is_prime(2)
    assert is_prime(13)
    assert not is_prime(1)
    assert not is_prime(4)


def test_find_primes_range():
    primes = find_primes_in_range(10, 20)
    assert primes == [11, 13, 17, 19]


def test_mod_inv_and_ext_euclidean():
    # 3 * 7 ≡ 1 mod 20 -> inverse of 3 mod 20 is 7
    inv = mod_inv(3, 20)
    assert inv == 7
    g, x, y = ext_euclidean(3, 20)
    assert g == 1
    assert (3 * x + 20 * y) == g


def test_generate_keys_properties():
    p, q, e, n, d = generate_rsa_keys()
    # p and q are prime and in correct range
    assert is_prime(p) and 1000 < p < 10000
    assert is_prime(q) and 1000 < q < 10000
    # n = p*q and e*d ≡ 1 mod phi
    phi = (p - 1) * (q - 1)
    assert n == p * q
    assert (e * d) % phi == 1


def test_encrypt_decrypt_integer():
    p, q, e, n, d = generate_rsa_keys()
    m = 42
    c = encrypt(m, e, n)
    m2 = decrypt(c, d, n)
    assert m2 == m


def test_encrypt_decrypt_message_rsa():
    # Test string 'rsa'
    msg = 'rsa'
    nums = str_to_nums(msg)
    p, q, e, n, d = generate_rsa_keys()
    decrypted_nums = []
    for m in nums:
        c = encrypt(m, e, n)
        m2 = decrypt(c, d, n)
        decrypted_nums.append(m2)
    assert decrypted_nums == nums
    assert nums_to_str(decrypted_nums) == msg
