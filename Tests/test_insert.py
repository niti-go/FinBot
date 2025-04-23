#!/usr/bin/env python3
"""Smoke-tests for the db_utils insert functions."""
from db_utils import (
    insert_filing,
    insert_holding,
    insert_investment_manager,
    insert_security,
)


def test_insert_all():
    """Insert sample data into each of the four tables."""
    # 1) Investment manager
    manager_cik = '1234567890'
    manager_name = 'Test Fund'
    asset_size = 5_000_000_000
    insert_investment_manager(manager_cik, manager_name, asset_size)
    print(
        f'Inserted test investment manager: '
        f'CIK={manager_cik}, Name={manager_name}, '
        f'Asset Size={asset_size}'
    )

    # 2) Filing
    filing_date = '2025-04-15'
    year = 2025
    quarter = 2
    raw_url = 'http://example.com/test_filing'
    filing_type = '13F'
    filing_id = insert_filing(
        manager_cik,
        filing_date,
        year,
        quarter,
        raw_url,
        filing_type,
    )
    print(
        f'Inserted test filing: ID={filing_id}, '
        f'Date={filing_date}, Q{quarter}-{year}, '
        f'Type={filing_type}'
    )

    # 3) Security
    ticker = 'TEST'
    cusip = 'TESTCSP'
    security_name = 'Test Security Inc.'
    sector = 'Test Sector'
    security_id = insert_security(
        ticker,
        cusip,
        security_name,
        sector,
    )
    print(
        f'Inserted test security: Ticker={ticker}, '
        f'CUSIP={cusip}, Name={security_name}, '
        f'Sector={sector}, Security ID={security_id}'
    )

    # 4) Holding
    position_size = 100_000
    market_value = 123_456.78
    weight = 5.25
    insert_holding(
        filing_id,
        security_id,
        position_size,
        market_value,
        weight,
    )
    print(
        f'Inserted test holding: Filing ID={filing_id}, '
        f'Security ID={security_id}, '
        f'Position Size={position_size}, '
        f'Market Value={market_value}, Weight={weight}'
    )


if __name__ == '__main__':
    test_insert_all()
