# Pipeline para o Banco BanVic

## Introdução

Este projeto simula a criação do pipeline de dados (ETL) para o banco fictício "BanVic". O objetivo é extrair dados de diferentes sistemas de origem, centralizá-los em um Data Warehouse e orquestrar todo o processo de forma automatizada, robusta e diária.

## Arquitetura da Solução

O pipeline foi construído utilizando uma arquitetura moderna e containerizada com Docker, garantindo total reprodutibilidade do ambiente.

- **Fontes de Dados**:
  1.  **Banco de Dados Relacional (PostgreSQL)**: Contém dados cadastrais de agências, clientes, colaboradores, contas e propostas de crédito.
  2.  **Arquivo de Transações (CSV)**: Um arquivo com o histórico de transações financeiras.
- **Orquestração**:
  - **Apache Airflow** Utilizado para agendar, executar e monitorar todo o fluxo de trabalho (DAG).
- **Data Lake Local**:
  - Um diretório no File System local (`data_lake/`) é usado para armazenar os dados extraídos no formato CSV, seguindo um particionamento por data.
- **Data Warehouse**:
  - Um banco de dados **PostgreSQL**, rodando em um contêiner Docker separado, serve como o Data Warehouse de destino, onde os dados são consolidados.

![Diagrama da Arquitetura](diagrama.png)

## Pré-requisitos

Para executar este projeto, você precisará ter os seguintes softwares instalados:

- **WSL2 (Windows Subsystem for Linux)**: Recomendado para usuários Windows, garantindo compatibilidade e performance.
- **Docker e Docker Compose**: Para a criação e gerenciamento dos contêineres.

## Estrutura do Projeto

O projeto está organizado da seguinte forma:

```
desafio_banvic/
|
├── dags/
|   └── banvic_etl_dag.py  # Script da DAG do Airflow
|
├── data_lake/             # Diretório onde os CSVs extraídos são salvos
|
├── source_data/
|   ├── banvic.sql         # Script de criação do banco de dados de origem
|   └── transacoes.csv     # Arquivo de dados de origem
|
├── .dockerignore
├── .gitignore
└── docker-compose.yml     # Arquivo de orquestração dos contêineres
```

## Setup e Execução

Siga os passos abaixo para executar o pipeline:

**1. Clone ou Faça o Download do Projeto:**
   Garanta que todos os arquivos estejam na estrutura de pastas descrita acima.
   **Importante para usuários WSL:** Certifique-se de que a pasta do projeto esteja dentro do sistema de arquivos do Linux (ex: `/home/seu_usuario/`) e não em uma pasta do Windows (ex: `/mnt/c/Users/...`).

**2. Ajuste as Permissões das Pastas (Apenas para Linux/WSL):**
   Para permitir que o contêiner do Airflow escreva na sua máquina local, execute o seguinte comando na raiz do projeto:
   ```bash
   sudo chmod -R 777 data_lake source_data
   ```

**3. Inicie os Serviços com Docker Compose:**
   Navegue até a pasta raiz do projeto no seu terminal e execute:
   ```bash
   docker-compose up -d
   ```
   Aguarde alguns minutos para que o Docker baixe as imagens e inicialize todos os serviços.

**4. Acesse a Interface do Airflow:**
   - Abra seu navegador e acesse: `http://localhost:8080`
   - Use as seguintes credenciais para fazer login:
     - **Usuário**: `admin`
     - **Senha**: `admin`

**5. Ative e Execute a DAG:**
   - Na página inicial, encontre a DAG `banvic_etl_pipeline`.
   - Ative-a usando o botão de alternância à esquerda.
   - Para uma execução de teste, clique no ícone de "Play" (▶️) à direita e depois em "Trigger DAG".
   - Você pode acompanhar o progresso em tempo real clicando no nome da DAG e acessando a "Grid View".

## Verificação dos Resultados

Após a execução bem-sucedida da DAG (todas as tarefas em verde escuro), você pode verificar os resultados:

**1. Arquivos no Data Lake:**
   - Navegue até a pasta `data_lake/` no seu projeto.
   - Uma nova pasta com a data da execução terá sido criada (ex: `2024-09-14/`).
   - Dentro dela, as subpastas `postgres_source` e `csv_source` conterão os arquivos `.csv` extraídos.

**2. Dados no Data Warehouse:**
   - Conecte-se ao banco de dados do Data Warehouse usando sua ferramenta preferida (DBeaver, DataGrip, etc.).
   - **Detalhes da Conexão:**
     - **Host**: `localhost`
     - **Porta**: `55433`
     - **Banco de Dados**: `banvic_dw`
     - **Usuário**: `dw_admin`
     - **Senha**: `dw_password`
   - Você verá as tabelas (`agencias`, `clientes`, `transacoes`, etc.) criadas e preenchidas com os dados.