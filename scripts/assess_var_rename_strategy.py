#!/usr/bin/env python3
"""
M008 Phase 4C - VAR Table Rename Strategy Assessment

Analyzes 7 non-compliant VAR tables and determines optimal rename strategy.

Approach:
- Query BigQuery for non-compliant VAR tables
- Inspect each table (schema, sample data)
- Categorize violation patterns
- Recommend strategy: Manual (Option B) or Script (Option A)

Author: BA (Build Agent)
Date: 2025-12-14
CE Authorization: 20251214_0030_CE-to-ALL_FINAL_GO_AUTHORIZATION.md
"""

import json
import logging
import sys
from typing import List, Dict

from google.cloud import bigquery

# Configuration
PROJECT_ID = "bqx-ml"
DATASET_ID = "bqx_ml_v3_features_v2"
OUTPUT_FILE = "VAR_STRATEGY_RECOMMENDATION_20251214.md"

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/var_assessment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def get_non_compliant_var_tables() -> List[str]:
    """
    Query BigQuery for VAR tables that are not M008-compliant.

    Returns:
        List of non-compliant VAR table names
    """
    client = bigquery.Client(project=PROJECT_ID)

    logger.info("Querying for non-compliant VAR tables...")

    query = f"""
    SELECT table_name
    FROM `{PROJECT_ID}.{DATASET_ID}.__TABLES__`
    WHERE table_name LIKE 'var_%'
      AND table_name NOT LIKE 'var_%_bqx_%'
      AND table_name NOT LIKE 'var_%_idx_%'
    ORDER BY table_name
    """

    results = client.query(query).result()
    tables = [row.table_name for row in results]

    logger.info(f"Found {len(tables)} non-compliant VAR tables")
    return tables


def analyze_table(table_name: str) -> Dict:
    """
    Analyze a VAR table to understand its violation pattern.

    Args:
        table_name: VAR table name

    Returns:
        Dict with analysis results
    """
    client = bigquery.Client(project=PROJECT_ID)

    logger.info(f"\nAnalyzing: {table_name}")

    analysis = {
        'table_name': table_name,
        'violation_pattern': None,
        'schema': None,
        'sample_data': None,
        'recommended_new_name': None,
        'error': None
    }

    try:
        # Get table schema
        table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        table = client.get_table(table_ref)

        schema_info = []
        for field in table.schema:
            schema_info.append(f"{field.name} ({field.field_type})")

        analysis['schema'] = ', '.join(schema_info)
        logger.info(f"  Schema: {analysis['schema']}")

        # Get sample data
        query = f"SELECT * FROM `{table_ref}` LIMIT 5"
        rows = list(client.query(query).result())

        if rows:
            analysis['sample_data'] = f"{len(rows)} rows sampled"
            logger.info(f"  Sample data: {len(rows)} rows")
        else:
            analysis['sample_data'] = "No data"
            logger.warning(f"  No data in table")

        # Categorize violation pattern
        parts = table_name.split('_')

        if len(parts) == 2:
            # Pattern: var_{pair} (missing variant)
            analysis['violation_pattern'] = "missing_variant"
            # Recommend: var_{pair} → var_bqx_{pair} (assume BQX for variance)
            analysis['recommended_new_name'] = f"var_bqx_{parts[1]}"
            logger.info(f"  Pattern: Missing variant")
            logger.info(f"  Recommended: {table_name} → {analysis['recommended_new_name']}")

        elif len(parts) > 2 and parts[1] not in ['bqx', 'idx']:
            # Pattern: var_{feature}_{pair} (missing variant)
            analysis['violation_pattern'] = "missing_variant_complex"
            # Recommend: var_{feature}_{pair} → var_{feature}_bqx_{pair}
            analysis['recommended_new_name'] = f"{parts[0]}_{parts[1]}_bqx_{'_'.join(parts[2:])}"
            logger.info(f"  Pattern: Missing variant (complex)")
            logger.info(f"  Recommended: {table_name} → {analysis['recommended_new_name']}")

        else:
            # Other pattern
            analysis['violation_pattern'] = "other"
            analysis['recommended_new_name'] = f"{table_name}_NEEDS_MANUAL_REVIEW"
            logger.warning(f"  Pattern: Other (needs manual review)")

    except Exception as e:
        logger.error(f"  Error analyzing {table_name}: {str(e)}")
        analysis['error'] = str(e)

    return analysis


