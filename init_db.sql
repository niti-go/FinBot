
CREATE TABLE InvestmentManagers (
    cik VARCHAR PRIMARY KEY,
    name VARCHAR,
    asset_size DECIMAL
);

CREATE TABLE Filings (
    filing_id BIGSERIAL PRIMARY KEY,
    manager_cik VARCHAR REFERENCES InvestmentManagers(cik),
    filing_date DATE,
    year INT,
    quarter SMALLINT,
    raw_data_url VARCHAR,
    filing_type VARCHAR
);

CREATE TABLE Securities (
    security_id SERIAL PRIMARY KEY,
    ticker VARCHAR,
    cusip VARCHAR,
    name VARCHAR,
    sector VARCHAR
);

CREATE TABLE Holdings (
    position_id SERIAL PRIMARY KEY,
    filing_id BIGINT REFERENCES Filings(filing_id),
    security_id INT REFERENCES Securities(security_id),
    position_size DECIMAL,
    market_value DECIMAL,
    weight DECIMAL
);