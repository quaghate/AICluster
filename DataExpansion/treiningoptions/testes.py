import unittest
from unittest.mock import MagicMock, patch
import logging
import sqlite3
from DatabaseManager import DBManager



# Configuração básica do logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TestDBManager(unittest.TestCase):

    def setUp(self):
        """Configuração executada antes de cada teste."""
        logging.info("Iniciando configuração do teste.")
        self.db_manager_sqlite = DBManager(db_type="sqlite", db_path=":memory:")
        self.db_manager_mysql = DBManager(db_type="mysql", host="localhost", user="usuario", password="senha", database="meudb")
        self.db_manager_mysql.get_connection = MagicMock()  # Simula a conexão MySQL
        logging.info("Configuração do teste concluída.")

    def tearDown(self):
        """Limpeza executada após cada teste."""
        logging.info("Finalizando teste.")

    def test_get_connection_sqlite(self):
        """Verifica se a conexão com o SQLite é estabelecida corretamente."""
        logging.info("Executando teste: test_get_connection_sqlite")
        connection = self.db_manager_sqlite.get_connection()
        self.assertIsInstance(connection, sqlite3.Connection)

    def test_criar_banco_de_dados_temporario_mysql(self):
        """Verifica se a criação de banco de dados temporário no MySQL retorna um nome."""
        logging.info("Executando teste: test_criar_banco_de_dados_temporario_mysql")
        nome_banco, _ = self.db_manager_mysql.criar_banco_de_dados_temporario(diretorio_temporario="/tmp")
        self.assertIsNotNone(nome_banco)

    # ... (Adicione mais testes para as outras funções e cenários)

if __name__ == '__main__':
    unittest.main()
    subprocess.check_call('python', '-m', 'unittest', 'DBmanager.py')