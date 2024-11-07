import argparse
import os
import string
import secrets
import time
import mysql.connector
import sqlite3
import subprocess

# --- Importe suas funções de criptografia e ErrorHandler aqui ---
from criptografia import handle_temp_file  # type: ignore
from DataExpansion.errorhandler import ErrorHandler
from DataExpansion.instalador import escolher_idioma

# --- Variável global para o idioma (se necessário) ---
language = 'pt'


# --- Função para escolher o idioma (se necessário) ---
def escolha_local_da_linguagem():
    global language

    language = escolher_idioma
    # ... (Seu código para escolher o idioma)


class MySQLManager:
    def __init__(self, config):
        self.config = config
        self.connection = None

    def connect_mysql(self):
        """Conecta ao banco de dados."""
        try:
            self.connection = mysql.connector.connect(**self.config)
            print("Conexão com o banco de dados MySQL estabelecida com sucesso!")
        except mysql.connector.Error as err:
            print(f"Erro ao conectar ao banco de dados MySQL: {err}")

    def close_mysql(self):
        """Fecha a conexão com o banco de dados."""
        if self.connection:
            self.connection.close()
            print("Conexão com o banco de dados MySQL fechada.")

    def criar_banco_de_dados_temporario(
        self, nome_base="temp_db_", diretorio_temporario=None
    ):
        """Cria um banco de dados temporário com senha criptografada."""
        nome_banco = nome_base + secrets.token_hex(8)
        senha = gerar_senha_forte()

        try:
            cursor = self.connection.cursor()
            cursor.execute(f"CREATE DATABASE {nome_banco};")
            cursor.execute(
                f"CREATE USER 'temp_user_{nome_banco}'@'localhost' IDENTIFIED BY '{senha}';"
            )
            cursor.execute(
                f"GRANT ALL PRIVILEGES ON {nome_banco}.* TO 'temp_user_{nome_banco}'@'localhost';"
            )
            self.connection.commit()

            # --- Salve as informações do banco de dados em um arquivo ---
            if diretorio_temporario:
                conteudo = f"Banco de dados: {nome_banco}\nSenha: {senha}\n"
                caminho_arquivo = os.path.join(
                    diretorio_temporario, f"{nome_banco}_info.txt"
                )
                # Chame sua função handle_temp_file aqui para criptografar e salvar o conteúdo
                # Exemplo:
                # handle_temp_file(caminho_arquivo, data=conteudo.encode())
                print(f"Informações do banco de dados temporário salvas em: {caminho_arquivo}")

            return nome_banco, senha

        except mysql.connector.Error as erro:
            print(f"Erro ao criar o banco de dados temporário: {erro}")
            return None, None


class SQLiteManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None

    def connect_sqlite(self):
        """Conecta ao banco de dados SQLite."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            print(
                f"Conexão com o banco de dados SQLite estabelecida com sucesso! Caminho: {self.db_path}"
            )
        except sqlite3.Error as err:
            print(f"Erro ao conectar ao banco de dados SQLite: {err}")

    def close_sqlite(self):
        """Fecha a conexão com o banco de dados SQLite."""
        if self.connection:
            self.connection.close()
            print("Conexão com o banco de dados SQLite fechada.")

    def criar_banco_de_dados_temporario(
        self, nome_base="temp_db_", diretorio_temporario=None
    ):
        """Cria um banco de dados temporário."""
        nome_banco = nome_base + secrets.token_hex(8)
        if diretorio_temporario:
            caminho_banco = os.path.join(
                diretorio_temporario, f"{nome_banco}.db"
            )
        else:
            caminho_banco = f"{nome_banco}.db"

        # Criar o banco de dados (o arquivo será criado automaticamente)
        conexao = sqlite3.connect(caminho_banco)
        conexao.close()

        print(f"Banco de dados SQLite temporário criado: {caminho_banco}")
        return nome_banco, caminho_banco


def criar_diretorio(caminho_diretorio):
    """Cria um diretório se ele não existir."""
    if not os.path.exists(caminho_diretorio):
        os.makedirs(caminho_diretorio)
        print(f"Diretório criado: {caminho_diretorio}")
    else:
        print(f"Diretório já existe: {caminho_diretorio}")


def gerar_senha_forte(tamanho=16):
    """Gera uma senha aleatória forte."""
    caracteres = string.ascii_letters + string.digits + string.punctuation
    senha = "".join(secrets.choice(caracteres) for _ in range(tamanho))
    return senha


def treinar_ia(db_manager, diretorio_temporario, num_iteracoes=10, **kwargs):
    """Treina a IA em múltiplos bancos de dados temporários."""
    for i in range(num_iteracoes):
        print(f"Iteração de Treinamento {i+1}:")

        # 1. Criar banco de dados temporário
        if kwargs["db_type"] == "all_mysql" or kwargs["db_type"] == "mysql_sqlite":
            # Usar MySQL
            nome_banco, senha = db_manager.criar_banco_de_dados_temporario(
                diretorio_temporario=diretorio_temporario
            )
            if not nome_banco:
                print(
                    "Erro ao criar banco de dados temporário MySQL. Pulando iteração."
                )
                continue
            # ... (Sua lógica para conectar ao banco de dados temporário MySQL)
        else:
            # Usar SQLite
            nome_banco, caminho_banco = (
                db_manager.criar_banco_de_dados_temporario(
                    diretorio_temporario=diretorio_temporario
                )
            )
            if not nome_banco:
                print(
                    "Erro ao criar banco de dados temporário SQLite. Pulando iteração."
                )
                continue
            # ... (Sua lógica para usar conexao_temporaria)

        # ... (Seu código para:
        #     - Copiar dados de treinamento
        #     - Treinar a IA
        #     - Salvar resultados
        #     - Descartar o banco de dados temporário)


class DockerManager:
    def __init__(self, dockerfile="Dockerfile"):
        self.dockerfile = dockerfile

    def build_image(self, image_name="meu_projeto"):
        """Constrói uma imagem Docker."""
        try:
            subprocess.run(
                ["docker", "build", "-t", image_name, "."], check=True
            )
            print(f"Imagem Docker '{image_name}' criada com sucesso!")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao criar a imagem Docker: {e}")

    def run_container(self, image_name="meu_projeto"):
        """Executa um container Docker."""
        try:
            subprocess.run(["docker", "run", "-d", image_name], check=True)
            print(f"Container Docker '{image_name}' iniciado com sucesso!")
        except subprocess.CalledProcessError as e:
            print(f"Erro ao iniciar o container Docker: {e}")
    def verificar_db(self, tipos_banco_dados):
        """Verifica se os bancos de dados estão instalados e em execução."""
        if tipos_banco_dados == "all_mysql":
            try:
                self.connect_mysql()
                self.close_mysql()
                print("MySQL está instalado e funcionando corretamente.")
            except mysql.connector.Error as e:
                # Use o ErrorHandler para tratar o erro
                error_handler.handle_error('mysql_connector_error', e) 
        elif tipos_banco_dados == "mysql_sqlite":
            try:
                self.connect_sqlite()
                self.close_sqlite()
                print("SQLite está instalado e funcionando corretamente.")
                self.connect_mysql()
                self.close_mysql()
                print("MySQL está instalado e funcionando corretamente.")
            except sqlite3.Error as e:
                # Use o ErrorHandler para tratar o erro
                error_handler.handle_error('biblioteca_nao_encontrada', 'sqlite3', e)
            except mysql.connector.Error as e:
                # Use o ErrorHandler para tratar o erro
                error_handler.handle_error('mysql_connector_error', e)
        else:  # tipos_banco_dados == "all_sqlite"
            try:
                self.connect_sqlite()
                self.close_sqlite()
                print("SQLite está instalado e funcionando corretamente.")
            except sqlite3.Error as e:
                # Use o ErrorHandler para tratar o erro
                error_handler.handle_error('biblioteca_nao_encontrada', 'sqlite3', e)

                # coloque o tratamento de erros no errorhandler.
    def criar_dockerfile(
        self, tipo_banco_dados, interruptor_mysql, interruptor_sqlite
    ):
        """Cria um arquivo Dockerfile com a imagem apropriada."""
        # ... (Seu código para criar o Dockerfile)


def main():
    """Função principal do programa."""
    global language

    parser = argparse.ArgumentParser(description="Data Expansion Script")

    # Argumentos para configurações do banco de dados
    parser.add_argument(
        "--db_host", default="localhost", help="Endereço do servidor MySQL"
    )
    parser.add_argument("--db_user", required=True, help="Usuário do MySQL")
    parser.add_argument("--db_password", required=True, help="Senha do MySQL")
    parser.add_argument("--db_name", required=True, help="Nome do banco de dados")

    # Argumentos para os diretórios
    parser.add_argument(
        "--permanent_dir",
        default="data",
        help="Diretório do banco de dados permanente",
    )
    parser.add_argument(
        "--temp_dir",
        default="temp_data",
        help="Diretório para bancos de dados temporários",
    )

    # Argumentos para o modelo básico
    parser.add_argument(
        "--basic_lr",
        type=float,
        default=0.001,
        help="Taxa de aprendizado do modelo básico",
    )
    parser.add_argument(
        "--basic_epochs", type=int, default=10, help="Número de épocas do modelo básico"
    )
    parser.add_argument(
        "--basic_batch_size",
        type=int,
        default=32,
        help="Tamanho do lote do modelo básico",
    )

    # Argumento para o número de bancos de dados temporários
    parser.add_argument(
        "--num_bancos_temporarios",
        type=int,
        default=1,
        help="Número de bancos de dados temporários a serem criados",
    )

    # Opção de escolha do banco de dados (argparse)
    tipo_banco_dados = parser.add_argument(
        "--db_type",
        choices=["all_mysql", "mysql_sqlite", "all_sqlite"],
        default=None,
        help="Tipo de banco de dados: 'all_mysql', 'mysql_sqlite' ou 'all_sqlite'",
    )

    # ... (Argumentos para o modelo avançado - adicione aqui)

    args = parser.parse_args()

    # --- Verificar a variável de ambiente DB_TYPE ---
    if "DB_TYPE" in os.environ:
        args.db_type = os.environ["DB_TYPE"]

    # --- Escolha do Banco de Dados (se não definido no argparse) ---
    if args.db_type is None:
        while True:
            db_type = input(
                "Escolha o tipo de banco de dados:\n"
                "1 - Todos MySQL\n"
                "2 - MySQL (permanente) + SQLite (temporários)\n"
                "3 - Todos SQLite\n"
                "Digite o número da opção: "
            )

            if db_type == "1":
                args.db_type = "all_mysql"
                break
            elif db_type == "2":
                args.db_type = "mysql_sqlite"
                break
            elif db_type == "3":
                args.db_type = "all_sqlite"
                break
            else:
                print("Opção inválida. Digite 1, 2 ou 3.")

    # --- Lógica Condicional para o Tipo de Banco de Dados ---
    if args.db_type == "all_mysql":
        print("Usando MySQL para todos os bancos de dados.")
        # --- Configuração do Banco de Dados ---
        db_config = {
            "host": args.db_host,
            "user": args.db_user,
            "password": args.db_password,
            "database": args.db_name,
        }
        db_manager = MySQLManager(db_config)
    elif args.db_type == "mysql_sqlite":
        print(
            "Usando MySQL para o banco de dados permanente e SQLite para os temporários."
        )
        # --- Configuração do Banco de Dados MySQL ---
        db_config = {
            "host": args.db_host,
            "user": args.db_user,
            "password": args.db_password,
            "database": args.db_name,
        }
        db_manager = MySQLManager(db_config)
    elif args.db_type == "all_sqlite":
        print("Usando SQLite para todos os bancos de dados.")
        db_path = os.path.join(args.permanent_dir, "main_db.db")
        db_manager = SQLiteManager(db_path)

    # Conectar ao banco de dados
    if args.db_type == "all_mysql" or args.db_type == "mysql_sqlite":
        db_manager.connect_mysql()
    elif args.db_type == "all_sqlite":
        db_manager.connect_sqlite()

    # --- Treinar a IA ---
    treinar_ia(
        db_manager, args.temp_dir, args.num_bancos_temporarios, **vars(args)
    )

    # --- Consultar o banco de dados permanente (opcional) ---
    # ... (Implemente a lógica de consulta, se necessário)

    # Fechar a conexão com o banco de dados
    if args.db_type == "all_mysql" or args.db_type == "mysql_sqlite":
        db_manager.close_mysql()
    elif args.db_type == "all_sqlite":
        db_manager.close_sqlite()


if __name__ == "__main__":
    escolher_idioma()
    main()

