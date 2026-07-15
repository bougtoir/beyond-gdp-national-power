"""
Generate reproducible LaTeX manuscript sources and submission materials.

Outputs (in manuscript/):
  manuscript.tex       — Main manuscript (LaTeX source)
  references.bib       — BibTeX bibliography
  manuscript.pdf       — Compiled PDF
  table_s1.tex         — Supplementary Table S1 (LaTeX)
  table_s1.pdf         — Supplementary Table S1 (PDF)
  cover_letter.tex/pdf — Cover letter
  figures/Fig1–Fig4.png — Separate figure files (unchanged)
  figures_pptx.pptx    — Editable PPTX (unchanged)
"""

import os
import sys
import re
import shutil
import subprocess
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import scipy.stats as stats
from docx import Document
from docx.shared import Cm, Pt

# reuse everything from the docx script
sys.path.insert(0, os.path.dirname(__file__))
from data import load_data
from sensitivity_technical_network_exclusion import (
    STRONG_CANDIDATES, MODERATE_CANDIDATES, RATIONALE,
    apply_technical_network_exclusion, apply_disrupted_assignment,
    compute_confusion_stats, compute_closure_analysis,
    compute_logistic_with_closure, compute_mediation_paths,
)
from create_manuscript import (
    run_analysis, create_figures, create_pptx, create_table_s1,
    MODERN_COUNTRY, ENGLISH_NAME, TURNING_POINT,
)

OUT = os.path.join(os.path.dirname(__file__), "manuscript")
FIG = os.path.join(OUT, "figures")
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__),
                            "springer-template", "sn-article-template")
os.makedirs(FIG, exist_ok=True)


def _esc(text):
    """Escape special LaTeX characters in plain text."""
    text = str(text)
    # Replace non-ASCII text with ASCII/LaTeX equivalents
    text = text.replace('\u73fe\u5728', 'present')  # 現在
    text = text.replace('\u301c', '--')  # 〜
    text = text.replace('\u2013', '--')  # –
    mapping = {
        '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#',
        '_': r'\_', '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
    }
    for char, replacement in mapping.items():
        text = text.replace(char, replacement)
    return text


def _pct(value):
    """Format a 0-1 fraction as a LaTeX-safe percentage string like '83.3\\%'."""
    return f"{value*100:.1f}\\%"


def _compile_latex(tex_path, out_dir):
    """Compile a .tex file to PDF using pdflatex + bibtex."""
    basename = os.path.splitext(os.path.basename(tex_path))[0]
    pdf = os.path.join(out_dir, basename + ".pdf")
    if shutil.which("pdflatex") is None:
        if os.path.exists(pdf):
            os.remove(pdf)
        return None

    cmd_latex = [
        "pdflatex", "-interaction=nonstopmode",
        "-output-directory", out_dir, tex_path
    ]

    # Clean aux to avoid duplicate bibstyle entries
    aux_path = os.path.join(out_dir, basename + ".aux")
    for ext in (".aux", ".bbl", ".blg"):
        p = os.path.join(out_dir, basename + ext)
        if os.path.exists(p):
            os.remove(p)

    # first pass (generates .aux with citation keys)
    subprocess.run(cmd_latex, capture_output=True, timeout=120)

    # bibtex (resolves citations from .bib file)
    bib_path = os.path.join(out_dir, "references.bib")
    if (
        shutil.which("bibtex") is not None
        and os.path.exists(bib_path)
        and os.path.exists(aux_path)
    ):
        cmd_bibtex = ["bibtex", basename]
        subprocess.run(cmd_bibtex, capture_output=True, timeout=60,
                       cwd=out_dir)

    # second + third pass (resolves references and cross-refs)
    subprocess.run(cmd_latex, capture_output=True, timeout=120)
    subprocess.run(cmd_latex, capture_output=True, timeout=120)

    return pdf if os.path.exists(pdf) else None


# ═══════════════════════════════════════════════════════════════
# BibTeX bibliography
# ═══════════════════════════════════════════════════════════════

def create_bibtex():
    bib = r"""@article{AcemogluJohnsonRobinson2002,
  author    = {Acemoglu, Daron and Johnson, Simon and Robinson, James A.},
  title     = {Reversal of Fortune: Geography and Institutions in the Making of the Modern World Income Distribution},
  journal   = {Quarterly Journal of Economics},
  volume    = {117},
  pages     = {1231--1294},
  year      = {2002},
  doi       = {10.1162/003355302320935025}
}

@book{AcemogluRobinson2012,
  author    = {Acemoglu, Daron and Robinson, James A.},
  title     = {Why Nations Fail: The Origins of Power, Prosperity, and Poverty},
  publisher = {Crown},
  address   = {New York},
  year      = {2012}
}

@article{AcemogluRestrepo2020,
  author    = {Acemoglu, Daron and Restrepo, Pascual},
  title     = {Robots and Jobs: Evidence from {US} Labor Markets},
  journal   = {Journal of Political Economy},
  volume    = {128},
  pages     = {2188--2244},
  year      = {2020},
  doi       = {10.1086/705716}
}

@article{CominEasterlyGong2010,
  author    = {Comin, Diego and Easterly, William and Gong, Erin},
  title     = {Was the Wealth of Nations Determined in 1000 {BC}?},
  journal   = {American Economic Journal: Macroeconomics},
  volume    = {2},
  number    = {3},
  pages     = {65--97},
  year      = {2010},
  doi       = {10.1257/mac.2.3.65}
}

@article{CominMestieri2018,
  author    = {Comin, Diego and Mestieri, Mart\'{i}},
  title     = {If Technology Has Arrived Everywhere, Why Has Income Diverged?},
  journal   = {American Economic Journal: Macroeconomics},
  volume    = {10},
  number    = {3},
  pages     = {137--178},
  year      = {2018},
  doi       = {10.1257/mac.20150175}
}

@book{Diamond1997,
  author    = {Diamond, Jared},
  title     = {Guns, Germs, and Steel: The Fates of Human Societies},
  publisher = {W.W. Norton},
  address   = {New York},
  year      = {1997}
}

@article{DiamondBellwood2003,
  author    = {Diamond, Jared and Bellwood, Peter},
  title     = {Farmers and Their Languages: The First Expansions},
  journal   = {Science},
  volume    = {300},
  pages     = {597--603},
  year      = {2003},
  doi       = {10.1126/science.1078208}
}

@book{FindlayORourke2007,
  author    = {Findlay, Ronald and O'Rourke, Kevin H.},
  title     = {Power and Plenty: Trade, War, and the World Economy in the Second Millennium},
  publisher = {Princeton University Press},
  address   = {Princeton},
  year      = {2007}
}

@book{Kennedy1987,
  author    = {Kennedy, Paul},
  title     = {The Rise and Fall of the Great Powers: Economic Change and Military Conflict from 1500 to 2000},
  publisher = {Random House},
  address   = {New York},
  year      = {1987}
}

@book{Mokyr2002,
  author    = {Mokyr, Joel},
  title     = {The Gifts of Athena: Historical Origins of the Knowledge Economy},
  publisher = {Princeton University Press},
  address   = {Princeton},
  year      = {2002}
}

@article{Nunn2008,
  author    = {Nunn, Nathan},
  title     = {The Long-Term Effects of {Africa}'s Slave Trades},
  journal   = {Quarterly Journal of Economics},
  volume    = {123},
  pages     = {139--176},
  year      = {2008},
  doi       = {10.1162/qjec.2008.123.1.139}
}

@book{Pomeranz2000,
  author    = {Pomeranz, Kenneth},
  title     = {The Great Divergence: {China}, {Europe}, and the Making of the Modern World Economy},
  publisher = {Princeton University Press},
  address   = {Princeton},
  year      = {2000}
}

@book{Tainter1988,
  author    = {Tainter, Joseph A.},
  title     = {The Collapse of Complex Societies},
  publisher = {Cambridge University Press},
  address   = {Cambridge},
  year      = {1988}
}
"""
    bib_path = os.path.join(OUT, "references.bib")
    with open(bib_path, "w", encoding="utf-8") as f:
        f.write(bib)
    print("  BibTeX saved to", bib_path)
    return bib_path


# ═══════════════════════════════════════════════════════════════
# Main manuscript (.tex)
# ═══════════════════════════════════════════════════════════════

