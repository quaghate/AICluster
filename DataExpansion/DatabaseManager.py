import os
import json
import random
import shutil
import sqlite3

import mysql.connector
from mysql.connector.pooling import MySQLConnectionPool
import psycopg2
import psycopg2.pool as pool
from faker import Faker

fake = Faker()

class DatabaseManager:
    def __init__(self, db_type, **kwargs):
        self.db_type = db_type
        self.connection = None
        self.connection_pool = None  # Para MySQL e PostgreSQL
        self.db_path = kwargs.get("db_path") # Para SQLite

        if db_type in ("mysql", "postgresql"):
            self.host = kwargs.get("host")
            self.user = kwargs.get("user")
            self.password = kwargs.get("password")
            self.database = kwargs.get("database")
            self.pool_size = kwargs.get("pool_size", 3)


    def _connect_mysql(self):
        self.connection_pool = MySQLConnectionPool(
            pool_name="mysql_pool",
            pool_size=self.pool_size,
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

    def _connect_postgresql(self):
        dsn = f"dbname={self.database} user={self.user} password={self.password} host={self.host}"
        self.connection_pool = pool.SimpleConnectionPool(2, self.pool_size, dsn=dsn)


    def _connect_sqlite(self):
        self.connection = sqlite3.connect(self.db_path)
        self.connection.execute("PRAGMA foreign_keys = ON;")

    def connect(self):
        if self.db_type == "mysql":
            self._connect_mysql()
        elif self.db_type == "postgresql":
            self._connect_postgresql()
        elif self.db_type == "sqlite":
            self._connect_sqlite()
        else:
            raise ValueError("Tipo de banco de dados inválido.")

    def _get_connection(self):
         if self.db_type in ("mysql", "postgresql"):
              return self.connection_pool.get_connection()
         return self.connection #SQLite não usa pool


    def close(self):
        if self.connection:
            self.connection.close()
        elif self.connection_pool:
             self.connection_pool.close()


    def _execute_query(self, query, params=None):
         conn = self._get_connection() # type: ignore
         try:

             cursor = conn.cursor() # type: ignore
             cursor.execute(query, params) # type: ignore
             conn.commit() # type: ignore
             return cursor # type: ignore

         except Exception as e:
            print(f"Erro ao executar query: {e}") # type: ignore
            conn.rollback() # type: ignore
            raise # type: ignore
         finally: # type: ignore
            if self.connection_pool:
               cursor.close() # type: ignore
               self.connection_pool.put_connection(conn) # type: ignore



    def carregar_dados(self, nome_tabela, colunas="*", where=None):

        query = f"SELECT {colunas} FROM {nome_tabela}"
        if where:
            query += f" WHERE {where}"

        cursor = self._execute_query(query) # type: ignore


        if self.db_type == "sqlite":
             return cursor.fetchall() # type: ignore
        return cursor # type: ignore




    def descartar_banco_temporario(self):
        if self.db_type == "sqlite":
            if os.path.exists(self.db_path):
                self.close()
                os.remove(self.db_path)
        elif self.db_type == "mysql":
             self._execute_query(f"DROP DATABASE IF EXISTS {self.database}") # type: ignore
        elif self.db_type == "postgresql":
             self._execute_query(f"DROP DATABASE IF EXISTS {self.database}") # type: ignore

    def criar_banco_de_dados(self):
        if self.db_type == "sqlite":
            self._execute_query('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    email TEXT UNIQUE
                )
            ''')
            self._execute_query('''
                CREATE TABLE IF NOT EXISTS produtos (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    usuario_id INTEGER,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
             ''')

        elif self.db_type == "mysql":
            temp_connection = mysql.connector.connect(host=self.host, user=self.user, password=self.password)
            try:
                cursor = temp_connection.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")

            except Exception as e:
                print(f"Erro ao criar o banco de dados MySQL: {e}")

            finally:

                cursor.close() # type: ignore
                temp_connection.close()



        elif self.db_type == "postgresql":
              self._execute_query(f"CREATE DATABASE IF NOT EXISTS {self.database}") # type: ignore

    def salvar_dados(self, dados, nome_tabela):
         try:
            if self.db_type == "sqlite":
                for item in dados:
                    cursor = self.connection.cursor() # type: ignore
                    colunas = ', '.join(item.keys())
                    placeholders = ', '.join(['?'] * len(item))
                    valores = tuple(item.values())
                    sql = f"INSERT INTO {nome_tabela} ({colunas}) VALUES ({placeholders})"
                    cursor.execute(sql, valores) # type: ignore
                self.connection.commit() # type: ignore

            elif self.db_type in ("mysql","postgresql"): # type: ignore


                for item in dados:

                    colunas = ', '.join(item.keys())
                    placeholders = ', '.join(['%s'] * len(item))
                    valores = tuple(item.values())
                    sql = f"INSERT INTO {nome_tabela} ({colunas}) VALUES ({placeholders})"
                    self._execute_query(sql, valores) # type: ignore


         except Exception as e:
             print(f"Erro ao salvar dados : {e}") # type: ignore

# ... (Restante do código - DBManager, copiar_dados_treinamento)

    def copiar_dados_treinamento(self, nome_banco, caminho_banco, diretorio_dados):
        dados = []
        for filename in os.listdir(diretorio_dados):
            filepath = os.path.join(diretorio_dados, filename)
            try:
                if filename.endswith(".json"):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        dados.extend(json.load(f))
                elif filename.endswith(".csv"):
                    with open(filepath, 'r', encoding='utf-8', newline='') as f:
                        reader = csv.DictReader(f)  # Lê CSV como dicionários
                        dados.extend(list(reader)) # type: ignore
                elif filename.endswith((".yaml", ".yml")):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        dados.extend(yaml.safe_load(f)) # type: ignore
                else:
                    # Lida com outros tipos de arquivo (imagens, vídeos, etc.)
                    dados.append({"filepath": filepath, "filetype": filename.split('.')[-1]})  # Guarda o caminho e o tipo do arquivo

            except Exception as e:
                print(f"Erro ao carregar o arquivo {filename}: {e}")

        # Salvar dados no banco de dados usando a DatabaseManager
        if dados:
            try:
                self.db_manager.salvar_dados(dados, "dados_treinamento")
            except Exception as e:
                print(f"Erro ao salvar dados no banco de dados: {e}")

