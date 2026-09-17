# Self-contained demo: expose where an "LLM shortcut" silently diverges from a reference
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def reference_fold_change(control, treated):
    # Trusted reference: log2 fold change on properly averaged replicates
    c = np.mean(control, axis=1)
    t = np.mean(treated, axis=1)
    return np.log2((t + 1.0) / (c + 1.0))


def llm_shortcut_fold_change(control, treated):
    # A plausible-looking but subtly wrong shortcut: averages logs instead of
    # logging the averaged ratio, which biases genes with high variance
    c = np.mean(np.log2(control + 1.0), axis=1)
    t = np.mean(np.log2(treated + 1.0), axis=1)
    return t - c


def main():
    os.makedirs("figures", exist_ok=True)
    os.makedirs("results", exist_ok=True)

    rng = np.random.default_rng(42)
    n_genes = 300
    n_reps = 3

    base = rng.gamma(shape=2.0, scale=50.0, size=n_genes)
    control = np.array([base * rng.lognormal(0.0, 0.4, n_genes) for _ in range(n_reps)]).T
    effect = rng.lognormal(0.0, 0.3, n_genes)
    treated = np.array([base * effect * rng.lognormal(0.0, 0.4, n_genes) for _ in range(n_reps)]).T

    ref = reference_fold_change(control, treated)
    shortcut = llm_shortcut_fold_change(control, treated)
    diff = shortcut - ref

    summary = pd.DataFrame({
        "metric": ["mean_ref_lfc", "mean_shortcut_lfc", "max_abs_diff", "mean_abs_diff", "n_disagree_gt_0p5"],
        "value": [
            float(np.mean(ref)),
            float(np.mean(shortcut)),
            float(np.max(np.abs(diff))),
            float(np.mean(np.abs(diff))),
            int(np.sum(np.abs(diff) > 0.5)),
        ],
    })
    summary.to_csv("results/summary.csv", index=False)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    axes[0].scatter(ref, shortcut, s=10, alpha=0.5, color="steelblue")
    lims = [min(ref.min(), shortcut.min()), max(ref.max(), shortcut.max())]
    axes[0].plot(lims, lims, "r--", label="perfect agreement")
    axes[0].set_xlabel("reference log2 fold change")
    axes[0].set_ylabel("LLM shortcut log2 fold change")
    axes[0].set_title("Trusted vs shortcut")
    axes[0].legend()

    axes[1].hist(diff, bins=40, color="indianred", alpha=0.8)
    axes[1].axvline(0.0, color="black", linestyle="--")
    axes[1].set_xlabel("shortcut - reference")
    axes[1].set_ylabel("gene count")
    axes[1].set_title("Silent divergence")

    fig.suptitle("Verify before you trust: AI shortcut vs reference")
    fig.tight_layout()
    fig.savefig("figures/demo.png", dpi=120)
    print("Wrote figures/demo.png and results/summary.csv")


if __name__ == "__main__":
    main()
