def importador(arquivo, bibliotecas_opcionais=None):
    """Importa as bibliotecas necessárias para cada arquivo."""
    if arquivo == "training.py":
        import os, secrets, string, time, subprocess, sqlite3, mysql.connector, yaml
        import secrets
        import string
        # ... outras importações para training.py
    elif arquivo == "docker_manager.py":
        import subprocess, os 
        # ... outras importações para docker_manager.py
    # ... adicione as importações para os outros arquivos
