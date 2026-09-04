# Retail ETL Project

## Project Objective

A production-level ETL (Extract, Transform, Load) pipeline built with Python for learning and interview preparation. This project demonstrates data extraction from source databases, transformation using business logic, and loading into a data warehouse.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Core programming language |
| MySQL 8.0.16+ | Source and Warehouse database |
| Pandas | Data manipulation and analysis |
| NumPy | Numerical operations |
| SQLAlchemy | Database ORM and connectivity |
| mysql-connector-python | MySQL driver |
| python-dotenv | Environment variable management |
| Faker | Test data generation |
| pytest | Unit and integration testing |
| colorama | Terminal output formatting |
| tqdm | Progress bar display |

## Prerequisites

- **MySQL 8.0.16+** is required (CHECK constraints are only enforced from this version)
- **Python 3.10+**

## Folder Structure

```
Retail_ETL_Project/
│
├── config/              # Configuration files (YAML, JSON)
├── data/
│   ├── raw/             # Raw extracted data (gitignored)
│   ├── processed/       # Transformed data (gitignored)
│   └── archive/         # Archived/historical data (gitignored)
│
├── docs/                # Project documentation
├── extract/             # Extraction modules (source → raw)
├── transform/           # Transformation modules (raw → processed)
├── load/                # Load modules (processed → warehouse)
├── logs/                # Application log files
├── reject/              # Rejected/failed records (gitignored)
├── sql/
│   ├── source/          # Source database SQL scripts
│   └── warehouse/       # Warehouse DDL and queries
│
├── tests/               # Unit and integration tests
├── utils/               # Utility/helper functions
├── warehouse/           # Warehouse schema and models
├── venv/                # Virtual environment (not in git)
│
├── main.py              # Main entry point
├── requirements.txt     # Python dependencies
├── .gitignore           # Git ignore rules
├── README.md            # Project documentation
├── config.py            # Configuration loader
└── .env.example         # Environment variable template
```

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Retail_ETL_Project
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
copy .env.example .env
```
Edit `.env` with your database credentials.

### 5. Setup Source Database

Run in MySQL Workbench (in order):
1. `sql/source/create_database.sql`
2. `sql/source/create_tables.sql`
3. `sql/source/constraints.sql`
4. `sql/source/indexes.sql`
5. `sql/source/sample_data.sql`

> **Note:** `sample_data.sql` uses `DELIMITER` blocks for stored procedures.
> It must be run via MySQL Workbench or the `mysql` CLI client.
> It cannot be executed through SQLAlchemy or mysql-connector-python.

> **Reset:** To start fresh, run `create_database.sql` which drops and recreates
> the database. None of the other scripts are re-runnable without this reset.

### 6. Run the Extraction Layer

```bash
python main.py
```

This connects to `retail_oltp`, extracts all 12 tables into DataFrames, and writes UTF-8 CSV snapshots to `data/raw/`.

### 7. Run Data Profiling & Quality Assessment

```bash
python -m profiling.profile_runner
```

Profile a single table:
```bash
python -m profiling.profile_runner --table customers
```

With verbose console output:
```bash
python -m profiling.profile_runner --verbose
```

Reports are written to `data/profiling/`. The HTML report is at:
```
data/profiling/reports/data_quality_report.html
```

## Expected Output

```
============================================================
  Retail ETL Project v1.0.0 - Extraction Layer
============================================================
[INFO] Host:         localhost:3306
[INFO] Source DB:    retail_oltp
[INFO] Log file:     logs/extract.log

Extracting source tables...
  [OK] categories     rows=    10  cols= 3  time=0.021s
  [OK] suppliers      rows=    10  cols= 7  time=0.004s
  [OK] stores         rows=     5  cols= 6  time=0.003s
  [OK] products       rows=    50  cols= 9  time=0.005s
  [OK] employees      rows=    20  cols= 7  time=0.004s
  [OK] customers      rows=   100  cols=12  time=0.008s
  [OK] inventory      rows=    60  cols= 5  time=0.005s
  [OK] orders         rows=   500  cols= 7  time=0.018s
  [OK] order_items    rows=  1193  cols=10  time=0.042s
  [OK] payments       rows=   907  cols= 6  time=0.031s
  [OK] shipments      rows=   331  cols= 7  time=0.014s
  [OK] returns        rows=   102  cols= 5  time=0.007s

Extraction Summary
| table       | rows | columns | status |
|-------------|------|---------|--------|
| categories  |   10 |       3 | OK     |
| ...         |  ... |     ... | ...    |

[INFO] Tables extracted: 12/12
[INFO] Total rows:       3,288
[INFO] CSV output:       data/raw/

[SUCCESS] Extraction completed.
```

> Row counts vary between loads because the sample data generators are randomised.

## Pipeline Stages

| Stage | Status | Docs |
|---|---|---|
| Source OLTP database | ✅ Complete | [docs/source_database_design.md](docs/source_database_design.md) |
| Extraction layer | ✅ Complete | [extract/README.md](extract/README.md) |
| Data Profiling & Quality Assessment | ✅ Complete | [docs/data_profiling.md](docs/data_profiling.md) |
| Transformation layer | 🔲 Not started | — |
| Load layer | 🔲 Not started | — |

## Database Setup

### Create a dedicated ETL user (recommended)

```sql
CREATE USER 'etl_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT SELECT ON retail_oltp.* TO 'etl_user'@'localhost';
GRANT ALL PRIVILEGES ON retail_dwh.* TO 'etl_user'@'localhost';
FLUSH PRIVILEGES;
```

## Author

Built for learning and interview preparation.

## License

MIT
