import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# --- 1. LOAD AND PREPARE THE DATA ---
file_name = 'data/Will & Agency/European_data_2000 copy.xlsx'
print(f"Loading dataset: {file_name}...")
df = pd.read_excel(file_name)

# Append budget and box office from IMDB_financials.xlsx to df

df_financial = pd.read_excel('IMDB_financials.xlsx', sheet_name='Both')
df_financial = df_financial.drop_duplicates(subset='titleId')
df = df.merge(
    df_financial[['titleId', 'budget_eur', 'gross_worldwide_eur']],
    on='titleId',
    how='left'
)
df = df[df['budget_eur'] > 0].copy()

# print(df.head())

# Ensure financial columns are numeric
df['budget_eur'] = pd.to_numeric(df['budget_eur'], errors='coerce')
# df['BoxOffice_Worldwide'] = pd.to_numeric(df['BoxOffice_Worldwide'], errors='coerce')
# df['Opening_Weekend'] = pd.to_numeric(df['Opening_Weekend'], errors='coerce')

# Drop rows that don't have both a budget_eur and a Worldwide Box Office for the core ROI analysis
analysis_df = df.dropna(subset=['budget_eur', 'gross_worldwide_eur']).copy()

# Calculate ROI (Return on Investment)
# Formula: (Revenue - Cost) / Cost
analysis_df['ROI'] = (analysis_df['gross_worldwide_eur'] - analysis_df['budget_eur']) / analysis_df['budget_eur']

print(f"Data ready. Analyzing {len(analysis_df)} movies with complete financial data.\n")


# --- TASK 1: CORRELATION BETWEEN BUDGET AND ROI ---
print("--- 1. budget_eur vs ROI ---")
budget_roi_corr = analysis_df['budget_eur'].corr(analysis_df['ROI'])
print(f"Correlation coefficient (budget_eur vs ROI): {budget_roi_corr:.4f}")

plt.figure(figsize=(10, 6))
sns.scatterplot(data=analysis_df, x='budget_eur', y='ROI', alpha=0.6, color='blue')
sns.regplot(data=analysis_df, x='budget_eur', y='ROI', scatter=False, color='red', line_kws={"linestyle":"--"})
plt.title('budget_eur vs Return on Investment (ROI)')
plt.xlabel('budget_eur ($)')
plt.ylabel('ROI (Multiplier)')
plt.axhline(0, color='black', linestyle='-', linewidth=1) # Breakeven line
plt.tight_layout()
#plt.savefig('1_budget_eur_vs_ROI.png')
#plt.close()
plt.show()

print("\n--- Task 1 Outliers: Top 3 Highest ROI Movies ---")
# Grab the 3 rows with the highest ROI, displaying key columns
top_3_overall = analysis_df.nlargest(3, 'ROI')[['titleId', 'budget_eur', 'gross_worldwide_eur', 'ROI']]
print(top_3_overall)

# --- TASK 2: CORRELATION BETWEEN ROI AND GENRES ---
print("\n--- 2. Most Profitable Genres ---")
# Split the comma-separated genres into individual rows
genre_df = analysis_df[['titleId', 'genres', 'ROI']].copy()
genre_df['genres'] = genre_df['genres'].str.split(', ')
genre_df = genre_df.explode('genres')

# Calculate median ROI per genre
genre_roi = genre_df.groupby('genres').agg(
    Median_ROI=('ROI', 'median'),
    Movie_Count=('titleId', 'count')
).reset_index()

# Filter for statistical significance (minimum 5 movies)
genre_roi = genre_roi[genre_roi['Movie_Count'] >= 5]
genre_roi = genre_roi.sort_values(by='Median_ROI', ascending=False)
print(genre_roi.head(10).to_string(index=False))

plt.figure(figsize=(12, 6))
sns.barplot(data=genre_roi, x='Median_ROI', y='genres', palette='viridis')
plt.title('Median ROI by Genre (Min. 5 Movies)')
plt.xlabel('Median ROI')
plt.ylabel('Genre')
plt.axvline(0, color='black', linestyle='-', linewidth=1)
plt.tight_layout()
#plt.savefig('2_ROI_by_Genre.png')
#plt.close()
plt.show()

