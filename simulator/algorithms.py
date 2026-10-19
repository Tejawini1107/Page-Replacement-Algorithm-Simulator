"""Page replacement algorithms.

Every algorithm takes (reference_string, frame_count) and returns a
SimResult containing per-step snapshots so the run can be displayed.
"""
from collections import OrderedDict, deque
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional


@dataclass
class Step:
    page: int
    frames: List[Optional[int]]
    fault: bool
    evicted: Optional[int] = None


@dataclass
class SimResult:
    name: str
    frame_count: int
    steps: List[Step] = field(default_factory=list)

    @property
    def faults(self) -> int:
        return sum(s.fault for s in self.steps)

    @property
    def hits(self) -> int:
        return len(self.steps) - self.faults

    @property
    def fault_rate(self) -> float:
        return self.faults / len(self.steps) if self.steps else 0.0

    @property
    def hit_rate(self) -> float:
        return 1 - self.fault_rate if self.steps else 0.0


def _validate(refs, n):
    if n < 1:
        raise ValueError("Frame count must be at least 1")
    if not refs:
        raise ValueError("Reference string is empty")


def fifo(refs: List[int], n: int) -> SimResult:
    _validate(refs, n)
    res = SimResult("FIFO", n)
    frames: List[Optional[int]] = [None] * n
    queue = deque()
    for p in refs:
        if p in frames:
            res.steps.append(Step(p, frames.copy(), False))
            continue
        evicted = None
        if None in frames:
            frames[frames.index(None)] = p
        else:
            evicted = queue.popleft()
            frames[frames.index(evicted)] = p
        queue.append(p)
        res.steps.append(Step(p, frames.copy(), True, evicted))
    return res


def lru(refs: List[int], n: int) -> SimResult:
    _validate(refs, n)
    res = SimResult("LRU", n)
    frames: List[Optional[int]] = [None] * n
    order = OrderedDict()  # least recently used first
    for p in refs:
        if p in frames:
            order.move_to_end(p)
            res.steps.append(Step(p, frames.copy(), False))
            continue
        evicted = None
        if None in frames:
            frames[frames.index(None)] = p
        else:
            evicted, _ = order.popitem(last=False)
            frames[frames.index(evicted)] = p
        order[p] = True
        res.steps.append(Step(p, frames.copy(), True, evicted))
    return res


def optimal(refs: List[int], n: int) -> SimResult:
    _validate(refs, n)
    res = SimResult("Optimal", n)
    frames: List[Optional[int]] = [None] * n
    for i, p in enumerate(refs):
        if p in frames:
            res.steps.append(Step(p, frames.copy(), False))
            continue
        evicted = None
        if None in frames:
            frames[frames.index(None)] = p
        else:
            future = refs[i + 1:]
            def next_use(pg):
                return future.index(pg) if pg in future else float("inf")
            evicted = max(frames, key=next_use)
            frames[frames.index(evicted)] = p
        res.steps.append(Step(p, frames.copy(), True, evicted))
    return res


def mru(refs: List[int], n: int) -> SimResult:
    _validate(refs, n)
    res = SimResult("MRU", n)
    frames: List[Optional[int]] = [None] * n
    last_used = {}
    for t, p in enumerate(refs):
        if p in frames:
            last_used[p] = t
            res.steps.append(Step(p, frames.copy(), False))
            continue
        evicted = None
        if None in frames:
            frames[frames.index(None)] = p
        else:
            evicted = max(frames, key=lambda pg: last_used[pg])
            frames[frames.index(evicted)] = p
        last_used[p] = t
        res.steps.append(Step(p, frames.copy(), True, evicted))
    return res


def lfu(refs: List[int], n: int) -> SimResult:
    """Least Frequently Used; ties broken by oldest load (FIFO)."""
    _validate(refs, n)
    res = SimResult("LFU", n)
    frames: List[Optional[int]] = [None] * n
    freq, loaded_at = {}, {}
    for t, p in enumerate(refs):
        if p in frames:
            freq[p] += 1
            res.steps.append(Step(p, frames.copy(), False))
            continue
        evicted = None
        if None in frames:
            frames[frames.index(None)] = p
        else:
            evicted = min(frames, key=lambda pg: (freq[pg], loaded_at[pg]))
            frames[frames.index(evicted)] = p
            del freq[evicted], loaded_at[evicted]
        freq[p] = 1
        loaded_at[p] = t
        res.steps.append(Step(p, frames.copy(), True, evicted))
    return res


def clock(refs: List[int], n: int) -> SimResult:
    """Second-chance / Clock algorithm with a circular hand."""
    _validate(refs, n)
    res = SimResult("Clock", n)
    frames: List[Optional[int]] = [None] * n
    ref_bit = [0] * n
    hand = 0
    for p in refs:
        if p in frames:
            ref_bit[frames.index(p)] = 1
            res.steps.append(Step(p, frames.copy(), False))
            continue
        evicted = None
        if None in frames:
            idx = frames.index(None)
            frames[idx] = p
            ref_bit[idx] = 1
            hand = (idx + 1) % n
        else:
            while ref_bit[hand] == 1:
                ref_bit[hand] = 0
                hand = (hand + 1) % n
            evicted = frames[hand]
            frames[hand] = p
            ref_bit[hand] = 1
            hand = (hand + 1) % n
        res.steps.append(Step(p, frames.copy(), True, evicted))
    return res


ALGORITHMS: Dict[str, Callable[[List[int], int], SimResult]] = {
    "fifo": fifo,
    "lru": lru,
    "optimal": optimal,
    "mru": mru,
    "lfu": lfu,
    "clock": clock,
}


def simulate(name: str, refs: List[int], frames: int) -> SimResult:
    try:
        algo = ALGORITHMS[name.lower()]
    except KeyError:
        raise ValueError(f"Unknown algorithm '{name}'. Choose from: {', '.join(ALGORITHMS)}")
    return algo(refs, frames)
