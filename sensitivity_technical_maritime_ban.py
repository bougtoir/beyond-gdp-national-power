"""
感度分析: 技術的海禁政策 (Technical Maritime Ban)

定義:
  定期的な航路が存在せず、冒険者・探検家のみが到達可能であった
  時代・地域の国家を「技術的海禁政策」(technical_maritime_ban) として
  再分類し、分析結果への影響を検証する。

  ベースライン: 既存の closure_type 分類（政策的海禁のみ）
  感度分析:    上記 + 技術的海禁を maritime_ban に再分類

対象候補（closure_type="none" → "technical_maritime_ban"）:
  ─ 強い候補（定期航路が明確に不在） ─
  1. 漢朝（前漢〜後漢）: 古代東アジア。地中海世界との定期海路なし。
     シルクロードは陸路のみ。海路は冒険的商人のみ。
  2. マリ帝国: 中世サヘル地域。外部からの定期海路なし。
     接触はサハラ縦断キャラバン交易のみ。
  3. クメール帝国（アンコール）: 中世東南アジア内陸。
     海岸部のシュリーヴィジャヤとは異なり、外洋からの直接航路なし。
  4. キエフ大公国: 中世東欧。河川交易（ヴァリャーグ路）が主。
     外洋からの定期航路なし。
  5. ティムール朝: 近世中央アジア。完全内陸、海洋アクセスなし。

  ─ 中程度の候補（航路の定期性が不確実） ─
  6. ササン朝ペルシア: ペルシア湾貿易はあるが地中海・インド洋との
     定期海路は限定的。陸路シルクロードが主な国際接続。
  7. ビルマ（コンバウン朝）: 沿岸アクセスはあるが、定期的な国際海路は
     英国進出まで限定的。

シナリオ:
  A) ベースライン（変更なし）
  B) 強い候補のみ再分類（5国）
  C) 全候補再分類（7国）
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import scipy.stats as stats
import math
import statsmodels.api as sm
from scipy.stats import norm, ncx2
from data import load_data


# ============================================================
# 技術的海禁政策の対象エンティティ定義
# ============================================================

STRONG_CANDIDATES = [
    "漢朝（前漢〜後漢）",
    "マリ帝国",
    "クメール帝国（アンコール）",
    "キエフ大公国",
    "ティムール朝",
]

MODERATE_CANDIDATES = [
    "ササン朝ペルシア",
    "ビルマ（コンバウン朝）",
]

RATIONALE = {
    "漢朝（前漢〜後漢）": "古代東アジア。地中海世界からの定期海路なし。シルクロード陸路のみ。"
                          "海路到達は冒険的商人の散発的試みに限定",
    "マリ帝国": "中世サヘル。大西洋岸への定期航路は15世紀ポルトガル探検まで不在。"
                "外部接触はサハラ縦断キャラバンのみ",
    "クメール帝国（アンコール）": "中世内陸東南アジア。近隣のシュリーヴィジャヤは海洋国家だが、"
                               "アンコール自体は内陸に位置し外洋からの直接航路なし",
    "キエフ大公国": "中世東欧。ドニエプル川・ヴァリャーグ路（河川）が主な国際接続。"
                   "外洋からの定期航路なし",
    "ティムール朝": "近世中央アジア。完全内陸国家。海洋アクセスなし。"
                   "シルクロード陸路のみ",
    "ササン朝ペルシア": "ペルシア湾交易はあるが限定的。"
                       "インド洋・地中海との定期海路は未確立。陸路が主な国際接続",
    "ビルマ（コンバウン朝）": "沿岸部はあるが外洋定期航路は英国進出まで限定的。"
                            "内陸志向の閉鎖的経済構造",
}


def apply_technical_maritime_ban(df, candidates):
    """指定候補を technical_maritime_ban に再分類したDataFrameを返す"""
    df_new = df.copy()
    mask = df_new["entity"].isin(candidates)
    df_new.loc[mask, "closure_type"] = "technical_maritime_ban"
    return df_new


# ============================================================
# 分析関数群
# ============================================================

def compute_confusion_stats(df):
    """混同行列の統計量を計算して辞書で返す"""
    ct = pd.crosstab(df["dominant"], df["outcome"])
    ct = ct.reindex(index=["stock", "flow"], columns=["conquered", "survived"])

    TP = ct.loc["stock", "conquered"]
    FP = ct.loc["stock", "survived"]
    FN = ct.loc["flow", "conquered"]
    TN = ct.loc["flow", "survived"]
    N = TP + FP + FN + TN

    stock_rate = TP / (TP + FP) if (TP + FP) > 0 else 0
    flow_rate = FN / (FN + TN) if (FN + TN) > 0 else 0

    sensitivity = TP / (TP + FN) if (TP + FN) > 0 else 0
    specificity = TN / (TN + FP) if (TN + FP) > 0 else 0
    accuracy = (TP + TN) / N
    ppv = TP / (TP + FP) if (TP + FP) > 0 else 0
    npv = TN / (TN + FN) if (TN + FN) > 0 else 0

    odds_ratio = (TP * TN) / (FP * FN) if (FP * FN) > 0 else float("inf")
    phi = (TP * TN - FP * FN) / math.sqrt(
        max(1, (TP + FP) * (FN + TN) * (TP + FN) * (FP + TN))
    )

    table = np.array([[TP, FP], [FN, TN]])
    _, p_fisher = stats.fisher_exact(table, alternative="greater")
    chi2, p_chi2, _, _ = stats.chi2_contingency(table, correction=True)

    return {
        "N": N, "TP": TP, "FP": FP, "FN": FN, "TN": TN,
        "stock_conquest_rate": stock_rate,
        "flow_conquest_rate": flow_rate,
        "sensitivity": sensitivity,
        "specificity": specificity,
        "accuracy": accuracy,
        "ppv": ppv, "npv": npv,
        "OR": odds_ratio, "phi": phi,
        "p_fisher": p_fisher, "chi2": chi2, "p_chi2": p_chi2,
    }


def compute_closure_analysis(df):
    """closure_type 別の征服率と統計量"""
    results = {}
    for ct in df["closure_type"].unique():
        sub = df[df["closure_type"] == ct]
        n = len(sub)
        n_conquered = sum(sub["outcome"] == "conquered")
        rate = n_conquered / n if n > 0 else 0
        results[ct] = {"n": n, "conquered": n_conquered, "rate": rate}
    return results


def compute_logistic_with_closure(df, include_closure_binary=True):
    """海禁ダミーを含む多変量ロジスティック回帰"""
    y = df["outcome_binary"]
    df_work = df.copy()

    if include_closure_binary:
        df_work["has_maritime_ban"] = (
            df_work["closure_type"].isin(["maritime_ban", "technical_maritime_ban", "sakoku"])
        ).astype(int)

    covariates_base = [
        "dominant_binary", "geo_barrier", "external_threat",
        "tech_position", "institutional_quality", "era_code",
        "has_external_patron",
    ]
    covariates_with_ban = covariates_base + ["has_maritime_ban"]

    results = {}

    for name, covs in [
        ("base", covariates_base),
        ("with_ban", covariates_with_ban if include_closure_binary else covariates_base),
    ]:
        X = sm.add_constant(df_work[covs].astype(float))
        try:
            model = sm.Logit(y, X).fit(disp=0, maxiter=200)
            coefs = {}
            for var in covs:
                coefs[var] = {
                    "coef": model.params[var],
                    "OR": np.exp(model.params[var]),
                    "p": model.pvalues[var],
                    "ci_lo": np.exp(model.conf_int().loc[var, 0]),
                    "ci_hi": np.exp(model.conf_int().loc[var, 1]),
                }
            results[name] = {
                "aic": model.aic,
                "bic": model.bic,
                "pseudo_r2": model.prsquared,
                "coefs": coefs,
                "converged": True,
            }
        except Exception as e:
            results[name] = {"converged": False, "error": str(e)}

    return results


def compute_mediation_paths(df):
    """主要な媒介パスの効果量を計算"""
    y = df["outcome_binary"]
    x = df["dominant_binary"]

    paths = {}

    X_const = sm.add_constant(x)

    # Total effect (mediator-independent)
    c = None
    try:
        mod_total = sm.Logit(y, X_const).fit(disp=0)
        c = mod_total.params.iloc[1]
    except Exception:
        pass

    # Path: stock → tech_position → outcome
    try:
        mod_m = sm.OLS(df["tech_position"], X_const).fit()
        a = mod_m.params.iloc[1]
        XM = sm.add_constant(pd.DataFrame({"x": x, "m": df["tech_position"]}))
        mod_y = sm.Logit(y, XM).fit(disp=0, maxiter=100)
        b = mod_y.params["m"]
        c_prime = mod_y.params["x"]
        paths["tech"] = {"a": a, "b": b, "ab": a * b, "c": c, "c_prime": c_prime}
    except Exception:
        paths["tech"] = None

    # Path: stock → institutional_quality → outcome
    try:
        mod_m = sm.OLS(df["institutional_quality"], X_const).fit()
        a = mod_m.params.iloc[1]
        XM = sm.add_constant(pd.DataFrame({"x": x, "m": df["institutional_quality"]}))
        mod_y = sm.Logit(y, XM).fit(disp=0, maxiter=100)
        b = mod_y.params["m"]
        c_prime = mod_y.params["x"]
        paths["inst"] = {"a": a, "b": b, "ab": a * b, "c": c, "c_prime": c_prime}
    except Exception:
        paths["inst"] = None

    # Path: stock → trade_openness → outcome
    try:
        mod_m = sm.OLS(df["trade_openness"], X_const).fit()
        a = mod_m.params.iloc[1]
        XM = sm.add_constant(pd.DataFrame({"x": x, "m": df["trade_openness"]}))
        mod_y = sm.Logit(y, XM).fit(disp=0, maxiter=100)
        b = mod_y.params["m"]
        c_prime = mod_y.params["x"]
        paths["trade"] = {"a": a, "b": b, "ab": a * b, "c": c, "c_prime": c_prime}
    except Exception:
        paths["trade"] = None

    return paths


# ============================================================
# メイン感度分析
# ============================================================

def run_sensitivity():
    df_base = load_data()

    scenarios = {
        "A_baseline": {
            "label": "ベースライン（変更なし）",
            "df": df_base,
            "reclassified": [],
        },
        "B_strong": {
            "label": "強い候補のみ再分類（5国）",
            "df": apply_technical_maritime_ban(df_base, STRONG_CANDIDATES),
            "reclassified": STRONG_CANDIDATES,
        },
        "C_all": {
            "label": "全候補再分類（7国）",
            "df": apply_technical_maritime_ban(
                df_base, STRONG_CANDIDATES + MODERATE_CANDIDATES
            ),
            "reclassified": STRONG_CANDIDATES + MODERATE_CANDIDATES,
        },
    }

    # ============================================================
    # 1. 再分類対象の詳細
    # ============================================================
    print("=" * 80)
    print("感度分析: 技術的海禁政策 (Technical Maritime Ban)")
    print("=" * 80)

    print("\n【再分類対象エンティティ】")
    print("-" * 80)
    for entity in STRONG_CANDIDATES + MODERATE_CANDIDATES:
        row = df_base[df_base["entity"] == entity].iloc[0]
        strength = "強" if entity in STRONG_CANDIDATES else "中"
        print(f"\n  [{strength}] {entity}")
        print(f"      時代: {row['era']}, 地域: {row['region']}")
        print(f"      元の closure_type: {row['closure_type']}")
        print(f"      trade_openness: {row['trade_openness']:.2f}")
        print(f"      dominant: {row['dominant']}, outcome: {row['outcome']}")
        print(f"      根拠: {RATIONALE[entity]}")

    # ============================================================
    # 2. closure_type 分布の変化
    # ============================================================
    print("\n\n" + "=" * 80)
    print("SECTION 1: closure_type 分布の変化")
    print("=" * 80)

    for key, sc in scenarios.items():
        df_sc = sc["df"]
        print(f"\n  --- {sc['label']} ---")
        vc = df_sc["closure_type"].value_counts()
        for ct, n in vc.items():
            conquered = sum((df_sc["closure_type"] == ct) & (df_sc["outcome"] == "conquered"))
            rate = conquered / n
            print(f"    {ct:25s}: {n:3d}国  征服率={rate:.1%} ({conquered}/{n})")

    # ============================================================
    # 3. 混同行列比較
    # ============================================================
    print("\n\n" + "=" * 80)
    print("SECTION 2: 混同行列統計量の比較")
    print("=" * 80)

    cm_results = {}
    for key, sc in scenarios.items():
        cm_results[key] = compute_confusion_stats(sc["df"])

    header = f"  {'指標':25s}"
    for key in scenarios:
        header += f" {scenarios[key]['label'][:12]:>14s}"
    print(f"\n{header}")
    print(f"  {'-' * 70}")

    metrics = [
        ("OR (オッズ比)", "OR", ".3f"),
        ("φ係数", "phi", ".3f"),
        ("Fisher p値(片側)", "p_fisher", ".4f"),
        ("χ² (Yates)", "chi2", ".3f"),
        ("χ² p値", "p_chi2", ".4f"),
        ("感度", "sensitivity", ".1%"),
        ("特異度", "specificity", ".1%"),
        ("正確度", "accuracy", ".1%"),
        ("PPV", "ppv", ".1%"),
        ("NPV", "npv", ".1%"),
        ("ストック征服率", "stock_conquest_rate", ".1%"),
        ("フロー征服率", "flow_conquest_rate", ".1%"),
    ]

    for label, key_m, fmt in metrics:
        line = f"  {label:25s}"
        for key in scenarios:
            val = cm_results[key][key_m]
            line += f" {val:>14{fmt}}"
        print(line)

    # ============================================================
    # 4. 海禁ダミー付きロジスティック回帰
    # ============================================================
    print("\n\n" + "=" * 80)
    print("SECTION 3: 多変量ロジスティック回帰（海禁ダミー追加）")
    print("=" * 80)

    for key, sc in scenarios.items():
        print(f"\n  === {sc['label']} ===")
        lr = compute_logistic_with_closure(sc["df"])

        for model_name, model_label in [
            ("base", "基本モデル（海禁ダミーなし）"),
            ("with_ban", "拡張モデル（海禁ダミーあり）"),
        ]:
            r = lr[model_name]
            if not r.get("converged", False):
                print(f"\n    [{model_label}] 収束失敗: {r.get('error', 'N/A')}")
                continue
            print(f"\n    [{model_label}]")
            print(f"      AIC={r['aic']:.1f}, BIC={r['bic']:.1f}, Pseudo-R²={r['pseudo_r2']:.3f}")
            print(f"      {'変数':30s} {'OR':>8s} {'95%CI':>22s} {'p値':>8s}")
            print(f"      {'-'*70}")
            for var, v in r["coefs"].items():
                sig = " *" if v["p"] < 0.05 else "  " if v["p"] < 0.10 else ""
                print(f"      {var:30s} {v['OR']:>8.3f} [{v['ci_lo']:>7.3f}, {v['ci_hi']:>7.3f}] {v['p']:>8.4f}{sig}")

    # ============================================================
    # 5. 海禁タイプ別の征服率（詳細）
    # ============================================================
    print("\n\n" + "=" * 80)
    print("SECTION 4: 海禁タイプ別征服率の詳細比較")
    print("=" * 80)

    for key, sc in scenarios.items():
        print(f"\n  === {sc['label']} ===")
        df_sc = sc["df"]

        # 海禁あり vs なし
        has_ban = df_sc["closure_type"].isin(
            ["maritime_ban", "technical_maritime_ban", "sakoku"]
        )
        ban_df = df_sc[has_ban]
        no_ban_df = df_sc[~has_ban]

        ban_rate = sum(ban_df["outcome"] == "conquered") / len(ban_df) if len(ban_df) > 0 else 0
        no_rate = sum(no_ban_df["outcome"] == "conquered") / len(no_ban_df) if len(no_ban_df) > 0 else 0

        print(f"    海禁あり: {len(ban_df)}国, 征服率={ban_rate:.1%}")
        print(f"    海禁なし: {len(no_ban_df)}国, 征服率={no_rate:.1%}")

        if len(ban_df) > 0 and len(no_ban_df) > 0:
            # Risk difference & ratio
            rd = ban_rate - no_rate
            rr = ban_rate / no_rate if no_rate > 0 else float("inf")
            print(f"    リスク差: {rd:+.1%}")
            print(f"    リスク比: {rr:.3f}")

            # Fisher's exact test for ban vs no-ban
            ban_conq = sum(ban_df["outcome"] == "conquered")
            ban_surv = len(ban_df) - ban_conq
            no_conq = sum(no_ban_df["outcome"] == "conquered")
            no_surv = len(no_ban_df) - no_conq
            table = np.array([[ban_conq, ban_surv], [no_conq, no_surv]])
            _, p = stats.fisher_exact(table, alternative="greater")
            print(f"    Fisher検定 (海禁→征服): p={p:.4f}")

    # ============================================================
    # 6. 媒介分析の感度
    # ============================================================
    print("\n\n" + "=" * 80)
    print("SECTION 5: 媒介分析パス係数の感度比較")
    print("=" * 80)

    path_labels = {
        "tech": "ストック優位→技術水準→征服",
        "inst": "ストック優位→制度品質→征服",
        "trade": "ストック優位→貿易開放度→征服",
    }

    med_results = {}
    for key, sc in scenarios.items():
        med_results[key] = compute_mediation_paths(sc["df"])

    for path_key, path_label in path_labels.items():
        print(f"\n  【{path_label}】")
        cprime_label = "c' (直接)"
        print(f"    {'シナリオ':14s} {'a (X→M)':>10s} {'b (M→Y)':>10s} {'a×b (間接)':>12s} {'c (総効果)':>12s} {cprime_label:>12s}")
        print(f"    {'-' * 72}")
        for key in scenarios:
            r = med_results[key].get(path_key)
            if r is None:
                print(f"    {scenarios[key]['label'][:14]:14s}  (収束失敗)")
                continue
            print(f"    {scenarios[key]['label'][:14]:14s} {r['a']:>10.4f} {r['b']:>10.4f} {r['ab']:>12.4f} {r['c']:>12.4f} {r['c_prime']:>12.4f}")

    # ============================================================
    # 7. 技術的海禁の効果: 反実仮想
    # ============================================================
    print("\n\n" + "=" * 80)
    print("SECTION 6: 反実仮想分析 — 技術的海禁国が開放的だった場合")
    print("=" * 80)

    df_c = scenarios["C_all"]["df"]
    tech_ban = df_c[df_c["closure_type"] == "technical_maritime_ban"]

    print(f"\n  技術的海禁に再分類された {len(tech_ban)} 国:")
    for _, row in tech_ban.iterrows():
        print(f"    {row['entity']:30s} | dominant={row['dominant']:5s} | outcome={row['outcome']}")

    # Compare: what if these entities had higher trade_openness?
    print(f"\n  【反実仮想: trade_openness を +0.2 したら？】")
    df_cf = df_c.copy()
    mask = df_cf["closure_type"] == "technical_maritime_ban"
    original_to = df_cf.loc[mask, "trade_openness"].values.copy()
    df_cf.loc[mask, "trade_openness"] = np.minimum(1.0, df_cf.loc[mask, "trade_openness"] + 0.2)

    # Re-run logistic with counterfactual
    y = df_cf["outcome_binary"]
    df_cf["has_maritime_ban"] = df_cf["closure_type"].isin(
        ["maritime_ban", "technical_maritime_ban", "sakoku"]
    ).astype(int)
    covs = ["dominant_binary", "trade_openness", "geo_barrier", "external_threat",
            "tech_position", "institutional_quality", "era_code", "has_external_patron"]
    X = sm.add_constant(df_cf[covs].astype(float))
    try:
        model = sm.Logit(y, X).fit(disp=0, maxiter=200)
        print(f"\n    反実仮想モデル (trade_openness +0.2 for tech_ban entities):")
        print(f"    AIC={model.aic:.1f}, Pseudo-R²={model.prsquared:.3f}")
        for var in covs:
            sig = " *" if model.pvalues[var] < 0.05 else ""
            print(f"      {var:30s} OR={np.exp(model.params[var]):.3f}  p={model.pvalues[var]:.4f}{sig}")
    except Exception as e:
        print(f"    収束失敗: {e}")

    # ============================================================
    # 8. ブートストラップによるOR感度
    # ============================================================
    print("\n\n" + "=" * 80)
    print("SECTION 7: ブートストラップOR推定（各シナリオ）")
    print("=" * 80)

    rng = np.random.default_rng(42)
    n_boot = 5000

    for key, sc in scenarios.items():
        df_sc = sc["df"]
        n = len(df_sc)
        boot_ors = np.zeros(n_boot)

        for i in range(n_boot):
            idx = rng.choice(n, size=n, replace=True)
            boot_df = df_sc.iloc[idx].reset_index(drop=True)
            try:
                ct = pd.crosstab(boot_df["dominant"], boot_df["outcome"])
                ct = ct.reindex(index=["stock", "flow"], columns=["conquered", "survived"], fill_value=0)
                tp = ct.loc["stock", "conquered"]
                fp = ct.loc["stock", "survived"]
                fn = ct.loc["flow", "conquered"]
                tn = ct.loc["flow", "survived"]
                boot_ors[i] = (tp * tn) / (fp * fn) if (fp * fn) > 0 else np.nan
            except (KeyError, ZeroDivisionError):
                boot_ors[i] = np.nan

        valid = boot_ors[~np.isnan(boot_ors)]
        if len(valid) >= 100:
            ci_lo, ci_hi = np.percentile(valid, [2.5, 97.5])
            median_or = np.median(valid)
            print(f"\n  {sc['label']}:")
            print(f"    Bootstrap OR: median={median_or:.3f}, 95%CI=[{ci_lo:.3f}, {ci_hi:.3f}]")
            print(f"    Point estimate OR: {cm_results[key]['OR']:.3f}")

    # ============================================================
    # 9. サマリーテーブル
    # ============================================================
    print("\n\n" + "=" * 80)
    print("SUMMARY: 感度分析結果一覧")
    print("=" * 80)

    summary_rows = []
    for key, sc in scenarios.items():
        cm = cm_results[key]
        lr = compute_logistic_with_closure(sc["df"])
        ban_info = compute_closure_analysis(sc["df"])

        n_ban = sum(
            v["n"] for k, v in ban_info.items()
            if k in ["maritime_ban", "technical_maritime_ban", "sakoku"]
        )
        ban_rate = sum(
            v["conquered"] for k, v in ban_info.items()
            if k in ["maritime_ban", "technical_maritime_ban", "sakoku"]
        ) / n_ban if n_ban > 0 else 0

        row = {
            "シナリオ": sc["label"],
            "再分類数": len(sc["reclassified"]),
            "海禁国数": n_ban,
            "海禁征服率": f"{ban_rate:.1%}",
            "OR": f"{cm['OR']:.3f}",
            "φ": f"{cm['phi']:.3f}",
            "Fisher p": f"{cm['p_fisher']:.4f}",
        }

        lr_with = lr.get("with_ban", {})
        if lr_with.get("converged"):
            ban_coef = lr_with["coefs"].get("has_maritime_ban", {})
            row["海禁OR(多変量)"] = f"{ban_coef.get('OR', 'N/A'):.3f}" if ban_coef else "N/A"
            row["海禁p(多変量)"] = f"{ban_coef.get('p', 'N/A'):.4f}" if ban_coef else "N/A"
        else:
            row["海禁OR(多変量)"] = "NC"
            row["海禁p(多変量)"] = "NC"

        summary_rows.append(row)

    summary_df = pd.DataFrame(summary_rows)
    print(f"\n{summary_df.to_string(index=False)}")

    # ============================================================
    # 10. 解釈
    # ============================================================
    print("\n\n" + "=" * 80)
    print("解釈と考察")
    print("=" * 80)

    or_base = cm_results["A_baseline"]["OR"]
    or_strong = cm_results["B_strong"]["OR"]
    or_all = cm_results["C_all"]["OR"]

    p_base = cm_results["A_baseline"]["p_fisher"]
    p_strong = cm_results["B_strong"]["p_fisher"]
    p_all = cm_results["C_all"]["p_fisher"]

    print(f"""
  1. 【OR（オッズ比）の頑健性】
     ベースライン OR = {or_base:.3f}
     強い候補再分類 OR = {or_strong:.3f} (Δ = {or_strong - or_base:+.3f})
     全候補再分類   OR = {or_all:.3f} (Δ = {or_all - or_base:+.3f})
     → 技術的海禁の再分類は主要結果に {'大きく' if abs(or_strong - or_base) > 0.3 else '軽微に'}影響。

  2. 【統計的有意性の安定性】
     ベースライン Fisher p = {p_base:.4f} {'(有意)' if p_base < 0.05 else '(非有意)'}
     強い候補再分類 Fisher p = {p_strong:.4f} {'(有意)' if p_strong < 0.05 else '(非有意)'}
     全候補再分類   Fisher p = {p_all:.4f} {'(有意)' if p_all < 0.05 else '(非有意)'}
     → {'結論は全シナリオで一貫している。' if (p_base < 0.05) == (p_strong < 0.05) == (p_all < 0.05)
        else '一部シナリオで統計的有意性が変化する。'}

  3. 【技術的海禁の含意】
     定期航路の不在（技術的海禁）は、政策的海禁と異なり意図的選択ではない。
     しかし、フロー遮断の効果は類似している可能性がある。
     再分類により海禁国の征服率パターンが変化するかを検証することで、
     「閉鎖性」の操作的定義に対する分析の感度を評価できる。

  4. 【政策的海禁 vs 技術的海禁】
     政策的海禁は「選択的閉鎖」であり、国家が意図的にフローを制限する。
     技術的海禁は「受動的閉鎖」であり、技術・地理的制約によりフローが不可能。
     両者が同様の帰結をもたらすならば、閉鎖メカニズムは意図ではなく
     フロー遮断そのものに由来することを示唆する。
""")


if __name__ == "__main__":
    run_sensitivity()
