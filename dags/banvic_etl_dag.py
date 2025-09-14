from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from pendulum import datetime
import pandas as pd
import os
import shutil

# Definição das conexões criadas no docker-compose.yml
POSTGRES_SOURCE_CONN_ID = "postgres_source"
POSTGRES_DW_CONN_ID = "postgres_dw"

# O caminho base onde os arquivos CSV serão salvos
DATA_LAKE_PATH = "/opt/airflow/data_lake"

# Lista de tabelas a serem extraídas do banco de dados de origem
TABLES_TO_EXTRACT = [
  "agencias",
  "clientes",
  "colaboradores",
  "contas",
  "propostas_credito",
]

@dag(
  dag_id="banvic_etl_pipeline",
  start_date=datetime(2024, 1, 1),

  # Executa diariamente às 04:35 da manhã (UTC)
  schedule_interval="35 4 * * *",
  catchup=False,
  tags=["banvic", "etl"],
  doc_md="DAG para extrair dados do BanVic e carregar em um Data Warehouse.",
)

def banvic_etl_pipeline():

    @task
    def extract_from_postgres():
    
        # Hook para se conectar ao banco de dados de origem
        hook = PostgresHook(postgres_conn_id=POSTGRES_SOURCE_CONN_ID)
        
        # Pega a data de execução para criar o nome da pasta (ex: 2024-09-08)
        execution_date = "{{ ds }}"

        output_dir = os.path.join(DATA_LAKE_PATH, execution_date, "postgres_source")
        os.makedirs(output_dir, exist_ok=True)

        print(f"Iniciando extração de tabelas para a pasta: {output_dir}")

        for table_name in TABLES_TO_EXTRACT:
            print(f"Extraindo tabela: {table_name}")

            # Usa o pandas para ler os dados da tabela
            df = hook.get_pandas_df(sql=f"SELECT * FROM {table_name};")
            
            # Define o caminho completo do arquivo de saída
            output_file = os.path.join(output_dir, f"{table_name}.csv")
            
            # Salva o DataFrame como CSV sem o índice
            df.to_csv(output_file, index=False)

            print(f"Tabela {table_name} salva em {output_file}")
            
        return output_dir

    @task
    def extract_from_csv_file():
       
        source_file_path = "/opt/airflow/source_data/transacoes.csv"
        
        execution_date = "{{ ds }}"
        output_dir = os.path.join(DATA_LAKE_PATH, execution_date, "csv_source")
        os.makedirs(output_dir, exist_ok=True)
        
        destination_file_path = os.path.join(output_dir, "transacoes.csv")
        
        print(f"Copiando {source_file_path} para {destination_file_path}")
        shutil.copy(source_file_path, destination_file_path)
        
        return output_dir

    @task
    def load_to_data_warehouse(postgres_output_dir: str, csv_output_dir: str):
      
        hook = PostgresHook(postgres_conn_id=POSTGRES_DW_CONN_ID)
        engine = hook.get_sqlalchemy_engine()
        
        # Lista de todas as pastas que contêm os CSVs a serem carregados
        folders_to_process = [postgres_output_dir, csv_output_dir]
        
        print("Iniciando carregamento para o Data Warehouse...")
        
        for folder in folders_to_process:
            for filename in os.listdir(folder):
                if filename.endswith(".csv"):
                    filepath = os.path.join(folder, filename)
                    table_name = filename.replace(".csv", "")
                    
                    print(f"Carregando {filename} para a tabela {table_name}...")
                    
                    # Usa o pandas para ler o CSV e o to_sql para inserir no banco
                    df = pd.read_csv(filepath)

                    df.to_sql(
                        name=table_name,
                        con=engine,
                        schema="public",
                        if_exists="replace",
                        index=False,
                    )
                    print(f"Tabela {table_name} carregada com sucesso.")


    # Define o fluxo das tarefas
    postgres_extraction_output = extract_from_postgres()
    csv_extraction_output = extract_from_csv_file()
    
    # A tarefa de carregamento depende das duas extrações
    load_to_data_warehouse(postgres_extraction_output, csv_extraction_output)


# Instancia a DAG para que o Airflow possa encontrá-la
banvic_etl_pipeline()