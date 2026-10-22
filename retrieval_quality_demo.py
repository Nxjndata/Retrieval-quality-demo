# %% [markdown]
# # Measuring retrieval quality for candidate matching (toy demo)
# All data below is INVENTED for illustration. It is not Sense's data.
# Each query is a job order; each result list is the top-5 candidates returned,
# with a human label: 1 = relevant, 0 = not relevant. An empty list = zero results.

# %%
import math

# Part 1: the same five job orders used in the written note.
queries = {
    "A": [1, 1, 0, 1, 0],   # 3 relevant in top 5
    "B": [0, 0, 1, 0, 0],   # 1 relevant, at rank 3
    "C": [0, 0, 0, 0, 0],   # results returned, none relevant (ranking/matching problem)
    "D": [0, 0, 0, 0, 1],   # 1 relevant, at rank 5
    "E": [],                # nothing returned (coverage/indexing problem)
}
K = 5

# %% [markdown]
# ## Metric definitions
# - hit rate@k: share of queries with at least one relevant result in the top k
# - zero-result rate: share of queries that returned nothing at all
# - relevant-result density: relevant results / results shown
#   (denominator choice matters, so we print both versions)
# - MRR: mean of 1/rank of the first relevant result (0 if none)

# %%
def hit_at_k(labels, k=K):
    return int(any(labels[:k]))

def reciprocal_rank(labels):
    for i, rel in enumerate(labels, start=1):
        if rel:
            return 1 / i
    return 0.0

def wilson_interval(successes, n, z=1.96):
    """95% Wilson score interval for a proportion. Shows how little n=5 tells you."""
    if n == 0:
        return (0.0, 0.0)
    p = successes / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))

def summarize(qs, k=K):
    n = len(qs)
    hits = sum(hit_at_k(v, k) for v in qs.values())
    zero = sum(1 for v in qs.values() if len(v) == 0)
    returned = {q: v for q, v in qs.items() if v}
    rel_returned = sum(sum(v[:k]) for v in returned.values())
    slots_returned = sum(len(v[:k]) for v in returned.values())
    mrr = sum(reciprocal_rank(v) for v in qs.values()) / n
    wrong = n - hits - zero  # returned results, none relevant
    return {
        "n_queries": n,
        "hit_rate": hits / n,
        "miss_rate": 1 - hits / n,
        "zero_result_rate": zero / n,
        "wrong_result_rate": wrong / n,
        "density_over_returned": rel_returned / slots_returned if slots_returned else 0.0,
        "density_over_all_slots": rel_returned / (n * k),
        "mrr": mrr,
        "hit_ci95": wilson_interval(hits, n),
    }

# %%
s = summarize(queries)
print(f"Queries: {s['n_queries']}")
print(f"Hit rate@{K}:            {s['hit_rate']:.0%}")
print(f"Miss rate:              {s['miss_rate']:.0%}")
print(f"  of which zero-result: {s['zero_result_rate']:.0%}  (coverage / indexing)")
print(f"  of which wrong-result:{s['wrong_result_rate']:.0%}  (matching / ranking)")
print(f"Density (returned only): {s['density_over_returned']:.0%}")
print(f"Density (all slots):     {s['density_over_all_slots']:.0%}")
print(f"MRR:                    {s['mrr']:.2f}")
lo, hi = s["hit_ci95"]
print(f"Hit rate 95% interval:  {lo:.0%} to {hi:.0%}  <- n=5 is far too small to trust")

# %% [markdown]
# ## Part 2: why an aggregate number hides problems
# A second INVENTED set of 12 job orders, tagged by segment.
# The overall hit rate looks acceptable; one segment is much worse.

# %%
segmented = [
    ("senior",    [1, 1, 0, 0, 0]), ("senior",    [1, 0, 1, 0, 0]),
    ("senior",    [0, 1, 0, 0, 0]), ("senior",    [1, 1, 1, 0, 0]),
    ("senior",    [1, 0, 0, 0, 0]), ("senior",    [0, 0, 1, 0, 0]),
    ("entry",     [1, 0, 0, 0, 0]), ("entry",     [0, 0, 0, 0, 0]),
    ("entry",     [0, 0, 0, 0, 0]), ("entry",     []),
    ("tier2_loc", [0, 0, 0, 0, 0]), ("tier2_loc", []),
]

def by_segment(rows):
    groups = {}
    for seg, labels in rows:
        groups.setdefault(seg, {})[len(groups.get(seg, {}))] = labels
    return {seg: summarize(qs) for seg, qs in groups.items()}

overall = summarize({i: lab for i, (_, lab) in enumerate(segmented)})
print(f"\nOVERALL: n={overall['n_queries']}, hit rate {overall['hit_rate']:.0%}, "
      f"zero-result {overall['zero_result_rate']:.0%}")
for seg, m in by_segment(segmented).items():
    print(f"  {seg:10s} n={m['n_queries']}  hit {m['hit_rate']:.0%}  "
          f"zero-result {m['zero_result_rate']:.0%}  wrong-result {m['wrong_result_rate']:.0%}")

# %% [markdown]
# ## What to take from this
# 1. Report zero-result and wrong-result separately: different owners, different fixes.
# 2. State the density denominator every time.
# 3. Small samples need intervals; do not chase a 60% vs 70% difference on n=5.
# 4. Always slice. Aggregates average away the segments that are failing.
