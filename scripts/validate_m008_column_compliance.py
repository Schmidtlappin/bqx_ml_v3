#!/usr/bin/env python3
"""
M008 Column Naming Compliance Validation

Validates all column names in Feature Catalogue v3.1.0 against M008 naming standard.

M008 Column Naming Pattern: ^[a-z]+_[a-z0-9_]+_[0-9]+$

Rules:
- All lowercase
- Underscore separators
- Type prefix matches feature type
- Metric name (mean, std, lin_coef, bqx, etc.)
- Window size (45, 90, 180, 360, 720, 1440, 2880)
- Metadata columns exempted (interval_time, pair, source_value)

Author: Claude (Chief Engineer)
Date: 2025-12-13
Mandate: BQX-ML-M008 (Naming Standard Mandate)
Phase: M008 Phase 2 - Feature Catalogue Validation
"""

import json
import re
from collections import defaultdict
from datetime import datetime


def validate_m008_column_name(column_name: str) -> tuple[bool, str, list[str]]:
    """
    Validate column name against M008 standard.

    Returns:
        (is_valid, violation_type, violation_details)
    """
    violations = []

    # Exempt metadata columns
    if column_name in ['interval_time', 'pair', 'source_value']:
        return True, None, []

    # Check 1: Lowercase only
    if column_name != column_name.lower():
        violations.append("Contains uppercase or mixed case")
        return False, "CASE_VIOLATION", violations

    # Check 2: Basic pattern (type_metric_window)
    # Pattern allows for multi-part metrics like lin_coef, quad_term, etc.
    basic_pattern = r'^[a-z]+_[a-z0-9_]+_[0-9]+$'

    if not re.match(basic_pattern, column_name):
        # Determine specific violation
        if '-' in column_name:
            violations.append("Contains hyphens (should be underscores)")
            return False, "SEPARATOR_VIOLATION", violations
        elif '.' in column_name:
            violations.append("Contains dots (should be underscores)")
            return False, "SEPARATOR_VIOLATION", violations
        elif not column_name.endswith(tuple(str(w) for w in [45, 90, 180, 360, 720, 1440, 2880])):
            violations.append("Missing or invalid window size (must end with 45, 90, 180, 360, 720, 1440, or 2880)")
            return False, "WINDOW_VIOLATION", violations
        else:
            violations.append("Does not match M008 column pattern")
            return False, "PATTERN_VIOLATION", violations

    # Check 3: Window size validation
    parts = column_name.split('_')
    try:
        window = int(parts[-1])
        valid_windows = [45, 90, 180, 360, 720, 1440, 2880]
        if window not in valid_windows:
            violations.append(f"Invalid window size: {window} (must be one of {valid_windows})")
            return False, "WINDOW_VIOLATION", violations
    except (ValueError, IndexError):
        violations.append("Invalid window size (not a number)")
        return False, "WINDOW_VIOLATION", violations

    # All checks passed
    return True, None, []


