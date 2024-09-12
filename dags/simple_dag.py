from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

# Função Python que será chamada pela tarefa
def hello_world():
    print("Hello, World!")

# Definindo os argumentos padrão para a DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 8, 5),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Criando a DAG
dag = DAG(
    'simple_hello_dag',
    default_args=default_args,
    description='Uma DAG simples que imprime Hello, World!',
    schedule_interval=timedelta(days=1),  # Executa diariamente
)

# Definindo a tarefa
hello_task = PythonOperator(
    task_id='hello_task',
    python_callable=hello_world,
    dag=dag,
)

# A DAG é composta por uma única tarefa