print("\n--- Task 2 Outliers: Top 3 Highest ROI Movies by Genre ---")
# Grab the 3 rows with the highest ROI in the exploded genre dataframe
top_3_genres = genre_df.nlargest(3, 'ROI')[['titleId', 'genres', 'ROI']]
print(top_3_genres)

# --- TASK 3: CORRELATION BETWEEN ROI AND PRODUCING COMPANY ---
print("\n--- 3. Most Profitable Production Companies ---")
prod_df = analysis_df[['titleId', 'production', 'ROI']].copy()

# Drop missing production data and split strings
prod_df = prod_df.dropna(subset=['production'])
prod_df['production'] = prod_df['production'].str.split(',')
prod_df = prod_df.explode('production')
prod_df['production'] = prod_df['production'].str.strip()

# Calculate median ROI per company
company_roi = prod_df.groupby('production').agg(
    Median_ROI=('ROI', 'median'),
    Movie_Count=('titleId', 'count')
).reset_index()

# Filter for companies with at least 3 movies
company_roi = company_roi[company_roi['Movie_Count'] >= 3]
company_roi = company_roi.sort_values(by='Median_ROI', ascending=False)
top_companies = company_roi.head(15)
print(top_companies.to_string(index=False))

plt.figure(figsize=(12, 8))
sns.barplot(data=top_companies, x='Median_ROI', y='production', palette='magma')
plt.title('Top 15 Most Profitable Production Companies (Min. 3 Movies)')
plt.xlabel('Median ROI')
plt.ylabel('Production Company')
plt.axvline(0, color='black', linestyle='-', linewidth=1)
plt.tight_layout()
#plt.savefig('3_ROI_by_Company.png')
#plt.close()
plt.show()

print("\n--- Task 3 Outliers: Top 3 Highest ROI Movies by Company ---")
top_3_companies = prod_df.nlargest(3, 'ROI')[['titleId', 'production', 'ROI']]
print(top_3_companies)

# --- TASK 4: CORRELATION BETWEEN OPENING WEEKEND AND ROI ---
print("\n--- 4. Opening Weekend vs ROI ---")
# Filter out movies that don't have an opening weekend logged
ow_df = analysis_df.dropna(subset=['Opening_Weekend']).copy()

if len(ow_df) > 0:
    ow_roi_corr = ow_df['Opening_Weekend'].corr(ow_df['ROI'])
    print(f"Analyzed {len(ow_df)} movies with Opening Weekend data.")
    print(f"Correlation coefficient (Opening Weekend vs ROI): {ow_roi_corr:.4f}")
    
    if ow_roi_corr > 0.5:
        print("Insight: Strong positive correlation. A big opening weekend heavily dictates the final ROI.")
    elif ow_roi_corr > 0:
        print("Insight: Weak positive correlation. A good opening helps, but movies might still grow through word-of-mouth (long legs).")
    else:
        print("Insight: Negative or no correlation. The opening weekend is not a reliable predictor of the final ROI.")

    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=ow_df, x='Opening_Weekend', y='ROI', alpha=0.6, color='green')
    sns.regplot(data=ow_df, x='Opening_Weekend', y='ROI', scatter=False, color='red', line_kws={"linestyle":"--"})
    plt.title('Opening Weekend vs Return on Investment (ROI)')
    plt.xlabel('Opening Weekend Gross ($)')
    plt.ylabel('ROI (Multiplier)')
    plt.axhline(0, color='black', linestyle='-', linewidth=1)
    plt.tight_layout()
    #plt.savefig('4_Opening_Weekend_vs_ROI.png')
    #plt.close()
    plt.show()
else:
    print("Not enough Opening Weekend data to calculate correlation.")

print("\n--- Task 4 Outliers: Top 3 Highest ROI Movies (with Opening Weekend data) ---")
top_3_ow = ow_df.nlargest(3, 'ROI')[['titleId', 'Opening_Weekend', 'ROI']]
print(top_3_ow)