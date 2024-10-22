from pickle import BUILD

from src.model.mlDomain.builders.AffiliatesHealthcarePathwaysBuilder import AffiliatesHealthcarePathwaysBuilder
from src.model.mlAlgorithm.SequencesClustering import SequencesClustering
from src.utils.ProcessState import ProcessState
from io import StringIO
import threading
import queue

import logging
from logging import getLogger

l = getLogger()
l.addHandler(logging.StreamHandler())
l.setLevel(logging.INFO)


class MLApplication:
    # THIS STRUCTURE IS FOR THE USER OF THIS CLASS TO KNOW WHICH PARAMETERS TO PASS
    parameters = {
        "affiliatesHealthcarePathways_clustering":
            {
                "debug": bool,

                "afiliados_practicas": [None, StringIO],
                "afiliados_monodrogas": [None, StringIO],

                "practicas_interes": {
                    "nombre": StringIO,
                    "...": "..."
                },
                "monodrogas_interes": {
                    "nombre": StringIO,
                    "...": "..."
                },
                #"estados_timeframes": 'un directorio',
                #"afiliados_secuencias": 'un directorio',
                #"afiliados_secuencias_etiquetadas": 'un directorio',

                "unidad_timeframe": ['mes', 'semestre', 'anio'],
                "numero_timeframes": int,
                "fecha_superior_ultimo_timeframe": "ejemplo:2024-07-22",

                "matriz_disimilitud_precomputada": bool,
                "matriz_disimilitud": [None,StringIO],

                "afiliados_secuencias_etiquetadas_precomputada": bool,
                "afiliados_secuencias_etiquetadas": [None, StringIO],

                "n_grupos": [int, "optimizado"],
                "umbral_de_filtrado_de_grupos": [float, None],

                #"agrupamiento": "un directorio"
            }
    }

    all_process_states = {
        'affiliatesHealthcarePathways_clustering':[
            'processing_datasets',
            'creating_timeframe_states_dataset',
            'creating_sequences_dataset',
            'creating_dissimilarity_matrix',
            'running_algorithm'
        ]
    }

    def __init__(self) -> None:
        self.ml_domain = None
        self.ml_domain_builder = None
        self.ml_algorithm = None

        self.process_state = ProcessState([
            'processing_datasets',
            'creating_timeframe_states_dataset',
            'creating_sequences_dataset',
            'creating_dissimilarity_matrix',
            'running_algorithm'
        ])
        #self.state_sem = threading.Semaphore(0)
        #self.lock = threading.Lock()
        #self.process_state = 'stop'

    def run_affiliatesHealthcarePathways_clustering(self, p: dict):
        '''
        '''
        l.info("11111111")
        ##########################################
        #      1. CREATE MLDOMAIN BUILDER        #
        ##########################################
        BUILDER = AffiliatesHealthcarePathwaysBuilder(p['debug'])

        self.process_state.pass_to_next_state()
        ##########################################
        #   2. ADD PRACTICES/DRUGS OF INTEREST   #
        ##########################################
        a = p.get("practicas_interes", None)
        l.info("22222")

        if a is not None:
            for key, value in a.items():
                BUILDER.add_rawDataset_practicesOfInterest(key, value)
            BUILDER.read_practicesOfInterest()
        a = p.get("monodrogas_interes", None)
        if a is not None:
            for key, value in a.items():
                BUILDER.add_rawDataset_drugsOfInterest(key, value)
            BUILDER.read_drugsOfInterest()

        ########################################
        #      ADD AND FILTER THE AFFILIATES   #
        #  3. CONSUMPTION OF PRACTICES/DRUGS   #
        #               DATASETS               #
        ########################################
        l.info("3333")

        ap = self.__get_subdict(p, ['afiliados_practicas'])
        if ap is not None:
            BUILDER.define_rawDataset_affiliatesPractices(ap)
            #BUILDER.filter_affiliatesPractices_raw_dataset()
        ad = self.__get_subdict(p, ['afiliados_monodrogas'])
        if ad is not None:
            BUILDER.define_rawDataset_affiliatesDrugs(ad)
            #BUILDER.filter_affiliatesDrugs_raw_dataset()

        ###############################################
        #  4. DEFINE THE BUILDER RESULTS DIRECTORIES  #
        ###############################################
        '''a = self.__get_subdict(p, [
            "estados_timeframes",
            "afiliados_secuencias",
            "afiliados_secuencias_etiquetadas",
            "matriz_disimilitud"])
        BUILDER.define_preprocessedDatasets(a)'''

        l.info("444")

        ###############################################
        #    5. DEFINE OTHER PROPERTIES AND DATA      #
        ###############################################
        u = p['unidad_timeframe']
        n = p['numero_timeframes']
        f = p['fecha_superior_ultimo_timeframe']
        l.info("AAA")

        BUILDER.define_timeframe_properties(u, n, f)
        l.info("BBB")

        if ap is not None:
            l.info("CCC")
            BUILDER.filter_affiliatesPractices_raw_dataset()
            l.info("CCCPASO")
        if ad is not None:
            l.info("DDD")
            BUILDER.filter_affiliatesDrugs_raw_dataset()
            l.info("444")
        BUILDER.define_affiliates_and_timeframes()

        ###############################################
        #          6. CREATE THE ML DOMAIN            #
        ###############################################
        self.process_state.pass_to_next_state()
        BUILDER.create_timeframe_states_dataset()

        self.process_state.pass_to_next_state()
        if p['afiliados_secuencias_etiquetadas_precomputada']:
            BUILDER.preprocessedDataset['afiliados_secuencias_etiquetadas'] = p['afiliados_secuencias_etiquetadas']
            BUILDER.preprocessedDataset['afiliados_secuencias'] = p['afiliados_secuencias']
        else:
            BUILDER.create_sequences_dataset()
        l.info("5555")

        self.process_state.pass_to_next_state()
        if p['matriz_disimilitud_precomputada']:
            BUILDER.preprocessedDataset['matriz_disimilitud'] = p['matriz_disimilitud']
        else:
            BUILDER.calculate_dissimilarity_matrix()
        l.info("6666")

        ML_DOMAIN = BUILDER.get_final_product()
        estados_timeframes = ML_DOMAIN.datasets['estados_timeframes']
        afiliados_secuencias =  ML_DOMAIN.datasets['afiliados_secuencias']
        afiliados_secuencias_etiquetadas =  ML_DOMAIN.datasets['afiliados_secuencias_etiquetadas']
        matriz_disimilitud = ML_DOMAIN.datasets['matriz_disimilitud']

        self.process_state.pass_to_next_state()
        ###############################################
        #          7. CREATE THE ML ALGORITHM         #
        ###############################################
        ALGORITHM = SequencesClustering()

        ###############################################
        #           8. UPLOAD THE DATASETS            #
        ###############################################
        result = {
            "estados_timeframes": estados_timeframes,
            "afiliados_secuencias": afiliados_secuencias,
            "afiliados_secuencias_etiquetadas": afiliados_secuencias_etiquetadas,
            "matriz_disimilitud": matriz_disimilitud
        }
        ALGORITHM.upload_datasets(result)

        ###############################################
        #          9. DEFINE HYPERPARAMETERS          #
        ###############################################
        a = self.__get_subdict(p, [
            "n_grupos",
            "umbral_de_filtrado_de_grupos"
        ])
        ALGORITHM.define_hyperparameters(a)

        ###############################################
        #               8. RUN ALGORITHM              #
        ###############################################
        ALGORITHM.apply_ML()
        clustering = ALGORITHM.get_results()

        result['agrupamiento_secuencias'] = clustering
        self.process_state.pass_to_next_state()
        return result


    def __get_subdict(self, dict, keys):
        try:
            d = {
                k: dict[k] for k in keys
            }
        except:
            d = None

        return d

    '''
    def set_process_state(self,state):
        with self.lock:
            self.process_state = state
        self.state_sem.release()

    def get_process_state(self):
        with self.lock:
            return self.process_state
    '''