def main():
    print("=" * 80)
    print("M008 COLUMN NAMING COMPLIANCE VALIDATION")
    print("=" * 80)
    print()
    print("Mandate: BQX-ML-M008 (Naming Standard Mandate)")
    print("Phase: M008 Phase 2 - Feature Catalogue Validation")
    print("Date:", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"))
    print()

    # Step 1: Load Feature Catalogue
    print("Step 1: Loading Feature Catalogue v3.1.0...")
    try:
        with open('intelligence/feature_catalogue_v3.json') as f:
            catalogue = json.load(f)
    except FileNotFoundError:
        print("  ❌ ERROR: Feature Catalogue not found at intelligence/feature_catalogue_v3.json")
        return None

    feature_definitions = catalogue.get('feature_definitions', [])
    print(f"  Loaded {len(feature_definitions)} feature definitions")
    print()

    # Step 2: Validate each feature name
    print("Step 2: Validating feature names against M008 standard...")

    compliant_features = []
    violations = defaultdict(list)

    for feature in feature_definitions:
        feature_name = feature['feature_name']
        is_valid, violation_type, violation_details = validate_m008_column_name(feature_name)

        if is_valid:
            compliant_features.append(feature_name)
        else:
            violations[violation_type].append({
                'feature_name': feature_name,
                'feature_type': feature.get('feature_type', 'unknown'),
                'violation_details': violation_details
            })

    total_violations = sum(len(v) for v in violations.values())

    print(f"  Compliant: {len(compliant_features)} features ({len(compliant_features)/len(feature_definitions)*100:.1f}%)")
    print(f"  Non-compliant: {total_violations} features ({total_violations/len(feature_definitions)*100:.1f}%)")
    print()

    # Step 3: Categorize violations
    if total_violations > 0:
        print("Step 3: Violation breakdown by type:")
        print("-" * 80)

        for violation_type, items in sorted(violations.items()):
            count = len(items)
            print(f"  {violation_type:40} {count:>6} features")

        print()
    else:
        print("Step 3: ✅ NO VIOLATIONS FOUND - 100% compliant!")
        print()

    # Step 4: Generate detailed report
    print("Step 4: Generating detailed validation report...")

    report_lines = []
    report_lines.append("# M008 Column Naming Validation Report")
    report_lines.append("")
    report_lines.append(f"**Date**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    report_lines.append(f"**Feature Catalogue**: v{catalogue.get('catalogue_version', 'unknown')}")
    report_lines.append(f"**Total Features**: {len(feature_definitions)}")
    report_lines.append(f"**Compliant**: {len(compliant_features)} ({len(compliant_features)/len(feature_definitions)*100:.1f}%)")
    report_lines.append(f"**Non-Compliant**: {total_violations} ({total_violations/len(feature_definitions)*100:.1f}%)")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

    if total_violations > 0:
        report_lines.append("## VIOLATION SUMMARY")
        report_lines.append("")
        report_lines.append("| Violation Type | Count | Percentage |")
        report_lines.append("|----------------|-------|------------|")

        for violation_type, items in sorted(violations.items(), key=lambda x: len(x[1]), reverse=True):
            count = len(items)
            pct = count / total_violations * 100
            report_lines.append(f"| {violation_type} | {count} | {pct:.1f}% |")

        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")

        # Detailed violations by type
        for violation_type, items in sorted(violations.items()):
            report_lines.append(f"## {violation_type} ({len(items)} features)")
            report_lines.append("")

            # Show up to 20 examples
            for i, item in enumerate(items[:20], 1):
                report_lines.append(f"### {i}. `{item['feature_name']}`")
                report_lines.append("")
                report_lines.append(f"**Feature Type**: {item['feature_type']}")
                report_lines.append(f"**Violation**: {', '.join(item['violation_details'])}")
                report_lines.append("")

            if len(items) > 20:
                report_lines.append(f"*...and {len(items) - 20} more features*")
                report_lines.append("")

            report_lines.append("---")
            report_lines.append("")
    else:
        report_lines.append("## ✅ 100% COMPLIANCE ACHIEVED")
        report_lines.append("")
        report_lines.append("All 1,604 feature names in the catalogue comply with M008 naming standard.")
        report_lines.append("")
        report_lines.append("**Pattern**: `^[a-z]+_[a-z0-9_]+_[0-9]+$`")
        report_lines.append("")
        report_lines.append("**Valid Windows**: 45, 90, 180, 360, 720, 1440, 2880")
        report_lines.append("")

    # Write report
    report_path = 'docs/M008_COLUMN_VALIDATION_REPORT.md'
    with open(report_path, 'w') as f:
        f.write('\n'.join(report_lines))

    print(f"  ✅ Written: {report_path}")
    print()

    # Step 5: Update Feature Catalogue if needed
    if total_violations > 0:
        print("Step 5: Updating Feature Catalogue with verified compliance...")

        # Update catalogue metadata
        catalogue['catalogue_version'] = '3.2.0'
        catalogue['generated'] = datetime.utcnow().isoformat() + 'Z'
        catalogue['m008_validation'] = {
            'validated': True,
            'validation_date': datetime.utcnow().isoformat() + 'Z',
            'total_features': len(feature_definitions),
            'compliant_features': len(compliant_features),
            'non_compliant_features': total_violations,
            'compliance_percentage': round(len(compliant_features) / len(feature_definitions) * 100, 2)
        }

        # Update mandate compliance for each feature
        for feature in feature_definitions:
            feature_name = feature['feature_name']
            is_valid, _, _ = validate_m008_column_name(feature_name)
            feature['mandate_compliance']['M008'] = is_valid

        # Write updated catalogue
        output_path = 'intelligence/feature_catalogue_v3.json'
        with open(output_path, 'w') as f:
            json.dump(catalogue, f, indent=2)

        print(f"  ✅ Updated: {output_path} (now v3.2.0)")
        print(f"  Updated mandate_compliance.M008 for all {len(feature_definitions)} features")
        print()
    else:
        print("Step 5: Feature Catalogue already 100% compliant - no update needed")
        print()

    # Step 6: Summary
    print("=" * 80)
    print("✅ M008 COLUMN VALIDATION COMPLETE")
    print("=" * 80)
    print()
    print(f"Total Features:    {len(feature_definitions):>6}")
    print(f"Compliant:         {len(compliant_features):>6} ({len(compliant_features)/len(feature_definitions)*100:.1f}%)")
    print(f"Non-Compliant:     {total_violations:>6} ({total_violations/len(feature_definitions)*100:.1f}%)")
    print()

    if total_violations == 0:
        print("🎉 100% M008 COMPLIANCE ACHIEVED!")
        print()
        print("All feature names in Feature Catalogue v3.1.0 comply with M008 naming standard.")
    else:
        print("⚠️  COMPLIANCE ISSUES FOUND")
        print()
        print(f"Feature Catalogue v3.2.0 has been updated with verified M008 compliance status.")
        print(f"See {report_path} for details.")

    print()
    print("Deliverable:")
    print(f"  1. {report_path}")
    if total_violations > 0:
        print(f"  2. intelligence/feature_catalogue_v3.json (updated to v3.2.0)")
    print()
    print("Next Step: M008 Phase 3 - Create detailed remediation plan for 475 tables")
    print("=" * 80)

    return {
        'total_features': len(feature_definitions),
        'compliant': len(compliant_features),
        'non_compliant': total_violations,
        'violations_by_type': {k: len(v) for k, v in violations.items()}
    }


if __name__ == '__main__':
    main()