def create_manuscript_tex(results):
    N = results["N"]
    df = results["df"]
    n_overtaken = len(df[df["outcome"] == "overtaken"])
    n_disrupted = len(df[df["outcome"] == "disrupted"])
    n_survived = len(df[df["outcome"] == "survived"])
    n_stock = len(df[df["dominant"] == "stock"])
    n_flow = len(df[df["dominant"] == "flow"])

    # Scenario data
    s_base_c = results["scenarios"]["as_conquered__baseline"]
    s_strong_c = results["scenarios"]["as_conquered__strong"]
    s_all_c = results["scenarios"]["as_conquered__all"]
    cm_base = s_base_c["cm"]
    cm_all_c = s_all_c["cm"]
    boot_c = results["bootstrap"].get("as_conquered__all", {})
    candidates = STRONG_CANDIDATES + MODERATE_CANDIDATES
    candidate_count = len(candidates)
    candidate_rate = apply_disrupted_assignment(df, "as_conquered")[
        lambda frame: frame["entity"].isin(candidates)
    ]["outcome_binary"].mean()
    closure_all_c = s_all_c["closure"]
    closure_all_s = results["scenarios"]["as_survived__all"]["closure"]

    # Table 4 computation
    df_all_c = apply_disrupted_assignment(
        apply_technical_network_exclusion(df, STRONG_CANDIDATES + MODERATE_CANDIDATES),
        "as_conquered"
    )
    has_closure = df_all_c["closure_type"].isin(
        ["maritime_ban", "technical_network_exclusion", "sakoku"])
    cells_64 = {}
    for dom in ["stock", "flow"]:
        for cl_label, cl_val in [("closed", True), ("open", False)]:
            sub = df_all_c[(df_all_c["dominant"] == dom) & (has_closure == cl_val)]
            n = len(sub)
            conquered = int(sub["outcome_binary"].sum())
            survived = n - conquered
            rate = sub["outcome_binary"].mean() if n > 0 else 0
            cells_64[(dom, cl_label)] = {
                "n": n, "c": conquered, "s": survived, "rate": rate}

    sc = cells_64[("stock", "closed")]
    so = cells_64[("stock", "open")]
    fc = cells_64[("flow", "closed")]
    fo = cells_64[("flow", "open")]

    def fisher_or_p(a, b):
        table = np.array([[a["c"], a["s"]], [b["c"], b["s"]]])
        odds_r, p_val = stats.fisher_exact(table, alternative="greater")
        return odds_r, p_val

    or_sc_fo, p_sc_fo = fisher_or_p(sc, fo)
    or_sc_so, p_sc_so = fisher_or_p(sc, so)
    or_fc_fo, p_fc_fo = fisher_or_p(fc, fo)
    or_fc_fo_str = r"\infty" if np.isinf(or_fc_fo) else f"{or_fc_fo:.2f}"

    # Table 1 data
    table1_rows = []
    rationale_en = {
        "\u6f22\u671d\uff08\u524d\u6f22\u301c\u5f8c\u6f22\uff09": "Excluded from Mediterranean network; Silk Road provided limited overland contact only.",
        "\u30de\u30ea\u5e1d\u56fd": "Excluded from Atlantic/Mediterranean networks until Portuguese contact (15th c.). Trans-Saharan caravan only.",
        "\u30af\u30e1\u30fc\u30eb\u5e1d\u56fd\uff08\u30a2\u30f3\u30b3\u30fc\u30eb\uff09": "Inland polity; excluded from dominant exchange networks unlike neighbouring Srivijaya.",
        "\u30ad\u30a8\u30d5\u5927\u516c\u56fd": "Dnieper river trade (Varangian route) only; excluded from dominant exchange networks.",
        "\u30c6\u30a3\u30e0\u30fc\u30eb\u671d": "Landlocked; Silk Road overland only. Excluded from dominant Mediterranean and Indian Ocean networks.",
        "\u30b5\u30b5\u30f3\u671d\u30da\u30eb\u30b7\u30a2": "Limited Persian Gulf trade; excluded from established Indian Ocean and Mediterranean networks.",
        "\u30d3\u30eb\u30de\uff08\u30b3\u30f3\u30d0\u30a6\u30f3\u671d\uff09": "Coastal access existed but excluded from regular international exchange networks until British arrival.",
    }
    for entity in candidates:
        en_name = ENGLISH_NAME.get(entity, entity)
        row_data = df[df["entity"] == entity].iloc[0]
        tier = "Strong" if entity in STRONG_CANDIDATES else "Moderate"
        rat = rationale_en.get(entity, "")
        table1_rows.append((en_name, row_data["period"], tier, rat))

    # Table 2 data
    table2_rows = []
    for d_mode, d_label in [("as_conquered", "Overtaken"),
                            ("as_survived", "Survived")]:
        for c_key, c_label in [
            ("baseline", "Baseline"),
            ("strong", f"+{len(STRONG_CANDIDATES)} Strong"),
            ("all", f"+{candidate_count} All"),
        ]:
            key = f"{d_mode}__{c_key}"
            s = results["scenarios"][key]
            sig = "*" if s["fisher_ban_p"] < 0.05 else ""
            table2_rows.append((
                d_label, c_label, s["ban_n"],
                _pct(s['ban_rate']), _pct(s['no_ban_rate']),
                f"{s['rr']:.3f}", f"{s['fisher_ban_p']:.4f}", sig
            ))

    # Table 3 data
    lr_all_c = results["scenarios"]["as_conquered__all"]["logistic"]
    lr_all_with_ban = lr_all_c.get("with_ban", {})
    lr_all_converged = bool(lr_all_with_ban.get("converged"))
    lr_all_coefs = lr_all_with_ban.get("coefs", {}) if lr_all_converged else {}
    table3_rows = []
    if lr_all_converged:
        var_labels = {
            "dominant_binary": "Stock-dominant",
            "geo_barrier": "Geographic barrier",
            "external_threat": "External threat",
            "tech_position": "Technological position",
            "institutional_quality": "Institutional quality",
            "era_code": "Era (time)",
            "has_external_patron": "External patron",
            "has_maritime_ban": "Network closure dummy",
        }
        coefs = lr_all_coefs
        for var, label in var_labels.items():
            v = coefs[var]
            sig = "*" if v["p"] < 0.05 else (r"\dag" if v["p"] < 0.10 else "")
            ci_lo_str = (f"{v['ci_lo']:.3f}" if v["ci_lo"] < 1e6
                         else r"$>10^{6}$")
            ci_hi_str = (f"{v['ci_hi']:.3f}" if v["ci_hi"] < 1e6
                         else r"$>10^{6}$")
            table3_rows.append((
                label, f"{v['OR']:.3f}",
                f"[{ci_lo_str}, {ci_hi_str}]",
                f"{v['p']:.4f}", sig
            ))

    # ── Build LaTeX source ──
    tex = []

    def W(line=""):
        tex.append(line)

    # Preamble
    W(r"% Reproducible manuscript source — target: Explorations in Economic History")
    W(r"% Generated by create_manuscript_latex.py")
    W(r"\documentclass[pdflatex,sn-basic]{sn-jnl}")
    W()
    W(r"\usepackage{graphicx}%")
    W(r"\usepackage{multirow}%")
    W(r"\usepackage{amsmath,amssymb,amsfonts}%")
    W(r"\usepackage{amsthm}%")
    W(r"\usepackage{mathrsfs}%")
    W(r"\usepackage[title]{appendix}%")
    W(r"\usepackage{xcolor}%")
    W(r"\usepackage{textcomp}%")
    W(r"\usepackage{manyfoot}%")
    W(r"\usepackage{booktabs}%")
    W(r"\usepackage{algorithm}%")
    W(r"\usepackage{algorithmicx}%")
    W(r"\usepackage{algpseudocode}%")
    W(r"\usepackage{listings}%")
    W(r"\usepackage{hyperref}")
    W(r"\usepackage[T1]{fontenc}")
    W()
    W(r"\theoremstyle{thmstyleone}%")
    W(r"\newtheorem{theorem}{Theorem}%")
    W(r"\newtheorem{proposition}[theorem]{Proposition}%")
    W(r"\theoremstyle{thmstyletwo}%")
    W(r"\newtheorem{example}{Example}%")
    W(r"\newtheorem{remark}{Remark}%")
    W(r"\theoremstyle{thmstylethree}%")
    W(r"\newtheorem{definition}{Definition}%")
    W()
    W(r"\raggedbottom")
    W()
    W(r"\begin{document}")
    W()

    # Title
    W(r"\title[Network Exclusion and State Collapse]{"
      r"Network Exclusion and State Collapse: "
      r"From Maritime Isolation to Technological Access Denial "
      r"in the Long Run of History}")
    W()

    # Author
    W(r"\author*[1]{\fnm{Author} \sur{Name}}\email{author@example.com}")
    W()
    W(r"\affil*[1]{\orgdiv{Department}, \orgname{University}, "
      r"\orgaddress{\street{Street}, \city{City}, "
      r"\postcode{00000}, \state{State}, \country{Country}}}")
    W()

    # Abstract
    W(r"\abstract{")
    W("Why do some states collapse while others endure? This exploratory study proposes that structural "
      "exclusion from the dominant technological network of an era---not merely deliberate "
      "trade closure---is a candidate correlate of state vulnerability, with technology-flow "
      "disruption proposed as one possible explanation for divergence between connected and "
      f"excluded polities. Using a comparative dataset of {N} historical polities spanning "
      "antiquity to the present, assembled as an AI-assisted exploratory dataset rather than a "
      "public-data measurement dataset, we distinguish between policy-driven isolation (e.g., Ming "
      r"\emph{haijin}, Tokugawa \emph{sakoku}) and what we term `technical network exclusion': "
      "involuntary disconnection from prevailing exchange networks due to geographic or "
      "technological constraints. Policy-based closure can reduce without eliminating technology "
      r"transfer (e.g., \emph{rangaku} via Dejima under \emph{sakoku}), whereas technical "
      "exclusion is coded as more severe involuntary disconnection. "
      f"Across a post hoc reclassification of {candidate_count} technically excluded polities, "
      f"the one-sided Fisher exact p-value for closure and conquest changes from "
      f"{s_base_c['fisher_ban_p']:.3f} to {s_all_c['fisher_ban_p']:.3f}; all {candidate_count} were coded as eventually conquered. "
      "Within these exploratory codings, multivariate logistic regression shows the largest "
      "conditional associations for external threat and institutional quality, while the stock--flow odds ratio "
      f"(OR $= {cm_base['OR']:.3f}$) remains stable across all scenarios. We present the "
      "underlying mechanism---technology flow disruption leading to an accumulating "
      "civilization-level gap---as a hypothesis beyond maritime isolation. As the dominant network "
      "shifts from sea lanes to semiconductors, artificial intelligence, and advanced robotics, "
      "states structurally excluded from these technological platforms may face analogous "
      "vulnerabilities.")
    W(r"}")
    W()

    # Keywords & JEL
    W(r"\keywords{network exclusion, economic history, technology flow disruption, "
      r"state collapse, technological access, sensitivity analysis}")
    W()

    W(r"\maketitle")
    W()

    # ════════════════════════════════════════
    # 1. INTRODUCTION
    # ════════════════════════════════════════
    W(r"\section{Introduction}\label{sec:intro}")
    W()
    W(r"Every era has a dominant network---a prevailing infrastructure of exchange through "
      r"which states access trade, technology, and strategic information. In antiquity, it "
      r"was the Mediterranean sea lanes and the Silk Road caravan routes. In the age of sail, "
      r"it was transoceanic maritime commerce. In the industrial age, it was railroad-linked "
      r"factory systems and colonial supply chains. Today, it is the digital and semiconductor "
      r"ecosystem. A recurring pattern in global history is that states excluded from the "
      r"dominant network of their era---whether by choice or by circumstance---face elevated "
      r"risks of decline and conquest \citep{Kennedy1987, FindlayORourke2007}.")
    W()
    W(r"The existing literature offers two broad explanations for why states fail. One "
      r"emphasizes internal dynamics: \citet{Tainter1988} argued that complex societies "
      r"collapse when the marginal returns to increasing complexity decline, and "
      r"\citet{AcemogluRobinson2012} showed that extractive institutions---those that "
      r"concentrate power and discourage innovation---undermine long-run prosperity. The "
      r"other emphasizes external connectivity: trade openness, technology diffusion, and "
      r"the consequences of isolation \citep{FindlayORourke2007, Mokyr2002}. Our "
      r"contribution lies at the intersection. We examine whether disconnection from the dominant "
      r"exchange network is associated with institutional quality and technological capacity---"
      r"the factors that the internal-dynamics literature identifies as proximate explanations "
      r"of collapse.")
    W()
    W(r"The literature on trade and isolation has overwhelmingly focused on deliberate "
      r"closure: the maritime prohibitions (\emph{haijin}) of Ming China, the \emph{sakoku} "
      r"decree of Tokugawa Japan, the autarkic blocs of the Cold War. Deliberate closure is "
      r"analytically convenient because it represents a policy choice with an identifiable "
      r"agent. Yet this focus on intentional closure overlooks a logically prior question: "
      r"what happens to polities that never had the option of connecting to the dominant "
      r"network in the first place? The Khmer Empire at Angkor, the Kievan Rus' principality, "
      r"or the Timurid dynasty were not isolated because their rulers chose closure; they were "
      r"isolated because the dominant exchange networks of their era did not reach them. If "
      r"these polities exhibit the same elevated conquest risk as deliberately closed ones, "
      r"then the pattern would be consistent with disconnection, rather than the policy "
      r"decision alone, as a candidate explanation.")
    W()
    W(r"We hypothesize that technology flow is a relevant channel. Maritime trade was never "
      r"merely an exchange of goods; it was the primary vehicle through which military "
      r"techniques, navigation methods, metallurgy, and institutional innovations diffused "
      r"across polities \citep{Pomeranz2000, Mokyr2002}. Deliberate closure, such as "
      r"\emph{sakoku}, restricted but did not eliminate this flow---Tokugawa Japan maintained "
      r"a narrow conduit of Western scientific knowledge (\emph{rangaku}) through the Dutch "
      r"trading post at Dejima. Technical exclusion, by contrast, is hypothesized to restrict "
      r"a broader set of channels. A possible result is a cumulative technology gap: over "
      r"generations, excluded polities may fall behind the technological frontier, and when contact with a more advanced "
      r"civilization eventually occurred---often through military confrontation---the gap "
      r"may have increased vulnerability. This is, in essence, a quantitative restatement of a long-recognized "
      r"pattern: when civilizations at markedly different technological levels collide, the "
      r"less advanced one may face elevated vulnerability \citep{Diamond1997}.")
    W()
    W(r"This paper makes three contributions. First, we construct a comparative historical "
      f"dataset of {N} polities spanning six eras (ancient, medieval, early modern, modern, "
      r"twentieth century, and contemporary) and classify each along two dimensions: its "
      r"predominant resource base---stock-oriented (accumulated assets such as human capital, "
      r"institutions, and natural resources) versus flow-oriented (trade, military projection, "
      r"and diplomatic engagement)---and its degree of closure from international networks. "
      r"Second, we introduce the concept of `technical network exclusion,' defined as the "
      r"involuntary disconnection of a polity from the dominant exchange network of its era "
      r"due to geographic or technological constraints. In the maritime age, this took the "
      r"form of geographic exclusion from sea routes, but the underlying mechanism generalizes "
      f"across eras. Third, we conduct a post hoc sensitivity analysis in which {candidate_count} "
      r"technically excluded polities are reclassified from `no closure' to `technical "
      r"network exclusion,' testing whether the closure--conquest association is an artifact "
      r"of how isolation is defined.")
    W()
    W(r"The reclassification changes the one-sided Fisher exact p-value from "
      f"{s_base_c['fisher_ban_p']:.3f} at baseline to {s_all_c['fisher_ban_p']:.3f}, while the core "
      f"stock--flow odds ratio remains unchanged at {cm_base['OR']:.3f}. All {candidate_count} technically "
      r"excluded polities were coded as eventually conquered. This exploratory result is consistent with the hypothesis that what matters "
      r"for state survival is not whether closure was chosen but whether the polity was "
      r"connected to the era's critical exchange platform.")
    W()
    W(r"The forward-looking implication follows directly. If the mechanism is technology flow "
      r"disruption leading to a cumulative gap, then the pattern need not be confined to the "
      r"maritime age. In a world where geography no longer blocks physical trade, the `dominant "
      r"network' has shifted from sea lanes to the semiconductor supply chain, artificial "
      r"intelligence infrastructure, and advanced robotics. States structurally excluded from "
      r"these technological platforms---whether by export controls, infrastructure deficits, "
      r"or institutional barriers---may face the same accumulating disadvantage that doomed "
      r"the technically excluded polities of the premodern era. We develop this argument in "
      r"the discussion.")
    W()
    W(r"The remainder of the paper is organized as follows. Section~\ref{sec:data} describes "
      r"the dataset and classification framework. Section~\ref{sec:methods} presents the "
      r"analytical methods. Section~\ref{sec:results} reports the baseline results. "
      r"Section~\ref{sec:sensitivity} details the sensitivity analysis. "
      r"Section~\ref{sec:discussion} discusses implications, including the extension to "
      r"technological access exclusion, and Section~\ref{sec:conclusion} concludes.")
    W()

    # ════════════════════════════════════════
    # 2. DATA AND CLASSIFICATION
    # ════════════════════════════════════════
    W(r"\section{Data and Classification}\label{sec:data}")
    W()
    W(r"\subsection{Dataset construction}\label{sec:data-construction}")
    W()
    W(f"The dataset comprises {N} manually constructed polity--period cases assembled with AI "
      r"assistance. The author supplied the conceptual research question but no record-level "
      r"values; the cases and original values were assigned during the AI-assisted assembly on "
      r"13 May 2026 rather than extracted from a public dataset. The variables predominant resource base, stock "
      r"index (0--1), trade openness (0--1), geographic barrier, external threat, relative "
      r"population, technological position, and institutional quality are therefore exploratory "
      r"AI-assisted judgments rather than observed measurements or validated expert ratings. "
      r"Closure type, historical outcome, and external-patron status are historically anchored "
      r"classifications. The complete editable dataset is provided in Supplementary Table~S1 and the public "
      r"code permits readers to replace any coding and rerun every analysis.")
    W()
    W(f"Of the {N} polities, {n_stock} are classified as stock-oriented and {n_flow} as "
      f"flow-oriented. Historical outcomes fall into three categories: overtaken "
      f"({n_overtaken} polities)---conquest, colonization, or annexation by an external power; "
      f"disrupted ({n_disrupted})---regime collapse followed by reconstitution under a "
      r"successor state (e.g., Tokugawa Japan giving way to Meiji Japan); and survived "
      f"({n_survived})---continuity of both regime and statehood. The `disrupted' category is "
      r"analytically ambiguous, as these polities neither clearly fell to foreign conquest nor "
      r"clearly persisted; we address this through a dual-assignment sensitivity design "
      r"(Section~\ref{sec:methods-binarization}).")
    W()

    W(r"\subsection{Closure typology}\label{sec:closure-typology}")
    W()
    W(r"We classify each polity's degree of closure into five categories, ordered by the "
      r"nature and intent of isolation: (1)~maritime ban---deliberate restriction of maritime "
      r"trade by state policy (e.g., Ming \emph{haijin}, Qing Canton system); "
      r"(2)~\emph{sakoku}---near-total isolation enforced by national decree (Tokugawa Japan, "
      r"Joseon Korea); (3)~bloc---closure within a geopolitical or economic bloc (e.g., "
      r"COMECON, imperial preference systems); (4)~technical network exclusion---involuntary "
      r"isolation from the dominant exchange network of the era due to geographic or "
      r"technological constraints (not limited to maritime routes); and (5)~none---no "
      r"significant closure from prevailing exchange networks.")
    W()
    W(r"Categories 1 through 3 represent deliberate closure: a policy choice by identifiable "
      r"agents. Category 4 represents structural exclusion: isolation imposed by geography "
      r"and the limits of contemporary transport technology. This distinction is central to "
      r"our argument, because a similar outcome pattern under structural and deliberate "
      r"exclusion would be consistent with disconnection itself, rather than the decision "
      r"alone, as the relevant hypothesis.")
    W()

    W(r"\subsection{Technical network exclusion: definition and candidates}"
      r"\label{sec:tech-exclusion}")
    W()
    W(r"We define technical network exclusion as the condition in which a polity was "
      r"structurally disconnected from the dominant exchange network of its era---whether "
      r"maritime, overland, or otherwise---due to geographic or technological constraints "
      r"rather than policy choice. In the maritime age, this typically meant the absence of "
      r"regular sea routes; for inland polities along the Silk Road, it meant that while some "
      r"goods traveled overland, the volume and variety of technology transfer fell far short "
      r"of what maritime-connected polities received. The key distinction from policy-based "
      r"closure is the absence of agency: these polities did not choose isolation. The "
      r"transport and communication infrastructure of their era had not yet extended effective "
      r"connectivity to their region.")
    W()
    W(f"We identify {candidate_count} reclassification candidates in two tiers.")
    W()
    W(r"The candidate set was developed after the initial dataset analysis and was neither "
      r"prespecified nor coded with outcomes blinded. It is therefore evaluated only as a "
      r"post hoc sensitivity analysis (Table~\ref{tab:reclass}).")
    W()

    # Table 1
    W(r"\begin{table}[htbp]")
    W(r"\caption{Technical network exclusion reclassification candidates. "
      r"`Strong' candidates were structurally excluded from the dominant exchange network of "
      r"their era; `Moderate' candidates had limited or uncertain connectivity.}")
    W(r"\label{tab:reclass}")
    W(r"\begin{tabular*}{\textwidth}{@{\extracolsep\fill}lllp{7cm}}")
    W(r"\toprule")
    W(r"Polity & Period & Tier & Rationale \\")
    W(r"\midrule")
    for en_name, period, tier, rat in table1_rows:
        W(f"{_esc(en_name)} & {_esc(period)} & {tier} & {_esc(rat)} \\\\")
    W(r"\botrule")
    W(r"\end{tabular*}")
    W(r"\end{table}")
    W()

    # ════════════════════════════════════════
    # 3. METHODS
    # ════════════════════════════════════════
    W(r"\section{Methods}\label{sec:methods}")
    W()
    W(r"\subsection{Outcome binarization and sensitivity design}"
      r"\label{sec:methods-binarization}")
    W()
    W(r"The three-category outcome (overtaken, disrupted, survived) poses a classification "
      f"problem. The {n_disrupted} `disrupted' polities experienced regime collapse but were not clearly "
      r"conquered by an external power; they could reasonably be grouped with either outcome. "
      r"Rather than making a single arbitrary assignment, we adopt a dual-assignment design: "
      f"in the `disrupted $\\to$ overtaken' scenario, all {n_disrupted} are coded as conquered "
      f"(yielding {s_base_c['cm']['TP'] + s_base_c['cm']['FN']} conquered, "
      f"{s_base_c['cm']['FP'] + s_base_c['cm']['TN']} survived); in the "
      f"`disrupted $\\to$ survived' scenario, they are coded as having survived (yielding "
      f"{results['scenarios']['as_survived__baseline']['cm']['TP'] + results['scenarios']['as_survived__baseline']['cm']['FN']} conquered, "
      f"{results['scenarios']['as_survived__baseline']['cm']['FP'] + results['scenarios']['as_survived__baseline']['cm']['TN']} survived). "
      f"Crossed with three closure reclassification levels (baseline, "
      f"+{len(STRONG_CANDIDATES)} strong candidates, +{candidate_count} all candidates), this "
      r"produces $3 \times 2 = 6$ scenarios. All results are reported across all six to "
      r"show sensitivity to these coding choices.")
    W()

    W(r"\subsection{Stock--flow association}\label{sec:methods-stockflow}")
    W()
    W(r"We construct $2 \times 2$ tables crossing the predominant resource base (stock vs.\ "
      r"flow) against the binarized outcome (overtaken vs.\ survived) and compute the odds "
      r"ratio (OR), phi coefficient ($\varphi$), one-sided Fisher's exact test, and "
      r"chi-squared test with Yates correction. Effect sizes are interpreted using Cohen's "
      r"benchmarks for $\varphi$.")
    W()

    W(r"\subsection{Closure--conquest association}\label{sec:methods-closure}")
    W()
    W(r"For each of the six scenarios, we construct a $2 \times 2$ table crossing closure "
      r"status (network closure vs.\ open) against the binarized outcome. The `network "
      r"closure' group includes polities coded as maritime ban, \emph{sakoku}, or technical "
      r"network exclusion. We compute one-sided Fisher's exact tests evaluating whether "
      r"closure is associated with elevated conquest rates, and report relative risks "
      r"alongside $p$-values.")
    W()

    W(r"\subsection{Multivariate logistic regression}\label{sec:methods-logistic}")
    W()
    W(r"To describe the closure--conquest association after covariate adjustment, we fit "
      r"logistic regression models with the binarized outcome as the "
      r"dependent variable and the following covariates: stock-dominant indicator, geographic "
      r"barrier, external threat level, technological position, institutional quality, era "
      r"(coded ordinally), external patron indicator, and a network closure indicator. We "
      r"report exponentiated coefficients (odds ratios) with 95\% confidence intervals.")
    W()

    W(r"\subsection{Bootstrap uncertainty assessment}\label{sec:methods-bootstrap}")
    W()
    W(r"We assess uncertainty in the stock--flow OR using a nonparametric bootstrap (5{,}000 resamples, "
      r"percentile method, seed = 42). This provides a distribution-free confidence interval "
      r"that does not depend on asymptotic normality---a relevant consideration given the "
      r"modest sample size.")
    W()

    # ════════════════════════════════════════
    # 4. RESULTS
    # ════════════════════════════════════════
    W(r"\section{Results}\label{sec:results}")
    W()
    W(r"\subsection{Baseline stock--flow association}\label{sec:results-baseline}")
    W()
    W(f"Under the disrupted $\\to$ overtaken assignment, the stock--flow $2 \\times 2$ table "
      f"yields OR $= {cm_base['OR']:.3f}$, $\\varphi = {cm_base['phi']:.3f}$, Fisher's exact "
      f"$p = {cm_base['p_fisher']:.4f}$ (one-sided). Stock-oriented polities have a conquest "
      f"rate of {_pct(cm_base['stock_conquest_rate'])}, compared with "
      f"{_pct(cm_base['flow_conquest_rate'])} for flow-oriented polities---a small-to-medium "
      f"effect by Cohen's benchmarks. Under the disrupted $\\to$ survived assignment, the OR "
      f"shifts to "
      f"{results['scenarios']['as_survived__baseline']['cm']['OR']:.3f}, illustrating the "
      "sensitivity of the stock--flow association to how the ambiguous `disrupted' category "
      "is handled. This dual sensitivity---to both closure definition and outcome "
      "binarization---motivates the full six-scenario analysis below.")
    W()

    W(r"\subsection{Network closure and conquest}\label{sec:results-closure}")
    W()
    W(f"Table~\\ref{{tab:scenarios}} reports the closure--conquest association across all six "
      f"scenarios. At baseline under the disrupted $\\to$ overtaken assignment, polities with "
      f"some form of network closure have a conquest rate of "
      f"{_pct(s_base_c['ban_rate'])}, compared with {_pct(s_base_c['no_ban_rate'])} for open "
      f"polities (Fisher $p = {s_base_c['fisher_ban_p']:.4f}$, not significant). "
      f"Reclassifying {len(STRONG_CANDIDATES)} strong candidates as technically excluded raises the "
      f"closure-group conquest rate to {_pct(s_strong_c['ban_rate'])} "
      f"(Fisher $p = {s_strong_c['fisher_ban_p']:.4f}$). "
      f"Including all {candidate_count} candidates yields a conquest rate of "
      f"{_pct(s_all_c['ban_rate'])}, Fisher $p = {s_all_c['fisher_ban_p']:.4f}$. "
      "The progressive change is reported as a sensitivity pattern under the alternative "
      "classification, not as independent validation that the candidates belong in the "
      "closure group.")
    W()

    # Table 2
    W(r"\begin{table}[htbp]")
    W(r"\caption{Network closure and conquest across six scenarios. $^{*}$~$p < 0.05$.}")
    W(r"\label{tab:scenarios}")
    W(r"\begin{tabular*}{\textwidth}{@{\extracolsep\fill}llcccccl}")
    W(r"\toprule")
    W(r"Disrupted As & Reclassification & Closure $n$ & Closure Rate & Open Rate & RR & Fisher $p$ & Sig. \\")
    W(r"\midrule")
    for row in table2_rows:
        sig_str = "$^{*}$" if row[7] == "*" else ""
        W(f"{row[0]} & {row[1]} & {row[2]} & {row[3]} & {row[4]} & {row[5]} & {row[6]} & {sig_str} \\\\")
    W(r"\botrule")
    W(r"\end{tabular*}")
    W(r"\end{table}")
    W()

    # Figures 1 and 2
    W(r"Figure~\ref{fig:conquest-rates} compares closure and open-group conquest rates "
      r"across the six scenarios.")
    W()
    W(r"\begin{figure}[htbp]")
    W(r"\centering")
    W(r"\includegraphics[width=\textwidth]{figures/Fig1.png}")
    W(r"\caption{Conquest rates comparing network closure vs.\ open polities across three "
      r"reclassification scenarios under both disrupted assignments.}")
    W(r"\label{fig:conquest-rates}")
    W(r"\end{figure}")
    W()
    W(r"Figure~\ref{fig:fisher-pvalues} shows how the one-sided Fisher $p$-value changes "
      r"under the same reclassification sequence.")
    W()
    W(r"\begin{figure}[htbp]")
    W(r"\centering")
    W(r"\includegraphics[width=0.85\textwidth]{figures/Fig2.png}")
    W(r"\caption{Fisher's exact test $p$-values for the network closure $\to$ conquest "
      r"association as polities are progressively reclassified.}")
    W(r"\label{fig:fisher-pvalues}")
    W(r"\end{figure}")
    W()

    # ════════════════════════════════════════
    # 5. SENSITIVITY ANALYSIS
    # ════════════════════════════════════════
    W(r"\section{Sensitivity Analysis: Technical Network Exclusion}\label{sec:sensitivity}")
    W()
    W(r"\subsection{Closure-type disaggregation}"
      r"\label{sec:sensitivity-dose}")
    W()
    W(f"Under the {candidate_count}-country reclassification, technically excluded "
      r"polities---those classified as severely disconnected from the dominant exchange networks of their "
      f"era---have a {_pct(candidate_rate)} conquest rate. Policy-based maritime bans, which restricted but "
      r"did not entirely eliminate external contact, show lower rates "
      f"({_pct(closure_all_c['maritime_ban']['rate'])} under disrupted "
      f"$\\to$ overtaken; {_pct(closure_all_s['maritime_ban']['rate'])} under disrupted $\\to$ survived). "
      f"\\emph{{Sakoku}} polities show {_pct(closure_all_c['sakoku']['rate'])} and "
      f"{_pct(closure_all_s['sakoku']['rate'])} rates under the two assignments, reflecting the borderline case of "
      r"Tokugawa Japan, which maintained a narrow technological conduit (\emph{rangaku}) "
      r"through Dejima. Bloc-type closures show the lowest conquest rates among closure "
      r"categories, consistent with the interpretation that bloc membership preserves some "
      r"technology transfer through alliance-internal channels.")
    W()
    W(r"Figure~\ref{fig:closure-types} shows that the category rates are not strictly monotonic: technical exclusion and \emph{sakoku} "
      r"have the highest rates, maritime bans are intermediate, and bloc closure is lower than "
      r"the open category. The disaggregation therefore motivates the technology-flow "
      r"hypothesis but does not independently establish a dose--response relationship.")
    W()

    # Figure 3
    W(r"\begin{figure}[htbp]")
    W(r"\centering")
    W(r"\includegraphics[width=\textwidth]{figures/Fig3.png}")
    W(f"\\caption{{Conquest rates by closure type under the {candidate_count}-country "
      f"reclassification scenario.}}")
    W(r"\label{fig:closure-types}")
    W(r"\end{figure}")
    W()

    W(r"\subsection{Stability of the stock--flow odds ratio}"
      r"\label{sec:sensitivity-or}")
    W()
    W(f"The stock--flow OR $= {cm_all_c['OR']:.3f}$ is identical across all three "
      r"reclassification scenarios. This invariance is expected: the reclassification changes "
      r"the closure-type label but does not alter the stock/flow or outcome coding. Bootstrap "
      f"resampling (5{{,}}000 draws) yields a median OR of "
      f"${boot_c.get('median', 0):.3f}$ (95\\% CI "
      f"[{boot_c.get('ci_lo', 0):.3f}, {boot_c.get('ci_hi', 0):.3f}]), "
      r"The median is close to the point estimate, but the interval is wide and includes the null.")
    W()

    W(r"\subsection{Multivariate regression stability}\label{sec:sensitivity-regression}")
    W()
    if lr_all_converged:
        W(r"Figure~\ref{fig:forest-plot} presents the multivariate logistic regression results "
          f"under the {candidate_count}-country reclassification with disrupted $\\to$ overtaken. "
          f"In this specification, external threat ($p = {lr_all_coefs['external_threat']['p']:.4f}$), "
          f"institutional quality ($p = {lr_all_coefs['institutional_quality']['p']:.4f}$), and era "
          f"($p = {lr_all_coefs['era_code']['p']:.4f}$) have the smallest p-values. The network closure "
          f"indicator is not independently significant ($p = {lr_all_coefs['has_maritime_ban']['p']:.4f}$) "
          r"after controlling for these covariates. "
          r"This pattern is consistent with, but does not identify, an indirect pathway involving "
          r"technological stagnation, institutional change, and heightened external vulnerability---"
          r"covariates that the multivariate model already captures.")
    else:
        W(r"Figure~\ref{fig:forest-plot} records that the multivariate logistic regression "
          f"did not converge under the {candidate_count}-country reclassification with disrupted "
          r"$\to$ overtaken. Coefficient estimates, confidence intervals, and conditional "
          r"associations are therefore not reported or interpreted for this specification.")
    W()

    # Figure 4
    W(r"\begin{figure}[htbp]")
    W(r"\centering")
    W(r"\includegraphics[width=0.9\textwidth]{figures/Fig4.png}")
    if lr_all_converged:
        W(f"\\caption{{Forest plot of multivariate logistic regression odds ratios "
          f"({candidate_count}-country reclassification, disrupted $\\to$ overtaken).}}")
    else:
        W(f"\\caption{{Multivariate logistic regression output "
          f"({candidate_count}-country reclassification, disrupted $\\to$ overtaken); "
          r"the model did not converge.}")
    W(r"\label{fig:forest-plot}")
    W(r"\end{figure}")
    W()

    # Table 3
    if table3_rows:
        W(r"Table~\ref{tab:regression} reports the corresponding coefficients, confidence "
          r"intervals, and $p$-values.")
        W()
        W(r"\begin{table}[htbp]")
        W(f"\\caption{{Multivariate logistic regression results ({candidate_count}-country "
          r"reclassification, disrupted $\to$ overtaken). $^{*}$~$p < 0.05$, "
          r"$^{\dag}$~$p < 0.10$.}")
        W(r"\label{tab:regression}")
        W(r"\begin{tabular*}{\textwidth}{@{\extracolsep\fill}lcccc}")
        W(r"\toprule")
        W(r"Variable & OR & 95\% CI & $p$-value & Sig. \\")
        W(r"\midrule")
        for row in table3_rows:
            W(f"{row[0]} & {row[1]} & {row[2]} & {row[3]} & {row[4]} \\\\")
        W(r"\botrule")
        W(r"\end{tabular*}")
        W(r"\end{table}")
        W()

    # ════════════════════════════════════════
    # 6. DISCUSSION
    # ════════════════════════════════════════
    W(r"\section{Discussion}\label{sec:discussion}")
    W()
    W(r"\subsection{The mechanism: technology flow disruption and cumulative divergence}"
      r"\label{sec:disc-mechanism}")
    W()
    W(r"In the post hoc sensitivity analysis, the closure--conquest association changes "
      r"when technically excluded polities are grouped with deliberately closed ones. "
      r"This classification sensitivity suggests a pattern relevant to the proposed mechanism. If closure harmed "
      r"states solely through lost trade revenue or reduced diplomatic leverage, then only "
      r"deliberate closure---which blocks trade but not necessarily knowledge---should matter. "
      r"Treating technical exclusion as a more severe disconnection category strengthens "
      r"the association relative to the policy-only coding, which is consistent with "
      r"technology flow as a candidate channel.")
    W()
    W(r"The closure-type pattern in Figure~\ref{fig:closure-types} provides a descriptive "
      f"comparison. Technical exclusion (classified as severe disconnection) is associated with a {_pct(candidate_rate)} "
      r"conquest rate. Policy-based maritime bans, which restrict but do not eliminate "
      f"technology flow, show a {_pct(closure_all_c['maritime_ban']['rate'])} rate under the main assignment. The case of Tokugawa Japan is "
      r"particularly instructive: despite the comprehensive closure of \emph{sakoku}, the "
      r"Tokugawa regime deliberately maintained a narrow conduit for Western scientific and "
      r"technical knowledge (\emph{rangaku}) through the Dutch trading post at Dejima. This "
      r"selective preservation of a technology transfer channel---even within an otherwise "
      r"closed system---is consistent with its avoidance of conquest. Japan was disrupted by "
      r"the forced opening of 1853--54 but was not conquered; it reconstituted itself as the "
      r"Meiji state and rapidly closed the technology gap. Bloc closures, which preserve "
      r"substantial within-bloc technology sharing, show the lowest rate among closure "
      r"categories. Because the category rates are not strictly monotonic, this comparison is "
      r"hypothesis-generating rather than evidence of a dose--response relationship.")
    W()
    if lr_all_converged:
        W(r"The multivariate results provide a descriptive comparison. External threat and institutional "
          r"quality have the largest conditional associations with conquest, and the network closure indicator "
          r"loses significance after their inclusion (Table~\ref{tab:regression}, "
          r"Fig.~\ref{fig:forest-plot}). This is compatible with a technology-gap hypothesis, "
          r"but does not establish one. One possible sequence is that technological stagnation "
          r"weakens institutional adaptive capacity and leaves a polity less able to respond to "
          r"external threats. This proposed ordering is "
          r"consistent with \citeauthor{AcemogluRobinson2012}'s (\citeyear{AcemogluRobinson2012}) "
          r"emphasis on institutions as a proximate determinant of national success. Network "
          r"access is treated here as a possible antecedent for future testing, not as an "
          r"identified upstream cause. The candidate mediating variables (external threat, "
          r"institutional quality) absorb the conditional association of the closure variable, "
          r"but the cross-sectional exploratory design cannot establish direction, mediation, "
          r"or causation.")
    else:
        W(r"The multivariate specification did not converge, so it cannot support conditional "
          r"comparisons or a mediation interpretation. The descriptive and sensitivity results "
          r"remain exploratory and do not establish direction or causation.")
    W()

    W(r"\subsection{First contact and a proposed divergence mechanism}"
      r"\label{sec:disc-firstcontact}")
    W()
    W(r"The exploratory results can be read as a quantitative formulation of a long-recognized "
      r"historical pattern: when civilizations that have developed in isolation encounter a "
      r"technologically superior civilization, asymmetric outcomes may follow "
      f"\\citep{{Diamond1997, DiamondBellwood2003}}. Within this selected dataset, "
      f"{_pct(candidate_rate)} of technically excluded cases are coded as conquered. The post "
      r"hoc classification and non-probability case selection prevent treating that descriptive "
      r"rate as a general historical estimate.")
    W()
    W(r"The hypothesized pathway is cumulative divergence through technology flow disruption. "
      r"International exchange networks carried not only goods but military techniques, "
      r"metallurgical innovations, navigational knowledge, and institutional models "
      r"\citep{Mokyr2002, Pomeranz2000}. Polities connected to these networks could adopt, "
      r"adapt, and build upon innovations generated elsewhere. Polities with weaker access may "
      r"have less capacity to do so. Over generations, a technology gap may widen---a process analogous to the "
      r"long-run consequences of network disruption documented by \citet{Nunn2008}, who showed "
      r"that regions more heavily affected by the slave trade experienced persistent "
      r"underdevelopment centuries later. When contact with a more advanced civilization "
      r"eventually occurred---often through military expansion---an accumulated gap may have "
      r"contributed to vulnerability. These case narratives motivate the proposed sequence but "
      r"do not test it.")
    W()
    W(r"Policy-closed polities that maintained narrow conduits of technology "
      r"transfer---Japan's \emph{rangaku} and Qing China's limited Canton trade---suggest a "
      r"contrast worth testing against more severe disconnection. The present data do not "
      r"measure residual technology flow or cumulative gaps and therefore cannot determine "
      r"whether those mechanisms explain the coded outcomes.")
    W()
    W(r"This finding has a corollary that is worth stating explicitly. If the critical "
      r"variable is not closure itself but the residual technology flow that closure permits, "
      r"then polities that close their borders while deliberately maintaining selective "
      r"channels for frontier knowledge occupy a qualitatively different position from those "
      r"that are more severely disconnected. Our dataset contains several instances of such conditional "
      r"closure. Tokugawa Japan preserved access to Western science through \emph{rangaku} at "
      r"Dejima and was disrupted but not conquered, reconstituting itself as the Meiji state. "
      r"Early Qing China maintained the Canton system---a single, tightly controlled port of "
      r"trade through which some foreign knowledge filtered---and survived the "
      r"Kangxi--Qianlong era intact. Joseon Korea sustained tributary trade with China, which "
      r"served as a conduit for Continental knowledge and technology. The Soviet Union, while "
      r"sealed from the Western bloc, maintained extensive technology sharing within the "
      r"Eastern bloc and invested heavily in indigenous research institutions. North Korea has "
      r"preserved a limited technology channel through its relationship with China. (Full "
      r"details of each polity's closure regime, technology channels, and outcomes are "
      r"recorded in Supplementary Table~S1.)")
    W()
    W(r"The outcomes, however, are mixed. Early Qing China survived, but late Qing "
      r"China---operating under the same Canton system---was semi-colonized after the Opium "
      r"Wars. Tokugawa Japan survived as a political entity, but Joseon Korea, despite its "
      r"Chinese conduit, was annexed by Japan in 1910. The Soviet Union collapsed internally "
      r"despite its bloc-level technology sharing, while North Korea has persisted under "
      r"extreme isolation with minimal Chinese patronage. These divergent outcomes suggest "
      r"that the mere existence of a selective channel does not guarantee survival; unmeasured "
      r"factors---the breadth and relevance of the knowledge flowing through the channel, the "
      r"domestic capacity to absorb and adapt that knowledge, the pace of change at the "
      r"technological frontier, and institutional dynamics that our dataset does not "
      r"capture---likely condition the effectiveness of conditional closure. The policy "
      r"question, then, is not binary (open or closed) but conditional, and the conditions "
      r"under which selective channels suffice to prevent a large technology gap remain an "
      r"open and consequential problem for future research. Readers interested in tracing "
      r"these cases in detail are referred to Supplementary Table~S1, which documents the "
      f"specific turning-point events and outcomes for all {N} polities in the dataset.")
    W()

    W(r"\subsection{Beyond geographic isolation: technological access exclusion in the "
      r"modern era}\label{sec:disc-modern}")
    W()
    W(r"If the mechanism we identify is technology flow disruption rather than network "
      r"closure per se, then the pattern should generalize beyond the age of sail. Each era "
      r"has its own dominant technological platform---the infrastructure through which "
      r"frontier knowledge diffuses across states. In antiquity, it was the Mediterranean "
      r"trade routes and Silk Road caravans. In the early modern period, it was oceanic "
      r"shipping. In the industrial age, it was railroad-linked factory systems and colonial "
      r"supply chains. In the twentieth century, it was aerospace and nuclear technology "
      r"networks.")
    W()
    W(r"Today, the dominant platform has shifted again. The critical networks are "
      r"semiconductor supply chains, artificial intelligence research ecosystems, and "
      r"advanced robotics and automation infrastructure "
      r"\citep{AcemogluRestrepo2020, CominMestieri2018}. "
      r"\citet{CominEasterlyGong2010} show that technology adoption levels in 1000~BC predict "
      r"income differences today, while \citet{AcemogluJohnsonRobinson2002} demonstrate that "
      r"colonial-era institutional reversals reshaped global inequality---both consistent "
      r"with the view that early technological access has persistent, cumulative consequences. "
      r"Global shipping and communication networks have reduced, but not eliminated, geographic "
      r"barriers to exchange. A further form of structural exclusion may arise when states are "
      r"cut off from the technological frontier not by mountains and oceans but by export "
      r"controls on advanced semiconductors, by the concentration of AI training "
      r"infrastructure in a handful of countries, or by the institutional and human-capital "
      r"barriers that prevent participation in cutting-edge research networks.")
    W()
    W(r"An exploratory analogy can be drawn to contemporary states excluded from advanced "
      r"semiconductor fabrication or AI model development, which may face a widening technology gap. "
      r"If the gap grows large enough, the eventual `first contact'---whether military, "
      r"economic, or geopolitical---could produce asymmetric outcomes. Whether the historical "
      r"coding captures a comparable process is an empirical question for future data.")
    W()
    W(r"We stress that this extrapolation is speculative and cannot be tested within our "
      r"historical dataset. The contemporary world differs from the premodern era in ways "
      r"that may attenuate or amplify the mechanism: nuclear deterrence, international "
      r"institutions, and the speed of modern communication all introduce novel dynamics. "
      r"The post hoc association in the selected cases provides a provisional "
      r"framework for thinking about which dimensions of modern technological access may be "
      r"most consequential.")
    W()

    W(r"\subsection{Stability of the stock--flow framework and the question of "
      r"resource-base transitions}\label{sec:disc-stockflow}")
    W()
    W(f"The stock--flow OR ({cm_all_c['OR']:.3f}) is unchanged across the reclassification "
      r"scenarios because those scenarios alter closure labels but not stock/flow or outcome "
      r"coding. The stock--flow and closure comparisons should therefore be interpreted as "
      r"separate exploratory descriptions rather than as evidence of distinct causal dimensions.")
    W()
    W(f"Crossing these two dimensions yields a four-cell classification whose conquest rates "
      f"are reported in Table~\\ref{{tab:stockflow-closure}}. Flow-oriented polities without "
      f"closure show the lowest conquest rate ({_pct(fo['rate'])}, $n = {fo['n']}$). "
      f"Stock-oriented polities without closure show a moderately elevated rate "
      f"({_pct(so['rate'])}, $n = {so['n']}$). Stock-oriented polities with closure show a "
      f"markedly higher rate ({_pct(sc['rate'])}, $n = {sc['n']}$). Flow-oriented polities with "
      f"closure---a small cell ($n = {fc['n']}$)---show a {_pct(fc['rate'])} conquest rate. "
      f"The contrast between the highest- and lowest-risk cells (stock + closed vs.\\ flow + "
      f"open) yields an odds ratio of {or_sc_fo:.2f} (one-sided Fisher exact "
      f"$p = {p_sc_fo:.3f}$). Within stock-oriented polities, the effect of closure "
      f"corresponds to an OR of {or_sc_so:.2f} ($p = {p_sc_so:.3f}$). Within flow-oriented "
      f"polities, the effect of closure yields an OR of "
      f"${or_fc_fo_str}$ ($p = {p_fc_fo:.3f}$), "
      f"though the cell size ($n = {fc['n']}$) precludes reliable inference.")
    W()

    # Table 4
    W(r"\begin{table}[htbp]")
    W(f"\\caption{{Conquest rates by resource-base orientation and closure status "
      f"({candidate_count}-country reclassification, disrupted $=$ conquered).}}")
    W(r"\label{tab:stockflow-closure}")
    W(r"\begin{tabular*}{\textwidth}{@{\extracolsep\fill}lcccc}")
    W(r"\toprule")
    W(r" & Conquered & Survived & $n$ & Rate \\")
    W(r"\midrule")
    for label, cell in [("Stock + closed", sc), ("Stock + open", so),
                        ("Flow + closed", fc), ("Flow + open", fo)]:
        rate_str = f"{cell['rate']*100:.1f}\\%"
        W(f"{label} & {cell['c']} & {cell['s']} & {cell['n']} & {rate_str} \\\\")
    W(r"\botrule")
    W(r"\end{tabular*}")
    W(r"\footnotetext{Fisher exact tests (one-sided): stock + closed vs.\ flow + open, "
      f"OR $= {or_sc_fo:.2f}$, $p = {p_sc_fo:.3f}$; within stock, closed vs.\\ open, "
      f"OR $= {or_sc_so:.2f}$, $p = {p_sc_so:.3f}$; within flow, closed vs.\\ open, "
      f"OR $= {or_fc_fo_str}$, $p = {p_fc_fo:.3f}$.}}")
    W(r"\end{table}")
    W()

    W(f"The pattern is consistent with the hypothesis that stock-orientation and network "
      f"exclusion compound each other's risk, though the small cell sizes---particularly for "
      f"flow + closed ($n = {fc['n']}$)---warrant caution. The stock + closed combination is "
      r"the only cell to reach a statistically significant difference from the baseline flow "
      f"+ open cell at conventional levels. Notably, {sc['s']} stock-oriented polities with "
      r"closure survived despite their high-risk classification; their individual "
      r"characteristics---including specific closure regimes, technology channels maintained, "
      r"and the historical circumstances of their survival---are documented in Supplementary "
      r"Table~S1.")
    W()
    W(r"An implication worth noting is that the stock--flow distinction is not permanently "
      r"fixed for any given state. Polities can transition from flow-oriented to "
      r"stock-oriented resource bases---or vice versa---as economic structures, demographic "
      r"conditions, and institutional incentives evolve. A state that was historically "
      r"flow-oriented (trade-dependent, outward-looking, innovation-absorbing) but that "
      r"gradually shifts toward reliance on accumulated domestic assets---physical capital, "
      r"territorial resources, existing institutional infrastructure---moves into the "
      r"higher-risk stock category. If such a transition coincides with reduced engagement in "
      r"the dominant technological network of the era, the compounding of stock-orientation "
      r"and network exclusion could amplify vulnerability. Our dataset cannot test this "
      r"dynamic directly, as polities are coded at a single point in time, but the "
      r"theoretical interaction between resource-base transition and network access merits "
      r"further investigation.")
    W()

    W(r"\subsection{Limitations}\label{sec:disc-limitations}")
    W()
    W(f"Several limitations warrant acknowledgment. First, the coding of historical polities "
      r"inevitably involves subjective judgment, particularly for the stock/flow "
      r"classification and the identification of technical exclusion candidates. The tiered "
      r"approach (strong vs.\ moderate candidates) and the six-scenario sensitivity design "
      r"partially address this, but cannot eliminate it. Second, the sample size ($N = "
      f"{N}$) constrains the power of the multivariate analyses; wide confidence intervals "
      r"for some regression coefficients reflect this constraint. Third, the dataset treats "
      r"polities as independent observations, though historical interconnections (e.g., "
      r"sequential Chinese dynasties sharing institutional continuity) may introduce "
      r"non-independence. Fourth, the `disrupted' category introduces a classification "
      r"ambiguity that the dual-assignment design addresses but cannot fully resolve. Fifth, "
      r"the forward-looking extension to modern technological exclusion is necessarily "
      r"speculative, as the mechanisms operating in a nuclear-armed, institutionally dense "
      r"modern world may differ qualitatively from those in premodern eras.")
    W()

    # ════════════════════════════════════════
    # 7. CONCLUSION
    # ════════════════════════════════════════
    W(r"\section{Conclusion}\label{sec:conclusion}")
    W()
    W(f"Within this AI-assisted exploratory dataset, a post hoc reclassification of {candidate_count} technically excluded polities---those "
      r"coded as disconnected from the dominant exchange networks of their era by geography "
      r"and technology rather than by policy---changes the one-sided Fisher exact p-value to "
      f"{s_all_c['fisher_ban_p']:.3f}, while the "
      f"core stock--flow odds ratio remains unchanged (OR $= {cm_base['OR']:.3f}$). The "
      f"{_pct(candidate_rate)} conquest rate among technically excluded polities, the closure-type comparison, "
      r"and the absorption of the closure effect by external threat "
      r"and institutional quality in multivariate models are consistent with, but do not "
      r"establish, a proposed mechanism in which disruption of technology flow leads to "
      r"cumulative divergence from the technological frontier.")
    W()
    W(r"The broader implication is that this mechanism is not specific to any single network "
      r"form. In every era, there exists a dominant network through which frontier "
      r"technologies diffuse. Polities excluded from that network---whether by oceans, "
      r"mountains, policy, or, in the contemporary period, by semiconductor export controls "
      r"and AI infrastructure concentration---may warrant comparison with historical patterns "
      r"of cumulative divergence. The exploratory comparison does not establish that modern "
      r"technological restrictions will produce the same outcomes. The converse question "
      r"suggested by the Tokugawa precedent is whether a state that recognizes the risk of "
      r"network exclusion can, through deliberate maintenance of selective technology channels, "
      r"reduce divergence while restricting broader engagement with the outside world.")
    W()

    # ════════════════════════════════════════
    # STATEMENTS AND DECLARATIONS
    # ════════════════════════════════════════
    W(r"\section*{Statements and Declarations}")
    W()
    W(r"\subsection*{Funding}")
    W(r"[To be completed by author]")
    W()
    W(r"\subsection*{Competing Interests}")
    W(r"[To be confirmed by author]")
    W()
    W(r"\subsection*{Author Contributions (CRediT)}")
    W(r"[To be completed by author]")
    W()
    W(r"\subsection*{Data Availability}")
    W(r"The complete dataset and analysis code are available at "
      r"\url{https://github.com/bougtoir/beyond-gdp-national-power}. "
      f"Supplementary Table~S1 provides the full dataset of {N} polities with all coded "
      r"variables.")
    W()
    W(r"\subsection*{Declaration of Generative AI and AI-Assisted Technologies in the "
      r"Manuscript Preparation Process}")
    W(r"During the preparation of this work, the author used Devin (Cognition AI) to "
      r"support code execution, dataset documentation, source auditing, and drafting and "
      r"editing. The author reviewed and edited the content as needed and takes full "
      r"responsibility for the content of the published article. [Author confirmation "
      r"required before submission.]")
    W()

    # JEL
    W(r"\subsection*{JEL Classification}")
    W(r"N40, N70, F50, O33, C25")
    W()

    # Bibliography
    # Note: \bibliographystyle is set automatically by sn-jnl.cls via the sn-basic option
    W(r"\bibliography{references}")
    W()
    W(r"\end{document}")

    # Write .tex
    tex_path = os.path.join(OUT, "manuscript.tex")
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(tex))
    print("  LaTeX manuscript saved to", tex_path)
    return tex_path


