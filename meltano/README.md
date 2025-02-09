# Documentação: Configuração do Ambiente Meltano

## 1. Acesso ao Terminal Linux (Ubuntu)

Certifique-se de acessar um terminal no ambiente Linux (Ubuntu) para executar os seguintes comandos.

## 2. Verificação e Instalação do Python 3.8

Verifique se o Python 3.8 está instalado:

```bash
python3.8 --version
```

Caso não esteja instalado, instale-o com:

```bash
sudo apt update
sudo apt install python3.8
```

## 3. Criação do Ambiente Virtual

Crie um ambiente virtual utilizando a versão do Python 3.8:

```bash
python3.9 -m venv desafio_indicium
```

Ative o ambiente virtual:

```bash
source desafio_indicium/bin/activate
```

## 4. Configuração do PostgreSQL

Certifique-se de que o PostgreSQL está instalado e configurado com as seguintes credenciais:

- **Host**: localhost
- **Port**: 5432
- **User**: postgres
- **Password**: 12345
- **Database**: northwind

Caso precise instalar o PostgreSQL, utilize:

```bash
sudo apt install postgresql postgresql-contrib
```

Para acessar o PostgreSQL e criar o banco de dados:

```bash
sudo -u postgres psql
CREATE DATABASE northwind;
ALTER USER postgres WITH PASSWORD '12345';
\q
```

## 5. Instalação do Framework Meltano

Instale o Meltano no ambiente virtual:

```bash
pip install "meltano"
```

## 6. Clonagem do Projeto

Acesse a pasta `indicium_challenge` e clone o repositório:

```bash
git clone https://github.com/EduardoDev94/code-challenge
```

Acesse a pasta `Meltano` dentro do repositório clonado:

```bash
cd code-challenge/Meltano
```

## 7. Instalação de Dependências para Manipulação de Dados

Adicione os plugins necessários:

```bash
meltano add loader target-csv
meltano add loader target-postgres
meltano add extractor tap-csv
meltano add extractor tap-postgres
```

Instale todas as dependências:

```bash
meltano install
```

## 8. Executando Fluxos de ETL Manualmente

**(Certifique-se de que o PostgreSQL está rodando com as credenciais configuradas)**

### 8.1 Recupera o CSV e carrega na pasta `data/csv`

```bash
meltano run tap-order-list-firststep target-firststep-csv
```

### 8.2 Carrega os dados do PostgreSQL e salva em tabelas `.csv`

```bash
meltano run tap-postgres-firststep target-postgres-to-csv
```

### 8.3 Recupera os arquivos `.csv` e adiciona ao PostgreSQL

```bash
meltano run tap-localfiles-postgrees target-postgres
```

### 8.4 Recupera os arquivos da `order list` e salva no PostgreSQL

```bash
meltano run tap-order-list-secondstep target-postgres
```
### 8.5 Consulta Final: Pedidos e Detalhes  

A seguinte consulta SQL combina os pedidos extraídos do banco **PostgreSQL** com os detalhes dos pedidos extraídos do **CSV**:  

```sql
SELECT 
    o.order_id, 
    o.customer_id, 
    o.order_date, 
    od.product_id, 
    od.unit_price, 
    od.quantity, 
    od.discount
FROM orders o
JOIN order_details od ON o.order_id = od.order_id;

## 9. Adição do Plugin do Airflow

Adicione o Airflow ao Meltano:

```bash
meltano add utility airflow
```

Inicialize o Airflow:

```bash
meltano invoke airflow:initialize
```

## 10. Criação de Usuário Admin no Airflow

Crie um usuário administrador:

```bash
meltano invoke airflow users create \
    --username admin \
    --firstname Peter \
    --lastname Parker \
    --role Admin \
    --email spiderman@superhero.org \
    --password 12345
```

## 11. Inicialização do Servidor Airflow

Inicie o servidor do Airflow:

```bash
meltano invoke airflow webserver
```

Acesse o navegador e abra:

```
http://localhost:8080/login/
```

Utilize as credenciais para login:

- **Usuário**: admin
- **Senha**: 12345

