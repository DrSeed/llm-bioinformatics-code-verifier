# Verification harness: check a fast implementation against a trusted reference
import numpy as np


def reference_zscore(x):
    # Slow-but-obvious reference: standardise a vector
    mu = sum(x) / len(x)
    var = sum((v - mu) ** 2 for v in x) / len(x)
    sd = var ** 0.5
    return [(v - mu) / sd for v in x]


def fast_zscore(x):
    # Vectorised version an LLM might hand you
    x = np.asarray(x, dtype=float)
    return (x - x.mean()) / x.std()


def check_invariants(z):
    # A correct z-score has mean ~0 and std ~1
    z = np.asarray(z, dtype=float)
    assert abs(z.mean()) < 1e-8, "z-score mean should be ~0"
    assert abs(z.std() - 1.0) < 1e-8, "z-score std should be ~1"


def verify(x, tol=1e-8):
    ref = np.asarray(reference_zscore(x))
    fast = np.asarray(fast_zscore(x))
    max_diff = float(np.max(np.abs(ref - fast)))
    check_invariants(fast)
    ok = max_diff < tol
    return ok, max_diff


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    data = rng.normal(5.0, 2.0, size=200).tolist()
    ok, diff = verify(data)
    print("reference vs fast max diff:", diff)
    print("verification passed:", ok)
    if not ok:
        raise SystemExit("Verification FAILED - do not trust the fast implementation")
