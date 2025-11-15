import random
from typing import List

def fisher_yates_shuffle(arr: List) -> List:
    shuffled = arr.copy()
    for i in range(len(shuffled) - 1, 0, -1):
        j = random.randint(0, i)
        shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
    return shuffled

def is_valid_position(row: int, col: int, max_rows: int, max_cols: int) -> bool:
    return 0 <= row < max_rows and 0 <= col < max_cols

def shuffle_subset_inplace(arr: List, indices: List[int]) -> None:
    subset = [arr[i] for i in indices]
    shuffled = fisher_yates_shuffle(subset)
    for i, v in zip(indices, shuffled):
        arr[i] = v