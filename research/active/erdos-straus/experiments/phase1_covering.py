"""
Phase 1: Covering Congruence Machine for Erdős–Straus Conjecture
================================================================
For each uncovered residue r mod 840, find primes q where r is NOT a QR mod q,
then attempt to construct polynomial identities covering n ≡ r (mod q).

Usage:
    python phase1_covering.py [--max-q 100000] [--verify-count 1000]
"""

import argparse
import json
from math import isqrt
from pathlib import Path
from typing import Any, Optional


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def primes_up_to(limit: int) -> list[int]:
    sieve = bytearray(b'\x01') * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, isqrt(limit) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]


def legendre_symbol(a: int, p: int) -> int:
    """Compute Legendre symbol (a/p) for odd prime p."""
    if a % p == 0:
        return 0
    result = pow(a, (p - 1) // 2, p)
    return -1 if result == p - 1 else result


def find_decomposition(n: int, max_denom: int = 10**7) -> Optional[tuple[int, int, int]]:
    """Find x, y, z > 0 such that 4/n = 1/x + 1/y + 1/z."""
    # x >= n/4 (ceiling), x <= n (from 4/n >= 1/x requires x >= n/4)
    x_min = (n + 3) // 4  # ceiling(n/4)
    x_max = min(n, max_denom)  # 4/n <= 3/x → x <= 3n/4 but we allow larger

    for x in range(x_min, x_max + 1):
        # 4/n - 1/x = (4x - n) / (nx)
        num = 4 * x - n
        if num <= 0:
            continue
        den = n * x
        # Need 1/y + 1/z = num/den with y <= z
        # y >= den/num (ceiling), y <= 2*den/num
        y_min = (den + num - 1) // num  # ceiling(den/num)
        y_max = min(2 * den // num, max_denom)
        for y in range(y_min, y_max + 1):
            # z = den * y / (num * y - den)
            zy_num = den * y
            zy_den = num * y - den
            if zy_den <= 0:
                continue
            if zy_num % zy_den == 0:
                z = zy_num // zy_den
                if z >= y and z <= max_denom:
                    return (x, y, z)
    return None


def check_mordell_identities(n: int) -> Optional[str]:
    """Check if n is covered by Mordell's modular identities."""
    if n % 3 == 2:
        return "n ≡ 2 (mod 3)"
    if n % 4 == 3:
        return "n ≡ 3 (mod 4)"
    if n % 5 in (2, 3):
        return f"n ≡ {n % 5} (mod 5)"
    if n % 7 in (3, 5, 6):
        return f"n ≡ {n % 7} (mod 7)"
    if n % 8 == 5:
        return "n ≡ 5 (mod 8)"
    return None


UNCOVERED_MOD840 = [1, 121, 169, 289, 361, 529]
# NOTE: These are all perfect squares (1², 11², 13², 17², 19², 23²).
# Mordell's barrier: k² is ALWAYS a QR mod any odd prime, so Legendre-based
# covering is impossible for these residues. We need direct decomposition search
# and divisibility-based identities instead.


def try_parametric_formulas(n: int) -> Optional[tuple[int, int, int, str]]:
    """Try known parametric formulas that work for specific forms of n."""
    # Formula A: n = 4k+3 → 4/(4k+3) = 1/(k+1) + 1/((k+1)(4k+3))  — covered
    # Formula B: If n ≡ 0 (mod 4), trivial
    # Formula C: For n = 4k+1, try x = k+1
    #   4/(4k+1) - 1/(k+1) = (4k+4-4k-1)/((4k+1)(k+1)) = 3/((4k+1)(k+1))
    #   Need 1/y + 1/z = 3/((4k+1)(k+1))
    if n % 4 == 1:
        k = (n - 1) // 4
        x = k + 1
        rest_den = n * x
        if rest_den % 3 == 0:
            # Potential equal-denominator branch for the residual term.
            pass
    # Formula D: Try x = ceil(n/4)
    x = (n + 3) // 4
    rem_num = 4 * x - n
    rem_den = n * x
    if rem_den % rem_num == 0:
        y = rem_den // rem_num
        return (x, y, y, "ceil_formula")  # 1/y + 1/y = 2/y
    # Formula E: Try x = ceil(n/4), then greedy for y
    if rem_num > 0:
        y = (rem_den + rem_num - 1) // rem_num
        z_num = rem_den * y
        z_den = rem_num * y - rem_den
        if z_den > 0 and z_num % z_den == 0:
            z = z_num // z_den
            return (x, y, z, "greedy_formula")
    return None


def search_decompositions_for_residue(
    r: int, mod: int, max_count: int = 200, max_denom: int = 10**6
) -> dict[str, Any]:
    """For primes p ≡ r (mod mod), find decompositions and patterns."""
    test_primes: list[int] = []
    n = r if r > 1 else r + mod
    while len(test_primes) < max_count:
        if is_prime(n):
            test_primes.append(n)
        n += mod

    successes = 0
    failures: list[int] = []
    formula_hits = {"parametric": 0, "brute": 0}
    max_denom_needed = 0

    for p in test_primes:
        # Try parametric first
        pf = try_parametric_formulas(p)
        if pf:
            successes += 1
            formula_hits["parametric"] += 1
            continue
        # Brute force
        result = find_decomposition(p, max_denom=max_denom)
        if result:
            successes += 1
            formula_hits["brute"] += 1
            max_denom_needed = max(max_denom_needed, max(result))
        else:
            failures.append(p)

    return {
        "residue": r,
        "modulus": mod,
        "tested": len(test_primes),
        "successes": successes,
        "failures": failures[:20],
        "coverage": successes / len(test_primes) if test_primes else 0,
        "formula_hits": formula_hits,
        "max_denom_needed": max_denom_needed,
        "note": "Mordell barrier: QR-based covering impossible for perfect square residues",
    }


def main():
    parser = argparse.ArgumentParser(description="Erdős–Straus covering congruence search")
    parser.add_argument("--max-q", type=int, default=10000, help="Max prime q to search")
    parser.add_argument("--verify-count", type=int, default=200, help="Samples per identity")
    parser.add_argument("--max-denom", type=int, default=10**6, help="Maximum denominator used in bounded decomposition search")
    parser.add_argument("--output", type=str, default="../artifacts/phase1_results.json")
    args = parser.parse_args()

    outpath = Path(__file__).parent / args.output
    outpath.parent.mkdir(parents=True, exist_ok=True)

    print(f"Erdős–Straus Covering Analysis")
    print(f"Uncovered residues mod 840: {UNCOVERED_MOD840}")
    print(f"(All are perfect squares — Mordell's barrier applies)")
    print(f"Strategy: direct decomposition search + pattern detection")
    print(f"Max denominator: {args.max_denom}")
    print()

    all_results = {
        "_meta": {
            "verify_count": args.verify_count,
            "max_denom": args.max_denom,
        }
    }
    for r in UNCOVERED_MOD840:
        print(f"\n--- Residue r = {r} (= {int(r**0.5 + 0.5)}²) mod 840 ---")
        result = search_decompositions_for_residue(
            r, 840, max_count=args.verify_count, max_denom=args.max_denom
        )
        print(f"  Coverage: {result['coverage']:.1%} ({result['successes']}/{result['tested']})")
        print(f"  Parametric: {result['formula_hits']['parametric']}, Brute: {result['formula_hits']['brute']}")
        if result['failures']:
            print(f"  Unsolved: {result['failures'][:5]}...")
        else:
            print(f"  ✓ All primes solved!")
        all_results[str(r)] = result

    # Save results
    with open(outpath, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults saved to {outpath}")


if __name__ == "__main__":
    main()
