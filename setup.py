from setuptools import setup, find_packages
import pathlib

# Diretório atual
HERE = pathlib.Path(__file__).parent

# Conteúdo do arquivo README
README = (HERE / "README.md").read_text()

setup(
    name='aicluster',
    version='1.0.0a1',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'psutil',
        'scikit-learn',
        'joblib',
        'mysql-connector-python',
        'psycopg2',
        'faker',
        'pandas',
        'sentence-transformers',
        'tensorflow',
        'pyyaml',  # Para o módulo yaml
        # Adicione outras dependências aqui
    ],
    author='Quaghate',
    author_email='rsabelha@gmail.com',
    description='Um miniframework para facilitar a criação e treinamento de IAs',
    long_description=README,  # Adiciona a descrição longa a partir do README.md
    long_description_content_type='text/markdown',  # Especifica o tipo de conteúdo do README
    url='https://github.com/seuusuario/aicluster',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
