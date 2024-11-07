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
