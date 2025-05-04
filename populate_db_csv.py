import pandas as pd
import json
from tqdm import tqdm

from db_utils import (
    insert_investment_manager,
    insert_filing,
    insert_security,
    insert_holding
)

def parse_aum(aum_str):
    try:
        if isinstance(aum_str, str):
            aum_str = aum_str.strip().replace("$", "")
            if aum_str.endswith("B"):
                return float(aum_str[:-1]) * 1e9
            elif aum_str.endswith("M"):
                return float(aum_str[:-1]) * 1e6
        return float(aum_str)
    except:
        return None

def populate_database(csv_path: str):
    df = pd.read_csv(csv_path)

    for _, row in df.iterrows():
        cik = row['cik']
        name = row['Institution Name']
        aum = parse_aum(row['Assets Under Management (AUM)'])
        filing_date = row['date']
        form = row['form']
        raw_data_url = row['text_url']
        sector = row['Sector/Industry']
        ticker = row['Ticker Symbol']

        # Parse date
        year = int(filing_date.split('-')[0])
        month = int(filing_date.split('-')[1])
        quarter = (month - 1) // 3 + 1

        # Insert investment manager
        insert_investment_manager(cik, name, aum)

        # Insert filing
        try:
            filing_id = insert_filing(cik, filing_date, year, quarter, raw_data_url, form)
        except Exception as e:
            print(f"Failed to insert filing for {cik} on {filing_date}: {e}")
            continue

        # Parse holdings
        try:
            holdings_data = json.loads(row['data'].replace('""', '"'))
        except json.JSONDecodeError as e:
            print(f"Error parsing holdings JSON for CIK {cik}: {e}")
            continue

        for h in tqdm(holdings_data):
            try:
                security_id = insert_security(
                    ticker=h.get("holdings_ticker"),
                    cusip=h.get("cusip"),
                    name=h.get("issuer_name"),
                    sector=sector
                )

                insert_holding(
                    filing_id=filing_id,
                    security_id=security_id,
                    position_size=h.get("shares"),
                    market_value=h.get("value"),
                    weight=None  # not sure
                )
            except Exception as e:
                print(f"Failed to insert holding for CIK {cik}, security {h.get('cusip')}: {e}")

    print("🌼 Database population complete.")

if __name__ == "__main__":
    populate_database("13f_filings_demo.csv")