#!/usr/bin/env python3
"""
Check which currency pairs are missing infrastructure
"""

# All 28 pairs required
all_pairs = [
    'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD',
    'EURGBP', 'EURJPY', 'EURCHF', 'EURAUD', 'EURCAD', 'EURNZD',
    'GBPJPY', 'GBPCHF', 'GBPAUD', 'GBPCAD', 'GBPNZD',
    'AUDJPY', 'AUDCHF', 'AUDCAD', 'AUDNZD',
    'NZDJPY', 'NZDCHF', 'NZDCAD',
    'CADJPY', 'CADCHF',
    'CHFJPY'
]

# Pairs with tables created
created_pairs = [
    'audcad', 'audchf', 'audjpy', 'audnzd', 'audusd',
    'cadchf', 'cadjpy', 'chfjpy',
    'euraud', 'eurcad', 'eurchf', 'eurgbp', 'eurjpy', 'eurnzd', 'eurusd',
    'gbpaud', 'gbpcad', 'gbpchf', 'gbpjpy', 'gbpnzd', 'gbpusd',
    'nzdcad', 'nzdchf', 'nzdjpy', 'nzdusd'
]

# Convert to uppercase for comparison
created_pairs_upper = [p.upper() for p in created_pairs]

# Find missing pairs
missing_pairs = [p for p in all_pairs if p not in created_pairs_upper]

print("="*60)
print("CURRENCY PAIR INFRASTRUCTURE STATUS")
print("="*60)
print(f"\n✅ Created: {len(created_pairs)} pairs")
print(f"❌ Missing: {len(missing_pairs)} pairs")

if missing_pairs:
    print(f"\n🔴 Missing pairs:")
    for pair in missing_pairs:
        print(f"   - {pair}")
else:
    print(f"\n✅ ALL 28 PAIRS HAVE INFRASTRUCTURE!")

print(f"\n📊 Total tables: {len(created_pairs) * 2}")
print(f"   - IDX tables: {len(created_pairs)}")
print(f"   - BQX tables: {len(created_pairs)}")