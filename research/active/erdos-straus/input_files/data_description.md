# Problem Brief — Erdős–Straus Conjecture

- Registry ID: erdos-straus
- Title: Erdős–Straus conjecture
- Tier: T1-computational
- Amenability Score: 8/10
- Route: experiment-first → covering-congruence proof search

## Problem Statement

For every integer n ≥ 2, there exist positive integers x, y, z such that
4/n = 1/x + 1/y + 1/z. Equivalently: 4xyz = n(xy + xz + yz).

## Current Status (April 2026)

- Verified computationally for all n ≤ 10^17 (Salez 2014).
- Only primes need checking: composites inherit solutions from factors.
- Modular identities cover all residues mod 840 except {1, 121, 169, 289, 361, 529}.
- Mordell's barrier: no single polynomial identity for n ≡ 1 (mod p) when 1 is QR mod p.
- Elsholtz–Tao (2013): average solution count grows polylogarithmically.
- Natural density of exceptions → 0 (Webb 1970, Vaughan 1970).

## Attack Vectors

### V1: Covering Congruence Expansion
Extend Mordell's identities to cover more residue classes mod larger moduli.
For each uncovered residue r mod M, find prime q > M with r non-QR mod q,
then construct a polynomial identity for n ≡ r (mod q).

### V2: Parametric Family Search
For hard primes p ≡ 1 (mod 24), search decompositions:
- Type I: n|x → 4yz = xy + xz + yz with x = nk
- Type II: n|y → search (x,z) given y = nl

### V3: Verification Frontier Push
Use optimized sieve to push past 10^17 with identity-based skip.

## Success Condition

1. New modular identities covering ≥1 residue class mod 840 → publishable
2. Verification frontier pushed to 10^18 with novel algorithm → publishable note
3. Complete covering system proof → major result (unlikely but dream target)

## Stop Conditions

- All uncovered residues remain hard after q-search up to 10^6
- No novel parametric families found after budget exhaustion
- Results duplicate Salez (2014) without improvement
