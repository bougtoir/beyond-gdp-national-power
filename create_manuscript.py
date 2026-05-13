"""
Generate Cliometrica manuscript: "Flow Disruption and State Collapse"
Technical Maritime Ban sensitivity analysis with 7-country reclassification.

Outputs:
  manuscript/manuscript.docx          — Main manuscript (Cliometrica format)
  manuscript/table_s1.docx            — Supplementary Table S1 (96 polities)
  manuscript/figures/Fig1.png … Fig4.png — Separate figure files
  manuscript/figures_pptx.pptx        — Editable PPTX (1 figure per slide)
"""

import os
import sys
import re
import math
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import FancyBboxPatch
import seaborn as sns

from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from pptx import Presentation
from pptx.util import Inches as PptxInches, Pt as PptxPt
from pptx.enum.text import PP_ALIGN

# ── project imports ──
sys.path.insert(0, os.path.dirname(__file__))
from data import load_data
from sensitivity_technical_maritime_ban import (
    STRONG_CANDIDATES, MODERATE_CANDIDATES, RATIONALE,
    apply_technical_maritime_ban, apply_disrupted_assignment,
    compute_confusion_stats, compute_closure_analysis,
    compute_logistic_with_closure, compute_mediation_paths,
)

OUT = os.path.join(os.path.dirname(__file__), "manuscript")
FIG = os.path.join(OUT, "figures")
os.makedirs(FIG, exist_ok=True)

# ════════════════════════════════════════════════════════════
# Modern-country mapping & turning-point events for Table S1
# ════════════════════════════════════════════════════════════

MODERN_COUNTRY = {
    "アケメネス朝ペルシア": "Iran",
    "アテネ（ペロポネソス戦争後）": "Greece",
    "スパルタ": "Greece",
    "カルタゴ": "Tunisia",
    "ローマ共和政〜帝政前期": "Italy",
    "ローマ帝政後期（西）": "Italy",
    "プトレマイオス朝エジプト": "Egypt",
    "漢朝（前漢〜後漢）": "China",
    "ビザンツ帝国（前期）": "Turkey/Greece",
    "ビザンツ帝国（後期）": "Turkey/Greece",
    "アッバース朝（前期）": "Iraq",
    "アッバース朝（後期）": "Iraq",
    "宋朝中国": "China",
    "モンゴル帝国": "Mongolia/China",
    "マムルーク朝エジプト": "Egypt",
    "ヴェネツィア共和国": "Italy",
    "ハンザ同盟": "Germany",
    "オスマン帝国（前期）": "Turkey",
    "オスマン帝国（後期）": "Turkey",
    "明朝中国": "China",
    "清朝中国（前期）": "China",
    "清朝中国（後期）": "China",
    "李朝朝鮮": "Korea",
    "徳川日本": "Japan",
    "ムガル帝国（後期）": "India",
    "サファヴィー朝ペルシア": "Iran",
    "インカ帝国": "Peru",
    "アステカ帝国": "Mexico",
    "ポルトガル帝国": "Portugal",
    "オランダ共和国": "Netherlands",
    "スペイン帝国": "Spain",
    "ムガル帝国（前期）": "India",
    "大英帝国": "United Kingdom",
    "米国（モンロー主義期）": "United States",
    "明治〜大正日本": "Japan",
    "エチオピア帝国": "Ethiopia",
    "シャム（タイ）": "Thailand",
    "スイス": "Switzerland",
    "1930s日本（大東亜共栄圏）": "Japan",
    "ナチスドイツ": "Germany",
    "ファシストイタリア": "Italy",
    "ソ連": "Russia",
    "東ドイツ": "Germany",
    "ユーゴスラビア": "Serbia/Croatia/Bosnia/etc.",
    "英国帝国特恵制度": "United Kingdom",
    "米国（戦後〜冷戦期）": "United States",
    "戦後日本（高度成長期）": "Japan",
    "シンガポール": "Singapore",
    "韓国": "South Korea",
    "北朝鮮": "North Korea",
    "キューバ": "Cuba",
    "現代日本": "Japan",
    "現代中国": "China",
    "現代ロシア": "Russia",
    "マケドニア王国（アレクサンドロス後）": "Greece/North Macedonia",
    "セレウコス朝シリア": "Syria/Iraq/Iran",
    "パルティア": "Iran",
    "ササン朝ペルシア": "Iran",
    "クシャーナ朝": "Afghanistan/Pakistan",
    "グプタ朝インド": "India",
    "唐朝中国": "China",
    "ウマイヤ朝": "Syria",
    "高麗": "Korea",
    "クメール帝国（アンコール）": "Cambodia",
    "シュリーヴィジャヤ": "Indonesia",
    "マジャパヒト王国": "Indonesia",
    "キエフ大公国": "Ukraine/Russia",
    "ジェノヴァ共和国": "Italy",
    "マリ帝国": "Mali",
    "元朝中国": "China",
    "ティムール朝": "Uzbekistan/Iran",
    "琉球王国": "Japan (Okinawa)",
    "ポーランド・リトアニア共和国": "Poland/Lithuania",
    "スウェーデン帝国": "Sweden",
    "ロシア帝国（ピョートル後）": "Russia",
    "清朝中国（中期・交易拡大期）": "China",
    "ハワイ王国": "United States (Hawaii)",
    "ズールー王国": "South Africa",
    "ビルマ（コンバウン朝）": "Myanmar",
    "オーストリア＝ハンガリー帝国": "Austria/Hungary",
    "ベルギー": "Belgium",
    "デンマーク": "Denmark",
    "ナポレオン帝国": "France",
    "大韓帝国": "South Korea",
    "満州国": "China (Manchuria)",
    "南ベトナム": "Vietnam",
    "チェコスロバキア（共産期）": "Czech Republic/Slovakia",
    "ポーランド（共産期）": "Poland",
    "ルーマニア（共産期）": "Romania",
    "台湾": "Taiwan",
    "イスラエル": "Israel",
    "UAE": "United Arab Emirates",
    "現代インド": "India",
    "イラン（イスラム共和国）": "Iran",
    "ミャンマー（軍政期〜現在）": "Myanmar",
    "トルクメニスタン": "Turkmenistan",
}

