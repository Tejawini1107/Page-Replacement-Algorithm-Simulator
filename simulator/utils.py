import random
from typing import List


def parse_refs(text: str) -> List[int]:
    cleaned = text.replace(",", " ").split()
    try:
        return [int(x) for x in cleaned]
    except ValueError:
        raise ValueError("Reference string must contain only integers")


def random_refs(length: int, max_page: int, seed=None, locality: float = 0.0) -> List[int]:
    """Random reference string. locality in [0,1): chance of repeating a recent page."""
    rng = random.Random(seed)
    refs: List[int] = []
    for _ in range(length):
        if refs and rng.random() < locality:
            refs.append(rng.choice(refs[-4:]))
        else:
            refs.append(rng.randint(0, max_page))
    return refs
