import os, sys, importlib, subprocess

class ErrorHandler:
    def __init__(self, language='pt'):
       self.language = backfront_do_idioma()
       self.error_messages = {
        'pt': {
            'file_not_found': 'O arquivo "{file}" não foi encontrado.',
            'yaml_error': 'Erro ao carregar o arquivo YAML: {error}',
            'argument_error': 'Número de argumentos inválido. Esperado: {expected}, recebido: {received}',
            'database_connection_error': 'Erro ao conectar ao banco de dados: {error}',
            'mysql_connector_error': 'Erro: O módulo mysql.connector não foi encontrado. Instale-o com "pip install mysql-connector-python"',
            'division_by_zero': 'Divisão por zero não é permitida.',
            'biblioteca_nao_encontrada': 'Erro: A biblioteca "{biblioteca}" não foi encontrada. Certifique-se de que ela esteja instalada.',
            'escolha_idioma': 'Escolha o idioma / Choose language (pt/en/ja/zh/es): ',
            'idioma_invalido': 'Idioma inválido / Invalid language. Choose from: pt, en, ja, zh, es.',
            'pip_nao_instalado': '[bold red]Erro:[/] O pip não está instalado.',
            'erro_obter_bibliotecas': '[bold red]Erro:[/] Ao obter a lista de bibliotecas instaladas.',
            'erro_instalar_biblioteca': '[bold red]Erro:[/] Não foi possível instalar a biblioteca {biblioteca}.',
            'KeyError': 'A chave "{chave}" não foi encontrada no dicionário.'
        },
        'en': {
            'file_not_found': 'The file "{file}" was not found.',
            'yaml_error': 'Error loading YAML file: {error}',
            'argument_error': 'Invalid number of arguments. Expected: {expected}, received: {received}',
            'database_connection_error': 'Error connecting to database: {error}',
            'mysql_connector_error': 'Error: The mysql.connector module was not found. Install it with "pip install mysql-connector-python"',
            'division_by_zero': 'Division by zero is not allowed.',
            'biblioteca_nao_encontrada': 'Error: The library "{biblioteca}" was not found. Make sure it is installed.',
            'escolha_idioma': 'Choose language / Escolha o idioma (pt/en/ja/zh/es): ',
            'idioma_invalido': 'Invalid language / Idioma inválido. Choose from: pt, en, ja, zh, es.',
            'pip_nao_instalado': '[bold red]Error:[/] pip is not installed.',
            'erro_obter_bibliotecas': '[bold red]Error:[/] When obtaining the list of installed libraries.',
            'erro_instalar_biblioteca': '[bold red]Error:[/] Could not install library {biblioteca}.',
            'KeyError': 'The key "{chave}" was not found in the dictionary.'
        },
        'ja': {
            'file_not_found': 'ファイル "{file}" が見つかりません。',
            'yaml_error': 'YAML ファイルの読み込み中にエラーが発生しました: {error}',
            'argument_error': '引数の数が不正です。期待される数: {expected}、受け取った数: {received}',
            'database_connection_error': 'データベースへの接続エラー: {error}',
            'mysql_connector_error': 'エラー: mysql.connector モジュールが見つかりません。"pip install mysql-connector-python" でインストールしてください',
            'division_by_zero': 'ゼロでの除算は許可されていません。',
            'biblioteca_nao_encontrada': 'エラー: ライブラリ "{biblioteca}" が見つかりません。インストールされていることを確認してください。',
            'escolha_idioma': '言語を選択してください / Choose language (pt/en/ja/zh/es): ',
            'idioma_invalido': '無効な言語です / Invalid language. Choose from: pt, en, ja, zh, es.',
            'pip_nao_instalado': '[bold red]エラー:[/] pip がインストールされていません。',
            'erro_obter_bibliotecas': '[bold red]エラー:[/] インストールされているライブラリのリストを取得しています。',
            'erro_instalar_biblioteca': '[bold red]エラー:[/] ライブラリ {biblioteca} をインストールできませんでした。',
            'KeyError': "辞書に '{chave}' というキーが見つかりません。"
        },
        'zh': {
            'file_not_found': '找不到文件 "{file}"。',
            'yaml_error': '加载 YAML 文件时出错: {error}',
            'argument_error': '参数数量无效。预期: {expected}，收到: {received}',
            'database_connection_error': '连接到数据库时出错: {error}',
            'mysql_connector_error': '错误: 找不到 mysql.connector 模块。请使用 "pip install mysql-connector-python" 安装',
            'division_by_zero': '不能除以零。',
            'biblioteca_nao_encontrada': '错误: 找不到库 "{biblioteca}"。请确保已安装。',
            'escolha_idioma': '选择语言 / Choose language (pt/en/ja/zh/es): ',
            'idioma_invalido': '无效的语言 / Invalid language. Choose from: pt, en, ja, zh, es.',
            'pip_nao_instalado': '[bold red]错误:[/] 未安装 pip。',
            'erro_obter_bibliotecas': '[bold red]错误:[/] 获取已安装库的列表时出错。',
            'erro_instalar_biblioteca': '[bold red]错误:[/] 无法安装库 {biblioteca}。',
            'KeyError': "在字典中找不到键 '{chave}'。"
        },
        'es': {
            'file_not_found': 'El archivo "{file}" no se encontró.',
            'yaml_error': 'Error al cargar el archivo YAML: {error}',
            'argument_error': 'Número de argumentos inválido. Esperado: {expected}, recibido: {received}',
            'database_connection_error': 'Error al conectar a la base de datos: {error}',
            'mysql_connector_error': 'Error: No se encontró el módulo mysql.connector. Instálelo con "pip install mysql-connector-python"',
            'division_by_zero': 'No se permite la división por cero.',
            'biblioteca_nao_encontrada': 'Error: No se encontró la biblioteca "{biblioteca}". Asegúrese de que esté instalada.',
            'escolha_idioma': 'Elija el idioma / Choose language (pt/en/ja/zh/es): ',
            'idioma_invalido': 'Idioma no válido / Invalid language. Choose from: pt, en, ja, zh, es.',
            'pip_nao_instalado': '[bold red]Error:[/] pip no está instalado.',
            'erro_obter_bibliotecas': '[bold red]Error:[/] Al obtener la lista de bibliotecas instaladas.',
            'erro_instalar_biblioteca': '[bold red]Error:[/] No se pudo instalar la biblioteca {biblioteca}.',
            'KeyError': 'The key "{chave}" was not found in the dictionary.'
        },
    }
       self.language = self.escolher_idioma(language)
    def get_message(self, error_code, *args):
        return self.error_messages[self.language].get(error_code, 'Erro desconhecido').format(*args)

    def handle_error(self, error_code, *args):
        error_message = self.get_message(error_code, *args)
        print(error_message)

        if error_code == 'mysql_connector_error':
            while True:
                resposta = input("Deseja reiniciar o programa e tentar instalar o mysql.connector? (s/n/sim/não): ").lower()
                if resposta in ("s", "sim", "y", "yes"):
                    try:
                        subprocess.check_call(['pip', 'install', 'mysql-connector-python'])
                        print("mysql-connector-python instalado com sucesso! Reiniciando o programa...")
                        os.execv(sys.executable, ['python'] + sys.argv)
                    except subprocess.CalledProcessError:
                        print("Erro ao instalar o mysql-connector-python. Saindo do programa...")
                        sys.exit(1)
                elif resposta in ("n", "não", "no"):
                    print("Saindo do programa...")
                    sys.exit(1)
                else:
                    print("Resposta inválida. Digite 's', 'sim', 'y', 'yes', 'n', 'não', ou 'no'.")

        elif error_code == 'biblioteca_nao_encontrada':
            while True:
                resposta = input(f"Deseja tentar instalar a biblioteca '{args[0]}'? (s/n/sim/não): ").lower()
                if resposta in ("s", "sim", "y", "yes"):
                    try:
                        subprocess.check_call(['pip', 'install', args[0]])
                        print(f"'{args[0]}' instalado com sucesso! Reiniciando o programa...")
                        os.execv(sys.executable, ['python'] + sys.argv)
                    except subprocess.CalledProcessError:
                        print(f"Erro ao instalar '{args[0]}'. Saindo do programa...")
                        sys.exit(1)
                elif resposta in ("n", "não", "no"):
                    print("Saindo do programa...")
                    sys.exit(1)
                else:
                    print("Resposta inválida. Digite 's', 'sim', 'y', 'yes', 'n', 'não', ou 'no'.")

def backfront_do_idioma(perguntar_idioma=True):
    """ Obtém a escolha de idioma do usuário e define a linguagem global. 

    Args:
        perguntar_idioma (bool, optional): Se True, pergunta o idioma ao usuário. 
                                          Se False, usa o valor da variável global LANGUAGE 
                                          ou o padrão 'pt'. Defaults to True.
    """
    LANGUAGE = 'en'

    if perguntar_idioma:
        while True:
            # Solicita ao usuário que escolha um idioma
            print('Escolha o idioma / Choose language (pt/en/ja/zh/es): ', end='')
            LANGUAGE = input().lower()

            # Verifica se o idioma escolhido é válido
            if LANGUAGE in ['pt', 'en', 'ja', 'zh', 'es']:
                break  # Sai do loop se o idioma for válido

            # Exibe uma mensagem de erro se o idioma for inválido
            print('Idioma inválido / Invalid language. Choose from: pt, en, ja, zh, es.')
    
    return LANGUAGE  # Retorna o idioma

