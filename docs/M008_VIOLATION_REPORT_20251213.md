# M008 Table Naming Violation Report

**Date**: 2025-12-13 05:35:14 UTC
**Total Tables**: 6069
**Compliant**: 5594 (92.2%)
**Non-Compliant**: 475 (7.8%)

---

## VIOLATION SUMMARY

| Violation Type | Count | Percentage |
|----------------|-------|------------|
| PATTERN_VIOLATION | 285 | 60.0% |
| ALPHABETICAL_ORDER_VIOLATION | 190 | 40.0% |

---

## ALPHABETICAL_ORDER_VIOLATION (190 tables)

### 1. `tri_agg_bqx_aud_usd_cad`

**Violation**: Wrong alphabetical order: aud_usd_cad (should be aud_cad_usd)
**Suggested Fix**: `tri_agg_bqx_aud_cad_usd`

### 2. `tri_agg_bqx_aud_usd_chf`

**Violation**: Wrong alphabetical order: aud_usd_chf (should be aud_chf_usd)
**Suggested Fix**: `tri_agg_bqx_aud_chf_usd`

### 3. `tri_agg_bqx_aud_usd_jpy`

**Violation**: Wrong alphabetical order: aud_usd_jpy (should be aud_jpy_usd)
**Suggested Fix**: `tri_agg_bqx_aud_jpy_usd`

### 4. `tri_agg_bqx_aud_usd_nzd`

**Violation**: Wrong alphabetical order: aud_usd_nzd (should be aud_nzd_usd)
**Suggested Fix**: `tri_agg_bqx_aud_nzd_usd`

### 5. `tri_agg_bqx_eur_usd_aud`

**Violation**: Wrong alphabetical order: eur_usd_aud (should be aud_eur_usd)
**Suggested Fix**: `tri_agg_bqx_aud_eur_usd`

### 6. `tri_agg_bqx_eur_usd_cad`

**Violation**: Wrong alphabetical order: eur_usd_cad (should be cad_eur_usd)
**Suggested Fix**: `tri_agg_bqx_cad_eur_usd`

### 7. `tri_agg_bqx_eur_usd_chf`

**Violation**: Wrong alphabetical order: eur_usd_chf (should be chf_eur_usd)
**Suggested Fix**: `tri_agg_bqx_chf_eur_usd`

### 8. `tri_agg_bqx_eur_usd_gbp`

**Violation**: Wrong alphabetical order: eur_usd_gbp (should be eur_gbp_usd)
**Suggested Fix**: `tri_agg_bqx_eur_gbp_usd`

### 9. `tri_agg_bqx_eur_usd_jpy`

**Violation**: Wrong alphabetical order: eur_usd_jpy (should be eur_jpy_usd)
**Suggested Fix**: `tri_agg_bqx_eur_jpy_usd`

### 10. `tri_agg_bqx_eur_usd_nzd`

**Violation**: Wrong alphabetical order: eur_usd_nzd (should be eur_nzd_usd)
**Suggested Fix**: `tri_agg_bqx_eur_nzd_usd`

### 11. `tri_agg_bqx_gbp_usd_aud`

**Violation**: Wrong alphabetical order: gbp_usd_aud (should be aud_gbp_usd)
**Suggested Fix**: `tri_agg_bqx_aud_gbp_usd`

### 12. `tri_agg_bqx_gbp_usd_cad`

**Violation**: Wrong alphabetical order: gbp_usd_cad (should be cad_gbp_usd)
**Suggested Fix**: `tri_agg_bqx_cad_gbp_usd`

### 13. `tri_agg_bqx_gbp_usd_chf`

**Violation**: Wrong alphabetical order: gbp_usd_chf (should be chf_gbp_usd)
**Suggested Fix**: `tri_agg_bqx_chf_gbp_usd`

### 14. `tri_agg_bqx_gbp_usd_jpy`

**Violation**: Wrong alphabetical order: gbp_usd_jpy (should be gbp_jpy_usd)
**Suggested Fix**: `tri_agg_bqx_gbp_jpy_usd`

### 15. `tri_agg_bqx_gbp_usd_nzd`

