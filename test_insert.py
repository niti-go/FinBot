from db_utils import insert_investment_manager, insert_filing, insert_security, insert_holding

def main():
    # -------------------------------
    # 1. Insert a sample investment manager
    # -------------------------------
    manager_cik = "1234567890"
    manager_name = "Test Fund"
    asset_size = 5000000000
    insert_investment_manager(manager_cik, manager_name, asset_size)
    print(f"Inserted test investment manager: CIK={manager_cik}, Name='{manager_name}', Asset Size={asset_size}")

    # -------------------------------
    # 2. Insert a sample filing for the investment manager
    # -------------------------------
    filing_date = "2025-04-15"  # YYYY-MM-DD format; psycopg2 will convert it to a DATE
    filing_year = 2025
    filing_quarter = 2
    raw_data_url = "http://example.com/test_filing"
    filing_type = "13F"
    # returns the auto-generated filing_id from the database
    filing_id = insert_filing(manager_cik, filing_date, filing_year, filing_quarter, raw_data_url, filing_type)
    print(f"Inserted test filing for manager {manager_cik}: Filing ID={filing_id}, Date={filing_date}, Year={filing_year}, Quarter={filing_quarter}, URL='{raw_data_url}', Filing Type='{filing_type}'")

    # # -------------------------------
    # # 3. Insert a sample security
    # # -------------------------------
    # ticker = "TEST"
    # cusip = "TESTCSP"
    # security_name = "Test Security Inc."
    # sector = "Test Sector"
    # # returns the generated security_id (or existing one if the insert conflicts)
    # security_id = insert_security(ticker, cusip, security_name, sector)
    # print(f"Inserted test security: Ticker='{ticker}', CUSIP='{cusip}', Name='{security_name}', Sector='{sector}', Security ID={security_id}")

    # # -------------------------------
    # # 4. Insert a sample holding for the filing and security just inserted
    # # -------------------------------
    # position_size = 100000
    # market_value = 123456.78
    # weight = 5.25
    # insert_holding(filing_id, security_id, position_size, market_value, weight)
    # print(f"Inserted test holding: Filing ID={filing_id}, Security ID={security_id}, Position Size={position_size}, Market Value={market_value}, Weight={weight}")

if __name__ == '__main__':
    main()
