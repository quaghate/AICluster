# __init__.py

from DataExpansion.DatabaseManager import DatabaseManager
from DataExpansion.Treinador_IA import Treinador_IA

print('Iniciando o AICluster')

__all__ = ['DatabaseManager', 'Treinador_IA']

# Função para configurar a conexão com o banco de dados
def setup_database_connection():
    db_type = input("Digite o tipo de banco de dados (mysql/sqlite), caso deseje pular essa parte, digite qualquer coisa. ").lower()

    if db_type == "mysql":
        db_config = {
            "db_type": db_type,
            "host": "localhost",
            "user": input("Digite o usuário do MySQL: "),
            "password": input("Digite a senha do MySQL: "),
            "database": input("Digite o nome do banco de dados do MySQL: ")
        }
    elif db_type == "sqlite":
        db_config = {
            "db_type": db_type,
            "db_path": input("Digite o caminho do banco de dados SQLite: ")
        }
    else:
        print("Escolha não suportada")
        return None

    try:
        db_manager = DatabaseManager(**db_config)
        connection = db_manager._get_connection()
        print(f"{db_type.capitalize()} iniciado com sucesso")
        return db_manager
    except Exception as e:
        print(f"Ocorreu o erro: {e}")
        print("Quando for executar o código, tente usar SQLite, que é um banco de dados embutido no Python.")
        return None

# Inicializar conexão
db_manager = setup_database_connection()

# Fechar conexão no final
if db_manager:
    db_manager.close()

__version__ = "1.0.0"
print(f"Versão: {__version__}")

__author__ = "quaghate"
print(f"Autor: {__author__}")

print("Inicialização concluída")