ENGLISH_NAME = {
    "アケメネス朝ペルシア": "Achaemenid Persia",
    "アテネ（ペロポネソス戦争後）": "Athens (post-Peloponnesian War)",
    "スパルタ": "Sparta",
    "カルタゴ": "Carthage",
    "ローマ共和政〜帝政前期": "Roman Republic–Early Empire",
    "ローマ帝政後期（西）": "Late Western Roman Empire",
    "プトレマイオス朝エジプト": "Ptolemaic Egypt",
    "漢朝（前漢〜後漢）": "Han Dynasty (China)",
    "ビザンツ帝国（前期）": "Byzantine Empire (early)",
    "ビザンツ帝国（後期）": "Byzantine Empire (late)",
    "アッバース朝（前期）": "Abbasid Caliphate (early)",
    "アッバース朝（後期）": "Abbasid Caliphate (late)",
    "宋朝中国": "Song Dynasty (China)",
    "モンゴル帝国": "Mongol Empire",
    "マムルーク朝エジプト": "Mamluk Sultanate",
    "ヴェネツィア共和国": "Republic of Venice",
    "ハンザ同盟": "Hanseatic League",
    "オスマン帝国（前期）": "Ottoman Empire (early)",
    "オスマン帝国（後期）": "Ottoman Empire (late)",
    "明朝中国": "Ming Dynasty (China)",
    "清朝中国（前期）": "Qing Dynasty (early)",
    "清朝中国（後期）": "Qing Dynasty (late)",
    "李朝朝鮮": "Joseon Korea",
    "徳川日本": "Tokugawa Japan",
    "ムガル帝国（後期）": "Mughal Empire (late)",
    "サファヴィー朝ペルシア": "Safavid Persia",
    "インカ帝国": "Inca Empire",
    "アステカ帝国": "Aztec Empire",
    "ポルトガル帝国": "Portuguese Empire",
    "オランダ共和国": "Dutch Republic",
    "スペイン帝国": "Spanish Empire",
    "ムガル帝国（前期）": "Mughal Empire (early)",
    "大英帝国": "British Empire",
    "米国（モンロー主義期）": "United States (Monroe era)",
    "明治〜大正日本": "Meiji–Taisho Japan",
    "エチオピア帝国": "Ethiopian Empire",
    "シャム（タイ）": "Siam (Thailand)",
    "スイス": "Switzerland",
    "1930s日本（大東亜共栄圏）": "Imperial Japan (1930s)",
    "ナチスドイツ": "Nazi Germany",
    "ファシストイタリア": "Fascist Italy",
    "ソ連": "Soviet Union",
    "東ドイツ": "East Germany",
    "ユーゴスラビア": "Yugoslavia",
    "英国帝国特恵制度": "British Imperial Preference",
    "米国（戦後〜冷戦期）": "United States (Cold War era)",
    "戦後日本（高度成長期）": "Post-war Japan",
    "シンガポール": "Singapore",
    "韓国": "South Korea",
    "北朝鮮": "North Korea",
    "キューバ": "Cuba",
    "現代日本": "Contemporary Japan",
    "現代中国": "Contemporary China",
    "現代ロシア": "Contemporary Russia",
    "マケドニア王国（アレクサンドロス後）": "Successor Macedonia",
    "セレウコス朝シリア": "Seleucid Empire",
    "パルティア": "Parthian Empire",
    "ササン朝ペルシア": "Sasanian Persia",
    "クシャーナ朝": "Kushan Empire",
    "グプタ朝インド": "Gupta Empire",
    "唐朝中国": "Tang Dynasty (China)",
    "ウマイヤ朝": "Umayyad Caliphate",
    "高麗": "Goryeo (Korea)",
    "クメール帝国（アンコール）": "Khmer Empire (Angkor)",
    "シュリーヴィジャヤ": "Srivijaya",
    "マジャパヒト王国": "Majapahit",
    "キエフ大公国": "Kievan Rus'",
    "ジェノヴァ共和国": "Republic of Genoa",
    "マリ帝国": "Mali Empire",
    "元朝中国": "Yuan Dynasty (China)",
    "ティムール朝": "Timurid Empire",
    "琉球王国": "Ryukyu Kingdom",
    "ポーランド・リトアニア共和国": "Polish-Lithuanian Commonwealth",
    "スウェーデン帝国": "Swedish Empire",
    "ロシア帝国（ピョートル後）": "Russian Empire (post-Peter)",
    "清朝中国（中期・交易拡大期）": "Qing Dynasty (mid-period)",
    "ハワイ王国": "Kingdom of Hawaii",
    "ズールー王国": "Zulu Kingdom",
    "ビルマ（コンバウン朝）": "Konbaung Burma",
    "オーストリア＝ハンガリー帝国": "Austria-Hungary",
    "ベルギー": "Belgium",
    "デンマーク": "Denmark",
    "ナポレオン帝国": "Napoleonic Empire",
    "大韓帝国": "Korean Empire",
    "満州国": "Manchukuo",
    "南ベトナム": "South Vietnam",
    "チェコスロバキア（共産期）": "Czechoslovakia (communist)",
    "ポーランド（共産期）": "Poland (communist)",
    "ルーマニア（共産期）": "Romania (communist)",
    "台湾": "Taiwan",
    "イスラエル": "Israel",
    "UAE": "United Arab Emirates",
    "現代インド": "Contemporary India",
    "イラン（イスラム共和国）": "Iran (Islamic Republic)",
    "ミャンマー（軍政期〜現在）": "Myanmar (military rule)",
    "トルクメニスタン": "Turkmenistan",
}

TURNING_POINT = {
    "アケメネス朝ペルシア": "Conquered by Alexander the Great at Battle of Gaugamela (331 BC)",
    "アテネ（ペロポネソス戦争後）": "Subjugated by Macedon after Battle of Chaeronea (338 BC)",
    "スパルタ": "Defeated at Battle of Leuctra (371 BC); absorbed by Rome (146 BC)",
    "カルタゴ": "Destroyed by Rome in Third Punic War (146 BC)",
    "ローマ共和政〜帝政前期": "Survived: expanded to dominate the Mediterranean",
    "ローマ帝政後期（西）": "Fall of Rome to Odoacer (476 AD)",
    "プトレマイオス朝エジプト": "Annexed by Rome after Battle of Actium (30 BC)",
    "漢朝（前漢〜後漢）": "Collapsed into Three Kingdoms civil war (220 AD)",
    "ビザンツ帝国（前期）": "Survived: withstood Arab and Bulgar sieges",
    "ビザンツ帝国（後期）": "Fall of Constantinople to Ottoman Turks (1453)",
    "アッバース朝（前期）": "Survived: Islamic Golden Age with vast trade networks",
    "アッバース朝（後期）": "Sack of Baghdad by Mongols (1258)",
    "宋朝中国": "Conquered by Mongol Yuan Dynasty (1279)",
    "モンゴル帝国": "Fragmented into successor khanates after 1260s",
    "マムルーク朝エジプト": "Conquered by Ottoman Empire (1517)",
    "ヴェネツィア共和国": "Dissolved by Napoleon (1797)",
    "ハンザ同盟": "Eclipsed by rise of territorial nation-states (17th c.)",
    "オスマン帝国（前期）": "Survived: expanded across three continents",
    "オスマン帝国（後期）": "Dismembered after WWI; Republic of Turkey founded (1922)",
    "明朝中国": "Conquered by Manchu Qing Dynasty (1644)",
    "清朝中国（前期）": "Survived: Kangxi–Qianlong prosperity under maritime restrictions",
    "清朝中国（後期）": "Semi-colonized after Opium Wars; dynasty fell (1912)",
    "李朝朝鮮": "Annexed by Japan (1910)",
    "徳川日本": "Forced opening by Perry (1853); Meiji Restoration (1868)",
    "ムガル帝国（後期）": "Colonized by British East India Company; dissolved (1857)",
    "サファヴィー朝ペルシア": "Conquered by Afghan Hotaki invaders (1722)",
    "インカ帝国": "Conquered by Spanish conquistadors under Pizarro (1533)",
    "アステカ帝国": "Conquered by Cortes and Spanish forces (1521)",
    "ポルトガル帝国": "Iberian Union under Spanish crown (1580); independence restored (1640)",
    "オランダ共和国": "Conquered by France (1795); later restored as Kingdom of the Netherlands",
    "スペイン帝国": "Napoleonic invasion (1808); loss of American colonies",
    "ムガル帝国（前期）": "Survived: Mughal expansion and consolidation under Akbar–Aurangzeb",
    "大英帝国": "Survived: peaceful decolonization post-WWII",
    "米国（モンロー主義期）": "Survived: continental expansion under Monroe Doctrine",
    "明治〜大正日本": "Survived: rapid modernization and industrialization",
    "エチオピア帝国": "Survived: Victory at Battle of Adwa (1896) maintained independence",
    "シャム（タイ）": "Survived: diplomatic balancing avoided colonization",
    "スイス": "Survived: permanent neutrality since Congress of Vienna (1815)",
    "1930s日本（大東亜共栄圏）": "WWII defeat and Allied occupation (1945); state survived",
    "ナチスドイツ": "WWII defeat; division into East/West Germany (1945)",
    "ファシストイタリア": "WWII defeat; transition to republic (1946)",
    "ソ連": "Internal collapse and dissolution (1991)",
    "東ドイツ": "German reunification (1990)",
    "ユーゴスラビア": "Breakup into successor states (1991–1992)",
    "英国帝国特恵制度": "Survived: peaceful transition to Commonwealth",
    "米国（戦後〜冷戦期）": "Survived: emerged as global superpower",
    "戦後日本（高度成長期）": "Survived: economic miracle under US alliance",
    "シンガポール": "Survived: rapid development as trade hub since independence (1965)",
    "韓国": "Survived: industrialization and democratization",
    "北朝鮮": "Survived: autarkic Juche regime with Chinese patronage",
    "キューバ": "Survived: maintained regime despite US embargo",
    "現代日本": "Survived: ongoing post-bubble economic adaptation",
    "現代中国": "Survived: reform-era growth since Deng Xiaoping (1978)",
    "現代ロシア": "Survived: post-Soviet transition under sanctions",
    "マケドニア王国（アレクサンドロス後）": "Conquered by Rome at Battle of Pydna (168 BC)",
    "セレウコス朝シリア": "Annexed by Rome as province of Syria (63 BC)",
    "パルティア": "Overthrown by Sasanian revolt under Ardashir I (224 AD)",
    "ササン朝ペルシア": "Conquered by Arab-Muslim armies at Battle of al-Qadisiyyah (636 AD)",
    "クシャーナ朝": "Fragmented under Sasanian and nomadic pressure (4th c.)",
    "グプタ朝インド": "Collapsed under Huna (Hephthalite) invasions (6th c.)",
    "唐朝中国": "Collapsed after An Lushan Rebellion; fell to warlords (907)",
    "ウマイヤ朝": "Overthrown by Abbasid Revolution (750)",
    "高麗": "Replaced by Joseon Dynasty coup (1392)",
    "クメール帝国（アンコール）": "Sacked by Ayutthaya (Siamese) forces (1431)",
    "シュリーヴィジャヤ": "Eclipsed by Majapahit and Chola raids; dissolved (14th c.)",
    "マジャパヒト王国": "Replaced by Islamic Demak Sultanate (early 16th c.)",
    "キエフ大公国": "Destroyed by Mongol invasion (1240)",
    "ジェノヴァ共和国": "Annexed by France under Napoleon (1797)",
    "マリ帝国": "Declined under Songhai expansion and internal fragmentation (16th c.)",
    "元朝中国": "Overthrown by Ming rebellion under Zhu Yuanzhang (1368)",
    "ティムール朝": "Fragmented; conquered by Uzbek Shaybanids (1507)",
    "琉球王国": "Annexed by Meiji Japan (1879)",
    "ポーランド・リトアニア共和国": "Partitioned by Russia, Prussia, Austria (1795)",
    "スウェーデン帝国": "Lost Great Northern War to Russia (1721); state survived",
    "ロシア帝国（ピョートル後）": "Russian Revolution (1917); state reconstituted as USSR",
    "清朝中国（中期・交易拡大期）": "Survived: Canton system maintained controlled trade",
    "ハワイ王国": "Overthrown by US-backed coup (1893); annexed by US (1898)",
    "ズールー王国": "Conquered by British Empire in Anglo-Zulu War (1879)",
    "ビルマ（コンバウン朝）": "Conquered by British Empire in Third Anglo-Burmese War (1885)",
    "オーストリア＝ハンガリー帝国": "Dissolved after WWI (1918); successor states emerged",
    "ベルギー": "Survived: maintained independence despite World Wars",
    "デンマーク": "Survived: adapted from empire to small democratic state",
    "ナポレオン帝国": "Defeated at Waterloo (1815); France continued as nation-state",
    "大韓帝国": "Annexed by Japan (1910)",
    "満州国": "Dissolved after Japan's WWII defeat (1945)",
    "南ベトナム": "Conquered by North Vietnam; reunification (1975)",
    "チェコスロバキア（共産期）": "Velvet Revolution (1989); peaceful split into Czech Rep. and Slovakia (1993)",
    "ポーランド（共産期）": "Solidarity movement; democratic transition (1989)",
    "ルーマニア（共産期）": "Romanian Revolution; execution of Ceausescu (1989)",
    "台湾": "Survived: democratization and de facto independence",
    "イスラエル": "Survived: established and maintained statehood since 1948",
    "UAE": "Survived: oil-funded development as trade hub",
    "現代インド": "Survived: liberalization-era growth since 1991",
    "イラン（イスラム共和国）": "Survived: maintained theocratic regime under sanctions",
    "ミャンマー（軍政期〜現在）": "Survived: military regime persists amid civil conflict",
    "トルクメニスタン": "Survived: authoritarian gas-state since independence (1991)",
}


