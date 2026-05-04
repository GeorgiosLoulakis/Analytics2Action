import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import time
import random
import os

# --- CONFIGURATION ---
INPUT_FILE = 'data/Will & Agency/European_data_2000.xlsx' 
OUTPUT_FILE = 'IMDb_Final_Financials.xlsx'
# ---------------------

def get_imdb_financials(title_id):
    """
    Parses the internal JSON block of an IMDb page to extract 
    accurate Box Office and Budget numbers.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    # Initialize dictionary for results
    results = {
        'Budget': None,
        'Gross_Domestic_US_Canada': None,
        'Gross_Worldwide': None,
        'Opening_Weekend_Domestic': None
    }

    url = f"https://www.imdb.com/title/{title_id}/"
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code != 200:
            return results

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # BLOCK 1: FIND DATA BLOCK
        # IMDb embeds its database info in this specific script tag
        script_tag = soup.find('script', id='__NEXT_DATA__')
        
        if script_tag:
            data = json.loads(script_tag.string)
            # This path leads to the "Box Office" section seen in your screenshot
            try:
                box = data['props']['pageProps']['mainColumnData']
                
                # Extract Budget
                if 'productionBudget' in box and box['productionBudget']:
                    b = box['productionBudget']['budget']
                    results['Budget'] = f"{b['currency']} {b['amount']:,}"

                # Extract Worldwide Total Gross
                if 'worldwideGross' in box and box['worldwideGross']:
                    results['Gross_Worldwide'] = f"{box['worldwideGross']['currency']} {box['worldwideGross']['total']:,}"

                # Extract US & Canada Total Gross
                if 'lifetimeGross' in box and box['lifetimeGross']:
                    results['Gross_Domestic_US_Canada'] = f"{box['lifetimeGross']['currency']} {box['lifetimeGross']['total']:,}"
                
                # Extract Opening Weekend
                if 'openingWeekendGross' in box and box['openingWeekendGross']:
                    results['Opening_Weekend_Domestic'] = f"{box['openingWeekendGross']['currency']} {box['openingWeekendGross']['total']:,}"

            except KeyError:
                pass # Structure changed or section missing for this movie

    except Exception as e:
        print(f"   ! Error on {title_id}: {e}")

    return results

def main():
    # BLOCK 2: LOAD FILE
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    df = pd.read_excel(INPUT_FILE)
    scraped_list = []
    
    # BLOCK 3: LOOP THROUGH MOVIES
    # Limit to 10 for your requested test set
    test_df = df.head(10).copy()
    print(f"Starting 10-movie financial parse...")

    for index, row in test_df.iterrows():
        t_id = row['titleId']
        print(f"[{index+1}/10] Extracting Box Office for: {t_id}")
        
        movie_data = get_imdb_financials(t_id)
        scraped_list.append(movie_data)
        
        # BLOCK 4: HUMAN-LIKE WAITING
        # We wait between 4 and 8 seconds to ensure IMDb doesn't flag your IP
        time.sleep(random.uniform(4, 8))

    # BLOCK 5: MERGE AND SAVE
    final_df = pd.concat([test_df, pd.DataFrame(scraped_list)], axis=1)
    final_df.to_excel(OUTPUT_FILE, index=False)
    print(f"\nDone! Results saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()