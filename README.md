# Page Replacement Algorithm Simulator

An Operating Systems project that simulates how an OS memory manager chooses
which page to evict when physical memory (frames) is full.

## Algorithms
| Algorithm | Evicts |
|-----------|--------|
| FIFO      | the page that has been in memory longest |
| LRU       | the least recently used page |
| Optimal (Belady/OPT) | the page not needed for the longest time in the future (benchmark only, needs future knowledge) |
| MRU       | the most recently used page |
| LFU       | the least frequently used page (ties -> oldest) |
| Clock (Second Chance) | first page with reference bit 0, clearing bits as the hand sweeps |

## Requirements
Python 3.8+. No external libraries.

## Usage
```bash
python main.py -r "7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1" -f 3 -a all --trace
python main.py -r "7 0 1 2 0 3 0 4 2 3" -f 3 -a lru
python main.py --random 40 --max-page 9 --locality 0.5 --seed 42 -f 4
python main.py -r "1 2 3 4 1 2 5 1 2 3 4 5" -a fifo --sweep 6
python main.py --belady          # Belady's anomaly demo
python main.py --interactive
python -m unittest discover -s tests
```

## Project structure
```
main.py                  CLI
simulator/algorithms.py  all algorithms + SimResult/Step data classes
simulator/display.py     tables, bar charts, trace rendering
simulator/utils.py       parsing and random reference-string generator
tests/test_algorithms.py unit tests (textbook results, Belady's anomaly)
```

## Metrics
Page faults, hits, fault rate = faults / references, hit rate = 1 - fault rate.

## Adding an algorithm
Write `def myalgo(refs, n) -> SimResult` in `algorithms.py` and register it in
the `ALGORITHMS` dict.
