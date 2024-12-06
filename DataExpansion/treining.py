import numpy as np
import os
import logging
from datetime import datetime
from sklearn.model_selection import train_test_split
from abc import ABC, abstractmethod
import multiprocessing
import psutil
import gc
from errorhandler import ErrorHandler
import joblib
from joblib import dump

class TreinadorIA(ABC):
    def __init__(self, db_manager, diretorio_temporario, num_iteracoes=10, memoria_maxima=None, cpu_maximo=None, **kwargs):
        self.db_manager = db_manager
        self.diretorio_temporario = diretorio_temporario
        self.num_iteracoes = num_iteracoes
        self.memoria_maxima = memoria_maxima  # Limite máximo de memória (em bytes)
        self.cpu_maximo = cpu_maximo  # Limite máximo de uso de CPU (em porcentagem)
        self.kwargs = kwargs
        self.logger = None  # Para configurar logging posteriormente
        self.modelo = self.criar_modelo()
        self.error_handler = ErrorHandler()  # Instancia o ErrorHandler

    @abstractmethod
    def criar_modelo(self):
        pass

    @abstractmethod
    def pre_processar_dados(self, dados):
        pass

    @abstractmethod
    def combinar_pesos(self, instancias_modelos):
        pass

    @abstractmethod
    def salvar_melhor_pesos(self, modelo):
        pass

    def configurar_logging(self, nome_logger):
        logger = logging.getLogger(nome_logger)
        logger.setLevel(logging.INFO)
        handler_console = logging.StreamHandler()
        handler_console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levellevel)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        handler_console.setFormatter(formatter)
        logger.addHandler(handler_console)
        log_filename = datetime.now().strftime(f'{nome_logger}_%Y%m%d_%H%M%S.log')
        log_filepath = os.path.join(self.diretorio_temporario, log_filename)
        file_handler = logging.FileHandler(log_filepath, mode='w', encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        self.logger = logger
        print(f"Logs de treinamento serão salvos em: {log_filepath}")

    def monitorar_recursos(self):
        try:
            if self.memoria_maxima and psutil.virtual_memory().used > self.memoria_maxima:
                raise MemoryError("O uso de memória excedeu o limite máximo permitido.")
            if self.cpu_maximo and psutil.cpu_percent(interval=1) > self.cpu_maximo:
                raise RuntimeError("O uso de CPU excedeu o limite máximo permitido.")
        except MemoryError as e:
            self.error_handler.handle_error('memory_error', str(e), 'memória')
        except RuntimeError as e:
            self.error_handler.handle_error('cpu_error', str(e), 'CPU')

    def treinar_multiplas_instancias(self, dados, num_instancias):
        with multiprocessing.Pool(processes=num_instancias) as pool:
            resultados = pool.starmap(self._treinar_instancia, [(dados, i) for i in range(num_instancias)])
        return resultados

    def _treinar_instancia(self, dados, i):
        print(f"Treinando instância {i+1}")
        modelo_instancia = self.criar_modelo()  # Cria uma nova instância do modelo
        treinador_instancia = self.__class__(self.db_manager, self.diretorio_temporario, self.num_iteracoes, self.memoria_maxima, self.cpu_maximo, **self.kwargs)
        treinador_instancia.configurar_logging(f'instancia_{i+1}')
        treinador_instancia.monitorar_recursos()  # Monitorar recursos antes de treinar
        modelo_instancia, precisao = treinador_instancia.treinar_modelo(dados, iteracao=i)
        return modelo_instancia, precisao

    def treinar_modelo(self, dados, iteracao):
        x, y = self.pre_processar_dados(dados)
        x_treino, x_teste, y_treino, y_teste = train_test_split(x, y, test_size=0.2, random_state=42)
        self.modelo.fit(x_treino, y_treino, epochs=self.num_iteracoes, batch_size=32)
        y_predito = self.modelo.predict(x_teste)
        precisao = accuracy_score(y_teste, y_predito.round())
        print(f"Iteração {iteracao}, Precisão: {precisao}")
        if self.logger:
            self.logger.info(f"Iteração {iteracao}, Precisão: {precisao}")
        return self.modelo, precisao

class TreinadorIATensorFlow(TreinadorIA):
    def __init__(self, db_manager, diretorio_temporario, num_iteracoes=10, **kwargs):
        super().__init__(db_manager, diretorio_temporario, num_iteracoes, **kwargs)

    def importar_bibliotecas_e_dados_necessarios(self):
        import tensorflow as tf
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import Dense, Flatten
        from tensorflow.keras.utils import to_categorical
        from sklearn.metrics import accuracy_score

    def criar_modelo(self):
        # Criar o modelo usando TensorFlow
        input_shape = self.kwargs['input_shape']
        layers_config = self.kwargs['layers']
        optimizer = self.kwargs.get('optimizer', 'rmsprop')
        loss = self.kwargs.get('loss', 'categorical_crossentropy')
        metrics = self.kwargs.get('metrics', ['accuracy'])
        
        model = Sequential()
        for layer in layers_config:
            model.add(layer)
        model.compile(optimizer=optimizer, loss=loss, metrics=metrics)
        return model

    def pre_processar_dados(self, dados):
        x = dados["features"]
        y = dados["labels"]

        # Normalizar dados, se necessário
        if isinstance(x, np.ndarray):
            x = x.astype('float32') / 255.0
        
        # Transformar labels em formato one-hot encoding
        if isinstance(y, np.ndarray):
            y = to_categorical(y)

        return x, y

    def combinar_pesos(self, instancias_modelos):
        # Combinar os pesos e biases dos modelos treinados
        numero_modelos = len(instancias_modelos)
        modelo_base = self.criar_modelo()
        for camada in range(len(modelo_base.layers)):
            pesos = [instancia[0].layers[camada].get_weights() for instancia in instancias_modelos]
            nova_pesos = [np.mean([peso[i] for peso in pesos], axis=0) for i in range(len(pesos[0]))]
            modelo_base.layers[camada].set_weights(nova_pesos)
        return modelo_base

    def salvar_melhor_pesos(self, modelo):
        # Salvar os melhores pesos do modelo treinado
        caminho_melhor_pesos = os.path.join(self.diretorio_temporario, "melhor_pesos.h5")
        modelo.save_weights(caminho_melhor_pesos)
        print(f"Pesos salvos em: {caminho_melhor_pesos}")
        return caminho_melhor_pesos


class TreinadorIAScikitLearn(TreinadorIA):
    def __init__(self, db_manager, diretorio_temporario, num_iteracoes=10, **kwargs):
        super().__init__(db_manager, diretorio_temporario, num_iteracoes, **kwargs)

    def importar_bibliotecas_e_dados_necessarios(self):
        import sklearn
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import StandardScaler
        from sklearn.pipeline import make_pipeline
        from sklearn.metrics import accuracy_score

    def criar_modelo(self):
        # Criar o modelo usando scikit-learn
        modelo = make_pipeline(StandardScaler(), RandomForestClassifier(n_estimators=100))
        return modelo

    def pre_processar_dados(self, dados):
        x = dados["features"]
        y = dados["labels"]
        return x, y

    def combinar_pesos(self, instancias_modelos):
        # Combinar pesos em modelos de scikit-learn não é trivial,
        # então para simplificar vamos escolher o modelo com a maior precisão
        melhor_modelo = max(instancias_modelos, key=lambda x: x[1])[0]
        return melhor_modelo

    def salvar_melhor_pesos(self, modelo):
        # Salvar o melhor modelo usando joblib
        caminho_melhor_modelo = os.path.join(self.diretorio_temporario, "melhor_modelo_sklearn.joblib")
        dump(modelo, caminho_melhor_modelo)
        print(f"Modelo salvo em: {caminho_melhor_modelo}")
        return caminho_melhor_modelo
