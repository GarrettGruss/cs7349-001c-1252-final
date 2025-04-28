# cs7349_001c_1252_final.scripts.utils.py
# Garrett Gruss 4/27/2025

import string

def str_to_nums(s: str) -> list:
    return [string.ascii_lowercase.index(ch) for ch in s]

def nums_to_str(nums: list) -> str:
    return ''.join(string.ascii_lowercase[n] for n in nums)