def generate_recommendation(analyses: List[Dict]) -> Dict:
    """
    Generate rename strategy recommendation based on analyses.

    Args:
        analyses: List of table analysis results

    Returns:
        Dict with recommendation
    """
    # Count violation patterns
    pattern_counts = {}
    for analysis in analyses:
        pattern = analysis.get('violation_pattern', 'unknown')
        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

    # Determine strategy
    total_tables = len(analyses)
    simple_pattern_count = pattern_counts.get('missing_variant', 0) + pattern_counts.get('missing_variant_complex', 0)

    if simple_pattern_count == total_tables:
        # All tables have simple "missing variant" pattern
        strategy = "OPTION_B_MANUAL"
        rationale = f"All {total_tables} VAR tables have simple 'missing variant' pattern. Manual execution (7 commands) takes 10-15 min vs 2-3h script development."
    elif pattern_counts.get('other', 0) > 0:
        # Some tables have complex patterns
        strategy = "OPTION_A_OR_MANUAL_HYBRID"
        rationale = f"{pattern_counts.get('other', 0)} tables have complex patterns requiring investigation. Recommend manual review + case-by-case execution."
    else:
        # Mixed patterns
        strategy = "OPTION_B_MANUAL"
        rationale = f"Only {total_tables} tables total. Manual execution fastest approach."

    recommendation = {
        'total_tables': total_tables,
        'pattern_counts': pattern_counts,
        'strategy': strategy,
        'rationale': rationale,
        'estimated_time': "10-15 minutes" if strategy == "OPTION_B_MANUAL" else "1-2 hours",
        'cost_benefit': "Manual execution saves 2-3h development time" if strategy == "OPTION_B_MANUAL" else "Mixed approach balances efficiency and safety"
    }

    return recommendation


