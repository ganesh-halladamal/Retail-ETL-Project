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

### 6. Run the Project

```bash
python main.py
```

## Expected Output

```
===========================================
       Retail ETL Project v1.0.0
  Project Initialized Successfully
===========================================

[INFO] Database Host: localhost
[INFO] Database Port: 3306
[INFO] Source DB: retail_oltp
[INFO] Warehouse DB: retail_dwh

[SUCCESS] Project setup complete. Ready for ETL development.
```

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