# ═══════════════════════════════════════════════════════════════
# Supplementary Table S1 (LaTeX)
# ═══════════════════════════════════════════════════════════════

def create_table_s1_latex(results):
    df = results["df"]
    era_map = {"ancient": "Ancient", "medieval": "Medieval",
               "early_modern": "Early Modern", "modern": "Modern",
               "20c": "20th Century", "contemporary": "Contemporary"}
    closure_map = {"none": "None", "maritime_ban": "Maritime ban",
                   "sakoku": "Sakoku", "bloc": "Bloc",
                   "technical_network_exclusion": "Technical network exclusion"}

    tex = []
    tex.append(r"\documentclass[11pt]{article}")
    tex.append(r"\usepackage[margin=1cm,landscape]{geometry}")
    tex.append(r"\usepackage{booktabs}")
    tex.append(r"\usepackage{longtable}")
    tex.append(r"\usepackage{array}")
    tex.append(r"\usepackage[T1]{fontenc}")
    tex.append(r"\begin{document}")
    tex.append(r"\footnotesize")
    tex.append(r"\begin{longtable}{rlllllllp{6cm}}")
    tex.append(
        f"\\caption{{Supplementary Table S1: Full dataset of {len(df)} historical polities.}} \\\\"
    )
    tex.append(r"\toprule")
    tex.append(r"\# & Polity & Modern Country & Period & Era & Dominant & Closure & Outcome & Turning-Point Event \\")
    tex.append(r"\midrule")
    tex.append(r"\endfirsthead")
    tex.append(r"\toprule")
    tex.append(r"\# & Polity & Modern Country & Period & Era & Dominant & Closure & Outcome & Turning-Point Event \\")
    tex.append(r"\midrule")
    tex.append(r"\endhead")
    tex.append(r"\midrule")
    tex.append(r"\endfoot")
    tex.append(r"\bottomrule")
    tex.append(r"\endlastfoot")

    for idx, (_, row) in enumerate(df.iterrows()):
        entity = row["entity"]
        vals = [
            str(idx + 1),
            _esc(ENGLISH_NAME.get(entity, entity)),
            _esc(MODERN_COUNTRY.get(entity, "---")),
            _esc(row["period"]),
            era_map.get(row["era"], row["era"]),
            row["dominant"].capitalize(),
            closure_map.get(row["closure_type"], row["closure_type"]),
            row["outcome"].capitalize(),
            _esc(TURNING_POINT.get(entity, "---")),
        ]
        tex.append(" & ".join(vals) + r" \\")

    tex.append(r"\end{longtable}")
    tex.append(r"\end{document}")

    path = os.path.join(OUT, "table_s1.tex")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(tex))
    print("  Table S1 (LaTeX) saved to", path)
    return path


