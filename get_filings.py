import pandas as pd
#from config import API_KEY #later on we will individually need to create a config.py file with api keys
import requests
import yfinance as yf
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
    headers = {"User-Agent": "Some Name (some.email@example.com)"}
    response = requests.get(URL, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to fetch data from {URL}")
        return pd.DataFrame()
    
    soup = BeautifulSoup(response.text, "lxml")
    
    holdings = []
    for info in soup.find_all("infoTable"):
        holding = {
            "issuer_name": info.find("nameOfIssuer").text if info.find("nameOfIssuer") else None,
            "cusip": info.find("cusip").text if info.find("cusip") else None,
            "value": int(info.find("value").text) * 1000 if info.find("value") else None,  # Value in thousands
            "shares": int(info.find("shrsOrPrnAmt").find("sshPrnamt").text) if info.find("shrsOrPrnAmt") else None,
            "investment_discretion": info.find("investmentDiscretion").text if info.find("investmentDiscretion") else None,
            "voting_authority": {
                "sole": int(info.find("votingAuthority").find("Sole").text) if info.find("votingAuthority") else None,
                "shared": int(info.find("votingAuthority").find("Shared").text) if info.find("votingAuthority") else None,
                "none": int(info.find("votingAuthority").find("None").text) if info.find("votingAuthority") else None,
            }
        }
        holdings.append(holding)
    
    return pd.DataFrame(holdings)
    

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


def fetch_cik_dict():
    """
    Returns a dictionary mapping CIKs to (Ticker Symbol, Institution Name) from the SEC website.
    """
    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {"User-Agent": "Some Name (some.email@example.com)"}
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {}
    
    data = response.json()
    return {str(item["cik_str"]).zfill(10): (item["ticker"], item["title"]) for item in data.values()}


def get_all_13f_filings(MAX_NUM_TO_FETCH=6):
    """
    Fetches all 13F filings for every CIK.
    MAX_NUM_TO_FETCH: An optional argument specifying the maximum number of 
    CIKs to scrape (to save time).
    
    Returns:
        df: A dataframe of all 13F filings across all CIKs.
    """
    cik_mapping = fetch_cik_dict()
    df = pd.DataFrame()
    count = 0
    
    for cik in tqdm(cik_mapping.keys(), desc="Fetching 13F Filings"):
        cik_filings = get_filings(cik)
        if cik_filings.empty:
            continue
      
        cik_filings["Ticker Symbol"] = cik_mapping[cik][0]
        cik_filings["Institution Name"] = cik_mapping[cik][1]
        cik_filings["Sector/Industry"] = cik_filings["Ticker Symbol"].apply(lambda x: get_sector_from_yahoo(x) if pd.notna(x) else "N/A")
        cik_filings["Assets Under Management (AUM)"] = cik_filings["Ticker Symbol"].apply(lambda x: get_aum_and_fund_type(x)["AUM"] if pd.notna(x) else "N/A")
        cik_filings["Fund Type"] = cik_filings["Ticker Symbol"].apply(lambda x: get_aum_and_fund_type(x)["Fund Type"] if pd.notna(x) else "N/A")
        df = pd.concat([df, cik_filings], ignore_index=True)
        count+=1
      
        if count == MAX_NUM_TO_FETCH:
            break

    return df


def get_sector_from_yahoo(ticker):
    """Fetch sector/industry from Yahoo Finance"""
    try:
        stock = yf.Ticker(ticker)
        sector = stock.info.get("sector", "N/A")
        return sector
    except:
        return "N/A"
    

def get_aum_and_fund_type(ticker):
    """Fetch AUM (Assets Under Management) and Fund Type from Yahoo Finance."""
    try:
        stock = yf.Ticker(ticker)
        aum = stock.info.get("totalAssets", "N/A")
        fund_type = stock.info.get("category", "N/A")
        
        if isinstance(aum, (int, float)):
            aum = f"${aum/1e9:.2f}B"
        
        return {"AUM": aum, "Fund Type": fund_type}
    except:
        return {"AUM": "N/A", "Fund Type": "N/A"}


def main():
    
    filings = get_all_13f_filings(MAX_NUM_TO_FETCH=6)
    print(f"Fetched {len(filings)} 13F filings.")
    filings.to_csv("13f_filings.csv", index=False)


if __name__ == "__main__":
    main()

