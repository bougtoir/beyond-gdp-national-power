"""
感度分析の可視化: 技術的海禁政策
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib import rcParams
import os

from sensitivity_technical_maritime_ban import (
    STRONG_CANDIDATES, MODERATE_CANDIDATES,
    apply_technical_maritime_ban, compute_closure_analysis,
)
from data import load_data
import scipy.stats as stats

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(SCRIPT_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# Japanese font setup
for f in fm.findSystemFonts():
    if any(name in f.lower() for name in ['noto', 'cjk', 'gothic', 'mincho']):
        prop = fm.FontProperties(fname=f)
        rcParams['font.family'] = prop.get_name()
        break
else:
    rcParams['font.family'] = 'DejaVu Sans'

rcParams['axes.unicode_minus'] = False


def plot_conquest_rates_by_closure():
    """Figure 1: closure_type 別征服率の比較（3シナリオ）"""
    df_base = load_data()
    scenarios = {
        "Baseline\n(N=96)": df_base,
        "Strong\n(+5 tech ban)": apply_technical_maritime_ban(df_base, STRONG_CANDIDATES),
        "All\n(+7 tech ban)": apply_technical_maritime_ban(
            df_base, STRONG_CANDIDATES + MODERATE_CANDIDATES
        ),
    }

    fig, axes = plt.subplots(1, 3, figsize=(18, 6), sharey=True)

    for ax, (sc_name, df_sc) in zip(axes, scenarios.items()):
        closure_types = sorted(df_sc["closure_type"].unique())
        rates = []
        ns = []
        colors = []
        color_map = {
            "none": "#4ECDC4",
            "bloc": "#45B7D1",
            "maritime_ban": "#FF6B6B",
            "technical_maritime_ban": "#FFB347",
            "sakoku": "#C44D58",
        }
        for ct in closure_types:
            sub = df_sc[df_sc["closure_type"] == ct]
            n = len(sub)
            r = sum(sub["outcome"] == "conquered") / n if n > 0 else 0
            rates.append(r * 100)
            ns.append(n)
            colors.append(color_map.get(ct, "#999999"))

        bars = ax.bar(range(len(closure_types)), rates, color=colors, edgecolor="white", linewidth=1.5)

        for bar, r, n in zip(bars, rates, ns):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                    f"{r:.0f}%\n(n={n})", ha="center", va="bottom", fontsize=9, fontweight="bold")

        labels = [ct.replace("_", "\n") for ct in closure_types]
        ax.set_xticks(range(len(closure_types)))
        ax.set_xticklabels(labels, fontsize=8)
        ax.set_title(sc_name, fontsize=12, fontweight="bold")
        ax.set_ylim(0, 115)
        ax.axhline(y=66.7, color="gray", linestyle="--", alpha=0.5, label="Overall avg")
        if ax == axes[0]:
            ax.set_ylabel("Conquest Rate (%)", fontsize=11)

    fig.suptitle("Sensitivity Analysis: Conquest Rate by Closure Type",
                 fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    path = os.path.join(FIG_DIR, "sensitivity_conquest_rates.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")
    return path


def plot_fisher_p_progression():
    """Figure 2: 海禁→征服 Fisher p値のシナリオ別推移"""
    df_base = load_data()

    steps = [
        ("Baseline\n(policy ban only)", []),
    ]
    for i, c in enumerate(STRONG_CANDIDATES, 1):
        steps.append((f"+{c[:6]}...\n(strong {i})", STRONG_CANDIDATES[:i]))
    for i, c in enumerate(MODERATE_CANDIDATES, 1):
        idx = len(STRONG_CANDIDATES) + i
        steps.append((f"+{c[:6]}...\n(moderate {i})", STRONG_CANDIDATES + MODERATE_CANDIDATES[:i]))

    p_values = []
    risk_diffs = []
    labels = []

    for label, candidates in steps:
        df_sc = apply_technical_maritime_ban(df_base, candidates) if candidates else df_base
        has_ban = df_sc["closure_type"].isin(
            ["maritime_ban", "technical_maritime_ban", "sakoku"]
        )
        ban_df = df_sc[has_ban]
        no_ban_df = df_sc[~has_ban]

        ban_conq = sum(ban_df["outcome"] == "conquered")
        ban_surv = len(ban_df) - ban_conq
        no_conq = sum(no_ban_df["outcome"] == "conquered")
        no_surv = len(no_ban_df) - no_conq

        table = np.array([[ban_conq, ban_surv], [no_conq, no_surv]])
        _, p = stats.fisher_exact(table, alternative="greater")
        p_values.append(p)

        ban_rate = ban_conq / len(ban_df) if len(ban_df) > 0 else 0
        no_rate = no_conq / len(no_ban_df) if len(no_ban_df) > 0 else 0
        risk_diffs.append((ban_rate - no_rate) * 100)
        labels.append(label)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)

    # Top: Fisher p-values
    colors = ["green" if p < 0.05 else "orange" if p < 0.10 else "red" for p in p_values]
    bars = ax1.bar(range(len(labels)), p_values, color=colors, edgecolor="white", linewidth=1.5)
    ax1.axhline(y=0.05, color="red", linestyle="--", linewidth=2, label="p = 0.05")
    ax1.axhline(y=0.10, color="orange", linestyle="--", linewidth=1, alpha=0.7, label="p = 0.10")
    for bar, p in zip(bars, p_values):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                 f"{p:.4f}", ha="center", va="bottom", fontsize=8, fontweight="bold")
    ax1.set_ylabel("Fisher p-value (one-sided)", fontsize=11)
    ax1.set_title("Maritime Ban -> Conquest: Fisher Exact Test p-value", fontsize=12, fontweight="bold")
    ax1.legend(fontsize=9)
    ax1.set_ylim(0, max(p_values) * 1.3)

    # Bottom: Risk difference
    colors2 = ["#FF6B6B" if rd > 20 else "#FFB347" if rd > 10 else "#4ECDC4" for rd in risk_diffs]
    bars2 = ax2.bar(range(len(labels)), risk_diffs, color=colors2, edgecolor="white", linewidth=1.5)
    for bar, rd in zip(bars2, risk_diffs):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                 f"{rd:+.1f}%", ha="center", va="bottom", fontsize=8, fontweight="bold")
    ax2.set_ylabel("Risk Difference (ban - no ban, %pts)", fontsize=11)
    ax2.set_title("Conquest Risk Difference: Maritime Ban vs Open", fontsize=12, fontweight="bold")
    ax2.set_xticks(range(len(labels)))
    ax2.set_xticklabels(labels, fontsize=7, rotation=0)

    fig.suptitle("Technical Maritime Ban Sensitivity Analysis\n"
                 "Incremental Reclassification of Isolated States",
                 fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    path = os.path.join(FIG_DIR, "sensitivity_fisher_progression.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")
    return path


def plot_policy_vs_technical():
    """Figure 3: 政策的海禁 vs 技術的海禁 vs 開放の征服率比較"""
    df_base = load_data()
    df_all = apply_technical_maritime_ban(
        df_base, STRONG_CANDIDATES + MODERATE_CANDIDATES
    )

    categories = {
        "Policy\nMaritime Ban\n(explicit)": df_all[df_all["closure_type"] == "maritime_ban"],
        "Technical\nMaritime Ban\n(geographic)": df_all[df_all["closure_type"] == "technical_maritime_ban"],
        "Sakoku\n(total\nclosure)": df_all[df_all["closure_type"] == "sakoku"],
        "Bloc\n(ideological)": df_all[df_all["closure_type"] == "bloc"],
        "None\n(open)": df_all[df_all["closure_type"] == "none"],
    }

    fig, ax = plt.subplots(figsize=(12, 7))

    x_pos = range(len(categories))
    rates = []
    ns = []
    colors = ["#FF6B6B", "#FFB347", "#C44D58", "#45B7D1", "#4ECDC4"]

    for (label, sub), color in zip(categories.items(), colors):
        n = len(sub)
        r = sum(sub["outcome"] == "conquered") / n * 100 if n > 0 else 0
        rates.append(r)
        ns.append(n)

    bars = ax.bar(x_pos, rates, color=colors, edgecolor="white", linewidth=2, width=0.6)

    for bar, r, n in zip(bars, rates, ns):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
                f"{r:.0f}%\n(n={n})", ha="center", va="bottom", fontsize=11, fontweight="bold")

    ax.set_xticks(x_pos)
    ax.set_xticklabels(categories.keys(), fontsize=10)
    ax.set_ylabel("Conquest Rate (%)", fontsize=12)
    ax.set_title("Conquest Rate by Closure Type\n"
                 "(Scenario C: All Candidates Reclassified, N=96)",
                 fontsize=13, fontweight="bold")
    ax.set_ylim(0, 115)
    ax.axhline(y=66.7, color="gray", linestyle="--", alpha=0.5)
    ax.text(len(categories) - 0.5, 68, "Overall avg (66.7%)", fontsize=9, color="gray")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    plt.tight_layout()
    path = os.path.join(FIG_DIR, "sensitivity_policy_vs_technical.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")
    return path


if __name__ == "__main__":
    p1 = plot_conquest_rates_by_closure()
    p2 = plot_fisher_p_progression()
    p3 = plot_policy_vs_technical()
    print(f"\nAll figures saved to {FIG_DIR}/")