# ═══════════════════════════════════════════════════════════════
# Cover letter (LaTeX)
# ═══════════════════════════════════════════════════════════════

def create_cover_letter_tex(results):
    N = results["N"]
    s_base_c = results["scenarios"]["as_conquered__baseline"]
    s_all_c = results["scenarios"]["as_conquered__all"]
    cm_base = s_base_c["cm"]
    candidate_count = len(STRONG_CANDIDATES + MODERATE_CANDIDATES)
    candidate_rate = apply_disrupted_assignment(results["df"], "as_conquered")[
        lambda frame: frame["entity"].isin(STRONG_CANDIDATES + MODERATE_CANDIDATES)
    ]["outcome_binary"].mean()
    tex = []
    tex.append(r"\documentclass[11pt]{letter}")
    tex.append(r"\usepackage[margin=2.5cm]{geometry}")
    tex.append(r"\usepackage[T1]{fontenc}")
    tex.append(r"\usepackage{hyperref}")
    tex.append(r"\signature{Author Name\\Affiliation\\Email}")
    tex.append(r"\address{Author Name\\Affiliation\\City, Country\\Email}")
    tex.append(r"\begin{document}")
    tex.append(r"\begin{letter}{The Editors, \emph{Explorations in Economic History}}")
    tex.append(r"\opening{Dear Editors,}")
    tex.append("")
    tex.append(r"I am pleased to submit the manuscript entitled ``Network Exclusion and "
               r"State Collapse: From Maritime Isolation to Technological Access Denial in "
               r"the Long Run of History'' for consideration by "
               r"\emph{Explorations in Economic History}.")
    tex.append("")
    tex.append(f"Using an AI-assisted exploratory dataset of {N} historical polities rather "
               r"than a public-data measurement dataset, we distinguish "
               r"between deliberate closure (policy-based trade "
               r"bans, \emph{sakoku}, bloc membership) and what we term \emph{technical "
               r"network exclusion}: involuntary disconnection from the dominant exchange "
               r"network of an era due to geographic or technological constraints. The "
               r"manuscript presents four features that we believe are of interest to the "
               r"journal's readership.")
    tex.append("")
    tex.append(r"First, a post hoc sensitivity analysis reports that reclassifying "
               f"{candidate_count} technically excluded polities changes the one-sided Fisher exact p-value "
               f"for closure and conquest from {s_base_c['fisher_ban_p']:.3f} to "
               f"{s_all_c['fisher_ban_p']:.3f} within the current codings, while the core stock--flow odds ratio remains stable "
               f"(OR $= {cm_base['OR']:.3f}$).")
    tex.append("")
    tex.append(r"Second, we analyze conditional closure---cases where polities maintained "
               r"selective technology channels while restricting broader trade. Examples "
               r"include Tokugawa Japan's \emph{rangaku} through Dejima, Qing China's Canton "
               r"system, Joseon Korea's tributary trade, and the Soviet Union's bloc-internal "
               r"technology sharing. The mixed outcomes of these cases suggest that the "
               r"open/closed dichotomy is insufficient; the conditions under which selective "
               r"channels mitigate technology gaps merit further investigation.")
    tex.append("")
    tex.append(r"Third, the closure-type comparison shows a "
               f"{_pct(candidate_rate)} conquest rate among the technically excluded candidates, "
               r"but the category rates are not strictly monotonic. We therefore present "
               r"technology-flow disruption as a hypothesis rather than an identified mechanism.")
    tex.append("")
    tex.append(r"Fourth, the hypothesis may generalize beyond geographic isolation: as the "
               r"dominant network shifts from sea lanes to semiconductors, AI, and advanced "
               r"robotics, states structurally excluded from these platforms may face "
               r"analogous vulnerabilities.")
    tex.append("")
    tex.append(r"The manuscript includes the analysis tables, figures, and a complete "
               r"Supplementary Table~S1 dataset. [Before submission, please confirm that "
               r"this work has not been published or submitted elsewhere.]")
    tex.append("")
    tex.append(r"We suggest the following reviewers based on their expertise in quantitative "
               r"economic history:")
    tex.append(r"\begin{itemize}")
    tex.append(r"\item Prof.\ J\"org Baten (University of T\"ubingen) --- cliometric methods "
               r"and long-run development")
    tex.append(r"\item Prof.\ Stephen Broadberry (University of Oxford) --- comparative "
               r"economic history and GDP estimation")
    tex.append(r"\item Prof.\ Nathan Nunn (University of British Columbia) --- long-run "
               r"persistence and historical institutions")
    tex.append(r"\end{itemize}")
    tex.append("")
    tex.append(r"\closing{Sincerely,}")
    tex.append(r"\end{letter}")
    tex.append(r"\end{document}")

    path = os.path.join(OUT, "cover_letter.tex")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(tex))
    print("  Cover letter (LaTeX) saved to", path)
    return path


