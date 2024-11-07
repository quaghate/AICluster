import subprocess, sys, rich, logging
from rich.progress import track
from rich import print
from DataExpansion.errorhandler import ErrorHandler

error_handler = ErrorHandler()

def instalar_bibliotecas(bibliotecas_opcionais, arquivo, error_handler, idioma='en'):
    """Instala bibliotecas e exibe uma barra de progresso com rich.

    Args:
        bibliotecas (list): Lista de bibliotecas a serem instaladas.
        error_handler (ErrorHandler): Instância do ErrorHandler para lidar com erros.
        idioma (str, optional): Idioma para as mensagens de erro. Defaults to 'en'.
    """
    def importar_bibliotecas_arquivo(importar_biblioteca_arquivo, bibliotecas_opcionais):
        bibliotecas = {
            "DatabaseManager": ["mysql", "sqlite3", "os", "psycopg2"] + bibliotecas_opcionais,
            "treining": ["os", "secrets", "string", "time", "subprocess", "sqlite3", "mysql.connector", "yaml"] + bibliotecas_opcionais,
        }
        try:
            bibliotecas_para_importar = bibliotecas[arquivo] + (bibliotecas_opcionais or []) # Aqui pode ocorrer o KeyError
            import bibliotecas_para_importar
        except KeyError:
            error_handler.handle_error('KeyError', arquivo) 
        except Exception as e:
            error_handler.handle_error('erro_generico', e)

    # Verifica se o pip está instalado
    try:
        subprocess.check_call(['pip', '--version'])
    except subprocess.CalledProcessError:
        error_handler.handle_error('pip_nao_instalado')  # Usando o ErrorHandler
        return

    # Obtém a lista de bibliotecas já instaladas
    try:
        resultado = subprocess.run(['pip', 'list'], capture_output=True, text=True)
        bibliotecas_instaladas = [linha.split()[0] for linha in resultado.stdout.splitlines()[2:]]
    except subprocess.CalledProcessError:
        error_handler.handle_error('erro_obter_bibliotecas')  # Usando o ErrorHandler
        return

    # Instala as bibliotecas com barra de progresso do rich
    for biblioteca in track(bibliotecas, description="Instalando bibliotecas..."):
        if biblioteca in bibliotecas_instaladas:
            print(f"[green]A biblioteca {biblioteca} já está instalada.[/]")
            continue

        try:
            subprocess.check_call(['pip', 'install', biblioteca])
        except subprocess.CalledProcessError:
            # Verificação se a biblioteca já está na biblioteca padrão
            if biblioteca in sys.modules:
                print(f"[blue]A biblioteca {biblioteca} pertence à biblioteca padrão do Python.[/]")
            else:
                error_handler.handle_error('erro_instalar_biblioteca', biblioteca)
bibliotecas = ['numpy', 'pandas', 'matplotlib', 'os', 'time', 'pyyaml', 'mysql-connector-python', 'secrets', 'string', 'argparse', 'sqlite3', 'mysql','importlib', 'sys']
instalar_bibliotecas(bibliotecas, error_handler)