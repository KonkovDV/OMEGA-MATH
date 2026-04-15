"""
Phase 2: Parametric Family Search for Erdős–Straus Conjecture
==============================================================
For hard primes p ≡ 1 (mod 24), systematically search for all decompositions.

Usage:
    python phase2_parametric.py [--max-n 10000] [--max-denom 10000000]
"""

import argparse
import json
import time
from math import gcd, isqrt
from pathlib import Path


def sieve_primes(limit: int) -> list[int]:
    sieve = bytearray(b'\x01') * (limit + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, isqrt(limit) + 1):
        if sieve[i]:
            sieve[i*i::i] = b'\x00' * len(sieve[i*i::i])
    return [i for i in range(2, limit + 1) if sieve[i]]


def find_all_decompositions(n: int, max_denom: int = 10**6) -> list[tuple[int, int, int]]:
    """Find ALL (x, y, z) with x ≤ y ≤ z and 4/n = 1/x + 1/y + 1/z."""
    solutions = []
    x_min = (n + 3) // 4
    x_max = min(3 * n // 4, max_denom)  # from 1/x >= (4/n)/3

    for x in range(x_min, x_max + 1):
        num = 4 * x - n
        if num <= 0:
            continue
        den = n * x
        # 1/y + 1/z = num/den, y ≤ z
        y_min = max(x, (den + num - 1) // num)
        y_max = min(2 * den // num, max_denom)

        for y in range(y_min, y_max + 1):
            zy_num = den * y
            zy_den = num * y - den
            if zy_den <= 0:
                continue
            if zy_num % zy_den == 0:
                z = zy_num // zy_den
                if z >= y and z <= max_denom:
                    solutions.append((x, y, z))

    return solutions


def classify_prime(p: int) -> str:
    """Classify difficulty of prime p for Erdős–Straus."""
    if p == 2:
        return "trivial"
    if p % 3 == 2 or p % 4 == 3:
        return "easy-modular"
    if p % 24 == 1:
        return "hard"
    return "medium"


def main():
    parser = argparse.ArgumentParser(description="Erdős–Straus parametric family search")
    parser.add_argument("--max-n", type=int, default=10000)
    parser.add_argument("--max-denom", type=int, default=10**6)
    parser.add_argument("--output", type=str, default="../artifacts/phase2_results.json")
    args = parser.parse_args()

    outpath = Path(__file__).parent / args.output
    outpath.parent.mkdir(parents=True, exist_ok=True)

    primes = sieve_primes(args.max_n)
    hard_primes = [p for p in primes if p % 24 == 1]

    print(f"Erdős–Straus Parametric Family Search")
    print(f"Total primes ≤ {args.max_n}: {len(primes)}")
    print(f"Hard primes (≡1 mod 24): {len(hard_primes)}")
    print(f"Max denominator: {args.max_denom}")
    print()

    results = {
        "meta": {
            "max_n": args.max_n,
            "max_denom": args.max_denom,
            "hard_prime_count": len(hard_primes),
        },
        "primes": {},
    }

    t0 = time.time()
    no_solution = []

    for i, p in enumerate(hard_primes):
        solutions = find_all_decompositions(p, args.max_denom)
        entry = {
            "prime": p,
            "solution_count": len(solutions),
            "first_solution": list(solutions[0]) if solutions else None,
            "classification": classify_prime(p),
        }
        results["primes"][str(p)] = entry

        if not solutions:
            no_solution.append(p)
            print(f"  ✗ p={p}: NO SOLUTION found (max_denom={args.max_denom})")
        elif i % 50 == 0:
            print(f"  p={p}: {len(solutions)} solutions, e.g. {solutions[0]}")

    elapsed = time.time() - t0
    results["meta"]["elapsed_sec"] = elapsed
    results["meta"]["unsolved_count"] = len(no_solution)
    results["meta"]["unsolved_primes"] = no_solution

    print(f"\nCompleted in {elapsed:.1f}s")
    print(f"Primes without solution (denom ≤ {args.max_denom}): {len(no_solution)}")
    if no_solution:
        print(f"  {no_solution[:20]}")

    with open(outpath, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {outpath}")


if __name__ == "__main__":
    main()
