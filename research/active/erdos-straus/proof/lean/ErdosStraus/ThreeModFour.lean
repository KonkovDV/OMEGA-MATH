import Mathlib

/-!
# Erdős–Straus for n ≡ 3 (mod 4)

The Erdős–Straus conjecture says that `4 / n = 1/x + 1/y + 1/z` has a solution in
positive integers for every `n ≥ 2`. For `n = 4k + 3` there is a classical identity:

  4 / (4k+3) = 1/(k+1) + 1/(2(k+1)(4k+3)) + 1/(2(k+1)(4k+3)).

This is a known, elementary case (it is one of the residue classes Mordell's
identities cover). It is here as the first machine-checked statement of the
erdos-straus workspace, not as a new result.
-/

namespace ErdosStraus

theorem three_mod_four (k : ℕ) :
    ∃ x y z : ℕ, 0 < x ∧ 0 < y ∧ 0 < z ∧
      (4 : ℚ) / (4 * k + 3) = 1 / x + 1 / y + 1 / z := by
  refine ⟨k + 1, 2 * (k + 1) * (4 * k + 3), 2 * (k + 1) * (4 * k + 3),
    by positivity, by positivity, by positivity, ?_⟩
  push_cast
  field_simp
  ring

end ErdosStraus
