from airflow import DAG
from airflow.decorators import task
from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.dates import days_ago
from airflow.models.param import Param
from datetime import datetime, timedelta
import json
import time
import re
from typing import List, Dict, Any
from requests.exceptions import HTTPError, RequestException

# Default DAG arguments
default_args = {
    'owner': 'airflow',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': False,
}

# Define DAG
with DAG(
    dag_id='adzuna_job_data_ingestion',
    default_args=default_args,
    start_date=days_ago(1),
    schedule_interval='@daily',
    catchup=False,
    params={
        'max_retries': Param(3, type='integer'),
        'retry_delay': Param(30, type='integer'),
        'batch_size': Param(50, type='integer'),
    },
) as dag:

    @task
    def create_table():
        """Creates the job_data table if it does not exist."""
        pg_hook = PostgresHook(postgres_conn_id='postgres_connection')
        create_table_query = """
            CREATE TABLE IF NOT EXISTS job_data (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                company TEXT,
                location TEXT,
                description TEXT,
                skills TEXT,
                experience_years_min INTEGER,
                experience_years_max INTEGER,
                experience_level TEXT,
                created_date TIMESTAMP NOT NULL,
                job_source TEXT NOT NULL,
                external_id TEXT NOT NULL,
                raw_data JSONB,
                CONSTRAINT unique_job UNIQUE (external_id, job_source)
            );
        """
        pg_hook.run(create_table_query)

    def extract_experience_info(description: str) -> Dict[str, Any]:
        """Extracts experience level and years from job descriptions."""
        experience_info = {'years_min': None, 'years_max': None, 'level': None}
        level_patterns = {
            'entry': r'\b(entry[ -]level|junior|fresh graduate|fresher)\b',
            'mid': r'\b(mid[ -]level|intermediate)\b',
            'senior': r'\b(senior|lead|principal)\b',
            'executive': r'\b(executive|director|head|chief|vp)\b'
        }
        years_pattern = r'(\d+)[\+]?\s*(?:-|to)?\s*(\d+)?\s*(?:years?|yrs?)(?:\s+of)?\s+experience'
        years_match = re.search(years_pattern, description.lower())
        if years_match:
            experience_info['years_min'] = int(years_match.group(1))
            experience_info['years_max'] = int(years_match.group(2)) if years_match.group(2) else experience_info['years_min']
        for level, pattern in level_patterns.items():
            if re.search(pattern, description.lower()):
                experience_info['level'] = level
                break
        return experience_info

    @task
    def extract_data(**context) -> List[Dict[str, Any]]:
        """Extract job data from Adzuna API with retries."""
        http_hook = HttpHook(http_conn_id='adzuna_api', method='GET')
        extracted_data = []
        max_retries = context['params']['max_retries']
        retry_delay = context['params']['retry_delay']
        conn = http_hook.get_connection('adzuna_api')
        app_id, app_key = conn.extra_dejson.get('app_id'), conn.extra_dejson.get('app_key')
        for role in ["Software Engineer", "Data Scientist", "Web Developer"]:
            retries = 0
            while retries <= max_retries:
                try:
                    response = http_hook.run(endpoint=f'v1/api/jobs/us/search/1', data={
                        "app_id": app_id,
                        "app_key": app_key,
                        "what": role,
                        "where": "us",
                        "max_days_old": 30,
                        "results_per_page": 50
                    })
                    extracted_data.extend(json.loads(response.text).get("results", []))
                    break
                except (HTTPError, RequestException) as e:
                    if retries == max_retries:
                        raise AirflowException(f"Failed after {max_retries} retries: {str(e)}")
                    retries += 1
                    time.sleep(retry_delay)
        return extracted_data

    @task
    def transform_data(extracted_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transforms extracted job data."""
        transformed_data = []
        for job in extracted_data:
            experience_info = extract_experience_info(job.get('description', ''))
            transformed_data.append({
                'title': job.get('title', 'N/A'),
                'company': job.get('company', {}).get('display_name', 'Unknown'),
                'location': job.get('location', {}).get('display_name', 'Unknown'),
                'description': job.get('description', ''),
                'skills': ', '.join(job.get('skill_tags', [])) if 'skill_tags' in job else 'N/A',
                'experience_years_min': experience_info['years_min'],
                'experience_years_max': experience_info['years_max'],
                'experience_level': experience_info['level'],
                'created_date': datetime.now(),
                'job_source': 'adzuna',
                'external_id': job.get('id', ''),
                'raw_data': json.dumps(job)
            })
        return transformed_data

    @task
    def load_data(transformed_data: List[Dict[str, Any]]) -> int:
        """Loads transformed data into PostgreSQL and returns the row count."""
        pg_hook = PostgresHook(postgres_conn_id='postgres_connection')
        rows_inserted = 0
        for record in transformed_data:
            insert_query = """
                INSERT INTO job_data (title, company, location, description, skills, experience_years_min, experience_years_max, experience_level, created_date, job_source, external_id, raw_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (external_id, job_source) 
                DO UPDATE SET title = EXCLUDED.title, description = EXCLUDED.description, experience_years_min = EXCLUDED.experience_years_min, experience_years_max = EXCLUDED.experience_years_max, experience_level = EXCLUDED.experience_level, raw_data = EXCLUDED.raw_data, created_date = EXCLUDED.created_date
                RETURNING id;
            """
            result = pg_hook.get_records(insert_query, parameters=tuple(record.values()))
            rows_inserted += len(result) if result else 0
        return rows_inserted

    # Define task dependencies and pass data between tasks
    create_table() >> extract_data() >> transform_data(extracted_data=extract_data()) >> load_data(transformed_data=transform_data(extracted_data=extract_data()))
