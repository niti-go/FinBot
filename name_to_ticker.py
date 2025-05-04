import pandas as pd
import re
from rapidfuzz import process, fuzz

"""
This file:
  1. Generates name_ticker_mapping.csv, which maps stock tickers to company names.
  2. Contains the utility function "get_ticker_from_name", used by get_filings.py 
     to map company names from institutional holdings to their tickers.
"""

  # Function to clean the Security Name
def clean_security_name(name):


  # List of nuisance phrases/words to remove
  nuisance_phrases = [
    "inc", "llc", "corp", "corporation", "group", "sa", "plc", "ltd", "limited",
    "common stock", "ordinary shares", "etf", "fund", "shares", "unit", "class a", 
    "class b", "depositary shares", "rights", "warrant", "options", "global", "active", 
    "corporate", "equity", "investors", "international", "the", "company", "incorporated",
    "inc", "co", "test", "industries", "solutions", "partners", "services"
]

  # Check if the name is a valid string (not NaN)
  if isinstance(name, str):
      # Normalize to lowercase
      name = name.lower()

      # Remove everything after a hyphen
      name = re.sub(r' -.*$', '', name)

      # Remove nuisance phrases
      for phrase in nuisance_phrases:
          name = name.replace(phrase, "")
      
      # Fix known abbreviations
      name = name.replace('rlty', 'realty')
      name = name.replace('agro', 'agriculture')
      name = name.replace('prod', 'products')
      name = name.replace('chems', 'chemicals')
      name = name.replace('invt','investment')
      name = name.replace('grp','group')
      name = name.replace('inds','industries')
      name = name.replace('centy','century')
      name = name.replace('labs','laboratories')
      name = name.replace('resh','research')
      name = name.replace('hldgs','holdings')
      
      # Special known fixes for common abbreviations or variations
      name = name.replace('aehr', 'aehr test systems')
      name = name.replace('adv energy', 'advanced energy industries')

      # Remove extra punctuation such as hyphens, commas, periods, etc.
      name = re.sub(r'[-,.\(\)]', ' ', name)

      # Remove extra spaces (multiple spaces) left after replacing phrases
      name = re.sub(r'\s+', ' ', name).strip()

      name = name.title()
      return name
  else:
      return ""


def create_name_ticker_mapping_file():
  """
  
  """
  nasdaq_url = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
  nyse_url = "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"

  # Load NASDAQ data
  nasdaq = pd.read_csv(nasdaq_url, sep='|')
  print(nasdaq.head())
  nasdaq = nasdaq[["Symbol", "Security Name"]]
  nasdaq.columns = ["Symbol", "Security Name"]

  # Load NYSE/Other data
  nyse = pd.read_csv(nyse_url, sep='|')
  nyse = nyse[["ACT Symbol", "Security Name"]]
  nyse.columns = ["Symbol", "Security Name"]
  nyse = nyse[["Symbol", "Security Name"]]
  # Combine both datasets
  combined = pd.concat([nasdaq, nyse], ignore_index=True)

  # Apply cleaning function to the Security Name column
  combined["Security Name"] = combined["Security Name"].apply(clean_security_name)

  # Save to CSV
  combined.to_csv("name_ticker_mapping.csv", index=False)
  print("✅ Combined CSV saved as 'name_ticker_mapping.csv'")
  

def get_ticker_from_name(original_name, choices, df):
    """
    original_name:the company name we are trying to match
    choices: the list of company names from name_ticker_mapping.csv we are matching against
    df: the data in name_ticker_mapping.csv
    """
    if not isinstance(original_name, str):
        return None
    
    # Clean the input name
    name = clean_security_name(original_name)
    
    # Run fuzzy matching using a fast and accurate scorer
    match = process.extractOne(
        query=name,
        choices=choices,
        scorer=fuzz.token_sort_ratio,  # Faster and better for slightly reordered words
        score_cutoff=90
    )

    if match:
        matched_name, score, idx = match
        ticker = df.iloc[idx]["Symbol"]
        # Optionally print match details
        # print(f"✅ Matched '{name}' → '{matched_name}' with score {score:.2f}")
        return ticker
    else:
        # print(f"❌ No match found for '{name}'")
        return None
  


if __name__ == "__main__":
    create_name_ticker_mapping_file()