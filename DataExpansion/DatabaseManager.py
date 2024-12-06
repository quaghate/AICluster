import os
import json
import random
import shutil
import sqlite3
import csv
import yaml

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
        self.db_path = kwargs.get("db_path")  # Para SQLite

        if db_type in ("mysql", "postgresql"):
            self.host = kwargs.get("host")
            self.user = kwargs.get("user")
            self.password = kwargs.get("password")
            self.database = kwargs.get("database")
            self.pool_size = kwargs.get("pool_size", 3)

    def _get_connection(self):
        if self.db_type == "sqlite":
            return self.connection
        elif self.db_type == "mysql":
            return self.connection_pool.get_connection()
        elif self.db_type == "postgresql":
            return self.connection_pool.getconn()

    def close(self):
        if self.connection:
            self.connection.close()
        elif self.connection_pool:
            self.connection_pool.closeall()

    def _execute_query(self, query, params=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
            return cursor.fetchall()  # Use fetchall para todas as consultas
        except Exception as e:
            print(f"Erro ao executar query: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            if self.db_type in ("mysql", "postgresql"):
                conn.close()

    def carregar_dados(self, nome_tabela, colunas="*", where=None):
        query = f"SELECT {colunas} FROM {nome_tabela}"
        if where:
            query += f" WHERE {where}"
        return self._execute_query(query)

    def descartar_banco_temporario(self):
        if self.db_type == "sqlite":
            if os.path.exists(self.db_path):
                self.close()
                os.remove(self.db_path)
        elif self.db_type in ("mysql", "postgresql"):
            self._execute_query(f"DROP DATABASE IF EXISTS {self.database}")

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
                cursor.close()
                temp_connection.close()
        elif self.db_type == "postgresql":
            self._execute_query(f"CREATE DATABASE IF NOT EXISTS {self.database}")

    def salvar_dados(self, dados, nome_tabela):
        try:
            if self.db_type == "sqlite":
                for item in dados:
                    cursor = self.connection.cursor()
                    colunas = ', '.join(item.keys())
                    placeholders = ', '.join(['?'] * len(item))
                    valores = tuple(item.values())
                    sql = f"INSERT INTO {nome_tabela} ({colunas}) VALUES ({placeholders})"
                    cursor.execute(sql, valores)
                self.connection.commit()
            elif self.db_type in ("mysql", "postgresql"):
                for item in dados:
                    colunas = ', '.join(item.keys())
                    placeholders = ', '.join(['%s'] * len(item))
                    valores = tuple(item.values())
                    sql = f"INSERT INTO {nome_tabela} ({colunas}) VALUES ({placeholders})"
                    self._execute_query(sql, valores)
        except Exception as e:
            print(f"Erro ao salvar dados: {e}")

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
                        reader = csv.DictReader(f)
                        dados.extend(list(reader))
                elif filename.endswith((".yaml", ".yml")):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        dados.extend(yaml.safe_load(f))
                else:
                    dados.append({"filepath": filepath, "filetype": filename.split('.')[-1]})
            except Exception as e:
                print(f"Erro ao carregar o arquivo {filename}: {e}")

        if dados:
            try:
                self.salvar_dados(dados, "dados_treinamento")
            except Exception as e:
                print(f"Erro ao salvar dados no banco de dados: {e}")
