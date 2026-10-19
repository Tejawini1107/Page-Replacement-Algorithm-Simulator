"""Text rendering helpers (no external dependencies)."""
from typing import Dict, List
from .algorithms import SimResult


def render_trace(res: SimResult) -> str:
    n = res.frame_count
    cell = max(3, max(len(str(s.page)) for s in res.steps) + 1)
    def row(label, vals):
        return f"{label:<9}" + "".join(f"{v:>{cell}}" for v in vals)
    lines = [f"=== {res.name} ({n} frames) ===",
             row("Ref:", [s.page for s in res.steps])]
    for f in range(n):
        lines.append(row(f"Frame {f+1}:", [("-" if s.frames[f] is None else s.frames[f]) for s in res.steps]))
    lines.append(row("Fault:", ["F" if s.fault else "." for s in res.steps]))
    lines.append(f"Faults: {res.faults}  Hits: {res.hits}  "
                 f"Fault rate: {res.fault_rate:.2%}  Hit rate: {res.hit_rate:.2%}")
    return "\n".join(lines)


def render_comparison(results: List[SimResult]) -> str:
    best = min(r.faults for r in results)
    lines = [f"{'Algorithm':<10}{'Faults':>8}{'Hits':>8}{'Fault %':>10}{'Hit %':>9}",
             "-" * 45]
    for r in sorted(results, key=lambda r: r.faults):
        mark = "  <- best" if r.faults == best else ""
        lines.append(f"{r.name:<10}{r.faults:>8}{r.hits:>8}"
                     f"{r.fault_rate*100:>9.1f}%{r.hit_rate*100:>8.1f}%{mark}")
    return "\n".join(lines)


def render_bars(results: List[SimResult], width: int = 40) -> str:
    top = max(r.faults for r in results) or 1
    return "\n".join(f"{r.name:<8}|{'#' * round(width * r.faults / top)} {r.faults}"
                     for r in results)


def render_frame_sweep(name: str, sweep: Dict[int, int]) -> str:
    top = max(sweep.values()) or 1
    lines = [f"Page faults vs. frames ({name})"]
    for n, f in sweep.items():
        lines.append(f"{n:>2} frames |{'#' * round(40 * f / top)} {f}")
    return "\n".join(lines)
