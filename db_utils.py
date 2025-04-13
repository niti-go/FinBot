import psycopg2

def connect():
    return psycopg2.connect(
        dbname="finbot",
        user="your_login",  # replace with your login, run whoami in terminal
        password="",
        host="localhost",
        port="5432"
    )

def insert_investment_manager(cik, name, asset_size):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO InvestmentManagers (cik, name, asset_size)
                VALUES (%s, %s, %s)
                ON CONFLICT (cik) DO NOTHING;
            """, (cik, name, asset_size))

def insert_filing(manager_cik, filing_date, year, quarter, raw_data_url, filing_type):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO Filings (manager_cik, filing_date, year, quarter, raw_data_url, filing_type)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING filing_id;
            """, (manager_cik, filing_date, year, quarter, raw_data_url, filing_type))
            return cur.fetchone()[0]  

def insert_security(ticker, cusip, name, sector):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO Securities (ticker, cusip, name, sector)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (cusip) DO NOTHING
                RETURNING security_id;
            """, (ticker, cusip, name, sector))
            result = cur.fetchone()
            if result:
                return result[0]
            else:
                # Fetch existing security_id if already inserted
                cur.execute("SELECT security_id FROM Securities WHERE cusip = %s", (cusip,))
                return cur.fetchone()[0]

def insert_holding(filing_id, security_id, position_size, market_value, weight):
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO Holdings (filing_id, security_id, position_size, market_value, weight)
                VALUES (%s, %s, %s, %s, %s);
            """, (filing_id, security_id, position_size, market_value, weight))