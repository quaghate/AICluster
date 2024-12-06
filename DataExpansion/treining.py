import json
import os
import logging
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sentence_transformers import SentenceTransformer
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from sklearn.metrics.pairwise import euclidean_distances, cosine_similarity
import tensorflow as tf
from tensorflow.keras.models import Sequential
from datetime import datetime
import traceback
import time
import sys
import subprocess
from errorhandler import ErrorHandler  # Importe o ErrorHandler


class TreinadorIA(ABC):
    def __init__(self, modelo, db_manager, diretorio_temporario, num_iteracoes=10, dados_rotulados=None, metrica_similaridade=None, pre_processamento=None, metricas_avaliacao=None, nivel_logging=logging.INFO, **kwargs):
        self.modelo = modelo
        self.db_manager = db_manager
        self.diretorio_temporario = diretorio_temporario
        self.num_iteracoes = num_iteracoes
        self.kwargs = kwargs
        self.dados_rotulados = dados_rotulados
        self.metrica_similaridade = metrica_similaridade or self.calcular_similaridade
        self.pre_processamento = pre_processamento or self._pre_processamento_padrao
        self.metricas = metricas_avaliacao or [accuracy_score]
        self.resultados = []
        self.precisao_media = 0
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.model_resnet = ResNet50(weights='imagenet', include_top=False, pooling='avg')
        self.epocas = kwargs.get("epocas", 10)
        self.tamanho_lote = kwargs.get("tamanho_lote", 32)
        self.nivel_logging = nivel_logging

        self.configurar_logging(__name__) # type: ignore
        self.logger = logging.getLogger(__name__)
        self.error_handler = ErrorHandler(logger=self.logger)


    def configurar_logging(self, nome_logger):
        logger = logging.getLogger(nome_logger)
        logger.setLevel(self.nivel_logging)

        handler_console = logging.StreamHandler()
        handler_console.setLevel(self.nivel_logging)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        handler_console.setFormatter(formatter)

        logger.addHandler(handler_console)


        try:
            log_filename = datetime.now().strftime('treinamento_%Y%m%d_%H%M%S.log')
            log_filepath = os.path.join(self.diretorio_temporario, log_filename) # type: ignore
            file_handler = logging.FileHandler(log_filepath, mode='w', encoding='utf-8') # type: ignore
            file_handler.setLevel(self.nivel_logging) # type: ignore
            file_handler.setFormatter(formatter) # type: ignore
            logger.addHandler(file_handler) # type: ignore
            print(f"Logs de treinamento serão salvos em: {log_filepath}") # type: ignore
        except Exception as e: # type: ignore
            print(f"Erro ao configurar o logging para arquivo: {e}") # type: ignore


    def treinar(self):
        for i in range(self.num_iteracoes): # type: ignore
            print(f"Iteração de Treinamento {i + 1}:")
            nome_banco = caminho_banco = None

            try:
                nome_banco, caminho_banco = self.criar_banco_temporario(i) # type: ignore

                if hasattr(self.db_manager, "copiar_dados_treinamento"):
                    self.db_manager.copiar_dados_treinamento(
                        nome_banco, caminho_banco, self.kwargs["local_dados"]
                    )

                dados_treinamento = self.carregar_dados_treinamento(nome_banco, caminho_banco)
                if dados_treinamento is None or not isinstance(dados_treinamento, pd.DataFrame) or dados_treinamento.empty:
                    self.error_handler.handle_error("dados_invalidos", mensagem="Dados de treinamento inválidos ou vazios.") # type: ignore
                    continue


                self.logger.info(f"Iniciando treinamento do modelo na iteração {i + 1}")
                inicio_treinamento = time.time()

                modelo_treinado, resultados_iteracao, precisao_media_iteracao = self.treinar_modelo(dados_treinamento.copy(), i)
                self.resultados.append(resultados_iteracao)


                fim_treinamento = time.time()
                tempo_treinamento = fim_treinamento - inicio_treinamento
                self.logger.info(f"Treinamento do modelo concluído em {tempo_treinamento:.2f} segundos. Precisão média: {precisao_media_iteracao}")



            except Exception as e:
                print(f"Erro na iteração {i+1}: {e}")
                self.resultados.append({"banco": nome_banco, "erro": str(e)}) # type: ignore

            finally:
                if nome_banco and caminho_banco:
                    try:
                         if hasattr(self.db_manager, "descartar_banco_temporario"):
                            if hasattr(self.db_manager,"db_path"): # type: ignore
                                self.db_manager.descartar_banco_temporario(db_path=caminho_banco) # type: ignore
                            else:
                                 self.db_manager.descartar_banco_temporario(nome_banco) # type: ignore


                    except Exception as e:
                       print(f"Erro ao descartar banco temporário: {e}")

        acuracias = [r.get("accuracy_score", float('nan')) for r in self.resultados if isinstance(r, dict)]  # type: ignore
        acuracias = [a for a in acuracias if not np.isnan(a)]
        self.precisao_media = np.mean(acuracias) if acuracias else float('nan')

        print(f"Precisão média após {self.num_iteracoes} iterações: {self.precisao_media}")

        self.salvar_resultados(self.resultados)

        return modelo_treinado, self.resultados, self.precisao_media

    def criar_banco_temporario(self, iteracao):
        if isinstance(self.db_manager, dict):
            db_type = self.db_manager.get("db_type") # type: ignore
        else:
            db_type = self.kwargs.get("db_type") # type: ignore

        try:

            if db_type == "all_mysql" or db_type == "mysql_sqlite":
                    nome_banco, senha = self.db_manager.criar_banco_de_dados_temporario(  # type: ignore
                            diretorio_temporario=self.diretorio_temporario # type: ignore
                        )
                    if not nome_banco:
                            raise Exception("Erro ao criar o banco de dados temporário MySQL.")
                    # ... (Sua lógica para conectar ao banco de dados temporário MySQL)

                    return nome_banco, None

            else: #SQLite
                    nome_banco, caminho_banco = self.db_manager.criar_banco_de_dados_temporario(diretorio_temporario=self.diretorio_temporario) # type: ignore
                    if not nome_banco:
                        raise Exception("Erro ao criar o banco de dados temporário SQLite.")


                    return nome_banco, caminho_banco
        except Exception as e:
            print(f"Erro ao criar banco temporário: {e}")
            return None, None



    def carregar_dados_treinamento(self, nome_banco, caminho_banco):
        try:
            if hasattr(self.db_manager, "carregar_dados"): # type: ignore

                dados = self.db_manager.carregar_dados(nome_banco) # type: ignore

                if dados is not None:
                    return pd.DataFrame(dados)
        except Exception as e:
            print(f"Erro ao carregar dados de treinamento: {e}")
            return None




    def treinar_modelo(self, dados, iteracao):
        try:

            x, y = self.pre_processar_dados(dados)


            x_treino, x_teste, y_treino, y_teste = train_test_split(x, y, test_size=0.2, random_state=42) # type: ignore


            if isinstance(x_treino, pd.DataFrame): # type: ignore
                colunas_numericas = x_treino.select_dtypes(include=np.number).columns # type: ignore
                for coluna in colunas_numericas: # type: ignore
                   x_treino[coluna] = self.scaler.fit_transform(x_treino[[coluna]]) # type: ignore
                   x_teste[coluna] = self.scaler.transform(x_teste[[coluna]]) # type: ignore

            elif isinstance(x_treino, np.ndarray) and x_treino.dtype == np.number: # type: ignore
                x_treino = self.scaler.fit_transform(x_treino) # type: ignore
                x_teste = self.scaler.transform(x_teste) # type: ignore



            # Treinamento
            self.modelo.fit(x_treino, y_treino, epochs=self.epocas, batch_size=self.tamanho_lote) # type: ignore

            # Avaliação
            metricas_resultado = {}
            y_predito = self.modelo.predict(x_teste) # type: ignore

            y_predito_classes = None # type: ignore
            if isinstance(self.modelo, Sequential): # type: ignore
                y_predito_classes = np.argmax(y_predito, axis=1) # type: ignore
            elif isinstance(y_predito, np.ndarray) and y_predito.ndim > 1: # type: ignore
                y_predito_classes = np.argmax(y_predito, axis=1) # type: ignore
            else:
                y_predito_classes = y_predito # type: ignore


            if isinstance(y_teste, pd.DataFrame) and y_teste.shape[1] > 1: # type: ignore
                y_teste_classes = np.argmax(y_teste.values, axis=1) # type: ignore
            elif isinstance(y_teste, np.ndarray) and y_teste.ndim > 1: # type: ignore
                y_teste_classes = np.argmax(y_teste, axis=1) # type: ignore
            else:
                y_teste_classes = y_teste # type: ignore


            for metrica in self.metricas:
                if y_predito_classes is not None:
                    resultado = metrica(y_teste_classes, y_predito_classes) # type: ignore
                    metricas_resultado[metrica.__name__] = resultado

            for nome_metrica, valor in metricas_resultado.items(): # type: ignore
                print(f"{nome_metrica}: {valor}")



            return self.modelo, metricas_resultado, self.precisao_media

        except Exception as e:
            self.error_handler.handle_error("erro_treinamento_modelo", erro=str(e), iteracao=iteracao+1, traceback=traceback.format_exc()) # type: ignore
            return None, {"erro": str(e)}, float('nan')  # type: ignore

    def _pre_processamento_padrao(self, dados):
        x = dados["features"] # type: ignore
        y = dados["labels"] # type: ignore

        if isinstance(x, pd.DataFrame): # type: ignore
            for coluna in x.columns: # type: ignore
                if x[coluna].dtype == object: # type: ignore
                    x[coluna] = x[coluna].astype(str) # type: ignore

        if isinstance(y, (pd.Series, np.ndarray, pd.DataFrame)):
            if y.dtype == object:
                 y = pd.Series(self.label_encoder.fit_transform(np.ravel(y.astype(str))))
            elif isinstance(y, np.ndarray):
                 y = self.label_encoder.fit_transform(np.ravel(y))
            elif isinstance(y, pd.DataFrame): # type: ignore
                 for column in y.columns: # type: ignore
                      if y[column].dtype == object: # type: ignore
                            y[column] = self.label_encoder.fit_transform(np.ravel(y[column].astype(str))) # type: ignore


        return x, y

    def pre_processar_dados(self, dados):

         x = dados["features"] # type: ignore
         y = dados["labels"] # type: ignore


         transformacoes = self.kwargs.get("transformacoes", {}) # type: ignore

         if isinstance(x, pd.DataFrame): # type: ignore
            for coluna, transformacao in transformacoes.items(): # type: ignore
                if coluna in x.columns: # type: ignore
                    x[coluna] = transformacao(x[coluna]) # type: ignore



         x,y = self._pre_processamento_padrao(dados)



         return x, y




    def calcular_similaridade(self, dado1, dado2):
        if isinstance(dado1, (int, float, np.ndarray)) and isinstance(dado2, (int, float, np.ndarray)):
            if isinstance(dado1, (int, float)):
                return np.isclose(dado1, dado2, atol=1e-05)
            else:
                distancia = euclidean_distances([dado1], [dado2])[0][0] # type: ignore
                similaridade = 1 / (1 + distancia)
                return similaridade

        elif isinstance(dado1, str) and isinstance(dado2, str):
            model = SentenceTransformer('all-mpnet-base-v2')
            embeddings = model.encode([dado1, dado2])
            similaridade = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            return similaridade

        elif isinstance(dado1, np.ndarray) and isinstance(dado2, np.ndarray): # type: ignore
            if dado1.ndim >= 2 and dado2.ndim >= 2:
                dado1_pre = preprocess_input(dado1)
                dado2_pre = preprocess_input(dado2)

                features1 = self.model_resnet.predict(np.expand_dims(dado1_pre, axis=0)).flatten() # type: ignore
                features2 = self.model_resnet.predict(np.expand_dims(dado2_pre, axis=0)).flatten() # type: ignore
                similaridade = cosine_similarity([features1], [features2])[0][0]
                return similaridade

        elif isinstance(dado1, list) and isinstance(dado2, list):
            intersection = len(list(set(dado1).intersection(dado2)))
            union = (len(dado1) + len(dado2)) - intersection
            similaridade = float(intersection) / union if union != 0 else 0
            return similaridade

        return None

    def salvar_resultados(self, resultados):

        try:
            caminho_arquivo = os.path.join(self.diretorio_temporario, "resultados_treinamento.json") # type: ignore
            with open(caminho_arquivo, "w") as f:
                json.dump(resultados, f, indent=4)
            self.logger.info(f"Resultados do treinamento salvos em: {caminho_arquivo}")
        except Exception as e:
             self.error_handler.handle_error("erro_salvar_resultados", erro=str(e)) # type: ignore