def create_cover_letter_docx(results):
    N = results["N"]
    s_base_c = results["scenarios"]["as_conquered__baseline"]
    s_all_c = results["scenarios"]["as_conquered__all"]
    cm_base = s_base_c["cm"]
    candidate_count = len(STRONG_CANDIDATES + MODERATE_CANDIDATES)
    candidate_rate = apply_disrupted_assignment(results["df"], "as_conquered")[
        lambda frame: frame["entity"].isin(STRONG_CANDIDATES + MODERATE_CANDIDATES)
    ]["outcome_binary"].mean()

    doc = Document()
    for section in doc.sections:
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)
    doc.styles["Normal"].font.name = "Times New Roman"
    doc.styles["Normal"].font.size = Pt(12)

    doc.add_paragraph("[Date]")
    doc.add_paragraph("The Editors\nExplorations in Economic History")
    doc.add_paragraph("Dear Editors,")
    doc.add_paragraph(
        "I am pleased to submit “Network Exclusion and State Collapse: From Maritime "
        "Isolation to Technological Access Denial in the Long Run of History” for "
        "consideration by Explorations in Economic History."
    )
    doc.add_paragraph(
        f"The study uses an AI-assisted exploratory dataset of {N} historical polity-period "
        "cases rather than a public-data measurement dataset. It distinguishes deliberate "
        "closure from technical network exclusion and makes the complete editable coding and "
        "case-level source supplement publicly available."
    )
    doc.add_paragraph(
        f"In the post hoc sensitivity analysis, reclassifying {candidate_count} technically excluded "
        f"polities changes the one-sided Fisher exact p-value from "
        f"{s_base_c['fisher_ban_p']:.3f} to {s_all_c['fisher_ban_p']:.3f}; the stock–flow "
        f"odds ratio remains {cm_base['OR']:.3f}. The candidates have a "
        f"{candidate_rate:.1%} conquest rate in the current codings, but closure-category "
        "rates are not strictly monotonic, so technology-flow disruption is presented as a "
        "hypothesis rather than an identified mechanism."
    )
    doc.add_paragraph(
        "The manuscript includes analysis tables, figures, a complete supplementary dataset, "
        "variable metadata, and a field-level historical source supplement. [Before submission, "
        "please confirm that the work is not under consideration elsewhere.]"
    )
    doc.add_paragraph("Sincerely,\n\n[Author Name]\n[Affiliation]\n[Email]")

    path = os.path.join(OUT, "cover_letter.docx")
    doc.save(path)
    print("  Cover letter (DOCX) saved to", path)
    return path


