from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable
from datetime import datetime

# Define a data de execução como uma variável para suportar reprocessamento de dias passados


execution_date = "{{ ds }}"  # Pega a data de execução do Airflow no formato YYYY-MM-DD


# Configurações padrão da DAG
DEFAULT_ARGS = {
    "owner": "Eduardo",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "catchup": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "concurrency": 1,
}

DEFAULT_TAGS = ["meltano"]
PROJECT_ROOT = os.getenv("MELTANO_PROJECT_ROOT", os.getcwd())
MELTANO_BIN = ".meltano/run/bin"

if not Path(PROJECT_ROOT).joinpath(MELTANO_BIN).exists():
    logger.warning(
        "A symlink to the 'meltano' executable could not be found at '%s'. "
        "Falling back on expecting it to be in the PATH instead. ",
        MELTANO_BIN,
    )
    MELTANO_BIN = "meltano"


# Definição da DAG
dag = DAG(
    'meltano_etl_pipeline',
    description='Pipeline de ETL usando Meltano e Airflow',
    schedule_interval='@daily',  # Executa todos os dias
    catchup=True,
)
# Step 1 - Extrair csv localmente para data/csv
extract_csv_to_csv = BashOperator(
    task_id='extract_csv_to_csv',
    bash_command=f'meltano run tap-order-list-firststep target-firststep-csv --job_id {execution_date}_step1_csv',
    dag=dag,
)

# Step 2 - Extrair dados do PostgreSQL e CSVs para o sistema de arquivos local
extract_postgres = BashOperator(
    task_id='extract_from_postgres',
    bash_command=f'meltano run tap-postgres-firststep target-postgres-to-csv --job_id {execution_date}_step1_postgres',
    dag=dag,
)

# Step 3 - Extrai order-list local para Postgres
extract_csv = BashOperator(
    task_id='extract_from_csv',
    bash_command=f'meltano run tap-order-list-secondstep target-postgres --job_id {execution_date}_step2_csv',
    dag=dag,
)

# Step 4 - Carregar dados do sistema de arquivos local para o PostgreSQL
load_to_postgres = BashOperator(
    task_id='load_to_postgres',
    bash_command=f'meltano run tap-localfiles-postgrees target-postgres --job_id {execution_date}_step2_load',
    dag=dag,
)

# Step 5 - Gerar evidência de execução bem-sucedida
generate_evidence = BashOperator(
    task_id='generate_evidence',
    bash_command=f'psql -h localhost -U postgres -d northwind -c "SELECT * FROM orders LIMIT 50" -o ./data/evidence_{execution_date}.csv',
    dag=dag,
)

# Definição da ordem de execução
[extract_postgres, extract_csv] >> load_to_postgres >> generate_evidence
