from mysql.connector.pooling import MySQLConnectionPool
import psycopg2
import psycopg2.pool as pool
from mysql.connector.pooling import MySQLConnectionPool
import sqlite3
import os
class DBManager:
    def __init__(self, db_type, **kwargs):
        """
        Inicializa o gerenciador de banco de dados.

        Args:
            db_type (str): Tipo de banco de dados ("sqlite", "mysql" ou "postgresql").
            **kwargs: Argumentos adicionais específicos do tipo de banco de dados.

        Keyword Args:
            db_path (str): Caminho para o arquivo do banco de dados SQLite (apenas para SQLite).
            host (str): Host do servidor de banco de dados (para MySQL e PostgreSQL).
            user (str): Nome de usuário do banco de dados (para MySQL e PostgreSQL).
            password (str): Senha do banco de dados (para MySQL e PostgreSQL).
            database (str): Nome do banco de dados (para MySQL e PostgreSQL).
            pool_size (int, optional): Tamanho do pool de conexões (para MySQL e PostgreSQL). 
                                        O padrão é 3.
        Raises:
            ValueError: Se o tipo de banco de dados for inválido.
        """
        self.db_type = db_type
        self.connection_pool = None

        if db_type == "sqlite":
            self.db_path = kwargs.get("db_path")
        elif db_type in ("mysql", "postgresql"):
            self.host = kwargs.get("host")
            self.user = kwargs.get("user")
            self.password = kwargs.get("password")
            self.database = kwargs.get("database")
            self.pool_size = kwargs.get("pool_size", 3)
            self.criar_pool_conexao()
        else:
            raise ValueError(f"Tipo de banco de dados inválido: {db_type}")
        
    def criar_pool_conexao(self):
            def criar_pool_conexao(self):         
                if self.db_type == "mysql":
                    self.connection_pool = MySQLConnectionPool(
                        pool_name="MySQL_pool",
                        pool_size=self.pool_size,
                        host=self.host,
                        user=self.user,
                        password=self.password,
                        database=self.database,
                        min_conn=2,
                        max_conn=2,
                        idle_timeout=120,
                        max_overflow=10,
                        timeout=300
                    )
                elif self.db_type == "postgresql":
                    dsn = f"dbname={self.database} user={self.user} password={self.password} host={self.host}"

                    self.connection_pool = pool.SimpleConnectionPool(
                        minconn=2, maxconn=self.pool_size, dsn=dsn
                    )

            # Crie a string de conexão
            dsn = f"dbname={self.database} user={self.user} password={self.password} host={self.host}"

            # Crie o pool de conexões
            self.connection_pool = pool.SimpleConnectionPool(
                minconn=2, maxconn=self.pool_size, dsn=dsn
            )

    def carregar_dados(self, nome_banco, caminho_banco):
        """
        Carrega dados do banco de dados.

        Args:
            nome_banco (str): Nome do banco de dados.
            caminho_banco (str): Caminho para o arquivo do banco de dados SQLite (apenas para SQLite).

        Returns:
            list: Uma lista de tuplas contendo os dados, ou None em caso de erro.
        
        Raises:
            ValueError: Se o tipo de banco de dados for inválido.
        """
        if self.db_type == "sqlite":
            try:
                connection = sqlite3.connect(caminho_banco)
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM dados_treinamento")  # Substitua 'dados_treinamento' pelo nome da sua tabela
                dados = cursor.fetchall()
                return dados
            except Exception as e:
                print(f"Erro ao carregar dados do SQLite: {e}")
                return None
            finally:
                if connection:
                    cursor.close()
                    connection.close()
        elif self.db_type in ("mysql", "postgresql"):
            try:
                connection = self.connection_pool.get_connection()
                cursor = connection.cursor()
                cursor.execute(f"USE {nome_banco}")  # Seleciona o banco de dados
                cursor.execute("SELECT * FROM sua_tabela")  # Substitua 'sua_tabela' pelo nome da tabela
                dados = cursor.fetchall()
                return dados
            except Exception as e:
                print(f"Erro ao carregar dados do MySQL/PostgreSQL: {e}")
                return None
            finally:
                if connection:
                    cursor.close()
                    self.connection_pool.put_connection(connection)
        else:
            raise ValueError(f"Tipo de banco de dados inválido: {self.db_type}")
        
    def descartar_banco_temporario(self, nome_banco, caminho_banco):

        """
        Descarta um banco de dados temporário.

        Args:
            nome_banco (str): Nome do banco de dados temporário.
            caminho_banco (str): Caminho para o arquivo do banco de dados SQLite 
                                 (apenas para SQLite).
        """
        if self.db_type == "sqlite":
            try:
                os.remove(caminho_banco)
                print(f"Banco de dados SQLite temporário '{caminho_banco}' removido com sucesso.")
            except OSError as e:
                print(f"Erro ao remover o banco de dados SQLite temporário '{caminho_banco}': {e}")
        elif self.db_type in ("mysql", "postgresql"):
            try:
                connection = self.connection_pool.get_connection()
                cursor = connection.cursor()
                cursor.execute(f"DROP DATABASE IF EXISTS {nome_banco}")
                connection.commit()
                print(f"Banco de dados temporário '{nome_banco}' removido com sucesso.")
            except Exception as e:
                print(f"Erro ao remover o banco de dados temporário '{nome_banco}': {e}")
            finally:
                if connection:
                    cursor.close()
                    self.connection_pool.put_connection(connection)

    def criar_banco_de_dados(self, banco_permanente_existente=None, escolha_usuario=None, separate_docker=False, docker_manager=None):
        """
        Cria e conecta a um banco de dados.

        Args:
            banco_permanente_existente (str, optional): Nome do banco de dados permanente existente.
            escolha_usuario (str, optional): Escolha do usuário para o tipo de banco de dados ("mysql", "postgresql", "sqlite").
            separate_docker (bool, optional): Se True, cria um contêiner Docker separado para o banco de dados.
            docker_manager (DockerManager, optional): Instância do DockerManager para gerenciar o contêiner Docker.

        Returns:
            connection: Objeto de conexão com o banco de dados.

        Raises:
            Database_connection_error: Se não for possível conectar a nenhum banco de dados.
        """
        connection = None
        error_message = None

        # Etapa 1: Tentar conectar ao banco de dados permanente
        if banco_permanente_existente:
            for db_type in ["mysql", "postgresql", "sqlite"]:
                try:
                    self.db_type = db_type
                    if db_type == "mysql":
                        self.criar_pool_conexao()
                        connection = self.connection_pool.get_connection()
                        cursor = connection.cursor()
                        cursor.execute(f"USE {banco_permanente_existente}")
                        connection.commit()
                    elif db_type == "postgresql":
                        self.criar_pool_conexao()
                        connection = self.connection_pool.get_connection()
                        cursor = connection.cursor()
                        cursor.execute(f"SELECT datname FROM pg_database WHERE datname = '{banco_permanente_existente}'")
                        if not cursor.fetchone():
                            raise Exception(f"Banco de dados PostgreSQL '{banco_permanente_existente}' não encontrado.")
                    elif db_type == "sqlite":
                        connection = sqlite3.connect(banco_permanente_existente)
                        cursor = connection.cursor()
                    print(f"Conectado ao banco de dados permanente {db_type.upper()}: {banco_permanente_existente}")
                    break  # Conexão bem-sucedida
                except Exception as e:
                    error_message = f"Erro ao conectar ao banco de dados permanente {db_type.upper()}: {e}"
                    with open("erro.log", "a") as f:
                        f.write(f"{error_message}\n")
                    connection = None

        # Etapa 2: Usar a escolha do usuário ou criar um banco de dados SQLite
        if not connection:
            if escolha_usuario in ("mysql", "postgresql", "sqlite"):
                self.db_type = escolha_usuario
                if escolha_usuario == "sqlite":
                    # Criar um novo banco de dados SQLite
                    db_path = os.path.join(self.permanent_db_dir, "main_db.db")
                    connection = sqlite3.connect(db_path)
                    print(f"Novo banco de dados SQLite criado: {db_path}")
                else:
                    # Criar pool de conexões para MySQL ou PostgreSQL
                    self.criar_pool_conexao()
                    connection = self.connection_pool.get_connection()
                    print(f"Conectado ao banco de dados {escolha_usuario.upper()}")
            else:
                # Criar um banco de dados SQLite por padrão
                self.db_type = "sqlite"
                db_path = os.path.join(self.permanent_db_dir, "main_db.db")
                connection = sqlite3.connect(db_path)
                print(f"Novo banco de dados SQLite criado: {db_path}")

        # Integração com Docker (se necessário)
        if separate_docker and docker_manager:
            # ... (Implemente a lógica para criar um contêiner Docker)

        if not connection:
            # Lançar erro para o ErrorHandler
            raise Database_connection_error(error_message)

        return connection
    def salvar_dados (self):
    pass
    def copiar_dados_treinamento(self, nome_banco, caminho_banco, diretory_copy, banco_permanente_existente=None, modificação_de_dados=False, criação_de_dados_sinteticos=False, modificação="ocultar_detalhes", aleatorização=False, treining_insane=False, tratamento_de_outliers_semanticos=False, treining_AI_detecte_outliers=False, percent_of_data_fictis=0.1, saved_information=False, diretory_of_saved_data=None, reatribute_saved_dats=False):
        """Copia dados de um diretório para o banco de dados, com opções de modificação e criação de dados sintéticos."""
        import shutil
        import json
        import random
        import pandas as pd
        import numpy as np
        from faker import Faker
        fake = Faker()

        # Carregar dados da fonte (banco de dados permanente ou diretório)
        dados = []
        if banco_permanente_existente:
            dados = self.carregar_dados(banco_permanente_existente, None)
        elif diretory_copy:
            for filename in os.listdir(diretory_copy):
                filepath = os.path.join(diretory_copy, filename)
                if os.path.isfile(filepath):
                    try:
                        with open(filepath, 'r') as f:
                            dados.extend(json.load(f))
                    except json.JSONDecodeError:
                        print(f"Erro ao carregar o arquivo JSON: {filepath}")
        else:
            print("Nenhuma fonte de dados especificada.")
            return

        # Modificar dados existentes
        if modificação_de_dados:
            dados_modificados = []
            for registro in dados:
                for _ in range(random.randint(1, 5)): # Criar até 5 dados sintéticos por dado real
                    novo_registro = registro.copy() #cria uma copia do registro
                    if modificação == "ocultar_detalhes": #verifica se a modificação é para ocultar detalhes
                        if treining_insane: #verifica se o treinamento é insano
                            # Ocultar detalhes importantes, mas mantendo o sentido geral
                            # Implemente sua lógica aqui para identificar e ocultar detalhes importantes
                            pass #passa caso não haja implementação
                        else: #caso não seja treinamento insano
                            # Ocultar detalhes sutis ou menos importantes
                            for k, v in novo_registro.items(): #percorre os itens do novo registro
                                if random.random() < 0.3: #gera um numero aleatorio entre 0 e 1, se for menor que 0.3
                                    novo_registro[k] = None #o valor do item é definido como nulo
                    if treining_insane and tratamento_de_outliers_semanticos and treining_AI_detecte_outliers: #verifica as condições
                        # Inserir outliers simples em dados de texto
                        # Implemente sua lógica aqui para inserir outliers em campos de texto
                        pass #passa caso não haja implementação
                    dados_modificados.append(novo_registro)

            dados.extend(dados_modificados)

        # Criar dados sintéticos aleatórios
        if criação_de_dados_sinteticos:
            dados_sinteticos = []
            if aleatorização:
                # Criar dados sintéticos aleatórios com base nos dados reais
                for _ in range(len(dados) * 10):  # Criar 10x dados sintéticos
                    novo_registro = {}
                    for k, v in dados[random.randint(0, len(dados) - 1)].items():
                        if isinstance(v, str):
                            novo_registro[k] = fake.word()  # Substituir strings por palavras aleatórias
                        elif isinstance(v, int):
                            novo_registro[k] = random.randint(0, 100)  # Substituir inteiros por números aleatórios
                        else:
                            novo_registro[k] = v
                    dados_sinteticos.append(novo_registro)
            if treining_insane:
                # Criar dados totalmente fictícios
                for _ in range(int(len(dados) * percent_of_data_fictis)):
                    novo_registro = {}
                    for k in dados[0].keys():  # Usar as mesmas chaves dos dados reais
                        if isinstance(dados[0][k], str):
                            novo_registro[k] = fake.word()
                        elif isinstance(dados[0][k], int):
                            novo_registro[k] = random.randint(0, 100)
                        else:
                            novo_registro[k] = None
                    dados_sinteticos.append(novo_registro)

            dados.extend(dados_sinteticos)

        # Salvar dados no banco de dados
        if self.db_type == "sqlite":
            # ... (Lógica para inserir dados no banco de dados SQLite)
        elif self.db_type == "mysql":
            # ... (Lógica para inserir dados no banco de dados MySQL)
        elif self.db_type == "postgresql":
            # ... (Lógica para inserir dados no banco de dados PostgreSQL)

        # Salvar 20% dos dados coletados em diretório
        if saved_information:
            if not diretory_of_saved_data:
                print("Diretório para salvar dados não especificado.")
            else:
                os.makedirs(diretory_of_saved_data, exist_ok=True)
                num_dados_salvar = int(len(dados) * 0.2)
                dados_salvar = random.sample(dados, num_dados_salvar)
                with open(os.path.join(diretory_of_saved_data, "dados_salvos.json"), 'w') as f:
                    json.dump(dados_salvar, f)

        # Reatribuir dados salvos ao banco de dados
        if reatribute_saved_dats:
            if not diretory_of_saved_data:
                print("Diretório de dados salvos não especificado.")
            else:
                filepath = os.path.join(diretory_of_saved_data, "dados_salvos.json")
                if os.path.isfile(filepath):
                    try:
                        with open(filepath, 'r') as f:
                            dados_reatribuir = json.load(f)
                        # ... (Lógica para inserir dados_reatribuir no banco de dados)
                    except json.JSONDecodeError:
                        print(f"Erro ao carregar o arquivo JSON: {filepath}")
