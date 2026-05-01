import pandas as pd
import matplotlib.pyplot as plt

#========== PART 1: ROI ==========
df_financial = pd.read_excel('IMDB_financials.xlsx', sheet_name='Both')
df_original = pd.read_excel('data/Will & Agency/European_data_2000.xlsx')

df_merged = pd.merge(df_financial, df_original[['titleId', 'genres']], on='titleId', how='left')
df_merged = df_merged[df_merged['budget_eur'] > 0].copy()

df_merged['roi'] = df_merged['gross_worldwide_eur'] / df_merged['budget_eur']

# Split comma-separated genres and expand so each genre gets its own row
df_merged['genre'] = df_merged['genres'].astype(str).str.split(',')
df_exploded = df_merged.explode('genre')

# Remove any leading/trailing spaces from genre names
df_exploded['genre'] = df_exploded['genre'].str.strip()

# Group by genre and calculate average (mean) and median ROI
roi_stats = df_exploded.groupby('genre')['roi'].agg(
    average_roi='mean',
    median_roi='median'
    ).reset_index()

roi_stats = roi_stats.sort_values(by='average_roi', ascending=True)

# Create the bar chart
roi_stats.plot(x='genre', y=['average_roi', 'median_roi'], kind='barh', width=0.8)

# Formatting the chart
plt.title('Average and Median ROI by Genre')
plt.xlabel('Return on Investment (ROI)')
plt.ylabel('Genre')
plt.legend(['Average ROI', 'Median ROI'])
plt.tight_layout()
plt.show()