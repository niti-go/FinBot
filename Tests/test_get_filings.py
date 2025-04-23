#!/usr/bin/env python3
"""Smoke-tests for the get_filings module."""
import pandas as pd

from get_filings import (
    fetch_holdings_data,
    get_filings,
    fetch_cik_dict,
    get_all_13f_filings,
    get_sector_from_yahoo,
    get_aum_and_fund_type,
)


def test_fetch_holdings_data():
    """Fetch holdings data from a known 13F filing URL."""
    url = (
        'https://www.sec.gov/Archives/edgar/data/1652044/'
        '000156761922020202/0001567619-22-020202.txt'
    )
    df = fetch_holdings_data(url)
    print(
        '[test_fetch_holdings_data] Retrieved '
        f'{len(df)} holdings from URL: {url}'
    )
    print(df.head(3))


def test_get_filings():
    """Retrieve filings metadata for a known CIK."""
    cik = '0001652044'
    df = get_filings(cik)
    print(
        '[test_get_filings] Retrieved '
        f'{len(df)} filings for CIK {cik}'
    )
    print(df[['form', 'date', 'url']].head(3))


def test_fetch_cik_dict():
    """Fetch the SEC’s CIK→(ticker, name) mapping."""
    mapping = fetch_cik_dict()
    sample = list(mapping.items())[:5]
    print(
        '[test_fetch_cik_dict] Retrieved '
        f'{len(mapping)} CIK mappings; sample:'
    )
    for key, (ticker, name) in sample:
        print(f'{key} → {ticker}, {name}')


def test_yahoo_helpers():
    """Verify sector and AUM/fund-type lookups via Yahoo Finance."""
    ticker = 'AAPL'
    sector = get_sector_from_yahoo(ticker)
    aum_ft = get_aum_and_fund_type(ticker)
    print(
        '[test_yahoo_helpers] '
        f"{ticker} → sector='{sector}', "
        f"AUM={aum_ft['AUM']}, type={aum_ft['Fund Type']}"
    )


def test_get_all_13f_filings():
    """Fetch all 13F filings, limited to 2 CIKs for speed."""
    df = get_all_13f_filings(MAX_NUM_TO_FETCH=2)
    print(
        '[test_get_all_13f_filings] '
        f'Retrieved {len(df)} total filings across 2 CIKs'
    )
    print(df[['cik', 'date', 'url']].head(5))


if __name__ == '__main__':
    pd.set_option('display.width', 120)
    test_fetch_holdings_data()
    test_get_filings()
    test_fetch_cik_dict()
    test_yahoo_helpers()
    test_get_all_13f_filings()
    print('\n✅ All tests executed.')
