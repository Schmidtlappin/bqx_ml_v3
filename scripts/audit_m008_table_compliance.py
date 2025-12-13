#!/usr/bin/env python3
"""
M008 Table Naming Compliance Audit

Identifies all tables that violate M008 naming standard and categorizes violations.

M008 Table Naming Pattern: ^[a-z]+_[a-z]+_[a-z0-9_]+$

Rules:
- All lowercase
- Underscore separators
- Type prefix (agg, mom, vol, reg, cov, corr, tri, mkt, csi, etc.)
- Variant indicator (bqx, idx, or other)
- Identifiers (pair names, currencies, ETF symbols)
- Alphabetical sorting for multi-entity tables

Author: Claude (Chief Engineer)
Date: 2025-12-13
Mandate: BQX-ML-M008 (Naming Standard Mandate)
Phase: M008 Phase 1 - Audit and Identification
"""

from google.cloud import bigquery
import re
import json
from collections import defaultdict
from datetime import datetime


def validate_m008_table_name(table_name: str) -> tuple[bool, str, list[str]]:
    """
    Validate table name against M008 standard.

    Returns:
        (is_valid, violation_type, violation_details)
    """
    violations = []

    # Check 1: Lowercase only
    if table_name != table_name.lower():
        violations.append("Contains uppercase or mixed case")
        return False, "CASE_VIOLATION", violations

    # Check 2: Basic pattern (type_variant_identifiers)
    basic_pattern = r'^[a-z]+_[a-z]+_[a-z0-9_]+$'
    if not re.match(basic_pattern, table_name):
        # Determine specific violation
        if '-' in table_name:
            violations.append("Contains hyphens (should be underscores)")
            return False, "SEPARATOR_VIOLATION", violations
        elif '.' in table_name:
            violations.append("Contains dots (should be underscores)")
            return False, "SEPARATOR_VIOLATION", violations
        elif not '_' in table_name:
            violations.append("Missing underscores (invalid structure)")
            return False, "STRUCTURE_VIOLATION", violations
        else:
            violations.append("Does not match M008 pattern")
            return False, "PATTERN_VIOLATION", violations

    # Check 3: Alphabetical sorting for multi-entity tables
    # Extract parts
    parts = table_name.split('_')

    # For COV tables: cov_{type}_{variant}_{pair1}_{pair2}
    if table_name.startswith('cov_') and len(parts) >= 5:
        # Extract pair names (last two parts)
        pair1, pair2 = parts[-2], parts[-1]

        # Check if they're in alphabetical order
        if pair1 > pair2:
            violations.append(f"Wrong alphabetical order: {pair1} before {pair2} (should be {pair2}_{pair1})")
            return False, "ALPHABETICAL_ORDER_VIOLATION", violations

    # For TRI tables: tri_{type}_{variant}_{curr1}_{curr2}_{curr3}
    if table_name.startswith('tri_') and len(parts) >= 6:
        # Extract currencies (last three parts)
        curr1, curr2, curr3 = parts[-3], parts[-2], parts[-1]

        # Check if they're in alphabetical order
        currencies = [curr1, curr2, curr3]
        sorted_currencies = sorted(currencies)
        if currencies != sorted_currencies:
            violations.append(f"Wrong alphabetical order: {curr1}_{curr2}_{curr3} (should be {'_'.join(sorted_currencies)})")
            return False, "ALPHABETICAL_ORDER_VIOLATION", violations

    # For CORR tables: corr_{type}_{variant}_{pair}_{etf}
    if table_name.startswith('corr_etf_') and len(parts) >= 5:
        # Component order should be: corr_etf_{variant}_{pair}_{etf}
        # Not: corr_{pair}_{etf}_{variant} or other permutations

        # This is actually correct if it matches the pattern
        # The key is that ETF should be at the end
        pass

    # All checks passed
    return True, None, []


def categorize_violation(table_name: str, violation_type: str, violation_details: list[str]) -> dict:
    """Categorize a violation for reporting."""
    return {
        'table_name': table_name,
        'violation_type': violation_type,
        'violation_details': violation_details,
        'parts': table_name.split('_'),
        'suggested_fix': suggest_fix(table_name, violation_type, violation_details)
    }


def suggest_fix(table_name: str, violation_type: str, violation_details: list[str]) -> str:
    """Suggest a corrected name for the violated table."""

    if violation_type == "CASE_VIOLATION":
        return table_name.lower()

    elif violation_type == "SEPARATOR_VIOLATION":
        # Replace hyphens/dots with underscores
        fixed = table_name.replace('-', '_').replace('.', '_')
        return fixed.lower()

    elif violation_type == "ALPHABETICAL_ORDER_VIOLATION":
        parts = table_name.split('_')

        # COV tables
        if table_name.startswith('cov_') and len(parts) >= 5:
            # cov_{type}_{variant}_{pair1}_{pair2}
            pair1, pair2 = parts[-2], parts[-1]
            if pair1 > pair2:
                # Swap pairs
                parts[-2], parts[-1] = pair2, pair1
                return '_'.join(parts)

        # TRI tables
        if table_name.startswith('tri_') and len(parts) >= 6:
            # tri_{type}_{variant}_{curr1}_{curr2}_{curr3}
            curr1, curr2, curr3 = parts[-3], parts[-2], parts[-1]
            sorted_currencies = sorted([curr1, curr2, curr3])
            parts[-3], parts[-2], parts[-1] = sorted_currencies
            return '_'.join(parts)

    # Default: lowercase
    return table_name.lower()


