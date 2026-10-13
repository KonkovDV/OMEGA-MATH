# Calibrating the triage tiers

OMEGA sorts problems into tiers T1–T5 by how much they are likely to benefit from computation and AI ([rubric](../protocol/amenability-rubric.md)). Until now nobody had checked whether those tiers predict anything. This note says what can be checked today, what cannot, and how the check will work.

## What exists to compare against

| Source | What it records | Fetched |
|---|---|---|
| [Tao's wiki "AI contributions to Erdős problems"](https://github.com/teorth/erdosproblems/wiki/AI-contributions-to-Erd%C5%91s-problems) | per Erdős problem: which AI tools, date, outcome (full solution, partial, variant, incorrect claim, literature found) | 13.10.2026 |
| [FrontierMath Erdős, arXiv:2609.25050](https://arxiv.org/abs/2609.25050) | 68 hard open Erdős problems, fixed budget; best model solved 2 | 13.10.2026 |
| [Tsoukalas et al., arXiv:2605.22763](https://arxiv.org/abs/2605.22763) | formal proof search: 9 of 353 open Erdős problems, 44 of 492 OEIS conjectures | 13.10.2026 |
| [Epoch AI, FrontierMath: Open Problems](https://epoch.ai/frontiermath/open-problems) | curated open problems with "AI", "human + AI" and "human" solution labels | 13.10.2026 |

## What can be checked today

Very little, and it is better to say so. The registry has eight entries with "Erdős" in the name, of which three are triaged (`erdos-straus` T1, `erdos-min-overlap` T1, `erdos-faber-lovasz` T3). None of them carries an erdosproblems.com number, so they cannot be joined to Tao's wiki automatically. Matching by name by hand would be error-prone: the same name often covers several numbered problems.

Two weak signals, recorded as signals and nothing more:

- `erdos-min-overlap` is T1, and the Einstein Arena table shows AI agents improving its best known bound (0.380876 → 0.380871). That fits T1.
- `erdos-straus` is T1. Computation has pushed the verified range to 10^18, but no AI system has proved the conjecture. T1 means "computation helps", not "AI will solve it", so this is consistent, but it also shows the tier name invites the wrong reading.

## Method for a real calibration

1. Add an optional `external_ids` field to the registry schema (`erdosproblems`, `oeis`, `frontiermath_op`).
2. Fill it for every entry where the match is unambiguous; leave the rest empty rather than guessing.
3. Take outcomes from the sources above as of a fixed date and store that snapshot with its date.
4. Report, per tier: how many problems had any AI contribution, how many had a verified full solution, and how many had an incorrect AI claim. Small numbers get exact counts, not percentages.
5. Re-run on every snapshot. If T1 does not do clearly better than T4–T5, the rubric needs revising, not the data.

Steps 1–2 are on the [roadmap](ROADMAP.md) for the next release.
