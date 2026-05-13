"""
Beyond GDP: Stock vs Flow National Power Analysis
拡張データセット — 交絡因子・広義ストック概念を含む

ストック概念（広義）:
  人的資本、都市鉱山・リサイクル資源、社会関係資本、制度資本、
  インフラ資本、文化資本、自然資本、技術蓄積、金融資本

フロー概念:
  貿易、軍事行動、外交活動、海外投資、移民、技術移転、文化輸出
"""

import pandas as pd

# fmt: off
records = [
    # ── 古代 ──────────────────────────────────────────────
    {
        "entity": "アケメネス朝ペルシア",
        "period": "BC550-BC330",
        "era": "ancient",
        "region": "middle_east",
        "dominant": "flow",          # 征服＋交易路整備、サトラップ制の通商促進
        "stock_index": 0.40,         # 自然資本◎、制度資本○、人的資本△
        "trade_openness": 0.70,      # 王の道、交易路開放
        "closure_type": "none",
        "outcome": "conquered",      # アレクサンドロスに征服
        "geo_barrier": 0.4,          # 平原が多い、防御困難
        "external_threat": 0.8,      # ギリシア・マケドニアの軍事革新
        "relative_pop": 0.9,         # 当時最大の人口
        "tech_position": 0.5,        # ギリシアに比べ軍事技術で劣位
        "institutional_quality": 0.6,
        "regime_duration_yrs": 220,
        "has_external_patron": 0,
    },
    {
        "entity": "アテネ（ペロポネソス戦争後）",
        "period": "BC404-BC338",
        "era": "ancient",
        "region": "europe",
        "dominant": "flow",
        "stock_index": 0.45,
        "trade_openness": 0.80,
        "closure_type": "none",
        "outcome": "conquered",      # マケドニアに征服
        "geo_barrier": 0.5,          # 海洋防御あるが半島は開放的
        "external_threat": 0.8,
        "relative_pop": 0.2,
        "tech_position": 0.6,
        "institutional_quality": 0.7,
        "regime_duration_yrs": 66,
        "has_external_patron": 0,
    },
    {
        "entity": "スパルタ",
        "period": "BC800-BC146",
        "era": "ancient",
        "region": "europe",
        "dominant": "stock",          # 閉鎖的軍事国家、外国人制限、通商忌避
        "stock_index": 0.65,          # 人的資本(軍事特化)◎、制度◎、自然資本△
        "trade_openness": 0.15,
        "closure_type": "maritime_ban",
        "outcome": "conquered",       # ローマに征服
        "geo_barrier": 0.5,
        "external_threat": 0.7,
        "relative_pop": 0.1,
        "tech_position": 0.4,
        "institutional_quality": 0.7,
        "regime_duration_yrs": 654,
        "has_external_patron": 0,
    },
    {
        "entity": "カルタゴ",
        "period": "BC814-BC146",
        "era": "ancient",
        "region": "africa",
        "dominant": "flow",
        "stock_index": 0.35,
        "trade_openness": 0.90,
        "closure_type": "none",
        "outcome": "conquered",
        "geo_barrier": 0.5,
        "external_threat": 0.9,
        "relative_pop": 0.3,
        "tech_position": 0.6,
        "institutional_quality": 0.5,
        "regime_duration_yrs": 668,
        "has_external_patron": 0,
    },
    {
        "entity": "ローマ共和政〜帝政前期",
        "period": "BC509-AD200",
        "era": "ancient",
        "region": "europe",
        "dominant": "flow",           # 征服＋交易路整備、地中海統合
        "stock_index": 0.55,          # インフラ◎、制度◎、人的資本○
        "trade_openness": 0.75,
        "closure_type": "none",
        "outcome": "survived",        # この時代は存続・繁栄
        "geo_barrier": 0.4,
        "external_threat": 0.4,
        "relative_pop": 0.9,
        "tech_position": 0.8,
        "institutional_quality": 0.8,
        "regime_duration_yrs": 709,
        "has_external_patron": 0,
    },
    {
        "entity": "ローマ帝政後期（西）",
        "period": "AD200-AD476",
        "era": "ancient",
        "region": "europe",
        "dominant": "stock",           # リメス防衛線、内向き化
        "stock_index": 0.60,           # インフラ蓄積あるが減耗中
        "trade_openness": 0.35,
        "closure_type": "maritime_ban",
        "outcome": "conquered",
        "geo_barrier": 0.3,
        "external_threat": 0.9,
        "relative_pop": 0.5,
        "tech_position": 0.5,
        "institutional_quality": 0.4,
        "regime_duration_yrs": 276,
        "has_external_patron": 0,
    },
    {
        "entity": "プトレマイオス朝エジプト",
        "period": "BC305-BC30",
        "era": "ancient",
        "region": "africa",
        "dominant": "flow",            # アレクサンドリア交易
        "stock_index": 0.55,           # 農業◎、文化◎
        "trade_openness": 0.70,
        "closure_type": "none",
        "outcome": "conquered",        # ローマに征服
        "geo_barrier": 0.6,            # 砂漠に囲まれるが海側開放
        "external_threat": 0.8,
        "relative_pop": 0.4,
        "tech_position": 0.6,
        "institutional_quality": 0.5,
        "regime_duration_yrs": 275,
        "has_external_patron": 0,
    },
    {
        "entity": "漢朝（前漢〜後漢）",
        "period": "BC206-AD220",
        "era": "ancient",
        "region": "east_asia",
        "dominant": "flow",            # シルクロード交易
        "stock_index": 0.65,           # 人的◎、制度◎、農業◎
        "trade_openness": 0.55,
        "closure_type": "none",
        "outcome": "conquered",        # 内乱→三国分裂（体制崩壊）
        "geo_barrier": 0.6,
        "external_threat": 0.5,
        "relative_pop": 0.95,
        "tech_position": 0.8,
        "institutional_quality": 0.7,
        "regime_duration_yrs": 426,
        "has_external_patron": 0,
    },
    # ── 中世 ──────────────────────────────────────────────
    {
        "entity": "ビザンツ帝国（前期）",
        "period": "AD330-AD1000",
        "era": "medieval",
        "region": "europe",
        "dominant": "flow",             # 東西交易の要衝
        "stock_index": 0.65,
        "trade_openness": 0.65,
        "closure_type": "none",
        "outcome": "survived",
        "geo_barrier": 0.7,             # 三方海、テオドシウス城壁
        "external_threat": 0.7,
        "relative_pop": 0.4,
        "tech_position": 0.8,           # ギリシア火
        "institutional_quality": 0.8,
        "regime_duration_yrs": 670,
        "has_external_patron": 0,
    },
    {
        "entity": "ビザンツ帝国（後期）",
        "period": "AD1000-AD1453",
        "era": "medieval",
        "region": "europe",
        "dominant": "stock",             # 縮小・内向き化
        "stock_index": 0.55,
        "trade_openness": 0.30,
        "closure_type": "maritime_ban",
        "outcome": "conquered",          # オスマンに征服
        "geo_barrier": 0.7,
        "external_threat": 0.9,
        "relative_pop": 0.1,
        "tech_position": 0.4,
        "institutional_quality": 0.4,
        "regime_duration_yrs": 453,
        "has_external_patron": 0,
    },
    {
        "entity": "アッバース朝（前期）",
        "period": "AD750-AD1000",
        "era": "medieval",
        "region": "middle_east",
        "dominant": "flow",
        "stock_index": 0.60,
        "trade_openness": 0.80,
        "closure_type": "none",
        "outcome": "survived",
        "geo_barrier": 0.3,
        "external_threat": 0.5,
        "relative_pop": 0.7,
        "tech_position": 0.9,           # イスラム黄金時代
        "institutional_quality": 0.7,
        "regime_duration_yrs": 250,
        "has_external_patron": 0,
    },
    {
        "entity": "アッバース朝（後期）",
        "period": "AD1000-AD1258",
        "era": "medieval",
        "region": "middle_east",
        "dominant": "stock",
        "stock_index": 0.50,
        "trade_openness": 0.35,
        "closure_type": "none",
        "outcome": "conquered",           # モンゴルに征服
        "geo_barrier": 0.3,
        "external_threat": 0.95,
        "relative_pop": 0.3,
        "tech_position": 0.5,
        "institutional_quality": 0.3,
        "regime_duration_yrs": 258,
        "has_external_patron": 0,
    },
    {
        "entity": "宋朝中国",
        "period": "AD960-AD1279",
        "era": "medieval",
        "region": "east_asia",
        "dominant": "stock",              # 経済フローはあるが軍事的に閉鎖・内向き
        "stock_index": 0.75,              # 人的◎、技術◎、制度◎、文化◎
        "trade_openness": 0.60,           # 海上交易は活発
        "closure_type": "none",
        "outcome": "conquered",           # モンゴルに征服
        "geo_barrier": 0.4,
        "external_threat": 0.95,
        "relative_pop": 0.8,
        "tech_position": 0.85,            # 火薬、羅針盤、印刷術
        "institutional_quality": 0.7,
        "regime_duration_yrs": 319,
        "has_external_patron": 0,
    },
    {
        "entity": "モンゴル帝国",
        "period": "AD1206-AD1368",
        "era": "medieval",
        "region": "central_asia",
        "dominant": "flow",                # 征服→交易路開放（パクスモンゴリカ）
        "stock_index": 0.20,
        "trade_openness": 0.85,
        "closure_type": "none",
        "outcome": "conquered",            # 分裂・崩壊
        "geo_barrier": 0.1,
        "external_threat": 0.3,
        "relative_pop": 0.15,
        "tech_position": 0.6,
        "institutional_quality": 0.3,
        "regime_duration_yrs": 162,
        "has_external_patron": 0,
    },
    {
        "entity": "マムルーク朝エジプト",
        "period": "AD1250-AD1517",
        "era": "medieval",
        "region": "middle_east",
        "dominant": "flow",                # 東西交易の中継
        "stock_index": 0.50,
        "trade_openness": 0.65,
        "closure_type": "none",
        "outcome": "conquered",            # オスマンに征服
        "geo_barrier": 0.5,
        "external_threat": 0.8,
        "relative_pop": 0.3,
        "tech_position": 0.4,              # 火器導入で遅れ
        "institutional_quality": 0.4,
        "regime_duration_yrs": 267,
        "has_external_patron": 0,
    },
    {
        "entity": "ヴェネツィア共和国",
        "period": "AD697-AD1797",
        "era": "medieval",
        "region": "europe",
        "dominant": "flow",
        "stock_index": 0.40,
        "trade_openness": 0.95,
        "closure_type": "none",
        "outcome": "conquered",
        "geo_barrier": 0.7,               # 潟の上
        "external_threat": 0.7,
        "relative_pop": 0.05,
        "tech_position": 0.7,
        "institutional_quality": 0.8,
        "regime_duration_yrs": 1100,
        "has_external_patron": 0,
    },
    {
        "entity": "ハンザ同盟",
        "period": "AD1200-AD1669",
        "era": "medieval",
        "region": "europe",
        "dominant": "flow",
        "stock_index": 0.30,
        "trade_openness": 0.90,
        "closure_type": "none",
        "outcome": "conquered",            # 領域国家に吸収
        "geo_barrier": 0.2,
        "external_threat": 0.6,
        "relative_pop": 0.1,
        "tech_position": 0.6,
        "institutional_quality": 0.5,
        "regime_duration_yrs": 469,
        "has_external_patron": 0,
    },
    # ── 近世 ──────────────────────────────────────────────
    {
        "entity": "オスマン帝国（前期）",
        "period": "AD1300-AD1600",
        "era": "early_modern",
        "region": "middle_east",
        "dominant": "flow",                # 征服＋東西交易
        "stock_index": 0.50,
        "trade_openness": 0.65,
        "closure_type": "none",
        "outcome": "survived",
        "geo_barrier": 0.5,
        "external_threat": 0.5,
        "relative_pop": 0.6,
        "tech_position": 0.8,
        "institutional_quality": 0.7,
        "regime_duration_yrs": 300,
        "has_external_patron": 0,
    },
    {
        "entity": "オスマン帝国（後期）",
        "period": "AD1600-AD1922",
        "era": "early_modern",
        "region": "middle_east",
        "dominant": "stock",               # 保護主義化・内向き
        "stock_index": 0.55,
        "trade_openness": 0.30,
        "closure_type": "maritime_ban",
        "outcome": "conquered",            # WWI後分割
        "geo_barrier": 0.4,
        "external_threat": 0.9,
        "relative_pop": 0.3,
        "tech_position": 0.3,
        "institutional_quality": 0.3,
        "regime_duration_yrs": 322,
        "has_external_patron": 0,
    },
    {
        "entity": "明朝中国",
        "period": "AD1368-AD1644",
        "era": "early_modern",
        "region": "east_asia",
        "dominant": "stock",
        "stock_index": 0.80,              # 人的◎、農業◎、制度◎、文化◎、インフラ◎
        "trade_openness": 0.15,
        "closure_type": "maritime_ban",    # 海禁令
        "outcome": "conquered",            # 満州族に征服
        "geo_barrier": 0.6,
        "external_threat": 0.7,
        "relative_pop": 0.95,
        "tech_position": 0.5,              # 停滞
        "institutional_quality": 0.6,
        "regime_duration_yrs": 276,
        "has_external_patron": 0,
    },
    {
        "entity": "清朝中国（前期）",
        "period": "AD1644-AD1800",
        "era": "early_modern",
        "region": "east_asia",
        "dominant": "stock",
        "stock_index": 0.85,
        "trade_openness": 0.20,
        "closure_type": "maritime_ban",     # 遷界令→広州一港制限
        "outcome": "survived",
        "geo_barrier": 0.6,
        "external_threat": 0.3,             # 外圧未到達
        "relative_pop": 0.95,
        "tech_position": 0.5,
        "institutional_quality": 0.7,
        "regime_duration_yrs": 156,
        "has_external_patron": 0,
    },
    {
        "entity": "清朝中国（後期）",
        "period": "AD1800-AD1912",
        "era": "modern",
        "region": "east_asia",
        "dominant": "stock",
        "stock_index": 0.70,               # 減耗中だが依然巨大（人的資本、農業、文化）
        "trade_openness": 0.25,
        "closure_type": "maritime_ban",
        "outcome": "conquered",             # 半植民地化
        "geo_barrier": 0.5,
        "external_threat": 0.9,
        "relative_pop": 0.90,
        "tech_position": 0.2,
        "institutional_quality": 0.3,
        "regime_duration_yrs": 112,
        "has_external_patron": 0,
    },
    {
        "entity": "李朝朝鮮",
        "period": "AD1392-AD1897",
        "era": "early_modern",
        "region": "east_asia",
        "dominant": "stock",
        "stock_index": 0.55,               # 制度◎(儒教)、農業○、人的資本△
        "trade_openness": 0.10,
        "closure_type": "sakoku",           # 隠者の国
        "outcome": "conquered",             # 日本に併合
        "geo_barrier": 0.5,                 # 半島
        "external_threat": 0.8,
        "relative_pop": 0.2,
        "tech_position": 0.3,
        "institutional_quality": 0.5,
        "regime_duration_yrs": 505,
        "has_external_patron": 0,
    },
    {
        "entity": "徳川日本",
        "period": "AD1603-AD1868",
        "era": "early_modern",
        "region": "east_asia",
        "dominant": "stock",
        "stock_index": 0.65,               # 人的◎(識字率高)、制度◎、文化◎、インフラ○
        "trade_openness": 0.05,
        "closure_type": "sakoku",
        "outcome": "conquered",             # 強制開国→幕府崩壊
        "geo_barrier": 0.8,                 # 島国
        "external_threat": 0.7,
        "relative_pop": 0.3,
        "tech_position": 0.3,
        "institutional_quality": 0.7,
        "regime_duration_yrs": 265,
        "has_external_patron": 0,
    },
    {
        "entity": "ムガル帝国（後期）",
        "period": "AD1700-AD1857",
        "era": "early_modern",
        "region": "south_asia",
        "dominant": "stock",
        "stock_index": 0.60,
        "trade_openness": 0.30,
        "closure_type": "none",
        "outcome": "conquered",             # 英国に植民地化
        "geo_barrier": 0.5,
        "external_threat": 0.9,
        "relative_pop": 0.8,
        "tech_position": 0.3,
        "institutional_quality": 0.3,
        "regime_duration_yrs": 157,
        "has_external_patron": 0,
    },
    {
        "entity": "サファヴィー朝ペルシア",
        "period": "AD1501-AD1736",
        "era": "early_modern",
        "region": "middle_east",
        "dominant": "stock",
        "stock_index": 0.55,
        "trade_openness": 0.35,
        "closure_type": "none",
        "outcome": "conquered",              # アフガン人に征服
        "geo_barrier": 0.5,
        "external_threat": 0.7,
        "relative_pop": 0.3,
        "tech_position": 0.5,
        "institutional_quality": 0.4,
        "regime_duration_yrs": 235,
        "has_external_patron": 0,
    },
    {
        "entity": "インカ帝国",
        "period": "AD1438-AD1533",
        "era": "early_modern",
        "region": "americas",
        "dominant": "stock",
        "stock_index": 0.55,                # インフラ◎(道路網)、農業◎、制度○
        "trade_openness": 0.05,
        "closure_type": "maritime_ban",       # 自給自足閉鎖経済
        "outcome": "conquered",
        "geo_barrier": 0.7,                  # 山岳
        "external_threat": 0.9,              # テクノロジーギャップ
        "relative_pop": 0.3,
        "tech_position": 0.1,
        "institutional_quality": 0.5,
        "regime_duration_yrs": 95,
        "has_external_patron": 0,
    },
    {
        "entity": "アステカ帝国",
        "period": "AD1428-AD1521",
        "era": "early_modern",
        "region": "americas",
        "dominant": "stock",
        "stock_index": 0.50,
        "trade_openness": 0.10,
        "closure_type": "maritime_ban",
        "outcome": "conquered",
        "geo_barrier": 0.4,
        "external_threat": 0.9,
        "relative_pop": 0.3,
        "tech_position": 0.1,
        "institutional_quality": 0.4,
        "regime_duration_yrs": 93,
        "has_external_patron": 0,
    },
    {
        "entity": "ポルトガル帝国",
        "period": "AD1415-AD1580",
        "era": "early_modern",
        "region": "europe",
        "dominant": "flow",
        "stock_index": 0.30,
        "trade_openness": 0.90,
        "closure_type": "none",
        "outcome": "conquered",              # スペイン同君連合
        "geo_barrier": 0.5,
        "external_threat": 0.7,
        "relative_pop": 0.05,
        "tech_position": 0.8,
        "institutional_quality": 0.5,
        "regime_duration_yrs": 165,
        "has_external_patron": 0,
    },
    {
        "entity": "オランダ共和国",
        "period": "AD1581-AD1795",
        "era": "early_modern",
        "region": "europe",
        "dominant": "flow",
        "stock_index": 0.35,
        "trade_openness": 0.95,
        "closure_type": "none",
        "outcome": "conquered",               # フランスに征服
        "geo_barrier": 0.3,
        "external_threat": 0.8,
        "relative_pop": 0.05,
        "tech_position": 0.8,
        "institutional_quality": 0.8,
        "regime_duration_yrs": 214,
        "has_external_patron": 0,
    },
    {
        "entity": "スペイン帝国",
        "period": "AD1492-AD1808",
        "era": "early_modern",
        "region": "europe",
        "dominant": "flow",                    # 新大陸からの金銀フロー
        "stock_index": 0.40,                   # フロー→ストック変換に失敗
        "trade_openness": 0.60,                # 重商主義だが交易は活発
        "closure_type": "none",
        "outcome": "conquered",                # ナポレオンに征服→帝国崩壊
        "geo_barrier": 0.6,
        "external_threat": 0.7,
        "relative_pop": 0.2,
        "tech_position": 0.5,
        "institutional_quality": 0.4,
        "regime_duration_yrs": 316,
        "has_external_patron": 0,
    },
    {
        "entity": "ムガル帝国（前期）",
        "period": "AD1526-AD1700",
        "era": "early_modern",
        "region": "south_asia",
        "dominant": "flow",                    # 征服＋交易開放
        "stock_index": 0.55,
        "trade_openness": 0.60,
        "closure_type": "none",
        "outcome": "survived",
        "geo_barrier": 0.5,
        "external_threat": 0.4,
        "relative_pop": 0.8,
        "tech_position": 0.6,
        "institutional_quality": 0.6,
        "regime_duration_yrs": 174,
        "has_external_patron": 0,
    },
    # ── 近代 (19C) ──────────────────────────────────────────
    {
        "entity": "大英帝国",
        "period": "AD1815-AD1945",
        "era": "modern",
        "region": "europe",
        "dominant": "flow",
        "stock_index": 0.65,                   # 制度◎、技術◎、インフラ◎、人的◎
        "trade_openness": 0.85,
        "closure_type": "none",
        "outcome": "survived",                 # 平和的脱植民地化
        "geo_barrier": 0.8,                    # 島国＋海軍
        "external_threat": 0.6,
        "relative_pop": 0.3,
        "tech_position": 0.9,
        "institutional_quality": 0.9,
        "regime_duration_yrs": 130,
        "has_external_patron": 0,
    },
    {
        "entity": "米国（モンロー主義期）",
        "period": "AD1823-AD1898",
        "era": "modern",
        "region": "americas",
        "dominant": "stock",                    # 大陸資源＋モンロー主義（閉鎖的）
        "stock_index": 0.80,                    # 自然◎、土地◎、人的○
        "trade_openness": 0.30,
        "closure_type": "bloc",                 # 西半球閉鎖＝ブロック的
        "outcome": "survived",
        "geo_barrier": 0.9,                     # 大西洋＋太平洋
        "external_threat": 0.2,
        "relative_pop": 0.4,
        "tech_position": 0.7,
        "institutional_quality": 0.8,
        "regime_duration_yrs": 75,
        "has_external_patron": 0,
    },
    {
        "entity": "明治〜大正日本",
        "period": "AD1868-AD1930",
        "era": "modern",
        "region": "east_asia",
        "dominant": "flow",                     # 開国→貿易立国→海外膨張
        "stock_index": 0.55,                    # 人的◎(識字率)、制度○、文化◎
        "trade_openness": 0.65,
        "closure_type": "none",
        "outcome": "survived",
        "geo_barrier": 0.8,
        "external_threat": 0.5,
        "relative_pop": 0.4,
        "tech_position": 0.7,
        "institutional_quality": 0.7,
        "regime_duration_yrs": 62,
        "has_external_patron": 0,
    },
    {
        "entity": "エチオピア帝国",
        "period": "AD1855-AD1936",
        "era": "modern",
        "region": "africa",
        "dominant": "stock",
        "stock_index": 0.40,
        "trade_openness": 0.15,
        "closure_type": "maritime_ban",
        "outcome": "survived",                  # アドワの戦い勝利→独立維持（1936年まで）
        "geo_barrier": 0.8,                     # 高原
        "external_threat": 0.6,
        "relative_pop": 0.2,
        "tech_position": 0.2,
        "institutional_quality": 0.4,
        "regime_duration_yrs": 81,
        "has_external_patron": 0,
    },
    {
        "entity": "シャム（タイ）",
        "period": "AD1782-AD1932",
        "era": "modern",
        "region": "southeast_asia",
        "dominant": "flow",                     # ボウリング条約→自由貿易・外交的バランス
        "stock_index": 0.45,
        "trade_openness": 0.60,
        "closure_type": "none",
        "outcome": "survived",                  # 植民地化を回避
        "geo_barrier": 0.3,
        "external_threat": 0.7,
        "relative_pop": 0.2,
        "tech_position": 0.4,
        "institutional_quality": 0.5,
        "regime_duration_yrs": 150,
        "has_external_patron": 0,
    },
    {
        "entity": "スイス",
        "period": "AD1815-AD現在",
        "era": "modern",
        "region": "europe",
        "dominant": "stock",
        "stock_index": 0.75,                   # 金融◎、人的◎、制度◎、インフラ◎
        "trade_openness": 0.40,                # 中立→やや閉鎖的
        "closure_type": "bloc",                # 永世中立＝実質的閉鎖
        "outcome": "survived",
        "geo_barrier": 0.9,                    # アルプス
        "external_threat": 0.5,
        "relative_pop": 0.05,
        "tech_position": 0.8,
        "institutional_quality": 0.9,
        "regime_duration_yrs": 210,
        "has_external_patron": 0,
    },
    # ── 20世紀 ──────────────────────────────────────────────
    {
        "entity": "1930s日本（大東亜共栄圏）",
        "period": "AD1930-AD1945",
        "era": "20c",
        "region": "east_asia",
        "dominant": "stock",
        "stock_index": 0.60,                   # 人的◎、制度○、技術蓄積○、都市鉱山×
        "trade_openness": 0.20,
        "closure_type": "bloc",
        "outcome": "conquered",
        "geo_barrier": 0.7,
        "external_threat": 0.9,
        "relative_pop": 0.3,
        "tech_position": 0.6,
        "institutional_quality": 0.5,
        "regime_duration_yrs": 15,
        "has_external_patron": 0,
    },
    {
        "entity": "ナチスドイツ",
        "period": "AD1933-AD1945",
        "era": "20c",
        "region": "europe",
        "dominant": "stock",
        "stock_index": 0.70,                   # 技術◎、人的◎、インフラ◎
        "trade_openness": 0.15,
        "closure_type": "bloc",                # アウタルキー
        "outcome": "conquered",
        "geo_barrier": 0.2,                    # 平原に囲まれる
        "external_threat": 0.9,
        "relative_pop": 0.3,
        "tech_position": 0.9,
        "institutional_quality": 0.4,
        "regime_duration_yrs": 12,
        "has_external_patron": 0,
    },
    {
        "entity": "ファシストイタリア",
        "period": "AD1922-AD1943",
        "era": "20c",
        "region": "europe",
        "dominant": "stock",
        "stock_index": 0.50,
        "trade_openness": 0.20,
        "closure_type": "bloc",
        "outcome": "conquered",
        "geo_barrier": 0.5,
        "external_threat": 0.8,
        "relative_pop": 0.2,
        "tech_position": 0.5,
        "institutional_quality": 0.3,
        "regime_duration_yrs": 21,
        "has_external_patron": 0,
    },
    {
        "entity": "ソ連",
        "period": "AD1922-AD1991",
        "era": "20c",
        "region": "europe",
        "dominant": "stock",
        "stock_index": 0.75,                   # 自然◎、人的○、技術○、インフラ○、軍事◎
        "trade_openness": 0.10,
        "closure_type": "bloc",                # COMECON
        "outcome": "conquered",                # 体制崩壊
        "geo_barrier": 0.6,
        "external_threat": 0.8,
        "relative_pop": 0.6,
        "tech_position": 0.7,
        "institutional_quality": 0.4,
        "regime_duration_yrs": 69,
        "has_external_patron": 0,
    },
    {
        "entity": "東ドイツ",
        "period": "AD1949-AD1990",
        "era": "20c",
        "region": "europe",
        "dominant": "stock",
        "stock_index": 0.55,
        "trade_openness": 0.15,
        "closure_type": "bloc",
        "outcome": "conquered",                # 体制崩壊
        "geo_barrier": 0.1,
        "external_threat": 0.7,
        "relative_pop": 0.1,
        "tech_position": 0.5,
        "institutional_quality": 0.3,
        "regime_duration_yrs": 41,
        "has_external_patron": 1,              # ソ連
    },
    {
        "entity": "ユーゴスラビア",
        "period": "AD1945-AD1992",
        "era": "20c",
        "region": "europe",
        "dominant": "stock",
        "stock_index": 0.45,
        "trade_openness": 0.30,
        "closure_type": "bloc",                # 非同盟だが計画経済的
        "outcome": "conquered",                # 内戦→崩壊
        "geo_barrier": 0.5,
        "external_threat": 0.5,
        "relative_pop": 0.1,
        "tech_position": 0.4,
        "institutional_quality": 0.3,
        "regime_duration_yrs": 47,
        "has_external_patron": 0,
    },
    {
        "entity": "英国帝国特恵制度",
        "period": "AD1932-AD1960",
        "era": "20c",
        "region": "europe",
        "dominant": "flow",                    # ブロック的だがフロー要素維持（英連邦内貿易）
        "stock_index": 0.65,
        "trade_openness": 0.55,                # 英連邦内フローは維持
        "closure_type": "bloc",
        "outcome": "survived",                 # 英連邦へ平和移行
        "geo_barrier": 0.8,
        "external_threat": 0.7,
        "relative_pop": 0.3,
        "tech_position": 0.7,
        "institutional_quality": 0.8,
        "regime_duration_yrs": 28,
        "has_external_patron": 0,
    },
    {
        "entity": "米国（戦後〜冷戦期）",
        "period": "AD1945-AD1991",
        "era": "20c",
        "region": "americas",
        "dominant": "flow",
        "stock_index": 0.85,                   # 自然◎、技術◎、制度◎、インフラ◎、人的◎
        "trade_openness": 0.70,
        "closure_type": "none",
        "outcome": "survived",
        "geo_barrier": 0.9,
        "external_threat": 0.6,
        "relative_pop": 0.5,
        "tech_position": 0.95,
        "institutional_quality": 0.9,
        "regime_duration_yrs": 46,
        "has_external_patron": 0,
    },
    {
        "entity": "戦後日本（高度成長期）",
        "period": "AD1945-AD1990",
        "era": "20c",
        "region": "east_asia",
        "dominant": "flow",                    # 加工貿易＝フロー依存
        "stock_index": 0.65,                   # 人的◎、技術蓄積◎、制度○
        "trade_openness": 0.65,
        "closure_type": "none",
        "outcome": "survived",
        "geo_barrier": 0.8,
        "external_threat": 0.3,
        "relative_pop": 0.3,
        "tech_position": 0.85,
        "institutional_quality": 0.7,
        "regime_duration_yrs": 45,
        "has_external_patron": 1,              # 日米安保
    },
    {
        "entity": "シンガポール",
        "period": "AD1965-AD現在",
        "era": "20c",
        "region": "southeast_asia",
        "dominant": "flow",
        "stock_index": 0.50,                   # 人的◎、金融◎、インフラ◎、自然×
        "trade_openness": 0.95,
        "closure_type": "none",
        "outcome": "survived",
        "geo_barrier": 0.5,
        "external_threat": 0.3,
        "relative_pop": 0.01,
        "tech_position": 0.8,
        "institutional_quality": 0.9,
        "regime_duration_yrs": 60,
        "has_external_patron": 0,
    },
    {
        "entity": "韓国",
        "period": "AD1961-AD現在",
        "era": "20c",
        "region": "east_asia",
        "dominant": "flow",
        "stock_index": 0.60,                   # 人的◎、技術◎、インフラ◎
        "trade_openness": 0.70,
        "closure_type": "none",
        "outcome": "survived",
        "geo_barrier": 0.5,
        "external_threat": 0.6,
        "relative_pop": 0.15,
        "tech_position": 0.8,
        "institutional_quality": 0.6,
        "regime_duration_yrs": 64,
        "has_external_patron": 1,               # 米韓同盟
    },
    {
        "entity": "北朝鮮",
        "period": "AD1948-AD現在",
        "era": "20c",
        "region": "east_asia",
        "dominant": "stock",
        "stock_index": 0.35,                   # 自然○(鉱物)、人的△、制度×
        "trade_openness": 0.05,
        "closure_type": "bloc",                # 主体思想・閉鎖経済
        "outcome": "survived",
        "geo_barrier": 0.5,
        "external_threat": 0.7,
        "relative_pop": 0.05,
        "tech_position": 0.3,
        "institutional_quality": 0.2,
        "regime_duration_yrs": 77,
        "has_external_patron": 1,               # 中国
    },
    {
        "entity": "キューバ",
        "period": "AD1959-AD現在",
        "era": "20c",
        "region": "americas",
        "dominant": "stock",
        "stock_index": 0.35,
        "trade_openness": 0.15,
        "closure_type": "bloc",
        "outcome": "survived",
        "geo_barrier": 0.7,                    # 島国
        "external_threat": 0.7,
        "relative_pop": 0.02,
        "tech_position": 0.3,
        "institutional_quality": 0.3,
        "regime_duration_yrs": 66,
        "has_external_patron": 1,               # ソ連→中国
    },
    # ── 現代 (1991〜) ──────────────────────────────────────
    {
        "entity": "現代日本",
        "period": "AD1990-AD現在",
        "era": "contemporary",
        "region": "east_asia",
        "dominant": "stock",                    # 対外純資産世界一、都市鉱山、人的蓄積
        "stock_index": 0.80,                    # 人的◎、技術蓄積◎、都市鉱山◎、金融◎、インフラ◎、文化◎
        "trade_openness": 0.35,                 # 貿易赤字化、内需型へ
        "closure_type": "none",                 # 明示的海禁はないが内向き傾向
        "outcome": "survived",                  # 現在進行中
        "geo_barrier": 0.8,
        "external_threat": 0.5,
        "relative_pop": 0.25,
        "tech_position": 0.7,
        "institutional_quality": 0.7,
        "regime_duration_yrs": 35,
        "has_external_patron": 1,
    },
    {
        "entity": "現代中国",
        "period": "AD1978-AD現在",
        "era": "contemporary",
        "region": "east_asia",
        "dominant": "flow",                     # 世界の工場→BRI（フロー展開中）
        "stock_index": 0.75,                    # 人的◎、インフラ◎、技術蓄積○
        "trade_openness": 0.60,
        "closure_type": "none",                 # GFWはデジタル海禁だがここでは経済を基準
        "outcome": "survived",
        "geo_barrier": 0.5,
        "external_threat": 0.5,
        "relative_pop": 0.95,
        "tech_position": 0.75,
        "institutional_quality": 0.5,
        "regime_duration_yrs": 47,
        "has_external_patron": 0,
    },
    {
        "entity": "現代ロシア",
        "period": "AD1991-AD現在",
        "era": "contemporary",
        "region": "europe",
        "dominant": "stock",                    # 資源ストック依存
        "stock_index": 0.65,                    # 自然◎、技術○(軍事)、人的△
        "trade_openness": 0.30,
        "closure_type": "bloc",                 # 制裁下で事実上のブロック化
        "outcome": "survived",                  # 現在進行中
        "geo_barrier": 0.6,
        "external_threat": 0.6,
        "relative_pop": 0.3,
        "tech_position": 0.5,
        "institutional_quality": 0.3,
        "regime_duration_yrs": 34,
        "has_external_patron": 0,
    },
]
# fmt: on


def load_data():
    """DataFrameとして返す"""
    df = pd.DataFrame(records)
    df["dominant_binary"] = (df["dominant"] == "stock").astype(int)
    df["outcome_binary"] = (df["outcome"] == "conquered").astype(int)
    # 中央値ベースの時代コード
    era_order = {
        "ancient": 0,
        "medieval": 1,
        "early_modern": 2,
        "modern": 3,
        "20c": 4,
        "contemporary": 5,
    }
    df["era_code"] = df["era"].map(era_order)
    return df


if __name__ == "__main__":
    df = load_data()
    print(f"Total records: {len(df)}")
    print(f"\nDominant distribution:\n{df['dominant'].value_counts()}")
    print(f"\nOutcome distribution:\n{df['outcome'].value_counts()}")
    print(f"\nCross-tabulation:")
    print(pd.crosstab(df["dominant"], df["outcome"], margins=True))
