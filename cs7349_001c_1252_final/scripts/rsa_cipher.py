# cs7349_001c_1252_final.scripts.rsa_cipher.py
# Garrett Gruss 4/27/2025
# Usage: python -m cs7349_001c_1252_final.scripts.rsa_cipher


import math
import time
from typing import Tuple, List
from cs7349_001c_1252_final.scripts.utils import str_to_nums, nums_to_str

# Logger Configuration
import logging
from cs7349_001c_1252_final.config.logging_config import setup_logging
logger = logging.getLogger(getattr(__spec__, "name", __name__))

def is_prime(n: int) -> bool:
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def find_primes_in_range(start: int, end: int) -> List[int]:
    logger.debug(f"Finding primes between {start} and {end}")
    primes = [n for n in range(start, end + 1) if is_prime(n)]
    logger.debug(f"Found {len(primes)} primes in range")
    return primes


def ext_euclidean(a: int, b: int) -> Tuple[int, int, int]:
    if a == 0:
        return (b, 0, 1)
    g, y, x = ext_euclidean(b % a, a)
    return (g, x - (b // a) * y, y)


def mod_inv(a: int, m: int) -> int:
    logger.debug(f"Computing modular inverse of {a} mod {m}")
    g, x, _ = ext_euclidean(a, m)
    if g != 1:
        logger.error(f"Modular inverse does not exist for {a} mod {m}")
        raise ValueError(f"Modular inverse does not exist for {a} mod {m}")
    inverse = x % m
    logger.debug(f"Modular inverse is {inverse}")
    return inverse


def generate_rsa_keys() -> Tuple[int, int, int, int, int]:
    primes = find_primes_in_range(1000, 10000)
    p = primes[9]   # 10th prime
    q = primes[18]  # 19th prime
    logger.debug(f"Selected primes p={p}, q={q}")
    n = p * q
    phi = (p - 1) * (q - 1)
    logger.debug(f"Calculated n={n} and phi={phi}")

    e = 65537
    if math.gcd(e, phi) != 1:
        logger.warning("65537 not coprime to phi; finding alternative e")
        e = 3
        while math.gcd(e, phi) != 1:
            e += 2
    logger.debug(f"Using public exponent e={e}")

    d = mod_inv(e, phi)
    logger.debug(f"Computed private exponent d={d}")
    return p, q, e, n, d


def brute_force_private_key(e: int, n: int) -> Tuple[int, int, int, float]:
    start = time.perf_counter()
    p = None
    for candidate in range(2, int(math.isqrt(n)) + 1):
        if n % candidate == 0 and is_prime(candidate):
            q = n // candidate
            if is_prime(q):
                p = candidate
                break
    if p is None:
        logger.error("Failed to factor n")
        return None, None, None, 0.0
    phi = (p - 1) * (q - 1)
    d = None
    for i in range(2, phi):
        if (e * i) % phi == 1:
            d = i
            break
    elapsed = time.perf_counter() - start
    logger.debug(f"Brute-forced p={p}, q={q}, d={d} in {elapsed:.4f} seconds")
    return p, q, d, elapsed


def encrypt(m: int, e: int, n: int) -> int:
    logger.debug(f"Encrypting message m={m} with e={e}, n={n}")
    c = pow(m, e, n)
    logger.debug(f"Encrypted ciphertext c={c}")
    return c


def decrypt(c: int, d: int, n: int) -> int:
    logger.debug(f"Decrypting ciphertext c={c} with d={d}, n={n}")
    m = pow(c, d, n)
    logger.debug(f"Decrypted message m={m}")
    return m


if __name__ == '__main__':
    setup_logging()

    # 1) Primality test on a pre-defined integer
    num = 7919
    result = is_prime(num)
    logger.info(f"{num} is {'a prime' if result else 'not a prime'}.\n")

    # 2) Generate RSA keys
    p, q, e, n, d = generate_rsa_keys()
    logger.info("Generated RSA key pair:")
    logger.info(f"PU = {{e: {e}, n: {n}}}")
    logger.info(f"PR = {{d: {d}, p: {p}, q: {q}}}\n")

    # 3) Encrypt/decrypt a fixed message "rsa"
    message = "rsa"
    logger.info(f"Original message: \"{message}\"")
    message_int = str_to_nums(message)
    logger.info(f"Mapped to integers: {message_int}")

    ciphertexts = [encrypt(m_i, e, n) for m_i in message_int]
    logger.info(f"Encrypted ciphertexts: {ciphertexts}")

    decrypted_ints = [decrypt(c_i, d, n) for c_i in ciphertexts]
    logger.info(f"Decrypted integers: {decrypted_ints}")

    decrypted_msg = nums_to_str(decrypted_ints)
    logger.info(f"Recovered message: \"{decrypted_msg}\"\n")

    # 4) Brute-force the private key and measure time
    p_b, q_b, d_b, elapsed = brute_force_private_key(e, n)
    if p_b is None:
        logger.info("4) Brute-force failed to factor n.\n")
    else:
        logger.info("4) Adversary brute-forces the private key:")
        logger.info(f"Found p = {p_b}, q = {q_b}, d = {d_b}")
        logger.info(f"Time taken: {elapsed:.4f} seconds\n")
