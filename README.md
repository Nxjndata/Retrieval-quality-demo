**Retrieval Quality Demo**

A small, dependency-free Python script that shows how I’d measure retrieval quality for a candidate-matching system: hit rate, zero-result rate, relevant-result density, MRR, and why you slice by segment.

All data is synthetic. This is not from any real company or system. It’s a demo of how I’d think about the metrics.

**Why I built it**

Retrieval systems (job matching, candidate search, RAG) often get reported with one number, like “60% hit rate”. That number hides at least two different failures that need different fixes. This script makes that visible on a tiny example.

Run it

Requires Python 3.8+. No installs needed.

python3 retrieval_quality_demo.py

(On Windows, use py instead of python3.)

What it does

Part 1 takes 5 job orders, each with the top-5 results labelled relevant (1) or not (0), and computes:

Hit rate@k: share of queries with at least one relevant result in the top k
Zero-result rate: share of queries that returned nothing (a coverage or indexing problem)
Wrong-result rate: queries that returned results but none relevant (a matching or ranking problem)
Relevant-result density: relevant results divided by results shown. The script prints it two ways (over queries that returned results, and over all slots) because the denominator choice changes the number
MRR: rewards putting the first relevant result near the top
A 95% Wilson interval on the hit rate, to show how little 5 queries can tell you

Part 2 uses 12 job orders tagged by segment (senior, entry-level, tier-2 location). The overall hit rate is 58%, but senior roles are at 100%, entry-level at 25%, and tier-2 locations at 0%. The aggregate hides the failing segments.

Example output
Hit rate@5:            60%
Miss rate:              40%
  of which zero-result: 20%
  of which wrong-result:20%
Density (returned only): 25%
Density (all slots):     20%
MRR:                    0.31
Hit rate 95% interval:  23% to 88%

OVERALL: n=12, hit rate 58%, zero-result 17%
  senior     n=6  hit 100%
  entry      n=4  hit 25%
  tier2_loc  n=2  hit 0%

**Takeaways**
Report zero-result and wrong-result separately. Different owners, different fixes.
State the density denominator every time.
Small samples need intervals. Don’t chase a 60% vs 70% difference on 5 queries.
Always slice by segment before trusting an aggregate.

**Limits**
Synthetic data, so it shows the method, not real performance.
Relevance labels are hand-written. In a real system I’d get them from recruiter-labelled golden sets and implicit signals like shortlists and replies.
Doesn’t cover embeddings, re-ranking, or faithfulness of AI explanations. Those would be the next layer.
Next steps
Add nDCG alongside MRR
Add a faithfulness check on a sampled set of AI explanations
Plot metrics by segment over time