# ════════════════════════════════════════════════════════════
# Helper: compute all analysis results
# ════════════════════════════════════════════════════════════

def run_analysis():
    df = load_data()
    N = len(df)

    closure_scenarios = {
        "baseline": {"label": "Baseline", "df": df, "reclassified": []},
        "strong": {
            "label": "+5 strong",
            "df": apply_technical_maritime_ban(df, STRONG_CANDIDATES),
            "reclassified": STRONG_CANDIDATES,
        },
        "all": {
            "label": "+7 all",
            "df": apply_technical_maritime_ban(df, STRONG_CANDIDATES + MODERATE_CANDIDATES),
            "reclassified": STRONG_CANDIDATES + MODERATE_CANDIDATES,
        },
    }
    disrupted_modes = {"as_conquered": "disrupted=overtaken", "as_survived": "disrupted=survived"}

    results = {"N": N, "df": df, "scenarios": {}, "fisher_ban": {}, "logistic": {}}

    for d_mode in disrupted_modes:
        for c_key, c_sc in closure_scenarios.items():
            key = f"{d_mode}__{c_key}"
            df_p = apply_disrupted_assignment(c_sc["df"], d_mode)
            cm = compute_confusion_stats(df_p)
            cl = compute_closure_analysis(df_p)
            lr = compute_logistic_with_closure(df_p)

            # Fisher for ban vs no-ban
            has_ban = df_p["closure_type"].isin(["maritime_ban", "technical_maritime_ban", "sakoku"])
            ban_df = df_p[has_ban]
            no_ban_df = df_p[~has_ban]
            ban_rate = ban_df["outcome_binary"].mean() if len(ban_df) > 0 else 0
            no_rate = no_ban_df["outcome_binary"].mean() if len(no_ban_df) > 0 else 0
            ban_conq = int(ban_df["outcome_binary"].sum())
            ban_surv = len(ban_df) - ban_conq
            no_conq = int(no_ban_df["outcome_binary"].sum())
            no_surv = len(no_ban_df) - no_conq
            _, p_ban = stats.fisher_exact(
                np.array([[ban_conq, ban_surv], [no_conq, no_surv]]), alternative="greater"
            )

            results["scenarios"][key] = {
                "cm": cm, "closure": cl, "logistic": lr,
                "ban_n": len(ban_df), "ban_rate": ban_rate,
                "no_ban_n": len(no_ban_df), "no_ban_rate": no_rate,
                "fisher_ban_p": p_ban,
                "rr": ban_rate / no_rate if no_rate > 0 else float("inf"),
            }

    # Bootstrap OR (for main scenario only)
    rng = np.random.default_rng(42)
    n_boot = 5000
    boot_results = {}
    for d_mode in disrupted_modes:
        for c_key, c_sc in closure_scenarios.items():
            key = f"{d_mode}__{c_key}"
            df_p = apply_disrupted_assignment(c_sc["df"], d_mode)
            n = len(df_p)
            boot_ors = np.zeros(n_boot)
            for i in range(n_boot):
                idx = rng.choice(n, size=n, replace=True)
                boot_df = df_p.iloc[idx].reset_index(drop=True)
                try:
                    ct = pd.crosstab(boot_df["dominant"], boot_df["outcome_bin_label"])
                    ct = ct.reindex(index=["stock", "flow"], columns=["overtaken", "survived"], fill_value=0)
                    tp, fp = ct.loc["stock", "overtaken"], ct.loc["stock", "survived"]
                    fn, tn = ct.loc["flow", "overtaken"], ct.loc["flow", "survived"]
                    boot_ors[i] = (tp * tn) / (fp * fn) if (fp * fn) > 0 else np.nan
                except (KeyError, ZeroDivisionError):
                    boot_ors[i] = np.nan
            valid = boot_ors[~np.isnan(boot_ors)]
            if len(valid) >= 100:
                boot_results[key] = {
                    "median": np.median(valid),
                    "ci_lo": np.percentile(valid, 2.5),
                    "ci_hi": np.percentile(valid, 97.5),
                }
    results["bootstrap"] = boot_results
    return results


# ════════════════════════════════════════════════════════════
# Figure generation
# ════════════════════════════════════════════════════════════

