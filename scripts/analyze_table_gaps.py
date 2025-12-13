#!/usr/bin/env python3
"""
Analyze table gaps by comparing expected vs actual tables in BigQuery.
Part of truth source reconciliation effort.
"""

from google.cloud import bigquery
import json
from collections import defaultdict

print("=" * 80)
print("BIGQUERY TABLE GAP ANALYSIS")
print("=" * 80)
print()

client = bigquery.Client(project='bqx-ml', location='us-central1')

# Query to get all tables
query = """
SELECT table_id
FROM `bqx-ml.bqx_ml_v3_features_v2.__TABLES__`
WHERE table_id NOT LIKE 'z_%'
ORDER BY table_id
"""

print("Fetching table list from BigQuery...")
results = client.query(query).result()

tables = [row.table_id for row in results]
total_tables = len(tables)

print(f"Total tables found: {total_tables:,}")
print()

# Categorize tables
categories = defaultdict(list)

for table in tables:
    # Determine category by prefix
    if table.startswith('csi_'):
        categories['CSI'].append(table)
    elif table.startswith('var_'):
        categories['VAR'].append(table)
    elif table.startswith('mkt_'):
        categories['MKT'].append(table)
    elif table.startswith('tri_'):
        categories['TRI'].append(table)
    elif table.startswith('corr_'):
        categories['CORR'].append(table)
    elif table.startswith('cov_'):
        categories['COV'].append(table)
    elif table.startswith('reg_'):
        categories['REG'].append(table)
    elif table.startswith('agg_'):
        categories['AGG'].append(table)
    elif table.startswith('lag_'):
        categories['LAG'].append(table)
    elif table.startswith('mom_'):
        categories['MOM'].append(table)
    elif table.startswith('vol_'):
        categories['VOL'].append(table)
    elif table.startswith('align_'):
        categories['ALIGN'].append(table)
    elif table.startswith('regime_'):
        categories['REGIME'].append(table)
    elif table.startswith('der_'):
        categories['DER'].append(table)
    elif table.startswith('div_'):
        categories['DIV'].append(table)
    elif table.startswith('rev_'):
        categories['REV'].append(table)
    elif table.startswith('mrt_'):
        categories['MRT'].append(table)
    elif table.startswith('tmp_'):
        categories['TMP'].append(table)
    else:
        categories['OTHER'].append(table)

# Print category summary
print("TABLE COUNT BY CATEGORY")
print("=" * 80)
print(f"{'Category':<15} {'Count':>8}  {'Documented':>10}  {'Difference':>10}  Status")
print("-" * 80)

# Expected counts from feature_catalogue.json
expected = {
    'CSI': 144,
    'VAR': 63,
    'MKT': 10,
    'TRI': 194,
    'CORR': None,  # Unknown expected count
    'COV': None,   # Unknown expected count
    'REG': 84,     # Post-Phase 0C
}

gap_analysis = {}

for category in sorted(categories.keys()):
    count = len(categories[category])
    exp = expected.get(category, None)

    if exp is not None:
        diff = count - exp
        if diff == 0:
            status = "✅ OK"
        elif diff > 0:
            status = f"⚠️  +{diff} extra"
        else:
            status = f"❌ {diff} missing"
        gap_analysis[category] = {
            'actual': count,
            'expected': exp,
            'difference': diff,
            'status': 'OK' if diff == 0 else ('EXTRA' if diff > 0 else 'MISSING')
        }
    else:
        exp = "N/A"
        diff = "N/A"
        status = "📋 Unknown"
        gap_analysis[category] = {
            'actual': count,
            'expected': None,
            'difference': None,
            'status': 'UNKNOWN'
        }

    print(f"{category:<15} {count:>8}  {str(exp):>10}  {str(diff):>10}  {status}")

print("-" * 80)
print(f"{'TOTAL':<15} {total_tables:>8}  {'5,845':>10}  {total_tables - 5845:>10}  {'✅ OK' if total_tables == 5845 else '❌ ERROR'}")
print()

# Detailed gap analysis for key categories
print()
print("DETAILED GAP ANALYSIS")
print("=" * 80)
print()

# CSI Analysis
print("1. CSI (Currency Strength Index) Tables")
print("-" * 80)
csi_tables = sorted(categories['CSI'])
print(f"Actual: {len(csi_tables)} tables")
print(f"Expected: 144 tables (8 currencies × 2 variants × 9 features)")
print(f"Difference: {len(csi_tables) - 144}")
if len(csi_tables) != 144:
    print("⚠️  GAP DETECTED")
    # Expected pattern: csi_{variant}_{currency}
    expected_csi = []
    for variant in ['bqx', 'idx']:
        for currency in ['aud', 'cad', 'chf', 'eur', 'gbp', 'jpy', 'nzd', 'usd']:
            expected_csi.append(f'csi_{variant}_{currency}')

    missing = [t for t in expected_csi if t not in csi_tables]
    extra = [t for t in csi_tables if t not in expected_csi]

    if missing:
        print(f"Missing {len(missing)} tables: {missing[:5]}...")
    if extra:
        print(f"Extra {len(extra)} tables: {extra[:5]}...")
else:
    print("✅ CSI tables complete")
print()

# VAR Analysis
print("2. VAR (Variance) Tables")
print("-" * 80)
var_tables = sorted(categories['VAR'])
print(f"Actual: {len(var_tables)} tables")
print(f"Expected: 63 tables")
print(f"Difference: {len(var_tables) - 63}")
if len(var_tables) != 63:
    print("⚠️  GAP DETECTED")
else:
    print("✅ VAR tables complete")
print()

# MKT Analysis
print("3. MKT (Market-Wide) Tables")
print("-" * 80)
mkt_tables = sorted(categories['MKT'])
print(f"Actual: {len(mkt_tables)} tables")
print(f"Expected: 10 tables")
print(f"Difference: {len(mkt_tables) - 10}")
if len(mkt_tables) != 10:
    print("⚠️  GAP DETECTED")
    print(f"Tables found: {', '.join(mkt_tables)}")
else:
    print("✅ MKT tables complete")
print()

# TRI Analysis
print("4. TRI (Triangulation) Tables")
print("-" * 80)
tri_tables = sorted(categories['TRI'])
print(f"Actual: {len(tri_tables)} tables")
print(f"Expected: 194 tables")
print(f"Difference: {len(tri_tables) - 194}")
if len(tri_tables) != 194:
    print("⚠️  GAP DETECTED")
else:
    print("✅ TRI tables complete")
print()

# Save gap analysis to JSON
gap_report = {
    'analysis_date': '2025-12-13T18:52:00Z',
    'total_tables': total_tables,
    'expected_tables': 5845,
    'discrepancy': total_tables - 5845,
    'categories': gap_analysis,
    'critical_gaps': {
        'CSI': {
            'actual': len(csi_tables),
            'expected': 144,
            'gap': len(csi_tables) - 144,
            'tables': csi_tables
        },
        'VAR': {
            'actual': len(var_tables),
            'expected': 63,
            'gap': len(var_tables) - 63,
            'tables': var_tables
        },
        'MKT': {
            'actual': len(mkt_tables),
            'expected': 10,
            'gap': len(mkt_tables) - 10,
            'tables': mkt_tables
        },
        'TRI': {
            'actual': len(tri_tables),
            'expected': 194,
            'gap': len(tri_tables) - 194,
            'tables': tri_tables[:20]  # First 20 only
        }
    }
}

with open('/tmp/gap_analysis_results.json', 'w') as f:
    json.dump(gap_report, f, indent=2)

print()
print("=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
print(f"Results saved to: /tmp/gap_analysis_results.json")
print()
