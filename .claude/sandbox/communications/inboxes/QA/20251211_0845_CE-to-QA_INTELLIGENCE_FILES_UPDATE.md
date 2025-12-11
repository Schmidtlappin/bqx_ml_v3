# CE DIRECTIVE: Update All Intelligence, Mandate, and Catalogue Files

**Date**: December 11, 2025 08:45 UTC
**From**: Chief Engineer (CE)
**To**: Quality Assurance Agent (QA)
**Priority**: P0 - CRITICAL
**Category**: Documentation Maintenance

---

## DIRECTIVE SUMMARY

Update and make current ALL intelligence, mandate, and catalogue files including JSON files and README.md files. Ensure consistency across all documentation.

---

## FILES TO UPDATE

### Intelligence Files (`/intelligence/`)

| File | Key Updates Required |
|------|---------------------|
| `context.json` | Step 6 status (622/669), V1 analytics deletion pending |
| `ontology.json` | Verify model counts (588), feature counts |
| `semantics.json` | Verify target formula references correct dataset |
| `roadmap_v2.json` | Update Step 6 progress, add Step 7 readiness |
| `feature_catalogue.json` | Verify 669 tables per pair, CSI complete |
| `bigquery_v2_catalog.json` | Add targets section (analytics_v2), remove V1 refs |
| `metadata.json` | Update timestamps, verify script references |
| `workflows.json` | Verify pipeline steps current |

### Mandate Files (`/mandate/`)

| File | Key Updates Required |
|------|---------------------|
| `README.md` | Update mandate index, add new mandates |
| `BQX_TARGET_FORMULA_MANDATE.md` | Verify analytics_v2 is authoritative |
| `BQX_ML_V3_FEATURE_INVENTORY.md` | Update table counts (669 per pair) |
| `FEATURE_LEDGER_100_PERCENT_MANDATE.md` | Verify ledger requirements |
| `BQX_ML_V3_FOUNDATION.md` | Verify architecture current |
| `BQX_ML_V3_ARCHITECTURE_CONFIRMATION.md` | Update model architecture |

### Root Files

| File | Key Updates Required |
|------|---------------------|
| `/README.md` | Project status, quick start current |

---

## CURRENT STATE TO REFLECT

### Step 6 Extraction
- Status: 622/669 tables (92.9%) for EURUSD
- Summary tables: Working via CROSS JOIN
- Process: Needs restart (crashed)
- Remaining pairs: 27

### Target Data
- Location: `bqx_ml_v3_analytics_v2` (AUTHORITATIVE)
- V1 analytics: Pending deletion (29 rogue tables)
- Formula: Verified 100% compliant

### Model Architecture
- Models: 588 (28 pairs × 7 horizons × 3 algorithms)
- Note: ElasticNet removed, now 3 base models
- Meta-learner: Stacking ensemble

### Feature Counts
- Tables per pair: 669 (including 2 summary tables)
- Feature categories: 5 (pair, tri, mkt, var, csi)
- Total columns: ~11,337
- Unique features: ~1,064

### BigQuery Datasets
| Dataset | Status |
|---------|--------|
| `bqx_ml_v3_features_v2` | ACTIVE |
| `bqx_ml_v3_analytics_v2` | ACTIVE (targets) |
| `bqx_bq_uscen1_v2` | ACTIVE (source) |
| `bqx_ml_v3_analytics` (V1) | PENDING DELETION |

---

## CONSISTENCY CHECKS

Ensure these values are consistent across ALL files:

| Metric | Correct Value |
|--------|---------------|
| Model count | 588 |
| Pairs | 28 |
| Horizons | 7 (h15-h105) |
| Base algorithms | 3 (LightGBM, XGBoost, CatBoost) |
| Tables per pair | 669 |
| Target columns | 49 (7×7) |
| Target dataset | `bqx_ml_v3_analytics_v2` |
| Features dataset | `bqx_ml_v3_features_v2` |

---

## REMOVAL ITEMS

Remove or mark as deprecated:
- References to `bqx_ml_v3_analytics` (V1)
- References to `bqx_ml_v3_features` (V1 - already deleted)
- ElasticNet references (removed from ensemble)
- 784 model count (was 4 algorithms, now 3)
- 59-feature references (obsolete baseline)

---

## DELIVERABLES

1. **Per-file update report**: List changes made to each file
2. **Consistency audit**: Confirm all files use same values
3. **Timestamp updates**: Update "last modified" dates

File: `inboxes/CE/[timestamp]_QA-to-CE_INTELLIGENCE_UPDATE_COMPLETE.md`

---

## EXECUTION PRIORITY

1. Intelligence JSON files (most referenced)
2. Mandate files (authoritative specs)
3. README files (user-facing)

---

**Chief Engineer (CE)**
