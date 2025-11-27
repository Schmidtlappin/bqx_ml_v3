#!/usr/bin/env python3
"""
Train first batch of BQX ML V3 models to verify pipeline
Testing with EURUSD (all 7 windows) and GBPUSD (all 7 windows)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from train_all_196_models import train_single_model, BASE_PARAMS, WINDOWS
from google.cloud import bigquery
from datetime import datetime
import json

def main():
    """
    Train first batch of 14 models (2 pairs × 7 windows)
    """

    print("\n" + "="*60)
    print("BQX ML V3 - FIRST BATCH TRAINING")
    print("Testing pipeline with 14 models")
    print("="*60)

    # Initialize BigQuery client
    client = bigquery.Client(project="bqx-ml")

    # Test pairs
    test_pairs = ['EURUSD', 'GBPUSD']

    # Results storage
    results = []
    start_time = datetime.now()

    for pair in test_pairs:
        print(f"\n{'='*60}")
        print(f"Training models for {pair}")
        print(f"{'='*60}")

        for window in WINDOWS:
            result = train_single_model(pair, window, client)
            results.append(result)

            # Summary
            if result['status'] == 'SUCCESS':
                r2 = result['metrics']['validation']['r2_score']
                dir_acc = result['metrics']['validation']['directional_accuracy']
                quality = result['quality_passed']

                print(f"\n📊 {pair}-{window} Summary:")
                print(f"   R² Score: {r2:.4f} {'✅' if r2 >= 0.35 else '❌'}")
                print(f"   Dir. Accuracy: {dir_acc:.2%} {'✅' if dir_acc >= 0.55 else '❌'}")
                print(f"   Quality Gates: {'✅ PASSED' if quality else '❌ FAILED'}")
            else:
                print(f"\n❌ {pair}-{window} failed: {result.get('error', 'Unknown error')}")

    # Summary report
    print("\n" + "="*60)
    print("FIRST BATCH COMPLETE - SUMMARY")
    print("="*60)

    successful = [r for r in results if r['status'] == 'SUCCESS']
    quality_passed = [r for r in successful if r['quality_passed']]

    print(f"\n📊 Results:")
    print(f"   Models trained: {len(successful)}/{len(results)}")
    print(f"   Quality gates passed: {len(quality_passed)}/{len(successful)}")

    if successful:
        avg_r2 = sum(r['metrics']['validation']['r2_score'] for r in successful) / len(successful)
        avg_dir_acc = sum(r['metrics']['validation']['directional_accuracy'] for r in successful) / len(successful)

        print(f"   Average R² score: {avg_r2:.4f}")
        print(f"   Average dir. accuracy: {avg_dir_acc:.2%}")

    print(f"   Total time: {(datetime.now() - start_time).total_seconds():.1f} seconds")

    # Save results
    output_file = '/home/micha/bqx_ml_v3/scripts/first_batch_results.json'
    with open(output_file, 'w') as f:
        json.dump({
            'summary': {
                'models_trained': len(successful),
                'quality_passed': len(quality_passed),
                'avg_r2': avg_r2 if successful else 0,
                'avg_dir_acc': avg_dir_acc if successful else 0,
                'duration_seconds': (datetime.now() - start_time).total_seconds()
            },
            'models': results
        }, f, indent=2)

    print(f"\n💾 Results saved to: {output_file}")

    # Recommendation
    if len(quality_passed) == len(results):
        print("\n✅ ALL MODELS PASSED QUALITY GATES!")
        print("🚀 Ready to scale to all 196 models")
    elif len(quality_passed) >= len(results) * 0.8:
        print("\n✅ Most models passed quality gates")
        print("📊 Consider proceeding with full scale")
    else:
        print("\n⚠️ Quality gate pass rate below 80%")
        print("🔍 Review parameters before scaling")

    return results

if __name__ == "__main__":
    try:
        results = main()
        print("\n✅ First batch training complete!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()