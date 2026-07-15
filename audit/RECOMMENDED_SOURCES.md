# Recommended Sources for the Revised Dataset

The current 0–1 scores are retained as legacy values in an AI-assisted
exploratory dataset. The sources below must not be cited as if they generated
those scores. They are recommended for validating factual fields, designing a
future objective coding scheme, and documenting coverage limitations.

## Record identity, dates, location, and outcomes

Use a record-level source manifest rather than relying only on three general
history books.

Preferred source order:

1. Scholarly polity databases or peer-reviewed datasets
2. National archives, museum collections, treaty texts, or institutional
   histories
3. Major scholarly encyclopedias such as Encyclopaedia Iranica or Britannica

Each record should contain:

- stable URL or DOI
- source title and author/institution
- edition or dataset version
- access date
- page, table, entry, or quoted passage
- exact field supported
- coder decision and uncertainty note

## Open historical datasets

| Source | Recommended use | Coverage limitation |
|---|---|---|
| [Seshat Cliopatria](https://zenodo.org/records/13363121) | polity identity, temporal bounds, and spatial extent | 3400 BCE–2024 CE; not every project-specific variable is available |
| [Maddison Project Database 2023](https://doi.org/10.34894/INZBF2) | population and income benchmarks | 1–2022 CE; strongest for modern states, and historical borders vary |
| [Clio-Infra](https://clio-infra.eu/) | long-run population, urbanization, institutions, and economic indicators | variable-specific geographic and temporal gaps |
| [HYDE](https://www.pbl.nl/en/hyde-history-database-of-the-global-environment) | gridded historical population and land use | estimates are spatial reconstructions, not polity-level ratings |
| [V-Dem v16](https://v-dem.net/data/the-v-dem-dataset/country-year-v-dem-core-v16/) | modern institutional indicators | primarily 1789 onward; no direct coverage for most ancient and medieval cases |
| [Correlates of War Formal Alliances v4.1](https://correlatesofwar.org/data-sets/formal-alliances/) | formal interstate alliance checks | 1816–2012; alliance membership is not itself a patron measure |
| [Polity5](https://www.systemicpeace.org/inscrdata.html) | modern regime and institutional measures | 1800–2018; not comparable to ancient polity coding without a bridge rule |

## Variable-specific recommendations

### `entity`, `period`, `era`, `region`, `regime_duration_yrs`

- assign each case a stable identifier where possible;
- source the start and end dates;
- derive `regime_duration_yrs` mechanically;
- define era boundaries once and apply them programmatically;
- add an `oceania` region rather than assigning the Hawaiian Kingdom to the
  Americas.

### `closure_type`

Create a prespecified decision tree distinguishing:

1. formal policy closure or maritime prohibition;
2. membership in a coercive or preferential economic bloc;
3. involuntary technical/network exclusion;
4. no closure.

Require a case-specific source documenting the policy, treaty, network
condition, and relevant dates. Geographic isolation alone must not be labeled a
maritime ban.

### `outcome`

Define the unit and time horizon before coding:

- external conquest or annexation;
- internal regime replacement with state continuity;
- temporary occupation followed by restoration;
- survival through the end of the observation window.

The Ethiopian case demonstrates why temporary conquest and later restoration
need an explicit rule.

### `has_external_patron`

Define whether tributary status, suzerainty, alliance protection, colonial
guarantee, occupation sponsorship, or great-power backing counts. Apply the
same rule to Ryukyu, Manchukuo, East Germany, South Vietnam, Taiwan, and other
comparable cases.

### AI-assisted subjective fields

The following may remain unchanged for the exploratory analysis:

- `dominant`
- `stock_index`
- `trade_openness`
- `geo_barrier`
- `external_threat`
- `relative_pop`
- `tech_position`
- `institutional_quality`

The manuscript and metadata must state that these are not public-data-derived
measurements. A future validation study should publish a scoring rubric, recruit
independent coders blinded to outcomes, report agreement, and rerun all models
under alternative codings.