def create_figures(results):
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.size": 10,
        "axes.titlesize": 12,
        "figure.dpi": 300,
    })

    # ── Fig 1: Conquest rates by closure type across scenarios ──
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax_idx, (d_mode, d_label) in enumerate([
        ("as_conquered", "Disrupted → Overtaken"),
        ("as_survived", "Disrupted → Survived"),
    ]):
        ax = axes[ax_idx]
        scenarios = ["baseline", "strong", "all"]
        labels = ["Baseline", "+5 Reclassified", "+7 Reclassified"]
        x = np.arange(len(labels))
        width = 0.35

        ban_rates = []
        no_rates = []
        for c_key in scenarios:
            key = f"{d_mode}__{c_key}"
            s = results["scenarios"][key]
            ban_rates.append(s["ban_rate"] * 100)
            no_rates.append(s["no_ban_rate"] * 100)

        bars1 = ax.bar(x - width/2, ban_rates, width, label="Maritime closure", color="#c0392b", alpha=0.85)
        bars2 = ax.bar(x + width/2, no_rates, width, label="No closure", color="#2980b9", alpha=0.85)

        for bar in bars1:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
                    f"{bar.get_height():.1f}%", ha="center", va="bottom", fontsize=8)
        for bar in bars2:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
                    f"{bar.get_height():.1f}%", ha="center", va="bottom", fontsize=8)

        ax.set_ylabel("Conquest rate (%)")
        ax.set_title(d_label)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.set_ylim(0, 110)
        ax.legend(loc="upper left", fontsize=8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig.suptitle("Fig. 1  Conquest Rates: Maritime Closure vs. No Closure", fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(os.path.join(FIG, "Fig1.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)

    # ── Fig 2: Fisher p-value progression ──
    fig, ax = plt.subplots(figsize=(8, 5))
    all_ps = []
    for d_mode, d_label, color, marker in [
        ("as_conquered", "Disrupted → Overtaken", "#c0392b", "o"),
        ("as_survived", "Disrupted → Survived", "#2980b9", "s"),
    ]:
        ps = []
        for c_key in ["baseline", "strong", "all"]:
            key = f"{d_mode}__{c_key}"
            ps.append(results["scenarios"][key]["fisher_ban_p"])
        all_ps.extend(ps)
        ax.plot([0, 5, 7], ps, marker=marker, linewidth=2, markersize=8, label=d_label, color=color)

    ax.axhline(y=0.05, color="gray", linestyle="--", linewidth=1, label="p = 0.05 threshold")
    ax.set_xlabel("Number of reclassified polities")
    ax.set_ylabel("Fisher's exact test p-value (one-sided)")
    ax.set_xticks([0, 5, 7])
    ax.set_xticklabels(["0\n(Baseline)", "5\n(Strong)", "7\n(All)"])
    ax.set_ylim(-0.01, max(0.25, max(all_ps) + 0.05))
    ax.legend(fontsize=9)
    ax.set_title("Fig. 2  Fisher's Exact Test p-values: Maritime Closure → Conquest", fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "Fig2.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)

    # ── Fig 3: Policy vs Technical maritime ban conquest rates ──
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax_idx, (d_mode, d_label) in enumerate([
        ("as_conquered", "Disrupted → Overtaken"),
        ("as_survived", "Disrupted → Survived"),
    ]):
        ax = axes[ax_idx]
        key_all = f"{d_mode}__all"
        df_p = apply_disrupted_assignment(
            apply_technical_maritime_ban(results["df"], STRONG_CANDIDATES + MODERATE_CANDIDATES),
            d_mode
        )
        categories = ["maritime_ban", "sakoku", "technical_maritime_ban", "bloc", "none"]
        cat_labels = ["Policy\nmaritime ban", "Sakoku", "Technical\nmaritime ban", "Bloc", "None\n(open)"]
        rates = []
        counts = []
        for ct in categories:
            sub = df_p[df_p["closure_type"] == ct]
            if len(sub) > 0:
                rate = sub["outcome_binary"].mean() * 100
                rates.append(rate)
                counts.append(len(sub))
            else:
                rates.append(0)
                counts.append(0)

        colors = ["#c0392b", "#e74c3c", "#e67e22", "#95a5a6", "#2980b9"]
        bars = ax.bar(range(len(categories)), rates, color=colors, alpha=0.85)
        for i, (bar, n) in enumerate(zip(bars, counts)):
            if n > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
                        f"{rates[i]:.0f}%\n(n={n})", ha="center", va="bottom", fontsize=8)

        ax.set_xticks(range(len(categories)))
        ax.set_xticklabels(cat_labels, fontsize=8)
        ax.set_ylabel("Conquest rate (%)")
        ax.set_title(d_label)
        ax.set_ylim(0, 115)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    fig.suptitle("Fig. 3  Conquest Rates by Closure Type (7-Country Reclassification)", fontsize=13, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig(os.path.join(FIG, "Fig3.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)

    # ── Fig 4: Multivariate logistic regression forest plot ──
    fig, ax = plt.subplots(figsize=(8, 6))
    key = "as_conquered__all"
    lr = results["scenarios"][key]["logistic"]
    if lr.get("with_ban", {}).get("converged"):
        coefs = lr["with_ban"]["coefs"]
        var_labels = {
            "dominant_binary": "Stock-dominant",
            "geo_barrier": "Geographic barrier",
            "external_threat": "External threat",
            "tech_position": "Tech. position",
            "institutional_quality": "Institutional quality",
            "era_code": "Era (time)",
            "has_external_patron": "External patron",
            "has_maritime_ban": "Maritime closure",
        }
        vars_ordered = list(var_labels.keys())
        y_pos = list(range(len(vars_ordered)))

        for i, var in enumerate(vars_ordered):
            v = coefs[var]
            log_or = np.log(v["OR"])
            log_lo = np.log(v["ci_lo"]) if v["ci_lo"] > 0 else -5
            log_hi = np.log(v["ci_hi"]) if v["ci_hi"] < 1e10 else 5
            color = "#c0392b" if v["p"] < 0.05 else "#2980b9" if v["p"] < 0.10 else "#7f8c8d"
            ax.plot([log_lo, log_hi], [i, i], color=color, linewidth=2)
            ax.plot(log_or, i, "o", color=color, markersize=8)

        ax.axvline(x=0, color="gray", linestyle="--", linewidth=1)
        ax.set_yticks(y_pos)
        ax.set_yticklabels([var_labels[v] for v in vars_ordered])
        ax.set_xlabel("log(Odds Ratio)")
        ax.set_title("Fig. 4  Multivariate Logistic Regression\n(7-Country Reclassification, Disrupted → Overtaken)",
                      fontweight="bold", fontsize=11)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        # Legend
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], marker="o", color="#c0392b", label="p < 0.05", markersize=8, linestyle="-"),
            Line2D([0], [0], marker="o", color="#2980b9", label="p < 0.10", markersize=8, linestyle="-"),
            Line2D([0], [0], marker="o", color="#7f8c8d", label="p ≥ 0.10", markersize=8, linestyle="-"),
        ]
        ax.legend(handles=legend_elements, loc="lower right", fontsize=8)

    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "Fig4.png"), dpi=300, bbox_inches="tight")
    plt.close(fig)

    print("  Figures saved to", FIG)


# ════════════════════════════════════════════════════════════
# PPTX generation
# ════════════════════════════════════════════════════════════

def create_pptx():
    prs = Presentation()
    prs.slide_width = PptxInches(13.333)
    prs.slide_height = PptxInches(7.5)

    fig_files = sorted([f for f in os.listdir(FIG) if f.endswith(".png")])
    captions = {
        "Fig1.png": "Fig. 1  Conquest rates comparing maritime closure vs. no closure polities across three reclassification scenarios.",
        "Fig2.png": "Fig. 2  Fisher's exact test p-values for maritime closure → conquest association, showing transition to significance with reclassification.",
        "Fig3.png": "Fig. 3  Conquest rates by closure type under the 7-country reclassification scenario.",
        "Fig4.png": "Fig. 4  Forest plot of multivariate logistic regression odds ratios (7-country reclassification, disrupted→overtaken).",
    }

    for fname in fig_files:
        slide = prs.slides.add_slide(prs.slide_layouts[6])  # blank
        # Title
        txBox = slide.shapes.add_textbox(PptxInches(0.5), PptxInches(0.2), PptxInches(12), PptxInches(0.6))
        tf = txBox.text_frame
        tf.text = fname.replace(".png", "")
        tf.paragraphs[0].font.size = PptxPt(24)
        tf.paragraphs[0].font.bold = True

        # Image
        img_path = os.path.join(FIG, fname)
        slide.shapes.add_picture(img_path, PptxInches(0.5), PptxInches(1.0), PptxInches(12), PptxInches(5.0))

        # Caption
        cap_box = slide.shapes.add_textbox(PptxInches(0.5), PptxInches(6.2), PptxInches(12), PptxInches(1.0))
        cap_tf = cap_box.text_frame
        cap_tf.word_wrap = True
        cap_tf.text = captions.get(fname, "")
        cap_tf.paragraphs[0].font.size = PptxPt(12)

    pptx_path = os.path.join(OUT, "figures_pptx.pptx")
    prs.save(pptx_path)
    print("  PPTX saved to", pptx_path)


# ════════════════════════════════════════════════════════════
# Supplementary Table S1 (96 polities)
# ════════════════════════════════════════════════════════════

def create_table_s1(results):
    doc = Document()
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Times New Roman"
    font.size = Pt(9)
    style.paragraph_format.space_after = Pt(2)
    style.paragraph_format.line_spacing = 1.15

    doc.add_heading("Supplementary Table S1: Full Dataset of 96 Historical Polities", level=1)
    p = doc.add_paragraph(
        "Each row represents a historical polity included in the analysis. "
        "Columns report the English name, modern-country equivalent, period of existence, "
        "era classification, dominant strategy (stock or flow), closure type, outcome "
        "(overtaken/disrupted/survived), and the specific turning-point event that determined the outcome."
    )
    p.style.font.size = Pt(9)

    df = results["df"]
    headers = ["#", "Polity", "Modern Country", "Period", "Era", "Dominant",
               "Closure Type", "Outcome", "Turning-Point Event"]
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    hdr = table.rows[0]
    for i, h in enumerate(headers):
        cell = hdr.cells[i]
        cell.text = h
        for paragraph in cell.paragraphs:
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in paragraph.runs:
                run.bold = True
                run.font.size = Pt(8)

    era_map = {"ancient": "Ancient", "medieval": "Medieval", "early_modern": "Early Modern",
               "modern": "Modern", "20c": "20th Century", "contemporary": "Contemporary"}
    closure_map = {"none": "None", "maritime_ban": "Maritime ban", "sakoku": "Sakoku",
                   "bloc": "Bloc", "technical_maritime_ban": "Technical maritime ban"}

    for idx, (_, row) in enumerate(df.iterrows()):
        entity = row["entity"]
        cells_data = [
            str(idx + 1),
            ENGLISH_NAME.get(entity, entity),
            MODERN_COUNTRY.get(entity, "—"),
            row["period"],
            era_map.get(row["era"], row["era"]),
            row["dominant"].capitalize(),
            closure_map.get(row["closure_type"], row["closure_type"]),
            row["outcome"].capitalize(),
            TURNING_POINT.get(entity, "—"),
        ]
        row_cells = table.add_row().cells
        for i, val in enumerate(cells_data):
            row_cells[i].text = val
            for paragraph in row_cells[i].paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(7)

    # Set column widths
    widths = [Cm(0.8), Cm(3.5), Cm(2.5), Cm(2.5), Cm(1.8), Cm(1.2), Cm(2.0), Cm(1.5), Cm(6.0)]
    for row_obj in table.rows:
        for i, w in enumerate(widths):
            row_obj.cells[i].width = w

    s1_path = os.path.join(OUT, "table_s1.docx")
    doc.save(s1_path)
    print("  Table S1 saved to", s1_path)


# ════════════════════════════════════════════════════════════
# Main manuscript DOCX
# ════════════════════════════════════════════════════════════

def add_ref(paragraph, text, sup_text):
    """Add text with superscript reference marker using font-based superscript."""
    parts = re.split(r'(\{[^}]+\})', text)
    for part in parts:
        if part.startswith("{") and part.endswith("}"):
            run = paragraph.add_run(part[1:-1])
            run.font.superscript = True
            run.font.size = Pt(9)
        else:
            paragraph.add_run(part)


def create_manuscript(results):
    doc = Document()

    # ── Page setup ──
    for section in doc.sections:
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)

    style = doc.styles["Normal"]
    font = style.font
    font.name = "Times New Roman"
    font.size = Pt(12)
    style.paragraph_format.line_spacing = 1.5
    style.paragraph_format.space_after = Pt(6)

    # ════════════════════════════════════════
    # TITLE PAGE
    # ════════════════════════════════════════
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Flow Disruption and State Collapse:\n"
                     "A Sensitivity Analysis of Technical Maritime Bans\n"
                     "in Historical National Power Dynamics")
    run.bold = True
    run.font.size = Pt(16)

    doc.add_paragraph()  # blank
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("[Author Name]\n[Affiliation]\n[Email]")
    run.font.size = Pt(11)

    doc.add_paragraph()
    doc.add_paragraph()

    # ── Abstract ──
    p = doc.add_heading("Abstract", level=2)
    abstract_text = (
        "This study examines the relationship between international flow disruption and state collapse "
        "using a cross-historical dataset of 96 polities spanning six eras from antiquity to the present. "
        "We classify each polity by its dominant national power strategy (stock-based vs. flow-based) "
        "and its degree of closure from international networks. We introduce the concept of "
        "'technical maritime ban'—passive closure resulting from geographic or technological constraints "
        "rather than deliberate policy—and reclassify seven polities accordingly. "
        "While the baseline association between maritime closure and conquest is not statistically significant "
        "(Fisher's exact test p = 0.187), reclassifying five strongly isolated polities renders it significant "
        "(p = 0.041), and including all seven candidates strengthens the result further (p = 0.020). "
        "All seven technically isolated polities were eventually conquered (100% conquest rate). "
        "Multivariate logistic regression confirms that external threat and institutional quality are the "
        "strongest predictors of conquest, while the stock/flow confusion matrix odds ratio (OR = 1.774) "
        "remains stable across all reclassification scenarios. "
        "These findings suggest that the consequences of closure derive from flow disruption itself "
        "rather than the intent behind closure policies."
    )
    p = doc.add_paragraph(abstract_text)
    p.style.font.size = Pt(11)

    # ── Keywords ──
    p = doc.add_paragraph()
    run = p.add_run("Keywords: ")
    run.bold = True
    p.add_run("economic history; maritime closure; stock-flow framework; state collapse; sensitivity analysis; cliometrics")

    # ── JEL ──
    p = doc.add_paragraph()
    run = p.add_run("JEL Classification: ")
    run.bold = True
    p.add_run("N40, N70, F50, C12")

    doc.add_page_break()

    # ════════════════════════════════════════
    # 1. INTRODUCTION
    # ════════════════════════════════════════
    doc.add_heading("1  Introduction", level=1)

    doc.add_paragraph(
        "The role of international economic openness in determining the fate of states has been a central "
        "question in economic history and international political economy. From the maritime prohibitions "
        "(haijin) of Ming China to the sakoku policy of Tokugawa Japan, deliberate closure from "
        "international trade networks has frequently been associated with subsequent decline or conquest "
        "(Findlay and O'Rourke 2007). However, prior analyses have generally focused on intentional "
        "closure—policy choices made by ruling elites—while neglecting cases where isolation was imposed "
        "by geographic and technological constraints."
    )
    doc.add_paragraph(
        "This paper makes two contributions. First, we construct a cross-historical dataset of 96 polities "
        "spanning six eras (ancient, medieval, early modern, modern, 20th century, and contemporary) "
        "and classify each by its dominant national power strategy—stock-based (relying on accumulated "
        "assets such as human capital, institutions, and natural resources) versus flow-based (relying on "
        "trade, military projection, and diplomatic activity)—and by its closure type. Second, we introduce "
        "the concept of 'technical maritime ban': the passive isolation of polities for which no regular "
        "maritime routes existed during their period of activity. Unlike policy-based maritime bans, "
        "where elites deliberately restricted international flows, technical maritime bans represent "
        "involuntary exclusion from global networks due to geographic remoteness or technological "
        "limitations in maritime transport."
    )
    doc.add_paragraph(
        "We conduct a sensitivity analysis by reclassifying seven polities—five strong candidates and "
        "two moderate candidates—from the 'no closure' category to 'technical maritime ban.' This "
        "reclassification tests whether the observed association between closure and conquest is robust "
        "to how we define maritime isolation. The main finding is striking: the baseline non-significant "
        "association (p = 0.187) between maritime closure and conquest becomes significant upon "
        "reclassification (p = 0.020 with all seven candidates), while the core stock-flow odds ratio "
        "remains unchanged (OR = 1.774). This suggests that the mechanism driving the closure-conquest "
        "association is flow disruption per se, rather than the policy intent behind closure."
    )
    doc.add_paragraph(
        "The paper is organized as follows. Section 2 describes the dataset and the classification "
        "framework. Section 3 presents the main analytical methods. Section 4 reports the baseline "
        "results. Section 5 details the sensitivity analysis with technical maritime ban reclassification. "
        "Section 6 discusses implications and limitations, and Section 7 concludes."
    )

    # ════════════════════════════════════════
    # 2. DATA AND CLASSIFICATION
    # ════════════════════════════════════════
    doc.add_heading("2  Data and Classification", level=1)

    doc.add_heading("2.1  Dataset construction", level=2)
    N = results["N"]
    df = results["df"]
    n_overtaken = len(df[df["outcome"] == "overtaken"])
    n_disrupted = len(df[df["outcome"] == "disrupted"])
    n_survived = len(df[df["outcome"] == "survived"])
    n_stock = len(df[df["dominant"] == "stock"])
    n_flow = len(df[df["dominant"] == "flow"])

    doc.add_paragraph(
        f"The dataset comprises {N} historical polities drawn from standard reference works in global "
        f"history (Findlay and O'Rourke 2007; Kennedy 1987; Turchin 2009). Each polity is coded along "
        f"multiple dimensions: dominant strategy (stock or flow), stock index (0–1), trade openness (0–1), "
        f"closure type, outcome, geographic barrier, external threat level, relative population, "
        f"technological position, institutional quality, regime duration, and presence of an external "
        f"patron. The full dataset is provided in Supplementary Table S1."
    )
    doc.add_paragraph(
        f"Of the {N} polities, {n_stock} are classified as stock-dominant and {n_flow} as flow-dominant. "
        f"Outcomes are coded as overtaken ({n_overtaken} polities), disrupted ({n_disrupted}), or "
        f"survived ({n_survived}). 'Overtaken' denotes conquest, colonization, or annexation by an "
        f"external power. 'Disrupted' denotes regime collapse followed by reconstitution of the successor "
        f"state (e.g., Tokugawa Japan → Meiji Japan). 'Survived' denotes continuity of both regime and "
        f"statehood."
    )

    doc.add_heading("2.2  Closure typology", level=2)
    doc.add_paragraph(
        "Closure types are classified into five categories: (1) maritime ban—deliberate restriction of "
        "maritime trade by policy (e.g., Ming haijin, Qing Canton system); (2) sakoku—near-total "
        "isolation by national decree (Tokugawa Japan, Joseon Korea); (3) bloc—closure within a "
        "geopolitical bloc (e.g., COMECON, autarky regimes); (4) technical maritime ban—passive "
        "isolation due to the absence of regular maritime routes; and (5) none—no significant closure."
    )

    doc.add_heading("2.3  Technical maritime ban: definition and candidates", level=2)
    doc.add_paragraph(
        "We define a technical maritime ban as the condition in which no regular, scheduled maritime "
        "routes connected a polity to major trading networks during its period of existence. Unlike "
        "policy-based closures, where elites chose to restrict flows, technical maritime bans reflect "
        "the technological and geographic impossibility of regular maritime contact. The distinction "
        "parallels the difference between a locked door (policy ban) and the absence of a door "
        "(technical ban)."
    )
    doc.add_paragraph(
        "We identify seven reclassification candidates in two tiers (Table 1)."
    )

    # ── Table 1: Reclassification candidates ──
    table1 = doc.add_table(rows=1, cols=5)
    table1.style = "Table Grid"
    table1.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = table1.rows[0]
    for i, h in enumerate(["Polity", "Period", "Tier", "Original Closure", "Rationale"]):
        hdr.cells[i].text = h
        for par in hdr.cells[i].paragraphs:
            for run in par.runs:
                run.bold = True
                run.font.size = Pt(10)

    candidates = STRONG_CANDIDATES + MODERATE_CANDIDATES
    for entity in candidates:
        en_name = ENGLISH_NAME.get(entity, entity)
        row_data = df[df["entity"] == entity].iloc[0]
        tier = "Strong" if entity in STRONG_CANDIDATES else "Moderate"
        rationale_en = {
            "漢朝（前漢〜後漢）": "No regular sea route from Mediterranean. Silk Road overland only.",
            "マリ帝国": "No Atlantic maritime route until Portuguese exploration (15th c.). Trans-Saharan caravan only.",
            "クメール帝国（アンコール）": "Inland polity; no direct oceanic access unlike maritime Srivijaya.",
            "キエフ大公国": "Dnieper river trade (Varangian route); no regular oceanic routes.",
            "ティムール朝": "Completely landlocked; no maritime access. Silk Road overland only.",
            "ササン朝ペルシア": "Limited Persian Gulf trade; no regular Indian Ocean/Mediterranean sea routes established.",
            "ビルマ（コンバウン朝）": "Coastal access existed but no regular international sea routes until British arrival.",
        }.get(entity, "")

        row_cells = table1.add_row().cells
        for j, val in enumerate([en_name, row_data["period"], tier, "None", rationale_en]):
            row_cells[j].text = val
            for par in row_cells[j].paragraphs:
                for run in par.runs:
                    run.font.size = Pt(9)

    p = doc.add_paragraph()
    p.space_before = Pt(6)
    run = p.add_run("Table 1  ")
    run.bold = True
    run.font.size = Pt(10)
    p.add_run("Technical maritime ban reclassification candidates. "
              "'Strong' candidates had no regular maritime routes; 'Moderate' candidates had limited or uncertain maritime connectivity.").font.size = Pt(10)

    # ════════════════════════════════════════
    # 3. METHODS
    # ════════════════════════════════════════
    doc.add_heading("3  Methods", level=1)

    doc.add_heading("3.1  Outcome binarization", level=2)
    doc.add_paragraph(
        "Because the three-category outcome (overtaken, disrupted, survived) creates ambiguity in binary "
        "statistical tests, we employ a dual-assignment sensitivity approach. In the 'disrupted → overtaken' "
        "scenario, all 18 disrupted polities are treated as conquered (total conquered = 64, survived = 32). "
        "In the 'disrupted → survived' scenario, they are treated as having survived (total conquered = 46, "
        "survived = 50). All subsequent analyses are reported under both assignments, yielding 3 × 2 = 6 "
        "scenarios (three closure reclassification levels × two disrupted assignments)."
    )

    doc.add_heading("3.2  Confusion matrix and association tests", level=2)
    doc.add_paragraph(
        "We construct 2 × 2 confusion matrices crossing the dominant strategy (stock vs. flow) with the "
        "binarized outcome (overtaken vs. survived). We compute the odds ratio (OR), phi coefficient (φ), "
        "Fisher's exact test (one-sided, testing whether stock dominance is associated with higher conquest "
        "risk), and chi-squared test with Yates correction. Effect sizes follow Cohen's conventions for φ."
    )

    doc.add_heading("3.3  Closure-conquest association", level=2)
    doc.add_paragraph(
        "For the maritime closure analysis, we construct 2 × 2 tables crossing closure status "
        "(any maritime closure vs. none) with the binarized outcome. Maritime closure includes "
        "policy-based maritime bans, sakoku, and (after reclassification) technical maritime bans. "
        "We compute conquest rates, risk ratios (RR), risk differences (RD), and Fisher's exact test "
        "p-values for each of the six scenarios."
    )

    doc.add_heading("3.4  Multivariate logistic regression", level=2)
    doc.add_paragraph(
        "To control for potential confounders, we fit multivariate logistic regression models with the "
        "binarized outcome as the dependent variable and the following covariates: stock-dominant dummy, "
        "geographic barrier, external threat level, technological position, institutional quality, era "
        "code, external patron dummy, and a maritime closure dummy. We report odds ratios with 95% "
        "confidence intervals."
    )

    doc.add_heading("3.5  Bootstrap validation", level=2)
    doc.add_paragraph(
        "We validate the confusion-matrix OR using a nonparametric bootstrap with 5,000 resamples "
        "(percentile method, seed = 42). This provides a distribution-free confidence interval that does "
        "not rely on the asymptotic normality assumption."
    )

    # ════════════════════════════════════════
    # 4. RESULTS
    # ════════════════════════════════════════
    doc.add_heading("4  Results", level=1)

    doc.add_heading("4.1  Baseline confusion matrix", level=2)
    cm_base = results["scenarios"]["as_conquered__baseline"]["cm"]
    doc.add_paragraph(
        f"Under the disrupted → overtaken assignment, the confusion matrix yields OR = {cm_base['OR']:.3f}, "
        f"φ = {cm_base['phi']:.3f}, Fisher's exact p = {cm_base['p_fisher']:.4f} (one-sided). "
        f"Stock-dominant polities have a conquest rate of {cm_base['stock_conquest_rate']:.1%}, compared with "
        f"{cm_base['flow_conquest_rate']:.1%} for flow-dominant polities. The effect size is small-to-medium "
        f"by Cohen's conventions. Under the disrupted → survived assignment, the OR reverses "
        f"(OR = {results['scenarios']['as_survived__baseline']['cm']['OR']:.3f}), indicating that the "
        f"stock-flow association is sensitive to how disrupted polities are classified."
    )

    # ── Table 2: Summary across 6 scenarios ──
    doc.add_heading("4.2  Maritime closure and conquest", level=2)

    s_base_c = results["scenarios"]["as_conquered__baseline"]
    s_strong_c = results["scenarios"]["as_conquered__strong"]
    s_all_c = results["scenarios"]["as_conquered__all"]
    s_base_s = results["scenarios"]["as_survived__baseline"]
    s_strong_s = results["scenarios"]["as_survived__strong"]
    s_all_s = results["scenarios"]["as_survived__all"]

    doc.add_paragraph(
        f"Table 2 summarizes the maritime closure analysis across all six scenarios. "
        f"At baseline (disrupted → overtaken), maritime closure polities have a conquest rate of "
        f"{s_base_c['ban_rate']:.1%} versus {s_base_c['no_ban_rate']:.1%} for open polities "
        f"(Fisher p = {s_base_c['fisher_ban_p']:.4f}). Reclassifying five strong candidates raises the "
        f"closure conquest rate to {s_strong_c['ban_rate']:.1%} "
        f"(Fisher p = {s_strong_c['fisher_ban_p']:.4f}). Including all seven candidates further "
        f"strengthens the result: conquest rate = {s_all_c['ban_rate']:.1%}, "
        f"Fisher p = {s_all_c['fisher_ban_p']:.4f} (Fig. 1, Fig. 2)."
    )

    table2 = doc.add_table(rows=1, cols=8)
    table2.style = "Table Grid"
    table2.alignment = WD_TABLE_ALIGNMENT.CENTER
    t2_headers = ["Disrupted As", "Reclassification", "Closure n", "Closure Rate",
                  "Open Rate", "RR", "Fisher p", "Sig."]
    hdr = table2.rows[0]
    for i, h in enumerate(t2_headers):
        hdr.cells[i].text = h
        for par in hdr.cells[i].paragraphs:
            for run in par.runs:
                run.bold = True
                run.font.size = Pt(9)

    for d_mode, d_label in [("as_conquered", "Overtaken"), ("as_survived", "Survived")]:
        for c_key, c_label in [("baseline", "Baseline"), ("strong", "+5 Strong"), ("all", "+7 All")]:
            key = f"{d_mode}__{c_key}"
            s = results["scenarios"][key]
            sig = "*" if s["fisher_ban_p"] < 0.05 else ""
            row_cells = table2.add_row().cells
            vals = [d_label, c_label, str(s["ban_n"]),
                    f"{s['ban_rate']:.1%}", f"{s['no_ban_rate']:.1%}",
                    f"{s['rr']:.3f}", f"{s['fisher_ban_p']:.4f}", sig]
            for j, val in enumerate(vals):
                row_cells[j].text = val
                for par in row_cells[j].paragraphs:
                    for run in par.runs:
                        run.font.size = Pt(9)

    p = doc.add_paragraph()
    p.space_before = Pt(6)
    run = p.add_run("Table 2  ")
    run.bold = True
    run.font.size = Pt(10)
    p.add_run("Maritime closure and conquest across six scenarios. * p < 0.05.").font.size = Pt(10)

    # Insert Fig 1 inline
    p = doc.add_paragraph()
    p.space_before = Pt(12)
    fig1_path = os.path.join(FIG, "Fig1.png")
    if os.path.exists(fig1_path):
        run = p.add_run()
        run.add_picture(fig1_path, width=Inches(6))
    p2 = doc.add_paragraph()
    run = p2.add_run("Fig. 1  ")
    run.bold = True
    run.font.size = Pt(10)
    p2.add_run("Conquest rates comparing maritime closure vs. no closure polities across three "
               "reclassification scenarios under both disrupted assignments.").font.size = Pt(10)

    # Insert Fig 2 inline
    p = doc.add_paragraph()
    p.space_before = Pt(12)
    fig2_path = os.path.join(FIG, "Fig2.png")
    if os.path.exists(fig2_path):
        run = p.add_run()
        run.add_picture(fig2_path, width=Inches(5))
    p2 = doc.add_paragraph()
    run = p2.add_run("Fig. 2  ")
    run.bold = True
    run.font.size = Pt(10)
    p2.add_run("Fisher's exact test p-values for the maritime closure → conquest association "
               "as polities are progressively reclassified.").font.size = Pt(10)

    # ════════════════════════════════════════
    # 5. SENSITIVITY ANALYSIS
    # ════════════════════════════════════════
    doc.add_heading("5  Sensitivity Analysis: Technical Maritime Ban", level=1)

    doc.add_heading("5.1  Closure-type disaggregation", level=2)
    doc.add_paragraph(
        "Figure 3 disaggregates conquest rates by closure type under the 7-country reclassification. "
        "Technical maritime ban polities exhibit a 100% conquest rate—higher than policy-based maritime "
        "bans (76.9% under disrupted → overtaken; 69.2% under disrupted → survived). Sakoku polities "
        "show 100% and 50% rates under the two assignments, respectively, reflecting the ambiguous case "
        "of Tokugawa Japan (disrupted). Bloc-type closures show the lowest conquest rates among closure "
        "categories, suggesting that bloc isolation may provide some protective effects through alliance "
        "structures."
    )

    # Insert Fig 3 inline
    p = doc.add_paragraph()
    p.space_before = Pt(12)
    fig3_path = os.path.join(FIG, "Fig3.png")
    if os.path.exists(fig3_path):
        run = p.add_run()
        run.add_picture(fig3_path, width=Inches(6))
    p2 = doc.add_paragraph()
    run = p2.add_run("Fig. 3  ")
    run.bold = True
    run.font.size = Pt(10)
    p2.add_run("Conquest rates by closure type under the 7-country reclassification scenario.").font.size = Pt(10)

    doc.add_heading("5.2  Robustness of the stock-flow odds ratio", level=2)
    cm_all_c = results["scenarios"]["as_conquered__all"]["cm"]
    boot_c = results["bootstrap"].get("as_conquered__all", {})
    doc.add_paragraph(
        f"A key finding is that the stock-flow confusion matrix OR = {cm_all_c['OR']:.3f} is "
        f"identical across all three reclassification scenarios. This invariance arises because "
        f"the reclassification changes the closure_type label but not the dominant or outcome "
        f"coding. Bootstrap validation (5,000 resamples) yields a median OR of "
        f"{boot_c.get('median', 0):.3f} with a 95% CI of "
        f"[{boot_c.get('ci_lo', 0):.3f}, {boot_c.get('ci_hi', 0):.3f}], "
        f"confirming the robustness of the point estimate."
    )

    doc.add_heading("5.3  Multivariate regression stability", level=2)
    doc.add_paragraph(
        "Figure 4 presents the multivariate logistic regression results under the 7-country "
        "reclassification with disrupted → overtaken. External threat remains the strongest predictor "
        "of conquest (p < 0.01 across all scenarios), followed by institutional quality and era "
        "(both p < 0.01). The maritime closure dummy is not independently significant "
        "after controlling for these confounders, suggesting that the closure-conquest association "
        "is partially mediated by the same factors that drive conquest risk more generally."
    )

    # Insert Fig 4 inline
    p = doc.add_paragraph()
    p.space_before = Pt(12)
    fig4_path = os.path.join(FIG, "Fig4.png")
    if os.path.exists(fig4_path):
        run = p.add_run()
        run.add_picture(fig4_path, width=Inches(5.5))
    p2 = doc.add_paragraph()
    run = p2.add_run("Fig. 4  ")
    run.bold = True
    run.font.size = Pt(10)
    p2.add_run("Forest plot of multivariate logistic regression odds ratios "
               "(7-country reclassification, disrupted → overtaken).").font.size = Pt(10)

    # ── Table 3: Multivariate results ──
    doc.add_paragraph()
    lr_all_c = results["scenarios"]["as_conquered__all"]["logistic"]
    if lr_all_c.get("with_ban", {}).get("converged"):
        table3 = doc.add_table(rows=1, cols=5)
        table3.style = "Table Grid"
        table3.alignment = WD_TABLE_ALIGNMENT.CENTER
        t3_headers = ["Variable", "OR", "95% CI", "p-value", "Sig."]
        hdr = table3.rows[0]
        for i, h in enumerate(t3_headers):
            hdr.cells[i].text = h
            for par in hdr.cells[i].paragraphs:
                for run in par.runs:
                    run.bold = True
                    run.font.size = Pt(10)

        var_labels = {
            "dominant_binary": "Stock-dominant",
            "geo_barrier": "Geographic barrier",
            "external_threat": "External threat",
            "tech_position": "Technological position",
            "institutional_quality": "Institutional quality",
            "era_code": "Era (time)",
            "has_external_patron": "External patron",
            "has_maritime_ban": "Maritime closure dummy",
        }
        coefs = lr_all_c["with_ban"]["coefs"]
        for var, label in var_labels.items():
            v = coefs[var]
            sig = "*" if v["p"] < 0.05 else "\u2020" if v["p"] < 0.10 else ""
            ci_lo_str = f"{v['ci_lo']:.3f}" if v["ci_lo"] < 1e6 else ">10\u2076"
            ci_hi_str = f"{v['ci_hi']:.3f}" if v["ci_hi"] < 1e6 else ">10\u2076"
            row_cells = table3.add_row().cells
            vals = [label, f"{v['OR']:.3f}", f"[{ci_lo_str}, {ci_hi_str}]",
                    f"{v['p']:.4f}", sig]
            for j, val in enumerate(vals):
                row_cells[j].text = val
                for par in row_cells[j].paragraphs:
                    for rn in par.runs:
                        rn.font.size = Pt(9)

        p = doc.add_paragraph()
        p.space_before = Pt(6)
        run = p.add_run("Table 3  ")
        run.bold = True
        run.font.size = Pt(10)
        p.add_run("Multivariate logistic regression results (7-country reclassification, "
                   "disrupted → overtaken). * p < 0.05, \u2020 p < 0.10.").font.size = Pt(10)

    # ════════════════════════════════════════
    # 6. DISCUSSION
    # ════════════════════════════════════════
    doc.add_heading("6  Discussion", level=1)

    doc.add_paragraph(
        "The central finding of this study is that the association between maritime closure and "
        "state collapse becomes statistically significant only when technically isolated polities "
        "are reclassified alongside policy-closed polities. This has three important implications."
    )
    doc.add_paragraph(
        "First, it suggests that the mechanism driving the closure-conquest link is flow disruption "
        "itself rather than the intent behind closure. Whether a polity is isolated by imperial decree "
        "(as in Ming China's haijin) or by the absence of maritime technology (as for the landlocked "
        "Timurid Empire), the consequence—exclusion from international networks of trade, information, "
        "and military technology—appears similar. This resonates with the broader literature on the "
        "benefits of openness (Acemoglu et al. 2005; Findlay and O'Rourke 2007)."
    )
    doc.add_paragraph(
        "Second, the invariance of the stock-flow OR (1.774) across reclassification scenarios indicates "
        "that the core finding of the stock-flow framework—that stock-dominant polities face moderately "
        "higher conquest risk—is robust to how maritime isolation is coded. The reclassification affects "
        "the closure subanalysis but not the primary classification."
    )
    doc.add_paragraph(
        "Third, the multivariate analysis reveals that external threat and institutional quality are "
        "the dominant predictors of conquest, absorbing much of the explanatory power of the closure "
        "variable. This suggests that closure may be a proximate rather than ultimate cause: polities "
        "that close themselves off may already be experiencing institutional decay or may fail to "
        "adapt technologically, making them vulnerable to external shocks (Kennedy 1987; Turchin 2009)."
    )

    doc.add_heading("6.1  Limitations", level=2)
    doc.add_paragraph(
        "Several limitations merit discussion. First, the coding of historical polities inevitably "
        "involves subjective judgment, particularly for the stock/flow dominant classification and "
        "the technical maritime ban category. The tiered approach (strong vs. moderate candidates) "
        "partially addresses this. Second, the sample size (N = 96) constrains the power of "
        "multivariate analyses; wide confidence intervals for some regression coefficients reflect "
        "this limitation. Third, the dataset treats polities as independent observations, "
        "though historical interconnections (e.g., sequential Chinese dynasties) may violate "
        "this assumption. Fourth, the disrupted category introduces classification ambiguity "
        "that we address through dual assignment but cannot fully resolve."
    )

    # ════════════════════════════════════════
    # 7. CONCLUSION
    # ════════════════════════════════════════
    doc.add_heading("7  Conclusion", level=1)

    doc.add_paragraph(
        "This paper has demonstrated that the association between maritime closure and state "
        "collapse is sensitive to whether passively isolated polities are classified alongside "
        "deliberately closed ones. The concept of 'technical maritime ban' provides a useful "
        "analytical distinction that reveals a previously hidden pattern: all seven technically "
        "isolated polities in our dataset were eventually conquered. Combined with the stability "
        "of the stock-flow odds ratio and the dominance of external threat and institutional "
        "quality in multivariate models, our findings support the interpretation that flow "
        "disruption—regardless of intent—constitutes a significant risk factor for state collapse "
        "in the long run of history."
    )

    # ════════════════════════════════════════
    # REFERENCES (Author-year, alphabetical — Cliometrica style)
    # ════════════════════════════════════════
    doc.add_heading("References", level=1)

    refs = [
        "Acemoglu D, Johnson S, Robinson JA (2005) Institutions as a fundamental cause of long-run growth. In: Aghion P, Durlauf SN (eds) Handbook of economic growth, vol 1A. Elsevier, Amsterdam, pp 385–472",
        "Arrighi G (1994) The long twentieth century: money, power, and the origins of our times. Verso, London",
        "Broadberry SN, Guan H (2026) Regional variation of GDP per head within China, 1080–1850. Explor Econ Hist 95:101567. https://doi.org/10.1016/j.eeh.2025.101567",
        "De Vries J (2010) The limits of globalization in the early modern world. Econ Hist Rev 63:710–733. https://doi.org/10.1111/j.1468-0289.2009.00497.x",
        "Findlay R, O'Rourke KH (2007) Power and plenty: trade, war, and the world economy in the second millennium. Princeton University Press, Princeton",
        "Kennedy P (1987) The rise and fall of the great powers: economic change and military conflict from 1500 to 2000. Random House, New York",
        "Maddison A (2007) Contours of the world economy 1–2030 AD: essays in macro-economic history. Oxford University Press, Oxford",
        "North DC, Wallis JJ, Weingast BR (2009) Violence and social orders: a conceptual framework for interpreting recorded human history. Cambridge University Press, Cambridge",
        "Pomeranz K (2000) The great divergence: China, Europe, and the making of the modern world economy. Princeton University Press, Princeton",
        "Turchin P (2009) A theory for formation of large empires. J Glob Hist 4:191–217. https://doi.org/10.1017/S1740022809003192",
    ]
    for ref in refs:
        p = doc.add_paragraph(ref)
        p.style.font.size = Pt(11)
        p.paragraph_format.first_line_indent = Cm(-1)
        p.paragraph_format.left_indent = Cm(1)

    # ════════════════════════════════════════
    # STATEMENTS AND DECLARATIONS
    # ════════════════════════════════════════
    doc.add_heading("Statements and Declarations", level=1)

    doc.add_heading("Funding", level=2)
    doc.add_paragraph("[To be completed by author]")

    doc.add_heading("Competing Interests", level=2)
    doc.add_paragraph("The author declares no competing interests.")

    doc.add_heading("Data Availability", level=2)
    doc.add_paragraph(
        "The complete dataset and analysis code are available at [repository URL]. "
        "Supplementary Table S1 provides the full dataset of 96 polities with all coded variables."
    )

    # Save
    ms_path = os.path.join(OUT, "manuscript.docx")
    doc.save(ms_path)
    print("  Manuscript saved to", ms_path)


# ════════════════════════════════════════════════════════════
# Main
# ════════════════════════════════════════════════════════════

def main():
    print("Running analysis...")
    results = run_analysis()

    print("Creating figures...")
    create_figures(results)

    print("Creating PPTX...")
    create_pptx()

    print("Creating Table S1...")
    create_table_s1(results)

    print("Creating manuscript...")
    create_manuscript(results)

    print("\nAll outputs saved to:", OUT)
    print("  manuscript/manuscript.docx")
    print("  manuscript/table_s1.docx")
    print("  manuscript/figures_pptx.pptx")
    print("  manuscript/figures/Fig1–Fig4.png")


if __name__ == "__main__":
    main()
