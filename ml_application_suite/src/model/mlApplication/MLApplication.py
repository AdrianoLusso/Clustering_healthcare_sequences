from debugpy.launcher.debuggee import process

from src.model.mlDomain.builders.AffiliatesHealthcarePathwaysBuilder import AffiliatesHealthcarePathwaysBuilder
from src.model.mlAlgorithm.SequencesClustering import SequencesClustering
from src.utils.ProcessState import ProcessState
import traceback

from io import StringIO


import logging
from logging import getLogger

##################################
##            LOGGER            ##
##################################
l = getLogger()
l.addHandler(logging.StreamHandler())
l.setLevel(logging.INFO)


class MLApplication:
    """
    Represents an API between for ML algorithms and ML domains, implementing a general workflow of it.
    It is recommended to use it to decrease the complexity of the programming, and when you don't need
    to have too specific configuration among the ML workflow.

    Attributes:
        - parameters (dict)
            a dictionary where, for each app. method of the class, stores the expected input dictionary of inputs.
        - all_process_states (dict)
            a dictionary where, for each app. method of the class, stores all the possible state the app will pass through.
            Specially useful for concurrent management of the current workflow state from the front-end.
        - ml_domain (MLDomain)
        - ml_domain_builder (MLDomainBuilder)
        - ml_algorithm_builder (MLAlgorithm)
        - process_state (ProcessState)
            an object that stores and evolute the current state of the MLApplication.

    """

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
                "unidad_timeframe": ['mes', 'semestre', 'anio'],
                "numero_timeframes": int,
                "fecha_superior_ultimo_timeframe": "ejemplo:2024-07-22",

                "matriz_disimilitud_precomputada": bool,
                "matriz_disimilitud": [None,StringIO],

                "afiliados_secuencias_etiquetadas_precomputada": bool,
                "afiliados_secuencias_etiquetadas": [None, StringIO],

                "n_grupos": [int, "optimizado"]
            }
    }

    # THIS STRUCTURE IS FOR THE USER OF THIS CLASS TO KNOW ALL THE STATE A PARTICULAR STATE PASS THROUGH
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

    def run_affiliatesHealthcarePathways_clustering(self, p: dict):
        """

        """
        try:
            ##########################################
            #      1. CREATE MLDOMAIN BUILDER        #
            ##########################################
            BUILDER = AffiliatesHealthcarePathwaysBuilder(p['debug'])

            self.process_state.pass_to_next_state()
            ##########################################
            #   2. ADD PRACTICES/DRUGS OF INTEREST   #
            ##########################################
            a = p.get("practicas_interes", None)

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
            #           ADD THE AFFILIATES         #
            #  3. CONSUMPTION OF PRACTICES/DRUGS   #
            #               DATASETS               #
            ########################################
            ap = self.__get_subdict(p, ['afiliados_practicas'])
            if ap is not None:
                BUILDER.define_rawDataset_affiliatesPractices(ap)
            ad = self.__get_subdict(p, ['afiliados_monodrogas'])
            if ad is not None:
                BUILDER.define_rawDataset_affiliatesDrugs(ad)

            ###############################################
            #    4. DEFINE OTHER PROPERTIES AND DATA      #
            ###############################################
            u = p['unidad_timeframe']
            n = p['numero_timeframes']
            f = p['fecha_superior_ultimo_timeframe']
            BUILDER.define_timeframe_properties(u, n, f)

            ###############################################
            #  5. CREATE THE AFFILIATES AND TIMEFRAMES    #
            ###############################################
            if ap is not None:
                BUILDER.filter_affiliatesPractices_raw_dataset()
            if ad is not None:
                BUILDER.filter_affiliatesDrugs_raw_dataset()
            BUILDER.define_affiliates_and_timeframes()

            ###############################################
            #          6. CREATE THE TIMEFRAME            #
            #               STATES DATASET                #
            ###############################################
            self.process_state.pass_to_next_state()
            BUILDER.create_timeframe_states_dataset()

            ###############################################
            #          7. CREATE, IF NECESSARY,           #
            #          THE SEQUENCES DATASET AND          #
            #          THE DISSIMILARITY MATRIX           #
            ###############################################
            self.process_state.pass_to_next_state()
            if p['afiliados_secuencias_etiquetadas_precomputada']:
                BUILDER.preprocessedDataset['afiliados_secuencias_etiquetadas'] = p['afiliados_secuencias_etiquetadas']
                BUILDER.preprocessedDataset['afiliados_secuencias'] = p['afiliados_secuencias']
            else:
                BUILDER.create_sequences_dataset()

            self.process_state.pass_to_next_state()
            if p['matriz_disimilitud_precomputada']:
                BUILDER.preprocessedDataset['matriz_disimilitud'] = p['matriz_disimilitud']
            else:
                BUILDER.calculate_dissimilarity_matrix()
            l.info("6666")

            ###############################################
            #           8. CREATE THE ML DOMAIN           #
            ###############################################
            ML_DOMAIN = BUILDER.get_final_product()
            estados_timeframes = ML_DOMAIN.datasets['estados_timeframes']
            afiliados_secuencias =  ML_DOMAIN.datasets['afiliados_secuencias']
            afiliados_secuencias_etiquetadas =  ML_DOMAIN.datasets['afiliados_secuencias_etiquetadas']
            matriz_disimilitud = ML_DOMAIN.datasets['matriz_disimilitud']

            self.process_state.pass_to_next_state()
            ###############################################
            #          9. CREATE THE ML ALGORITHM         #
            ###############################################
            ALGORITHM = SequencesClustering()

            ###############################################
            #           10. UPLOAD THE DATASETS            #
            ###############################################
            result = {
                "estados_timeframes": estados_timeframes,
                "afiliados_secuencias": afiliados_secuencias,
                "afiliados_secuencias_etiquetadas": afiliados_secuencias_etiquetadas,
                "matriz_disimilitud": matriz_disimilitud
            }
            ALGORITHM.upload_datasets(result)

            ###############################################
            #          11. DEFINE HYPERPARAMETERS          #
            ###############################################
            a = self.__get_subdict(p, [
                "n_grupos"
            ])
            ALGORITHM.define_hyperparameters(a)

            ###############################################
            #               12. RUN ALGORITHM              #
            ###############################################
            ALGORITHM.apply_ML()
            clustering = ALGORITHM.get_results()

            result['agrupamiento_secuencias'] = clustering
            self.process_state.pass_to_next_state()
        except:
            traceback.print_exc()
            self.process_state.set_fail_state()
            result = -1
        return result


    def __get_subdict(self, dict, keys):
        try:
            d = {
                k: dict[k] for k in keys
            }
        except:
            d = None

        return d

