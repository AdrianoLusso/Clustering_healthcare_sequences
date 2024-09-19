from ..utils.Package import Package
from ..mlDomain.AffiliatesHealthcarePathways import AffiliatesHealthcarePathways
from ..mlDomain.builders.AffiliatesHealthcarePathwaysBuilder import AffiliatesHealthcarePathwaysBuilder
from ..mlAlgorithm.SequencesClustering import SequencesClustering

from typing import Union

class MLApplication():

    # THIS STRUCTURE IS FOR THE USER OF THIS CLASS TO KNOW WHICH PARAMETERS TO PASS
    parameters = {
        "affiliatesHealthcarePathways_clustering":
            {
                "debug":bool,
                
                "afiliados_practicas":[None,'un directorio'],
                "afiliados_monodroga":[None,'un directorio'],
                
                "practicas_interes":{
                    "nombre":"'un directorio'",
                    "...":"..."
                },
                "monodrogas_interes":{
                    "nombre":"'un directorio'",
                    "...":"..."
                },
                "estados_timeframes":'un directorio',
                "afiliados_secuencias":'un directorio',
                "afiliados_secuencias_etiquetadas":'un directorio',
                
                "unidad_timeframe":['mes','semestre','anio'],
                "numero_timeframes":int,
                "fecha_superior_ultimo_timeframe":"ejemplo:2024-07-22",
                
                "matriz_disimilitud_precomputada":bool,
                "matriz_disimilitud":"un directorio",

                "n_grupos" : [int,"optimizado"],
                "umbral_de_filtrado_de_grupos": [float,None],

                "agrupamiento":"un directorio"
            }
    }

    def __init__(self) -> None:
        self.ml_domain = None
        self.ml_domain_builder = None
        self.ml_algorithm = None

    def run_affiliatesHealthcarePathways_clustering(self,p:dict):
        '''
        '''
        
        ##########################################
        #      1. CREATE MLDOMAIN BUILDER        #
        ##########################################
        BUILDER = AffiliatesHealthcarePathwaysBuilder(p['debug'])


        ##########################################
        #   2. ADD PRACTICES/DRUGS OF INTEREST   #
        ##########################################
        a:dict = p.get("practicas_interes",None)
        if a is not None:
            for key,value in a.items():
                BUILDER.add_rawDataset_practicesOfInterest(key,value)
            BUILDER.read_practicesOfInterest()
        a:dict = p.get("monodrogas_interes",None)
        if a is not None:
            for key,value in a.items():
                BUILDER.add_rawDataset_drugsOfInterest(key,value)
            BUILDER.read_drugsOfInterest()
                    

        ########################################
        #      ADD AND FILTER THE AFFILIATES   #
        #  3. CONSUMPTION OF PRACTICES/DRUGS   #
        #               DATASETS               #
        ########################################
        a = self.__get_subdict(p,['afiliados_practicas'])
        if a is not None:
            BUILDER.define_rawDataset_affiliatesPractices(a)
            BUILDER.filter_affiliatesPractices_raw_dataset()
        a = self.__get_subdict(p,['afiliados_monodrogas'])
        if a is not None:
            BUILDER.define_rawDataset_affiliatesDrugs(a)
            BUILDER.filter_affiliatesDrugs_raw_dataset()


        ###############################################
        #  4. DEFINE THE BUILDER RESULTS DIRECTORIES  #
        ###############################################
        a = self.__get_subdict(p,[
                                    "estados_timeframes",
                                    "afiliados_secuencias",
                                    "afiliados_secuencias_etiquetadas",
                                    "matriz_disimilitud"])
        BUILDER.define_preprocessedDatasets(a)


        ###############################################
        #    5. DEFINE OTHER PROPERTIES AND DATA      #
        ###############################################
        u = p['unidad_timeframe']
        n = p['numero_timeframes']
        f = p['fecha_superior_ultimo_timeframe']
        BUILDER.define_timeframe_properties(u,n,f)
        BUILDER.define_affiliates_and_timeframes()


        ###############################################
        #          6. CREATE THE ML DOMAIN            #
        ###############################################
        BUILDER.create_timeframe_states_dataset()
        #BUILDER.create_sequences_dataset()
        if not p['matriz_disimilitud_precomputada']:
            BUILDER.calculate_dissimilarity_matrix()
        ML_DOMAIN = BUILDER.get_final_product()


        ###############################################
        #          7. CREATE THE ML ALGORITHM         #
        ###############################################
        ALGORITHM = SequencesClustering()


        ###############################################
        #           8. UPLOAD THE DATASETS            #
        ###############################################
        a = self.__get_subdict(p,[
            "estados_timeframes",
            "afiliados_secuencias",
            "afiliados_secuencias_etiquetadas",
            "matriz_disimilitud"
            ])
        ALGORITHM.upload_datasets(a)


        ###############################################
        #          9. DEFINE HYPERPARAMETERS          #
        ###############################################
        a = self.__get_subdict(p,[
            "n_grupos",
            "umbral_de_filtrado_de_grupos"
        ])
        ALGORITHM.define_hyperparameters(a)


        ###############################################
        #               8. RUN ALGORITHM              #
        ###############################################
        ALGORITHM.apply_ML()
        ALGORITHM.save_results()
        

    def __get_subdict(self,dict,keys):
        try:
            d={
                k:dict[k] for k in keys
            }
        except:
            d=None
        
        return d
    