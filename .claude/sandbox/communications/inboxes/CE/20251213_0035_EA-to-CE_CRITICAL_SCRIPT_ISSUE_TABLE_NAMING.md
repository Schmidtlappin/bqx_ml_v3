# EA CRITICAL ISSUE: Generation Scripts - Table Naming Mismatch Detected

**Date**: December 13, 2025 00:35 UTC
**From**: Enhancement Assistant (EA)
**To**: Chief Engineer (CE) / User
**Re**: Scripts delivered to BA have critical naming pattern issues
**Priority**: P0-CRITICAL (BLOCKER)
**Session**: 05c73962-b9f1-4e06-9a5a-a5ae556cae5a

---

## ISSUE DISCOVERED

After delivering generation scripts to BA (00:30 UTC), I downloaded and analyzed the EURUSD training file (`/tmp/training_eurusd.parquet`, 9.3 GB) to verify feature coverage.

**Finding**: The actual column naming patterns in the training data **DO NOT MATCH** the table naming patterns in my scripts.

---

## EVIDENCE: Actual Feature Columns in Training Data

**Total tri/cov/corr/mkt columns**: 9,214
- TRI: 6,460 columns
- COV: 2,364 columns
- CORR: 240 columns
- MKT: 150 columns

### TRI Column Pattern (✅ APPEARS CORRECT)

**Actual columns**:
```
tri_agg_bqx_aud_usd_cad_arb_opportunity
tri_agg_bqx_aud_usd_cad_error_ma_180
tri_agg_bqx_aud_usd_cad_tri_error
```

**My script generates**:
```
Table: tri_agg_bqx_aud_usd_cad
Columns: arb_opportunity, error_ma_180, tri_error, ...
```

**Result**: When extracted and flattened, columns will be: `tri_agg_bqx_aud_usd_cad_arb_opportunity` ✅ MATCH

### COV Column Pattern (❌ POTENTIAL MISMATCH)

**Actual columns**:
```
cov_agg_audusd_mean_reversion_signal
cov_agg_audusd_spread
cov_agg_bqx_audusd_ratio
```

**Pattern**: `cov_agg_{secondpair}_{feature}` and `cov_agg_bqx_{secondpair}_{feature}`

**My script generates**:
```
Table: cov_agg_eurusd_audusd
Columns: mean_reversion_signal, spread, ratio, ...
```

**Result**: When extracted and flattened, columns will be: `cov_agg_eurusd_audusd_mean_reversion_signal`

**PROBLEM**: Actual pattern shows `cov_agg_audusd_*` (EURUSD is implicit), but my script creates `cov_agg_eurusd_audusd_*`

**Question**: Is this a EURUSD-specific extraction pattern, or is the table actually named `cov_agg_audusd` (without the first pair)?

### CORR Column Pattern (❌ MISMATCH)

**Actual columns**:
```
corr_bqx_ibkr_ewa_bqx_45
corr_bqx_ibkr_ewg_bqx_180
```

**Pattern**: `corr_bqx_ibkr_{etf}_bqx_{window}`

**My script generates**:
```
Table: corr_etf_bqx_eurusd_ewa
Columns: corr_45, corr_180, ...
```

**Result**: When extracted and flattened, columns will be: `corr_etf_bqx_eurusd_ewa_corr_45`

**PROBLEM**:
- Actual pattern: `corr_bqx_ibkr_{etf}_bqx_{window}` (no pair name, "ibkr" not "etf")
- My script: `corr_etf_bqx_{pair}_{etf}_corr_{window}`
- **COMPLETE MISMATCH**

### MKT Column Pattern (❌ MISSING ENTIRELY)

**Actual columns**:
```
mkt_corr_bqx_avg_market_corr
mkt_dispersion_bqx_mkt_dispersion_mean_180
mkt_regime_bqx_mkt_direction_45
mkt_sentiment_bqx_mkt_avg_momentum_180
mkt_vol_bqx_mkt_vol_atr_180
```

**Pattern**: Multiple table types:
- `mkt_corr` (22 columns)
- `mkt_dispersion` (58 columns)
- `mkt_regime` (16 columns)
- `mkt_sentiment` (34 columns)
- `mkt_vol` (46 columns)

**My script**: NO MKT GENERATION SCRIPT CREATED

---

## ROOT CAUSE ANALYSIS

### Problem 1: COV Table Naming Ambiguity

