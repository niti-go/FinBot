import pandas as pd
#from config import API_KEY #later on we will individually need to create a config.py file with api keys
import requests
from tqdm import tqdm
from bs4 import BeautifulSoup

def fetch_holdings_data(URL):
    """
    TODO: Visit the URL to and return the holdings data for this filing.
    (example URL that will be passed in, a filing for GOOGL: https://www.sec.gov/Archives/edgar/data/1652044/000156761922020202/0001567619-22-020202.txt)
   
    Each filing contains a list of holdings. We want to extract the information of all the holdings for this filing.
    This involves parsing the XML data at the URL.
    Each holding includes the name of the issuer, CUSIP, value, shares, investment discretion, and voting authority, and maybe some other information.
    Extract this information for each holding (maybe as a dictionary) and return a list of all holdings.
    (Or maybe return a dataframe where each row is a holding)
    """

    pass
    

def get_filings(cik):
    """
    Fetches all recent 13F filings for a given Central Index Key (CIK).
    
    Args:
        cik (str): The CIK number of the institution.
    
    Returns:
        df: A dataframe containing filings for the CIK. The columns are form type, filing date, URL, and holdings listed in the filing.
    """
    #See https://www.sec.gov/search-filings/edgar-application-programming-interfaces 
    #for more information on the SEC EDGAR API we are using.

    url = f"https://data.sec.gov/submissions/CIK{cik:010}.json"
    headers = {"User-Agent": "Some Name (some.email@example.com)"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"There was an error fetching the data for CIK {cik}.")
        return []  # Return empty list
  
    data = response.json()
    filings = data.get("filings", {}).get("recent", {})
    
    indices = [i for i, form in enumerate(filings.get("form", [])) if "13F" in form]
    if not indices:
        return pd.DataFrame() #return empty dataframe; this cik has no 13f filings
    
    results = []
    for i in indices:
        accession = filings["accessionNumber"][i].replace("-", "")
        text_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{filings['accessionNumber'][i]}.txt"
        #print(text_url)

        one_filing = {
            "form": filings["form"][i],
            "cik": cik,
            "date": filings["filingDate"][i],
            "url": f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{filings['accessionNumber'][i]}-index.html",
            "text_url": text_url,
            "data" : fetch_holdings_data(text_url) #the textual data of a filing is multiple holdings 
            }

        results.append(one_filing)

    return pd.DataFrame(results)


def fetch_cik_list():
    """
    Returns the list of all CIKs from the SEC website as strings.
    """
    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {"User-Agent": "Some Name (some.email@example.com)"}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return []
    
    data = response.json()
    return [str(item["cik_str"]).zfill(10) for item in data.values()]


def get_all_13f_filings(MAX_NUM_TO_FETCH=6):
    """
    Fetches all 13F filings for every CIK.
    MAX_NUM_TO_FETCH: An optional argument specifying the maximum number of 
    CIKs to scrape (to save time).
    
    Returns:
        df: A dataframe of all 13F filings across all CIKs.
    """
    ciks = fetch_cik_list()
    df = pd.DataFrame()
    count = 0
    
    for cik in tqdm(ciks, desc="Fetching 13F Filings"):
      df = pd.concat([df, get_filings(cik)], ignore_index=True)
      count+=1
      
      if count == MAX_NUM_TO_FETCH:
        break

    return df


def main():
    
    filings = get_all_13f_filings(MAX_NUM_TO_FETCH=6)
    print(f"Fetched {len(filings)} 13F filings.")
    filings.to_csv("13f_filings.csv", index=False)


if __name__ == "__main__":
    main()

