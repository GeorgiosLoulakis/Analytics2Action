"""
Run this in your VS Code / GitHub setup.
Adjust the file paths below to match your actual CSV locations.
"""

import pandas as pd

# ── UPDATE THESE PATHS ──────────────────────────────────
ADMISSIONS_CSV = "Data\Lumiere_Country_Full_Backup.csv"
CLUSTERS_CSV   = "Data\clustered_films_k6.csv"
# ────────────────────────────────────────────────────────

SAMPLE_N = 15  # rows to sample from each file

def preview(path, label):
    print(f"\n{'='*60}")
    print(f"  {label}  —  {path}")
    print(f"{'='*60}")
    df = pd.read_csv(path)
    print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns\n")
    print("Columns & dtypes:")
    print(df.dtypes.to_string())
    print(f"\nNull counts:")
    print(df.isnull().sum().to_string())
    print(f"\nSample ({SAMPLE_N} rows):")
    sample = df.sample(n=min(SAMPLE_N, len(df)), random_state=42)
    print(sample.to_string())
    return sample

s1 = preview(ADMISSIONS_CSV, "ADMISSIONS")
s2 = preview(CLUSTERS_CSV, "CLUSTERS")

# Save samples so you can upload them to Claude
s1.to_csv("admissions_sample.csv", index=False)
s2.to_csv("clusters_sample.csv", index=False)

print("\n✅ Saved admissions_sample.csv and clusters_sample.csv")
print("   Upload these two files to the chat so we can get started!")