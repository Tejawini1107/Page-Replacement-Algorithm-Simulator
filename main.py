#!/usr/bin/env python3
"""Page Replacement Algorithm Simulator - CLI entry point.

Examples:
  python main.py -r "7 0 1 2 0 3 0 4 2 3 0 3 2" -f 3 -a all
  python main.py -r "7 0 1 2 0 3 0 4 2 3 0 3 2" -f 3 -a lru --trace
  python main.py --random 30 --max-page 9 --seed 1 -f 4 -a all --trace
  python main.py --belady
  python main.py -r "1 2 3 4 1 2 5 1 2 3 4 5" -a fifo --sweep 6
  python main.py --interactive
"""
import argparse
import sys

from simulator import ALGORITHMS, simulate
from simulator.display import (render_bars, render_comparison,
                               render_frame_sweep, render_trace)
from simulator.utils import parse_refs, random_refs

BELADY_REFS = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]


def run(refs, frames, algos, trace):
    print(f"\nReference string: {' '.join(map(str, refs))}")
    print(f"Frames: {frames}\n")
    results = [simulate(a, refs, frames) for a in algos]
    if trace:
        for r in results:
            print(render_trace(r), end="\n\n")
    if len(results) > 1:
        print(render_comparison(results))
        print("\nPage faults (bar chart):")
        print(render_bars(results))
    elif not trace:
        print(render_trace(results[0]))


def belady():
    print("Belady's anomaly demo: FIFO on", BELADY_REFS)
    for n in (3, 4):
        r = simulate("fifo", BELADY_REFS, n)
        print(f"  {n} frames -> {r.faults} page faults")
    print("More frames produced MORE faults under FIFO (LRU/Optimal never do this).")
    for name in ("lru", "optimal"):
        print(f"  {name.upper():<8}", {n: simulate(name, BELADY_REFS, n).faults for n in (3, 4)})


def interactive():
    print("Page Replacement Simulator (interactive)")
    refs = parse_refs(input("Reference string (space/comma separated): "))
    frames = int(input("Number of frames: "))
    choice = input(f"Algorithm [{'/'.join(ALGORITHMS)}/all]: ").strip().lower() or "all"
    algos = list(ALGORITHMS) if choice == "all" else [choice]
    run(refs, frames, algos, trace=input("Show step-by-step trace? [y/N]: ").lower() == "y")


def main(argv=None):
    p = argparse.ArgumentParser(description="Page replacement algorithm simulator")
    p.add_argument("-r", "--refs", help="reference string, e.g. '7 0 1 2 0 3'")
    p.add_argument("--random", type=int, metavar="LEN", help="generate random reference string of this length")
    p.add_argument("--max-page", type=int, default=9, help="highest page number for random strings")
    p.add_argument("--locality", type=float, default=0.0, help="0-1, probability of re-referencing a recent page")
    p.add_argument("--seed", type=int)
    p.add_argument("-f", "--frames", type=int, default=3)
    p.add_argument("-a", "--algo", default="all", help=f"{', '.join(ALGORITHMS)} or all")
    p.add_argument("--trace", action="store_true", help="show step-by-step frame table")
    p.add_argument("--sweep", type=int, metavar="MAXFRAMES", help="faults for 1..MAXFRAMES frames")
    p.add_argument("--belady", action="store_true", help="demonstrate Belady's anomaly")
    p.add_argument("--interactive", action="store_true")
    a = p.parse_args(argv)

    try:
        if a.belady:
            return belady()
        if a.interactive:
            return interactive()
        if a.random:
            refs = random_refs(a.random, a.max_page, a.seed, a.locality)
        elif a.refs:
            refs = parse_refs(a.refs)
        else:
            p.error("provide --refs, --random, --belady or --interactive")

        algos = list(ALGORITHMS) if a.algo == "all" else [a.algo.lower()]
        if a.sweep:
            for name in algos:
                sweep = {n: simulate(name, refs, n).faults for n in range(1, a.sweep + 1)}
                print(render_frame_sweep(name.upper(), sweep), end="\n\n")
            return
        run(refs, a.frames, algos, a.trace)
    except ValueError as e:
        sys.exit(f"Error: {e}")


if __name__ == "__main__":
    main()
