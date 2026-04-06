import Mathlib

namespace OmegaWorkbench

theorem add_zero_commutes (n : Nat) : n + 0 = n := by
  simpa using Nat.add_zero n

theorem zero_add_echo (n : Nat) : 0 + n = n := by
  simpa using Nat.zero_add n

end OmegaWorkbench