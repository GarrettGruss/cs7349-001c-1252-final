# cs7349_001c_1252_final.scripts.utils.py
# Garrett Gruss 4/27/2025

import string

def str_to_nums(s: str) -> list:
    return [string.ascii_lowercase.index(ch) for ch in s]

def nums_to_str(nums: list) -> str:
    return ''.join(string.ascii_lowercase[n] for n in nums)

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