def main():
    print("=" * 80)
    print("M008 TABLE NAMING COMPLIANCE AUDIT")
    print("=" * 80)
    print()
    print("Mandate: BQX-ML-M008 (Naming Standard Mandate)")
    print("Phase: M008 Phase 1 - Audit and Identification")
    print("Date:", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"))
    print()

    client = bigquery.Client(project='bqx-ml', location='us-central1')

    # Step 1: Get all tables
    print("Step 1: Querying all tables in bqx_ml_v3_features_v2...")
    tables_query = """
    SELECT table_name
    FROM `bqx-ml.bqx_ml_v3_features_v2.INFORMATION_SCHEMA.TABLES`
    WHERE table_type = 'BASE TABLE'
    ORDER BY table_name
    """

    tables = [row.table_name for row in client.query(tables_query).result()]
    print(f"  Found {len(tables)} tables")
    print()

    # Step 2: Validate each table
    print("Step 2: Validating table names against M008 standard...")

    compliant_tables = []
    violations = defaultdict(list)

    for table in tables:
        is_valid, violation_type, violation_details = validate_m008_table_name(table)

        if is_valid:
            compliant_tables.append(table)
        else:
            violation = categorize_violation(table, violation_type, violation_details)
            violations[violation_type].append(violation)

    total_violations = sum(len(v) for v in violations.values())

    print(f"  Compliant: {len(compliant_tables)} tables ({len(compliant_tables)/len(tables)*100:.1f}%)")
    print(f"  Non-compliant: {total_violations} tables ({total_violations/len(tables)*100:.1f}%)")
    print()

    # Step 3: Categorize violations
    print("Step 3: Violation breakdown by type:")
    print("-" * 80)

    violation_summary = {}
    for violation_type, items in sorted(violations.items()):
        count = len(items)
        print(f"  {violation_type:40} {count:>6} tables")
        violation_summary[violation_type] = count

    print()

    # Step 4: Generate detailed report
    print("Step 4: Generating detailed violation report...")

    report_lines = []
    report_lines.append("# M008 Table Naming Violation Report")
    report_lines.append("")
    report_lines.append(f"**Date**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    report_lines.append(f"**Total Tables**: {len(tables)}")
    report_lines.append(f"**Compliant**: {len(compliant_tables)} ({len(compliant_tables)/len(tables)*100:.1f}%)")
    report_lines.append(f"**Non-Compliant**: {total_violations} ({total_violations/len(tables)*100:.1f}%)")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")
    report_lines.append("## VIOLATION SUMMARY")
    report_lines.append("")
    report_lines.append("| Violation Type | Count | Percentage |")
    report_lines.append("|----------------|-------|------------|")

    for violation_type, count in sorted(violation_summary.items(), key=lambda x: x[1], reverse=True):
        pct = count / total_violations * 100 if total_violations > 0 else 0
        report_lines.append(f"| {violation_type} | {count} | {pct:.1f}% |")

    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

    # Detailed violations by type
    for violation_type, items in sorted(violations.items()):
        report_lines.append(f"## {violation_type} ({len(items)} tables)")
        report_lines.append("")

        # Show up to 20 examples
        for i, item in enumerate(items[:20], 1):
            report_lines.append(f"### {i}. `{item['table_name']}`")
            report_lines.append("")
            report_lines.append(f"**Violation**: {', '.join(item['violation_details'])}")
            report_lines.append(f"**Suggested Fix**: `{item['suggested_fix']}`")
            report_lines.append("")

        if len(items) > 20:
            report_lines.append(f"*...and {len(items) - 20} more tables*")
            report_lines.append("")

        report_lines.append("---")
        report_lines.append("")

    # Write report
    report_path = 'docs/M008_VIOLATION_REPORT_20251213.md'
    with open(report_path, 'w') as f:
        f.write('\n'.join(report_lines))

    print(f"  ✅ Written: {report_path}")
    print()

    # Step 5: Generate JSON patterns
    print("Step 5: Generating violation patterns (JSON)...")

    patterns = {
        'generated': datetime.utcnow().isoformat() + 'Z',
        'total_tables': len(tables),
        'compliant_tables': len(compliant_tables),
        'non_compliant_tables': total_violations,
        'compliance_percentage': round(len(compliant_tables) / len(tables) * 100, 2),
        'violation_summary': violation_summary,
        'violations_by_type': {
            violation_type: [
                {
                    'table_name': item['table_name'],
                    'violation_details': item['violation_details'],
                    'suggested_fix': item['suggested_fix']
                }
                for item in items
            ]
            for violation_type, items in violations.items()
        }
    }

    patterns_path = 'docs/M008_VIOLATION_PATTERNS.json'
    with open(patterns_path, 'w') as f:
        json.dump(patterns, f, indent=2)

    print(f"  ✅ Written: {patterns_path}")
    print()

    # Step 6: Summary
    print("=" * 80)
    print("✅ M008 AUDIT COMPLETE")
    print("=" * 80)
    print()
    print(f"Total Tables:      {len(tables):>6}")
    print(f"Compliant:         {len(compliant_tables):>6} ({len(compliant_tables)/len(tables)*100:.1f}%)")
    print(f"Non-Compliant:     {total_violations:>6} ({total_violations/len(tables)*100:.1f}%)")
    print()
    print("Deliverables:")
    print(f"  1. {report_path}")
    print(f"  2. {patterns_path}")
    print()
    print("Next Step: M008 Phase 2 - Feature Catalogue Column Validation")
    print("=" * 80)

    return patterns


if __name__ == '__main__':
    main()
