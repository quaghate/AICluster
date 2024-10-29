import yaml
from database import DatabaseManager
from data_expansion import DataExpansion

def main():
    # Carregar a configuração do arquivo YAML
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Criar uma instância do DatabaseManager
    db_manager = DatabaseManager(config, config['encryption_key'])
    db_manager.create_connection()

    # Criar uma instância do DataExpansion
    data_expander = DataExpansion(config=config)
    data_expander.initialize()

    # Executar as tarefas desejadas
    data_expander.execute('train_advanced_models')  # Exemplo de tarefa

if __name__ == "__main__":
    main()