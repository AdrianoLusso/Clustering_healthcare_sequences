from .MLDomainBuilder import MLDomainBuilder
from ..AffiliatesHealthcarePathways import AffiliatesHealthcarePathways
from ...utils.Package import Package

import numpy as np
import pandas as pd
import itertools

class AffiliatesHealthcarePathwaysBuilder(MLDomainBuilder):

    def __init__(self,debug) -> None:
        super().__init__(debug)

        ####################      
        #   DIRECTORIES    # 
        ####################
        self.rawDataset_affiliatesPractices_directory = Package(types={
            'afiliados_practicas':str
            }
        )
        self.rawDataset_affiliatesDrugs_directory = Package(
            types={
            'afiliados_monodrogas':str
            }
        )
        self.rawDataset_practicesOfInterest_directories = {}
        self.rawDataset_drugsOfInterest_directories = {}
        self.preprocessedDataset_directories = Package(types={
            "estados_timeframes":str,
            "afiliados_secuencias":str,
            "afiliados_secuencias_etiquetadas":str
        })

        ##########################      
        #   DATASETS AND INFO    # 
        ##########################
        self.affiliatesPractices = None
        self.affiliatesDrugs = None
        self.practicesOfInterest_ids = []
        self.drugsOfInterest_ids = []
        



    #############################################
    ##        DEFINE AND ADD DIRECTORIES       ##
    ############################################# 
    def define_rawDataset_affiliatesPractices(self,input_directory):
        '''
        '''
        self.rawDataset_affiliatesPractices_directory.fit(input_directory)

    def define_rawDataset_affiliatesDrugs(self,input_directory):
        '''
        '''
        self.rawDataset_affiliatesDrugs_directory.fit(input_directory)

    def add_rawDataset_practicesOfInterest(self,input_name,input_directory):
        '''
        '''
        self.rawDataset_practicesOfInterest_directories[input_name] = input_directory

    def add_rawDataset_drugsOfInterest(self,input_name,input_directory):
        '''
        '''
        self.rawDataset_drugsOfInterest_directories[input_name] = input_directory

    def define_preprocessedDatasets(self,input_directories):
        '''
        '''
        self.preprocessedDataset_directories.fit(input_directories)
    #                                           #
    ############################################# 




    #############################################
    ##   OTHER DEFINITIONS AND CALCULATIONS    ##
    ############################################# 
    def define_timeframe_properties(self,unity:str,n:int,sup_date:str):
        '''
        '''
        if unity not in AffiliatesHealthcarePathways.timeframes_spanish_to_english.keys():
            raise ValueError("Timeframe unity must be 'mes', 'semestre' or 'anio'")

        self.timeframe_unity = AffiliatesHealthcarePathways.timeframes_spanish_to_english[unity]
        self.n_timeframes = n
        self.sup_date = sup_date

    def read_practicesOfInterest(self):
        '''
        '''
        # read practices of interest (pi) to analyze dataset
        # and other important data
        pi_ids = []
        for _,value in self.rawDataset_practicesOfInterest_directories.items():
            dataset = pd.read_csv(value)
            pi_ids += list(dataset.get('id_practica'))

        self.practicesOfInterest_ids = pi_ids

    def read_drugsOfInterest(self):
        '''
        '''
        # read drugs of interest (di) to analyze dataset
        # and other important data
        di_raw_datasets = []
        di_ids = []
        for key,value in self.rawDataset_drugsOfInterest_directories.items():
            dataset = pd.read_csv(value)
            di_raw_datasets.append(dataset)
            di_ids.append(list(dataset.get('id_monodroga')))  

        self.drugsOfInterest_ids = di_ids      
    #                                           #
    ############################################# 




    #############################################
    ##            MLDOMAIN CREATION            ##
    ############################################# 
    def create_timeframe_states_dataset(self):
        '''
        '''
        output_directory = self.preprocessedDataset_directories['estados_timeframes']

        # defines the columns names, and the tuples data
        all_ids = self.practicesOfInterest_ids + self.drugsOfInterest_ids
        if len(all_ids)>22:
            raise MemoryError("Amount of practices/drugs > 22 unsupported. There will be an exponential calculus over this amount."+
                              +"Going beyond this limit could colapse the memory.")

        num_combinations = 2 ** len(all_ids)
        codes = [hex(i) for i in range(num_combinations)]
        combinations = list(itertools.product([0, 1], repeat=len(all_ids)))
        data = [combination + (code,) for combination,code in zip(combinations,codes)]

        # create the semester states structure
        columns = all_ids.copy()
        columns.append('code')
        semester_states_dataset = pd.DataFrame(data,columns=columns)
        semester_states_dataset.to_csv(output_directory,index=False)

        if self.debug:
            print("SEMESTER STATES DATASET SAVED IN "+output_directory+'\n')

    def filter_affiliatesPractices_raw_dataset(self):
        '''
        '''
        ap_raw_dataset = pd.read_csv(self.rawDataset_affiliatesPractices_directory['afiliados_practicas'])
        pi_ids = self.practicesOfInterest_ids
        self.affiliatesPractices = self.__filter_raw_dataset(ap_raw_dataset,pi_ids)

    def filter_affiliatesDrugs_raw_dataset(self):
        '''
        '''
        ad_raw_dataset = pd.read_csv(self.rawDataset_affiliatesDrugs_directory['afiliados_monodrogas'])
        di_ids = self.drugsOfInterest_ids
        self.affiliatesDrugs = self.__filter_raw_dataset(ad_raw_dataset,di_ids)

    def __filter_raw_dataset(self,raw_dataset,ids):
        '''
        '''
        # cast 'fecha' attribute to date
        raw_dataset = raw_dataset.copy()
        raw_dataset['fecha'] = pd.to_datetime(raw_dataset['fecha'],format='%d/%m/%Y')

        # define the dates interval
        sup_date = pd.to_datetime('01/07/2024', format='%d/%m/%Y')
        low_date = pd.to_datetime('31/12/2020', format='%d/%m/%Y')

        # filter dates outside the interval
        raw_dataset = raw_dataset[raw_dataset['fecha'] < sup_date]
        raw_dataset = raw_dataset[raw_dataset['fecha'] > low_date]

        #filter all the tuples in which its 'id_practica' is not part of the practices of interest
        raw_dataset = raw_dataset[raw_dataset['id_practica'].isin(ids)]

        return raw_dataset

    def define_affiliates_and_timeframes(self):
        '''
        '''
        ap_filtered_dataset = self.affiliatesPractices
        ad_filtered_dataset = self.affiliatesDrugs

        # getting the ids of the affiliates and how many them are
        affiliates_ids = []
        if ap_filtered_dataset is not None:
            affiliates_ids += list(set(ap_filtered_dataset['id_afiliado']))
        if ad_filtered_dataset is not None:
            affiliates_ids += list(set(ad_filtered_dataset['id_afiliado']))
        self.affiliates = affiliates_ids

        freq = AffiliatesHealthcarePathways.timeframe_english_to_pandas[self.timeframe_unity]
        timeframes = pd.date_range(end=self.sup_date, periods=self.n_timeframes+1, freq=freq) 
        self.timeframes = {
            self.timeframe_unity+'_'+str(i+1):[timeframes[i],timeframes[i+1]]
            for i in range(len(timeframes)-1)
            }

    def create_sequences_dataset(self):
        '''
        '''
        sequences = []
        ap = self.affiliatesPractices

        for _,affiliate_id in enumerate(self.affiliates):
            
            sequence = []
            for timeframe in self.timeframes.values():
                # initializa a timeframe state structure
                current_timeframe_state = self.__get_new_timeframe_state()

                # the low and superior dates of the current timeframe
                low_date = timeframe[0]
                sup_date = timeframe[1]

                # given an affiliate an a timeframe, we get the practices done by that affiliate in that timeframe
                practices = ap[ 
                        (ap['fecha'] >= low_date)
                        & (ap['fecha'] < sup_date)
                        & (ap['id_afiliado'] == affiliate_id)
                        ]['id_practica']

                # we use each practice found to change acordingly the timeframe state data structure
                # if a practice was found, its corresponding binary value changes to 1
                for practice in practices:
                    current_timeframe_state[practice] = 1
                # translate the timegrame state to its code and append to the sequence
                sequence.append(self.__timeframe_state_to_code(list(current_timeframe_state.values())))
            # append the resulting sequence to the general data structure
            sequences.append(sequence)
            
        # pass dataset to numpy
        sequences = np.array(sequences)

        # pass dataset to pandas
        columns = ['id_affiliate']+list(self.timeframes.keys())
        data = np.column_stack((np.array(self.affiliates),sequences))
        sequences_dataset = pd.DataFrame(data,columns=columns)

        sequences_dataset.to_csv(self.preprocessedDataset_directories['afiliados_secuencias_etiquetadas'],index=False)
        sequences_dataset.drop(columns=['id_affiliate']).to_csv(self.preprocessedDataset_directories['afiliados_secuencias'],index=False)

        if self.debug:
            print("LABELED SEQUENCES DATASET SAVED IN "+self.preprocessedDataset_directories['afiliados_secuencias_etiquetadas'])
            print("LABELED SEQUENCES DATASET SAVED IN "+self.preprocessedDataset_directories['afiliados_secuencias']+'\n')

    def __get_new_timeframe_state(self):
        '''
        '''
        ids = self.practicesOfInterest_ids + self.drugsOfInterest_ids

        semester_state = dict(zip(ids,[0 for i in ids]))
        return semester_state
    
    def __timeframe_state_to_code(self,semester_state):
        '''
        Given a timeframe state as a binary list, its transform it to its hexadecimal code.
        '''
        # transform binary list to binary string
        binary_string = ''.join(str(bit) for bit in semester_state)
        
        # the binary string must have a size multiple of 4
        padded_binary = binary_string.zfill(len(binary_string) + (4 - len(binary_string) % 4) % 4)
        
        # transform binary string into a decimal
        decimal_value = int(padded_binary, 2)
        
        # transform decimal into hexadecimal
        code = format(decimal_value, 'X')  # 'X' is mayuscules
        
        return code
    #                                           #
    ############################################# 




    #############################################
    ##                 RESULTS                 ##
    ############################################# 
    def get_final_product(self):
        directories = {}
        directories.update(self.rawDataset_affiliatesPractices_directory)
        directories.update(self.rawDataset_affiliatesDrugs_directory)
        directories.update(self.rawDataset_practicesOfInterest_directories)
        directories.update(self.rawDataset_drugsOfInterest_directories)
        directories.update(self.preprocessedDataset_directories)

        self.product = AffiliatesHealthcarePathways(
            directories
            ,self.timeframe_unity
            ,self.n_timeframes
        )

        return self.product
    #                                           #
    ############################################# 