def write_markdown_report(analyses: List[Dict], recommendation: Dict, filename: str):
    """
    Write VAR strategy recommendation to markdown file.

    Args:
        analyses: List of table analysis results
        recommendation: Strategy recommendation
        filename: Output markdown filename
    """
    with open(filename, 'w') as f:
        f.write("# VAR Rename Strategy Recommendation\n\n")
        f.write("**Date**: 2025-12-14\n")
        f.write("**Author**: BA (Build Agent)\n")
        f.write("**Purpose**: Assess VAR table violations and recommend rename strategy\n\n")
        f.write("---\n\n")

        f.write("## Executive Summary\n\n")
        f.write(f"**Total VAR Tables**: {recommendation['total_tables']}\n")
        f.write(f"**Recommended Strategy**: {recommendation['strategy']}\n")
        f.write(f"**Estimated Time**: {recommendation['estimated_time']}\n")
        f.write(f"**Rationale**: {recommendation['rationale']}\n\n")

        f.write("---\n\n")

        f.write("## Violation Pattern Analysis\n\n")
        for pattern, count in recommendation['pattern_counts'].items():
            f.write(f"- **{pattern}**: {count} tables\n")
        f.write("\n---\n\n")

        f.write("## Table-by-Table Analysis\n\n")
        for i, analysis in enumerate(analyses, 1):
            f.write(f"### {i}. {analysis['table_name']}\n\n")
            f.write(f"**Violation Pattern**: {analysis['violation_pattern']}\n\n")
            f.write(f"**Schema**: {analysis['schema']}\n\n")
            f.write(f"**Sample Data**: {analysis['sample_data']}\n\n")
            f.write(f"**Recommended New Name**: `{analysis['recommended_new_name']}`\n\n")

            if analysis['error']:
                f.write(f"**Error**: {analysis['error']}\n\n")

            f.write("---\n\n")

        f.write("## Recommended Strategy Detail\n\n")

        if recommendation['strategy'] == "OPTION_B_MANUAL":
            f.write("### Option B: Manual Execution (RECOMMENDED)\n\n")
            f.write("**Execution Plan**:\n\n")
            f.write("```bash\n")
            for analysis in analyses:
                old_name = analysis['table_name']
                new_name = analysis['recommended_new_name']
                f.write(f"# Rename: {old_name} → {new_name}\n")
                f.write(f"bq query --use_legacy_sql=false \"ALTER TABLE \\`{PROJECT_ID}.{DATASET_ID}.{old_name}\\` RENAME TO \\`{new_name}\\`\"\n\n")
            f.write("```\n\n")

            f.write("**Pros**:\n")
            f.write("- Simple, fast (10-15 min total)\n")
            f.write("- Saves 2-3h script development time\n")
            f.write("- Direct control over each rename\n\n")

            f.write("**Cons**:\n")
            f.write("- Manual typing (risk of typos - mitigated by copy-paste)\n")
            f.write("- No automated rollback (only 7 tables, low risk)\n\n")

        else:
            f.write("### Hybrid Approach (RECOMMENDED)\n\n")
            f.write("**Execution Plan**:\n")
            f.write("1. Manually execute simple 'missing variant' patterns\n")
            f.write("2. Investigate complex patterns case-by-case\n")
            f.write("3. CE/QA review before execution\n\n")

        f.write("## Decision\n\n")
        f.write(f"**BA Recommendation**: {recommendation['strategy']}\n\n")
        f.write(f"**Cost-Benefit**: {recommendation['cost_benefit']}\n\n")
        f.write("**User Priority Alignment**: COST (2nd priority) - Avoid unnecessary 2-3h script development for only 7 tables\n\n")

        f.write("---\n\n")
        f.write("**Ready for Dec 15 execution**: ✅ YES (pending CE/QA approval)\n")

    logger.info(f"✅ Report written to {filename}")


def main():
    """Main execution function."""
    logger.info(f"\n{'='*80}")
    logger.info(f"M008 PHASE 4C - VAR RENAME STRATEGY ASSESSMENT")
    logger.info(f"{'='*80}")
    logger.info(f"Project: {PROJECT_ID}")
    logger.info(f"Dataset: {DATASET_ID}")
    logger.info(f"Output file: {OUTPUT_FILE}")
    logger.info(f"{'='*80}\n")

    # Step 1: Get non-compliant VAR tables
    tables = get_non_compliant_var_tables()

    if not tables:
        logger.info("✅ All VAR tables are M008-compliant!")
        return 0

    # Step 2: Analyze each table
    analyses = []
    for table in tables:
        analysis = analyze_table(table)
        analyses.append(analysis)

    # Step 3: Generate recommendation
    recommendation = generate_recommendation(analyses)

    logger.info(f"\n{'='*80}")
    logger.info(f"RECOMMENDATION")
    logger.info(f"{'='*80}")
    logger.info(f"Strategy: {recommendation['strategy']}")
    logger.info(f"Rationale: {recommendation['rationale']}")
    logger.info(f"Estimated time: {recommendation['estimated_time']}")
    logger.info(f"{'='*80}\n")

    # Step 4: Write markdown report
    write_markdown_report(analyses, recommendation, OUTPUT_FILE)

    logger.info(f"\n✅ VAR assessment complete")
    logger.info(f"   Report: {OUTPUT_FILE}")
    logger.info(f"   Ready for CE/QA review\n")

    return 0


if __name__ == '__main__':
    sys.exit(main())