**Violation**: Wrong alphabetical order: gbp_usd_nzd (should be gbp_nzd_usd)
**Suggested Fix**: `tri_agg_bqx_gbp_nzd_usd`

### 16. `tri_agg_bqx_nzd_usd_cad`

**Violation**: Wrong alphabetical order: nzd_usd_cad (should be cad_nzd_usd)
**Suggested Fix**: `tri_agg_bqx_cad_nzd_usd`

### 17. `tri_agg_bqx_nzd_usd_chf`

**Violation**: Wrong alphabetical order: nzd_usd_chf (should be chf_nzd_usd)
**Suggested Fix**: `tri_agg_bqx_chf_nzd_usd`

### 18. `tri_agg_bqx_nzd_usd_jpy`

**Violation**: Wrong alphabetical order: nzd_usd_jpy (should be jpy_nzd_usd)
**Suggested Fix**: `tri_agg_bqx_jpy_nzd_usd`

### 19. `tri_agg_idx_aud_usd_cad`

**Violation**: Wrong alphabetical order: aud_usd_cad (should be aud_cad_usd)
**Suggested Fix**: `tri_agg_idx_aud_cad_usd`

### 20. `tri_agg_idx_aud_usd_chf`

**Violation**: Wrong alphabetical order: aud_usd_chf (should be aud_chf_usd)
**Suggested Fix**: `tri_agg_idx_aud_chf_usd`

*...and 170 more tables*

---

## PATTERN_VIOLATION (285 tables)

### 1. `agg_audcad`

**Violation**: Does not match M008 pattern
**Suggested Fix**: `agg_audcad`

### 2. `agg_audchf`

**Violation**: Does not match M008 pattern
**Suggested Fix**: `agg_audchf`

### 3. `agg_audjpy`

**Violation**: Does not match M008 pattern
**Suggested Fix**: `agg_audjpy`

### 4. `agg_audnzd`

**Violation**: Does not match M008 pattern
**Suggested Fix**: `agg_audnzd`

### 5. `agg_audusd`

**Violation**: Does not match M008 pattern
**Suggested Fix**: `agg_audusd`

### 6. `agg_cadchf`

**Violation**: Does not match M008 pattern
**Suggested Fix**: `agg_cadchf`

### 7. `agg_cadjpy`

**Violation**: Does not match M008 pattern
**Suggested Fix**: `agg_cadjpy`

### 8. `agg_chfjpy`

**Violation**: Does not match M008 pattern
**Suggested Fix**: `agg_chfjpy`

### 9. `agg_euraud`

**Violation**: Does not match M008 pattern
**Suggested Fix**: `agg_euraud`

### 10. `agg_eurcad`

**Violation**: Does not match M008 pattern
**Suggested Fix**: `agg_eurcad`

### 11. `agg_eurchf`

**Violation**: Does not match M008 pattern
**Suggested Fix**: `agg_eurchf`

### 12. `agg_eurgbp`

**Violation**: Does not match M008 pattern
**Suggested Fix**: `agg_eurgbp`

### 13. `agg_eurjpy`

**Violation**: Does not match M008 pattern
**Suggested Fix**: `agg_eurjpy`

### 14. `agg_eurnzd`

**Violation**: Does not match M008 pattern
**Suggested Fix**: `agg_eurnzd`

### 15. `agg_eurusd`

**Violation**: Does not match M008 pattern
**Suggested Fix**: `agg_eurusd`

### 16. `agg_gbpaud`

**Violation**: Does not match M008 pattern
**Suggested Fix**: `agg_gbpaud`

### 17. `agg_gbpcad`

**Violation**: Does not match M008 pattern
**Suggested Fix**: `agg_gbpcad`

### 18. `agg_gbpchf`

**Violation**: Does not match M008 pattern
**Suggested Fix**: `agg_gbpchf`

### 19. `agg_gbpjpy`

**Violation**: Does not match M008 pattern
**Suggested Fix**: `agg_gbpjpy`

### 20. `agg_gbpnzd`

**Violation**: Does not match M008 pattern
**Suggested Fix**: `agg_gbpnzd`

*...and 265 more tables*

---
