terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 2.13.0"
    }
  }
}

provider "docker" {
  host = "unix:///var/run/docker.sock"
}

resource "docker_network" "airflow_network" {
  name = "airflow_network"
}

resource "docker_volume" "airflow_volume" {
  name = "airflow_volume"
}

resource "docker_volume" "pgdata" {
  name = "pgdata"
}

resource "docker_container" "postgres" {
  image   = "postgres:13"
  name    = "postgres"
  restart = "always"

  env = [
    "POSTGRES_USER=airflow",
    "POSTGRES_PASSWORD=airflow",
    "POSTGRES_DB=airflow"
  ]

  networks_advanced {
    name = docker_network.airflow_network.name
  }

  mounts {
    target = "/var/lib/postgresql/data"
    source = docker_volume.pgdata.name
    type   = "volume"
  }

  ports {
    internal = 5432
    external = 5432
  }
}

resource "docker_container" "airflow" {
  image   = "apache/airflow:2.3.0"
  name    = "airflow"
  restart = "always"

  networks_advanced {
    name = docker_network.airflow_network.name
  }

  mounts {
    target = "/opt/airflow/dags" # O caminho padrão onde o Airflow procura as DAGs
    source = "/home/nycolas/inflation-project/dags" # O caminho no seu WSL2
    type   = "bind" # Use "bind" para montar um diretório do host
  }


  ports {
    internal = 8080
    external = 8080
  }

  env = [
    "AIRFLOW__CORE__EXECUTOR=LocalExecutor",
    "AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres:5432/airflow",
    "AIRFLOW__WEBSERVER__AUTHENTICATE=True",
    "AIRFLOW__WEBSERVER__AUTH_BACKEND=airflow.contrib.auth.backends.password_auth"
  ]

  depends_on = [docker_container.postgres]

  entrypoint = [
    "/bin/bash",
    "-c",
    "airflow db init && airflow users create --username admin --firstname FIRST_NAME --lastname LAST_NAME --role Admin --email admin@example.com --password admin_password && airflow webserver"
  ]
}