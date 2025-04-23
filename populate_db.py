#!/usr/bin/env python3
"""Populate the FinBot PostgreSQL database with SEC 13F filings data."""

import os
import re
import argparse

from dotenv import load_dotenv

from get_filings import get_all_13f_filings
from db_utils import (
    insert_investment_manager,
    insert_filing,
    insert_security,
    insert_holding,
)


def parse_aum(aum_str):
    """Convert strings like '$12.34B' into a numeric AUM value.

    Returns:
        float: Assets under management in dollars, or None on parse failure.
    """
    if not isinstance(aum_str, str):
        return None

    match = re.match(r'^\$(\d+(?:\.\d+)?)B$', aum_str)
    if match:
        return float(match.group(1)) * 1e9

    return None


def run(max_num_to_fetch):
    """Fetch filings and populate the database.

    Args:
        max_num_to_fetch (int): Maximum number of CIKs to process (0 = no limit).
    """
    print('▶️  Loading environment variables from .env')
    load_dotenv()

    print('▶️  Fetching 13F filings…')
    df = get_all_13f_filings(MAX_NUM_TO_FETCH=max_num_to_fetch)

    # Rename columns to valid Python identifiers
    df.rename(
        columns={
            'Institution Name': 'institution_name',
            'Assets Under Management (AUM)': 'aum_str',
        },
        inplace=True,
    )

    total = len(df)
    print(f'Fetched {total} filings in total')

    for idx, row in enumerate(df.itertuples(), start=1):
        cik = row.cik
        name = row.institution_name
        aum = parse_aum(row.aum_str)

        insert_investment_manager(cik, name, aum)
        print(f'[{idx}/{total}] Manager upserted: CIK={cik}, Name={name}, AUM={aum}')

        filing_date = row.date
        year = int(filing_date[:4])
        month = int(filing_date[5:7])
        quarter = (month - 1) // 3 + 1
        filing_id = insert_filing(
            cik,
            filing_date,
            year,
            quarter,
            row.text_url,
            row.form,
        )
        print(
            f'    ↳ Filing inserted: ID={filing_id}, '
            f'Date={filing_date}, Q{quarter}-{year}'
        )

        holdings = row.data.to_dict(orient='records')
        for holding in holdings:
            security_id = insert_security(
                None,
                holding.get('cusip'),
                holding.get('issuer_name'),
                None,
            )
            insert_holding(
                filing_id,
                security_id,
                holding.get('shares'),
                holding.get('value'),
                None,
            )

        print(f'    ↳ Inserted {len(holdings)} holdings for filing {filing_id}\n')

    print('✅ Database population complete.')


def main():
    """Parse CLI arguments and invoke run()."""
    parser = argparse.ArgumentParser(
        description='Populate PostgreSQL with SEC 13F filings data.'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=0,
        help='Max number of CIKs to fetch (0 = no limit)',
    )
    args = parser.parse_args()

    run(max_num_to_fetch=args.limit)


if __name__ == '__main__':
    main()
