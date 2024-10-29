import os
import time
from cryptography.fernet import Fernet

def handle_temp_file(file_path, mode='replace', delay=120, reencrypt=True, new_file=True, key=None):
    """
    Gerencia um arquivo temporário, oferecendo diversas opções de tratamento.

    Args:
        file_path: Caminho do arquivo original.
        mode: Modo de operação ('replace' ou 'reencrypt').
        delay: Tempo de espera antes de excluir o arquivo (em segundos).
        reencrypt: Indica se o arquivo deve ser recriptografado.
        new_file: Indica se um novo arquivo deve ser criado.
        key: Chave de criptografia.

    Returns:
        A nova chave de criptografia.
    """

    # Lê o conteúdo do arquivo original
    with open(file_path, 'rb') as f:
        data = f.read()

    # Gera uma nova chave se necessário
    if not key:
        key = Fernet.generate_key()

    # Criptografa os dados
    f = Fernet(key)
    encrypted_data = f.encrypt(data)

    # Determina o nome do novo arquivo
    if new_file:
        new_file_path = file_path + '.enc'
    else:
        new_file_path = file_path

    # Recriptografa o arquivo (se necessário) e salva
    if reencrypt:
        with open(new_file_path, 'wb') as f:
            f.write(encrypted_data)

    # Exclui o arquivo antigo (se o modo for 'replace' e um novo arquivo foi criado)
    if mode == 'replace' and new_file:
        time.sleep(delay)
        os.remove(file_path)

    return key

# Exemplos de uso:
# Excluir e recriar:
handle_temp_file('meu_arquivo.txt', 'replace', 120, True, True)

# Recriptografar sem criar novo arquivo:
handle_temp_file('meu_arquivo.txt', 'reencrypt', False, False, nova_chave)

# Apenas substituir a chave:
handle_temp_file('meu_arquivo.txt', 'replace', 0, False, False, nova_chave)