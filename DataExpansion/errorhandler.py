

import os
import sys
import subprocess
import gc

class ErrorHandler:
    def __init__(self, language='pt'):
        self.language = self.escolher_idioma(language)
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
                'memory_error': 'O uso de memória excedeu o limite máximo permitido.',
                'cpu_error': 'O uso de CPU excedeu o limite máximo permitido.',
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
                'memory_error': 'Memory usage exceeded the maximum allowed limit.',
                'cpu_error': 'CPU usage exceeded the maximum allowed limit.',
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
                'memory_error': 'メモリ使用量が許可された最大限度を超えました。',
                'cpu_error': 'CPU 使用率が許可された最大限度を超えました。',
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
                'memory_error': '内存使用量超出了允许的最大限制。',
                'cpu_error': 'CPU 使用率超出了允许的最大限制。',
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
                'memory_error': 'El uso de memoria superó el límite máximo permitido.',
                'cpu_error': 'El uso de CPU superó el límite máximo permitido.',
                'KeyError': 'The key "{chave}" was not found in the dictionary.'
            }
        }

    def escolher_idioma(self, language):
        if language in self.error_messages:
            return language
        

    def get_message(self, error_code, *args):
        return self.error_messages[self.language].get(error_code, 'Erro desconhecido').format(*args)

    def handle_error(self, error_code, *args):
        error_message = self.get_message(error_code, *args)
        print(error_message)

        if error_code in ['memory_error', 'cpu_error']:
            self.limpar_cache()
            if error_code == 'memory_error':
                self.tratar_erro_memoria()
            elif error_code == 'cpu_error':
                self.tratar_erro_cpu()

    def limpar_cache(self):
        gc.collect()
        print("Cache limpo e coletor de lixo executado.")

    def tratar_erro_memoria(self):
        resposta = input("Deseja limpar todas as variáveis lixo no sistema para liberar memória? (s/n): ").lower()
        if resposta in ("s", "sim", "y", "yes"):
            gc.collect()
            if psutil.virtual_memory().used < self.memoria_maxima:
                print("Memória liberada com sucesso. Continuando treinamento...")
                return
        print("Memória insuficiente. Tente aumentar o limite de memória ou aprimorar seu hardware.")
        sys.exit(1)

    def tratar_erro_cpu(self):
        print("O consumo de CPU está muito alto e alcançou os limites. Tente aumentar o limite de CPU ou aprimorar seu hardware.")
        sys.exit(1)
