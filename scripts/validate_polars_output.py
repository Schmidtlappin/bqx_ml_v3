import polars as pl

# Read output
df = pl.read_parquet('/home/micha/bqx_ml_v3/data/training/training_eurusd.parquet')

# Check dimensions
print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns):,}")

# Check targets
target_cols = [c for c in df.columns if c.startswith('target_')]
print(f"Target columns: {len(target_cols)}")
print(f"Target column names: {sorted(target_cols)[:5]}...")  # First 5

# Check for all-null columns (data integrity)
null_cols = []
for col in df.columns:
    if df[col].null_count() == len(df):
        null_cols.append(col)

if null_cols:
    print(f"WARNING: {len(null_cols)} columns are all NULL")
    print(f"Sample: {null_cols[:10]}")
else:
    print("✅ No all-NULL columns")

# Check interval_time
print(f"Interval time range: {df['interval_time'].min()} to {df['interval_time'].max()}")
print(f"Unique intervals: {df['interval_time'].n_unique():,}")

print("\n✅ Validation complete")
