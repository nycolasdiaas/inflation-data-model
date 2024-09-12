from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.email_operator import EmailOperator
from airflow.operators.subdag_operator import SubDagOperator
from airflow.operators.postgres_operator import PostgresOperator

# Função Python simples para DAGs introdutórias
def hello_world():
    print("Hello World")

# DAG Básica
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'basic_dag',
    default_args=default_args,
    description='Uma DAG básica',
    schedule_interval=timedelta(days=1),
)

start = DummyOperator(
    task_id='start',
    dag=dag,
)

hello_task = PythonOperator(
    task_id='hello_task',
    python_callable=hello_world,
    dag=dag,
)

end = DummyOperator(
    task_id='end',
    dag=dag,
)

start >> hello_task >> end

# DAG Intermediária com Operações Bash e Email
dag_intermediate = DAG(
    'intermediate_dag',
    default_args=default_args,
    description='Uma DAG intermediária',
    schedule_interval=timedelta(days=1),
)

start_intermediate = DummyOperator(
    task_id='start_intermediate',
    dag=dag_intermediate,
)

bash_task = BashOperator(
    task_id='bash_task',
    bash_command='echo "Rodando um comando bash!"',
    dag=dag_intermediate,
)

email_task = EmailOperator(
    task_id='email_task',
    to='example@example.com',
    subject='Airflow Email',
    html_content='<p>O comando bash foi executado com sucesso!</p>',
    dag=dag_intermediate,
)

end_intermediate = DummyOperator(
    task_id='end_intermediate',
    dag=dag_intermediate,
)

start_intermediate >> bash_task >> email_task >> end_intermediate

# DAG Avançada com SubDAG e Operação no PostgreSQL
def subdag(parent_dag_name, child_dag_name, args):
    dag_subdag = DAG(
        dag_id=f'{parent_dag_name}.{child_dag_name}',
        default_args=args,
        schedule_interval=timedelta(days=1),
    )

    with dag_subdag:
        start_subdag = DummyOperator(
            task_id='start_subdag',
        )

        task_subdag = BashOperator(
            task_id='task_subdag',
            bash_command='echo "SubDAG!"',
        )

        end_subdag = DummyOperator(
            task_id='end_subdag',
        )

        start_subdag >> task_subdag >> end_subdag

    return dag_subdag

dag_advanced = DAG(
    'advanced_dag',
    default_args=default_args,
    description='Uma DAG avançada',
    schedule_interval=timedelta(days=1),
)

start_advanced = DummyOperator(
    task_id='start_advanced',
    dag=dag_advanced,
)

subdag_task = SubDagOperator(
    task_id='subdag_task',
    subdag=subdag('advanced_dag', 'subdag_task', default_args),
    dag=dag_advanced,
)

postgres_task = PostgresOperator(
    task_id='postgres_task',
    postgres_conn_id='your_postgres_connection',
    sql='''
        CREATE TABLE IF NOT EXISTS test_table (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50) NOT NULL
        );
    ''',
    dag=dag_advanced,
)

end_advanced = DummyOperator(
    task_id='end_advanced',
    dag=dag_advanced,
)

start_advanced >> subdag_task >> postgres_task >> end_advanced