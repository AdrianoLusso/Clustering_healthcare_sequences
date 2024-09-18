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
                
                "afiliados_practicas":Union(None,'un directorio'),
                "afiliados_monodroga":Union(None,'un directorio'),
                
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
                "fecha_superior_ultimo_timeframe":"2024-07-22",
                
                "matriz_disimilitud_precomputada":bool,
                "matriz_disimilitud":"un directorio"
                ### QUEDE ACAA, VOY A PASAR LO DE DISMILITUD AL ML DOMAIN
            }
    }

    def __init__(self) -> None:
        self.ml_domain = None
        self.ml_domain_builder = None
        self.ml_algorithm = None

    def run_affiliatesHealthcarePathways_clustering(self,p:dict):
        '''
        '''
        
        b = AffiliatesHealthcarePathwaysBuilder(p['debug'])

        ##########################################
        #   1. ADD PRACTICES/DRUGS OF INTEREST   #
        ##########################################
        a:dict = p.get("practicas_interes",None)
        if a is not None:
            for key,value in a.items():
                b.add_rawDataset_practicesOfInterest(key,value)
            b.read_practicesOfInterest()
        a:dict = p.get("monodrogas_interes",None)
        if a is not None:
            for key,value in a.items():
                b.add_rawDataset_drugsOfInterest(key,value)
            b.read_drugsOfInterest()
                    

        ########################################
        #      ADD AND FILTER THE AFFILIATES   #
        #  2. CONSUMPTION OF PRACTICES/DRUGS   #
        #               DATASETS               #
        ########################################
        a = self.__get_subdict(p,['afiliados_practicas'])
        if a is not None:
            b.define_rawDataset_affiliatesPractices(a)
            b.filter_affiliatesPractices_raw_dataset()
        a = self.__get_subdict(p,['afiliados_monodrogas'])
        if a is not None:
            b.define_rawDataset_affiliatesDrugs(a)
            b.filter_affiliatesDrugs_raw_dataset()


        ###############################################
        #  3. DEFINE THE BUILDER RESULTS DIRECTORIES  #
        ###############################################
        a = self.__get_subdict(p,[
                                    "estados_timeframes",
                                    "afiliados_secuencias",
                                    "afiliados_secuencias_etiquetadas"])
        b.define_preprocessedDatasets(a)


        ###############################################
        #    5. DEFINE OTHER PROPERTIES AND DATA      #
        ###############################################
        u = p['unidad_timeframe']
        n = p['numero_timeframes']
        f = p['fecha_superior_ultimo_timeframe']
        b.define_timeframe_properties(u,n,f)
        b.define_affiliates_and_timeframes()


        ###############################################
        #          6. CREATE THE ML DOMAIN            #
        ###############################################
        b.create_timeframe_states_dataset()
        b.create_sequences_dataset()
        ML_DOMAIN = b.get_final_product()


        algorithm = SequencesClustering()
        
        a = self.__get_subdict(p,[
            "estados_semestre",
            "afiliados_secuencias",
            "afiliados_secuencias_etiquetadas",
            "matriz_disimilitud"
            ])

        if p['matriz_disimilitud'] is None:
            algorithm.calculate_dissimilarity_matrix()


        algorithm.upload_datasets(a)




        



        

    def __get_subdict(dict,keys):
        try:
            d={
                k:dict[k] for k in keys
            }
        except:
            d=None
        
        return d
    