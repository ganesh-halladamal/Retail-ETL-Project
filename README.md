# Retail ETL Project

## Project Objective

A production-level ETL (Extract, Transform, Load) pipeline built with Python for learning and interview preparation. This project demonstrates data extraction from source databases, transformation using business logic, and loading into a data warehouse.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Core programming language |
| Pandas | Data manipulation and analysis |
| NumPy | Numerical operations |
| SQLAlchemy | Database ORM and connectivity |
| MySQL | Source and Warehouse database |
| python-dotenv | Environment variable management |
| Faker | Test data generation |
| pytest | Unit and integration testing |
| colorama | Terminal output formatting |
| tqdm | Progress bar display |

## Folder Structure

```
Retail_ETL_Project/
│
├── config/              # Configuration files (YAML, JSON)
├── data/
│   ├── raw/             # Raw extracted data
│   ├── processed/       # Transformed data ready for loading
│   └── archive/         # Archived/historical data
│
├── docs/                # Project documentation
├── extract/             # Extraction modules (source → raw)
├── transform/           # Transformation modules (raw → processed)
├── load/                # Load modules (processed → warehouse)
├── logs/                # Application log files
├── reject/              # Rejected/failed records
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
cp .env.example .env
# Edit .env with your database credentials
```

### 5. Run the Project

```bash
python main.py
```

## Expected Output

```
===========================================
       Retail ETL Pipeline
  Project Initialized Successfully
===========================================

[INFO] Database Host: localhost
[INFO] Database Port: 3306
[INFO] Source DB: Not Configured
[INFO] Warehouse DB: Not Configured

[SUCCESS] Project setup complete. Ready for ETL development.
```

## Author

Built for learning and interview preparation.

## License

MIT