**Hypothesis 1**: Tables are pair-specific (e.g., `cov_agg_audusd` is EURUSD's covariance with AUDUSD)
- Would mean: Each pair has its own set of COV tables
- Expected count: 27 other pairs × 2 variants (agg, align) = 54 tables per pair
- Training file shows only "audusd" not "eurusd_audusd"

**Hypothesis 2**: Tables are universal (e.g., `cov_agg_eurusd_audusd` exists once in dataset)
- Would mean: All pairs share same COV tables
- Expected count: C(28,2) × 2 = 756 tables total
- My script implements THIS approach

**Resolution Needed**: Verify actual table names in BigQuery

### Problem 2: CORR Table Naming Mismatch

**Migration History**: From earlier investigation, I found:
- Migration script renamed `corr_ibkr_*` → `corr_etf_idx_*`
- Migration script renamed `corr_bqx_ibkr_*` → `corr_etf_bqx_*`

**But training data shows**: `corr_bqx_ibkr_*` (OLD NAME, not migrated?)

**Possibilities**:
1. Migration incomplete - some tables still use old names
2. Extraction used old table names before migration
3. My script should use old naming pattern `corr_bqx_ibkr_*`

### Problem 3: MKT Tables Not Generated

**Gap**: No MKT generation script created

**Actual MKT tables needed** (from training data):
- `mkt_corr` (1 table with 22 columns)
- `mkt_dispersion` (2 tables: idx + bqx, 58 total columns)
- `mkt_regime` (2 tables: idx + bqx, 16 total columns)
- `mkt_sentiment` (2 tables: idx + bqx, 34 total columns)
- `mkt_vol` (2 tables: idx + bqx, 46 total columns)
- **Total**: 8-10 tables

---

## IMPACT ASSESSMENT

### If Scripts Run As-Is:

**TRI**: ✅ Likely OK (pattern appears to match)
- 194 tables generated
- 6,460 columns expected ≈ 6,460 actual

**COV**: ⚠️ UNCERTAIN (naming ambiguity)
- May create tables with wrong names
- Validation will fail if names don't match existing tables
- Could create duplicate tables with different naming

**CORR**: ❌ HIGH RISK (naming mismatch)
- Will create `corr_etf_bqx_*` tables
- But training data uses `corr_bqx_ibkr_*` tables
- Validation will show 0% match
- **BLOCKER for production use**

**MKT**: ❌ MISSING (not generated)
- 150 columns will remain 100% NULL
- Feature catalogue gap will persist
- **INCOMPLETE remediation**

---

## RECOMMENDED ACTIONS

### IMMEDIATE (Before BA Executes Scripts)

1. ⏸️ **HOLD BA Tier 1 Execution** - scripts may create wrong tables
2. ✅ **Verify actual table names in BigQuery**:
   ```sql
   -- Check COV pattern
   SELECT table_name FROM `bqx-ml.bqx_ml_v3_features_v2.INFORMATION_SCHEMA.TABLES`
   WHERE table_name LIKE 'cov_%' LIMIT 10;

   -- Check CORR pattern
   SELECT table_name FROM `bqx-ml.bqx_ml_v3_features_v2.INFORMATION_SCHEMA.TABLES`
   WHERE table_name LIKE 'corr_%' LIMIT 10;

   -- Check MKT pattern
   SELECT table_name FROM `bqx-ml.bqx_ml_v3_features_v2.INFORMATION_SCHEMA.TABLES`
   WHERE table_name LIKE 'mkt_%' LIMIT 10;
   ```

3. ✅ **USER DECISION REQUIRED**:
   - Should COV tables be pair-specific (`cov_agg_audusd`) or universal (`cov_agg_eurusd_audusd`)?
   - Should CORR tables use old naming (`corr_bqx_ibkr_*`) or new naming (`corr_etf_bqx_*`)?
   - Are MKT tables in scope for Tier 1, or separate tier?

### SHORT-TERM (After Verification)

4. 🔧 **Update COV script** with correct naming pattern
5. 🔧 **Update CORR script** with correct naming pattern
6. 🔧 **Create MKT generation script** (or confirm out of scope)
7. ✅ **Re-validate all 3+ scripts** in dry-run mode
8. ✅ **Re-deliver to BA** with corrected scripts

### ALTERNATIVE PATH (If Time-Critical)

If user wants to proceed despite uncertainty:

1. ✅ **Run TRI script only** (high confidence)
2. ⏸️ **Hold COV/CORR/MKT** pending verification
3. ✅ **Partial remediation**: Fix 6,460 TRI columns (70% of gap)
4. 🔧 **Phase 2**: Fix COV/CORR/MKT after naming verified

---

## QUESTIONS FOR USER/CE

1. **COV Naming**: Are COV tables pair-specific or universal? What is the actual table naming pattern?

2. **CORR Migration**: Did the migration to `corr_etf_*` naming complete? Should I use old (`corr_bqx_ibkr_*`) or new (`corr_etf_bqx_*`) names?

3. **MKT Scope**: Are MKT tables in scope for this remediation? (150 columns, 8-10 tables)

4. **Execution Strategy**:
   - **Option A**: HOLD all scripts, fix naming, re-deliver (delay: 1-2 hours)
   - **Option B**: Run TRI only (70% fix), hold rest pending verification (delay: 0 hours for partial fix)
   - **Option C**: Run all scripts and accept risk of wrong table names (not recommended)

---

## EA ASSESSMENT

**Confidence in Scripts**:
- TRI: HIGH (pattern appears correct)
- COV: MEDIUM (ambiguous naming, needs verification)
- CORR: LOW (clear naming mismatch)
- MKT: N/A (not created)

**Recommended Path**: **Option A** (hold, fix, re-deliver)

**Rationale**: Running scripts with wrong naming could create 3,000+ incorrectly-named tables, requiring cleanup and re-execution. Better to verify first.

**Risk if Proceeding**: Tables generated may not match extraction patterns, causing 0% coverage in training files.

---

**Enhancement Assistant (EA)**
*Feature Generation Scripts - Critical Issue Detected*

**Status**: ⏸️ SCRIPTS ON HOLD - awaiting user/CE verification of table naming patterns

**Next**: User decision on execution strategy + table naming verification

---

**END OF CRITICAL ISSUE REPORT**
