# FinBot
Cornell Fintech Club Sp'25 Project

## About

A chatbot that provides financial guidance to users using Retrieval-Augmented Generation (RAG). By referencing grounded financial data, our chatbot helps users gain a fast, contextual understanding of the financial landscape.

## Contributors
PM: Kelly Lambert  
TPM: Niti Goyal  
APM: Samuel Hecht  
SWE: Jane Tenecota-Villa  
SWE: Adeeb Khan  
SWE: Noah Lingo  
SWE: Saanvi Jain

## FinBot Local Development Setup

This guide walks you through:

1. Cloning the repo  
2. Creating a Python virtual environment  
3. Installing dependencies  
4. Setting up PostgreSQL locally  
5. Populating the database  
6. Running tests  

---

## 1. Clone the repository

```bash
git clone git@github.com:niti-go/FinBot.git
cd FinBot
```

---

## 2. Create and activate a Python virtual environment

```bash
python3 -m venv venv
# macOS/Linux:
source venv/bin/activate
# Windows PowerShell:
# .\\venv\\Scripts\\activate
```

---

## 3. Install Python dependencies

Install `requirements.txt` with:

```bash
pip install -r requirements.txt
```

---

## 4. Set up PostgreSQL locally

### A. Starting PostgreSQL server manually

- **macOS (Homebrew)**:
  ```bash
  brew services start postgresql
  ```

- **Linux (systemd)**:
  ```bash
  sudo systemctl start postgresql
  ```

- **Windows (pgAdmin4 bundled service)**:
  1. Open **pgAdmin 4**.
  2. In the Browser panel, right-click **Servers** → **Create** → **Server...** and configure your local server connection if not present.

### B. Creating the database via pgAdmin 4

1. In pgAdmin's Browser, expand your server, right-click **Databases** → **Create** → **Database...**
2. In the **General** tab:
   - **Database**: `finbot`
   - **Owner**: your user (e.g. `postgres`)
3. In the **Definition** tab:
   - **Template**: `template0`
4. Click **Save**.

### C. Applying the schema

1. Right-click the new `finbot` database → **Query Tool**.
2. Open or paste the contents of `init_db.sql` into the editor.
3. Click **Execute/Refresh** (▶️) to run the script and create tables.

Verify tables via the Query Tool:

```sql
\dt
-- should list: investmentmanagers, filings, securities, holdings
```

---

## 5. Configure environment variables

Create a `.env` file:

```ini
DB_NAME=FinBot (OR WTVR YOU NAMED YOUR DB)
DB_USER=postgres (OR YOUR SERVER USERNAME
DB_PASSWORD=YOURPASSWORD
DB_HOST=localhost
DB_PORT=5432
```

---

## 6. Populate the database

```bash
# Full run (7.6k CIKs) - may take 1-2 hours
python populate_db.py

# Quick run (first 10 CIKs)
python populate_db.py --limit 10
```

---

## 7. Running tests

```bash
python Tests/test_insert.py
python Tests/test_get_filings.py
```

---

## 8. Inspect data

In pgAdmin4, view tables by clicking through Schemas --> Tables --> Right click desired table --> View/Edit Data --> All Rows

Or through query tool:
```sql
SELECT COUNT(*) FROM InvestmentManagers;
SELECT COUNT(*) FROM Filings;
SELECT COUNT(*) FROM Securities;
SELECT COUNT(*) FROM Holdings;
```
