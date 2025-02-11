# 🚀 Adzuna Job Data Ingestion Pipeline

[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/austinLorenzMccoy)

## 📌 Project Overview
This project is a fully automated **ETL (Extract, Transform, Load) pipeline** built with **Apache Airflow** to extract job data from the **Adzuna API**, transform the data, and load it into a **PostgreSQL** database. The stored data can be viewed using **SQLECTRON** for analysis. The pipeline ensures robust error handling and retry mechanisms, making it resilient to failures.

## 📖 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Technologies](#technologies)
- [Setup Instructions](#setup-instructions)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Project](#running-the-project)
- [Configuration](#configuration)
- [DAG Details](#dag-details)
- [Database Schema](#database-schema)
- [Verifying API Connection](#verifying-api-connection)
- [Contributing](#contributing)

## 🌐 GitHub Repository
Find the source code and contribute on GitHub:  
[https://github.com/austinLorenzMccoy](https://github.com/austinLorenzMccoy)

## 🏗️ Architecture
### System Components
- **Apache Airflow** for orchestrating ETL workflows.
- **PostgreSQL** for storing transformed job data.
- **Astronomer (Astro CLI)** for local Airflow management.
- **SQLECTRON** for querying and viewing stored data.

### High-Level Flow
1. **Extract**: Fetch job postings from Adzuna API.
2. **Transform**: Clean and structure the data, extract experience levels.
3. **Load**: Store the refined job data in PostgreSQL.
4. **View**: Query and analyze the data using SQLECTRON.

## ⚙️ Technologies Used
- **Apache Airflow**: Task scheduling & workflow automation.
- **PostgreSQL**: Database for structured job data storage.
- **Python**: Data extraction and transformation logic.
- **Docker & Astro CLI**: Containerization & workflow management.
- **SQLECTRON**: UI tool for database query visualization.

## 🔥 Setup Instructions
### Prerequisites
- [Docker](https://www.docker.com/)
- [Astronomer CLI](https://docs.astronomer.io/astro/install-cli)
- [SQLECTRON](https://sqlectron.github.io/)

### Installation & Run
#### 🚀 Start the Environment
```sh
astro dev start
```
#### 🌍 Access Airflow Web UI
- Open: [http://localhost:8080](http://localhost:8080)
- **Username/Password**: `admin` / `admin`

#### 📊 View Data in SQLECTRON
1. Open **SQLECTRON**.
2. Create a PostgreSQL connection:
   - **Host**: `localhost`
   - **Port**: `5433`
   - **Database**: `airflow`
   - **User**: `postgres`
   - **Password**: `postgres`
3. Connect and run SQL queries.

## 🔧 Configuration
### Environment Variables
Set these in `astro config.yaml`:
- **Database**: `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- **Airflow**: `AIRFLOW__CORE__SQL_ALCHEMY_CONN`

### API Connection (Adzuna)
1. Go to **Admin > Connections** in Airflow UI.
2. Create a new connection:
   - **Conn ID**: `adzuna_api`
   - **Conn Type**: `HTTP`
   - **Extra**:
   ```json
   {
       "app_id": "your_app_id",
       "app_key": "your_app_key"
   }
   ```

## 📜 DAG Details
### Tasks Overview
1. **`create_table()`**: Creates the `job_data` table in PostgreSQL.
2. **`extract_data()`**: Fetches job listings from the Adzuna API.
3. **`transform_data()`**: Parses job descriptions for experience years and levels.
4. **`load_data()`**: Inserts cleaned data into PostgreSQL.

Task Execution Order:
- `create_table` → `extract_data` → `transform_data` → `load_data`

## 🗄️ Database Schema
### `job_data` Table
| Column                  | Type       | Description                                     |
|-------------------------|------------|-------------------------------------------------|
| `id`                    | `SERIAL`   | Primary key.                                    |
| `title`                 | `TEXT`     | Job title.                                      |
| `company`               | `TEXT`     | Hiring company name.                            |
| `location`              | `TEXT`     | Job location.                                   |
| `description`           | `TEXT`     | Full job description.                           |
| `skills`                | `TEXT`     | Required skills (comma-separated).              |
| `experience_years_min`  | `INTEGER`  | Minimum experience required.                    |
| `experience_years_max`  | `INTEGER`  | Maximum experience required.                    |
| `experience_level`      | `TEXT`     | Entry, mid, senior, executive level.            |
| `created_date`          | `TIMESTAMP`| Job posting date.                               |
| `job_source`            | `TEXT`     | Data source (Adzuna).                           |
| `external_id`           | `TEXT`     | Unique identifier from Adzuna API.              |
| `raw_data`              | `JSONB`    | Raw JSON data from API response.                |

## 🔍 Verifying API Connection
To test the API manually:
```sh
curl -X GET "https://api.adzuna.com/v1/api/jobs/gb/search/1?app_id=your_app_id&app_key=your_app_key&what=Python&where=gb"
```

If the response is **400 Bad Request**, check:
- API credentials (`app_id`, `app_key`).
- Required parameters (`what`, `where`).

## 🤝 Contributing
We welcome contributions! Please fork the repository, make your changes, and submit a pull request.

## 🚀 Deployment & Maintenance
### ⏸ Stop Services
```sh
astro dev stop
```

### 🔄 Restart Services
```sh
astro dev restart
```

### 🗑 Remove All Containers
```sh
astro dev kill
```

## 🛠 Troubleshooting
### Port Conflict (PostgreSQL)
Modify `astro config.yaml` to update port mappings if necessary.

### Debugging DAG Issues
- View Airflow logs:
```sh
astro dev logs
```
- Check DAG execution status in Airflow UI.

### SQLECTRON Connection Issues
- Ensure PostgreSQL is running with the correct port (`5433`).
- Verify credentials in SQLECTRON match those in `astro config.yaml`.

💡 *Happy Coding! 🚀*
```

---

### How to Use This Updated README

1. **Update Repository URL (Optional):**  
   If your project repository is within your GitHub profile (for example, `https://github.com/austinLorenzMccoy/adzuna-job-data-ingestion-pipeline`), update the GitHub link in both the badge and the "GitHub Repository" section.

2. **Commit & Push:**  
   Save the file as `README.md` in your repository root, commit your changes, and push them to GitHub.