# ═══════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════

def main():
    print("Running analysis...")
    results = run_analysis()

    print("Creating figures...")
    create_figures(results)

    print("Creating PPTX...")
    create_pptx(results)

    print("Creating Table S1 (docx)...")
    create_table_s1(results)

    print("Creating BibTeX...")
    create_bibtex()

    print("Creating manuscript (LaTeX)...")
    tex_path = create_manuscript_tex(results)

    print("Creating Table S1 (LaTeX)...")
    s1_path = create_table_s1_latex(results)

    print("Creating cover letter (LaTeX)...")
    cl_path = create_cover_letter_tex(results)
    print("Creating cover letter (DOCX)...")
    create_cover_letter_docx(results)

    # Copy sn-jnl.cls and bst to manuscript dir
    for f in ["sn-jnl.cls"]:
        src = os.path.join(TEMPLATE_DIR, f)
        dst = os.path.join(OUT, f)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"  Copied {f} to {OUT}")

    bst_src = os.path.join(TEMPLATE_DIR, "bst", "sn-basic.bst")
    bst_dst = os.path.join(OUT, "sn-basic.bst")
    if os.path.exists(bst_src):
        shutil.copy2(bst_src, bst_dst)
        print(f"  Copied sn-basic.bst to {OUT}")

    # Compile LaTeX → PDF
    print("Compiling manuscript PDF...")
    pdf = _compile_latex(tex_path, OUT)
    if pdf:
        print(f"  PDF compiled: {pdf}")
    elif shutil.which("pdflatex") is None:
        print("  PDF compilation skipped: pdflatex is not installed.")
    else:
        print("  WARNING: PDF compilation failed. Check LaTeX logs.")

    print("Compiling Table S1 PDF...")
    s1_pdf = _compile_latex(s1_path, OUT)
    if s1_pdf:
        print(f"  Table S1 PDF: {s1_pdf}")

    print("Compiling cover letter PDF...")
    cl_pdf = _compile_latex(cl_path, OUT)
    if cl_pdf:
        print(f"  Cover letter PDF: {cl_pdf}")

    print("\nAll outputs saved to:", OUT)


if __name__ == "__main__":
    main()
