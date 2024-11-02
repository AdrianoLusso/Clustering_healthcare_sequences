from .MLDomainBuilder import MLDomainBuilder
from ..AffiliatesHealthcarePathways import AffiliatesHealthcarePathways
from src.utils.Package import Package

import numpy as np
import pandas as pd
import itertools
from io import StringIO

import subprocess
import os
import tempfile

import logging
from logging import getLogger

import streamlit

##################################
##            LOGGER            ##
##################################
l = getLogger()
l.addHandler(logging.StreamHandler())
l.setLevel(logging.INFO)



class AffiliatesHealthcarePathwaysBuilder(MLDomainBuilder):
    """
    A builder for AffiliatesHealthcarePathways class.

    Attributes:
        - debug (bool)
            if True, makes some prints for debugging purposes.
        - rawDataset_affiliatesPractices (Package)
            saves the raw dataset of medical practices taken by the affiliates.
        - rawDataset_affiliatesDrugs (Package)
            saves the raw dataset of drugs takes by the affiliates.
        - rawDataset_practicesOfInterest (Package)
            saves the raw datasets of the practices of interest. For each category of practices, a different dataset is used.
        - rawDataset_drugsOfInterest (Package)
            saves the raw datasets of the drugs of interest. For each category of drugs, a different dataset is used.
        - preprocessedDataset (Package)
            saves the preprocessed datasets.

        - affiliatesPractices (pd.Dataframe)
            dataframe where each tuple correspond to an affiliate and a practice consumption. Taken from the corresponding dataset.
        - affiliatesDrugs
            dataframe where each tuple correspond to an affiliate and a drug consumption. Taken from the corresponding dataset.
        - practicesOfInterest_ids (list)
            list of ids of practices of interest
        - drugsOfInterest_ids (list)
            list of ids of drugs of interest
        - timeframe_unity (str)
            'mes', 'semestre' or 'anio'
        - n_timeframes (int)
        - sup_date (str)
            the last date of the last dataframe. That means, the superior limit date.
        - affiliates (list)
            list of ids of affiliates
        - timeframes (list)
            list of timeframes


    """

    def __init__(self,debug:bool) -> None:
        """
        Parameters:
            - debug (bool)
                if True, makes some prints for debugging purposes.
        """

        super().__init__(debug)

        ####################      
        #      FILES       #
        ####################
        self.rawDataset_affiliatesPractices = Package(types={
            'afiliados_practicas':StringIO
            }
        )
        self.rawDataset_affiliatesDrugs = Package(types={
            'afiliados_monodrogas':StringIO
            }
        )
        self.rawDataset_practicesOfInterest = {}
        self.rawDataset_drugsOfInterest = {}
        self.preprocessedDataset = {
            "estados_timeframes":StringIO(), # dataset of all possible timeframes states
            "afiliados_secuencias":StringIO(), # dataset of affiliates pathways
            "afiliados_secuencias_etiquetadas":StringIO(), # dataset of affiliates pathways, tagged with the affiliate id
            "matriz_disimilitud":StringIO() # dataset of dissimilarity matrix
        }


        ##########################      
        #       OTHER INFO       #
        ##########################
        self.affiliatesPractices = None
        self.affiliatesDrugs = None
        self.practicesOfInterest_ids = []
        self.drugsOfInterest_ids = []

        self.timeframe_unity = None
        self.n_timeframes = None
        self.sup_date = None
        self.affiliates = None
        self.timeframes = None

    #############################################
    ##           DEFINE AND ADD FILES          ##
    ############################################# 
    def define_rawDataset_affiliatesPractices(self,input_file:dict[str,StringIO]) -> None:
        """
        Saves the raw dataset of medical practices taken by the affiliates.

        Args:
            - input_file (dict[str,str])
                a dictionary with the expected files.
        """
        self.rawDataset_affiliatesPractices.fit(input_file)

    def define_rawDataset_affiliatesDrugs(self,input_file:dict[str,StringIO]) -> None:
        """
        Saves the raw dataset directory of drugs taken by the affiliates.

        Args:
            - input_file (dict[str,StringIO])
                a dictionary with the expected file.
        """
        self.rawDataset_affiliatesDrugs.fit(input_file)

    def add_rawDataset_practicesOfInterest(self,input_name:str,input_file:StringIO) -> None:
        """
        Add a raw dataset of medical practices taken by the affiliates to be saved.

        Args:
            -input_name (str)
                the name of the category of the medical practices to add.
            -input_file (str)
                the expected file.
        """
        self.rawDataset_practicesOfInterest[input_name] = input_file

    def add_rawDataset_drugsOfInterest(self,input_name:str,input_file:StringIO) -> None :
        """
        Add a raw dataset directory of drugs taken by the affiliates to be saved.

        Args:
            - input_name (str)
                the name of the category of the drugs to add.
            - input_file (StringIO)
                the expected file.
        """
        self.rawDataset_drugsOfInterest[input_name] = input_file
    #                                           #
    ############################################# 




    #############################################
    ##   OTHER DEFINITIONS AND CALCULATIONS    ##
    ############################################# 
    def define_timeframe_properties(self,unity:str,n:int,sup_date:str) -> None:
        """
        Saves the time frame properties.

        Args:
            - unity (str)
                the unity size of a timeframe. It could be 'anio', 'semestre' or 'mes'.
            - n (int)
                number of timeframes per pathway.
            - sup_date (str)
                the last date of the last dataframe. That means, the superior limit date.
        """
        if unity not in AffiliatesHealthcarePathways.timeframe_spanish_to_english.keys():
            raise ValueError("Timeframe unity must be 'mes', 'semestre' or 'anio'")

        self.timeframe_unity = AffiliatesHealthcarePathways.timeframe_spanish_to_english[unity]
        self.n_timeframes = n
        self.sup_date = sup_date

    def read_practicesOfInterest(self) -> None:
        """
        Reads the practices of interest from the saved directories, and store them as variables.
        """

        # read each directory and save it in the pi_ids list
        pi_ids = []
        for _,value in self.rawDataset_practicesOfInterest.items():
            dataset = pd.read_csv(value)
            pi_ids += list(dataset.get('id_practica'))
        self.practicesOfInterest_ids = pi_ids

    def read_drugsOfInterest(self) -> None:
        """
        Reads the drugs of interest from the saved directories, and store them as variables.
        """

        # read each directory and save it in the pi_ids list
        di_ids = []
        for key,value in self.rawDataset_drugsOfInterest.items():
            dataset = pd.read_csv(value)
            di_ids += list(dataset.get('id_monodroga'))
        self.drugsOfInterest_ids = di_ids
    #                                           #
    ############################################# 




    #############################################
    ##            MLDOMAIN CREATION            ##
    ############################################# 
    def create_timeframe_states_dataset(self) -> None:
        """
        This method creates and saves the dataset that shows all the possible states for a timeframe.
        """
        #output_directory = self.preprocessedDataset['estados_timeframes']

        # defines the columns names, and the tuples data
        all_ids = self.practicesOfInterest_ids + self.drugsOfInterest_ids
        if len(all_ids)>22:
            raise MemoryError("Amount of practices/drugs > 22 unsupported. There will be an exponential calculus over this amount."
                              +"Going beyond this limit could colapse the memory.")

        num_combinations = 2 ** len(all_ids)
        codes = [hex(i) for i in range(num_combinations)]
        combinations = list(itertools.product([0, 1], repeat=len(all_ids)))
        data = [combination + (code,) for combination,code in zip(combinations,codes)]

        # create the semester states structure
        columns = all_ids.copy()
        columns.append('code')

        semester_states_dataset = pd.DataFrame(data,columns=columns)
        semester_states_dataset.to_csv(self.preprocessedDataset['estados_timeframes'],index=False)
        self.preprocessedDataset['estados_timeframes'].seek(0)
        #semester_states_dataset.to_csv(output_directory,index=False)

        if self.debug:
            print("SEMESTER STATES DATASET SAVED\n")

    def filter_affiliatesPractices_raw_dataset(self) -> None:
        """
        This method filter the raw dataset of medical practices taken by the affiliates, leaving only the tuples between a certain dates interval and associated to the practices of interest.
        """
        ap_raw_dataset = pd.read_csv(self.rawDataset_affiliatesPractices['afiliados_practicas'])
        pi_ids = self.practicesOfInterest_ids

        # filter the tuples that are related to the practices of interest.
        ap_raw_dataset = ap_raw_dataset[ap_raw_dataset['id_practica'].isin(pi_ids)]

        # filter the tuples between a certain dates interval.
        self.affiliatesPractices = self.__filter_raw_dataset_by_dates(ap_raw_dataset)

    def filter_affiliatesDrugs_raw_dataset(self) -> None:
        """
        This method filter the raw dataset of monodrugs taken by the affiliates, leaving only the tuples between a certain dates interval and associated to the practices of interest.
        """
        ad_raw_dataset = pd.read_csv(self.rawDataset_affiliatesDrugs['afiliados_monodrogas'])
        di_ids = self.drugsOfInterest_ids

        # filter the tuples that are related to the practices of interest.
        ad_raw_dataset = ad_raw_dataset[ad_raw_dataset['id_monodroga'].isin(di_ids)]

        # filter the tuples between a certain dates interval.
        self.affiliatesDrugs = self.__filter_raw_dataset_by_dates(ad_raw_dataset)

    def __filter_raw_dataset_by_dates(self,raw_dataset) -> pd.DataFrame:
        """
        This method filters a raw datasets, getting only the tuples between a certain dates interval.

        Parameters:
            - raw_dataset (DataFrame)
                the raw dataset.

        Returns:
            - raw_dataset (DataFrame)
                the pd dataframe filtered by a dates interval.
        """
        # cast 'fecha' attribute to date
        raw_dataset = raw_dataset.copy()
        raw_dataset['fecha'] = pd.to_datetime(raw_dataset['fecha'],format='%d/%m/%Y')

        # generate the inf. limit date
        freq = AffiliatesHealthcarePathways.timeframe_english_to_pandas[self.timeframe_unity]
        inf_date = pd.date_range(end=self.sup_date, periods=self.n_timeframes + 1, freq=freq)[0]

        # define the dates interval
        sup_date = pd.to_datetime(self.sup_date, format='%Y-%m-%d')
        low_date = pd.to_datetime(inf_date, format='%Y-%m-%d')

        # filter dates outside the interval
        raw_dataset = raw_dataset[raw_dataset['fecha'] < sup_date]
        raw_dataset = raw_dataset[raw_dataset['fecha'] > low_date]

        return raw_dataset

    def define_affiliates_and_timeframes(self)-> None:
        """
        This method creates the data structures of affiliates and timeframes
        """
        ap_filtered_dataset = self.affiliatesPractices
        ad_filtered_dataset = self.affiliatesDrugs

        # getting the ids of the affiliates and how many them are.
        affiliates_ids = []
        if ap_filtered_dataset is not None:
            affiliates_ids += list(set(ap_filtered_dataset['id_afiliado']))
        if ad_filtered_dataset is not None:
            affiliates_ids += list(set(ad_filtered_dataset['id_afiliado']))
        self.affiliates = affiliates_ids

        # create the timeframes
        freq = AffiliatesHealthcarePathways.timeframe_english_to_pandas[self.timeframe_unity]
        timeframes = pd.date_range(end=self.sup_date, periods=self.n_timeframes+1, freq=freq) 
        self.timeframes = {
            self.timeframe_unity+'_'+str(i+1):[timeframes[i],timeframes[i+1]]
            for i in range(len(timeframes)-1)
            }

    def create_sequences_dataset(self) -> None:
        """
        This method creates the affiliates healthcare pathways dataset.
        """
        sequences = []

        affiliate_datasets = []
        affiliate_datasets_ids = []
        if self.affiliatesPractices is not None:
            affiliate_datasets.append(self.affiliatesPractices)
            affiliate_datasets_ids.append('id_practica')
        if self.affiliatesDrugs is not None:
            affiliate_datasets.append(self.affiliatesDrugs)
            affiliate_datasets_ids.append('id_monodroga')

        for _,affiliate_id in enumerate(self.affiliates):
            sequence = []
            for timeframe in self.timeframes.values():
                # initialize a timeframe state structure
                current_timeframe_state = self.__get_new_timeframe_state()
                current_timeframe_state = self.__set_timeframe_state(affiliate_id,timeframe,affiliate_datasets,affiliate_datasets_ids,current_timeframe_state)

                # translate the timeframe state to its code and append to the sequence
                sequence.append(self.__timeframe_state_to_code(list(current_timeframe_state.values())))

            # append the resulting sequence to the general data structure
            sequences.append(sequence)
            
        # pass dataset to numpy
        sequences = np.array(sequences)

        # pass dataset to pandas
        columns = ['id_affiliate']+list(self.timeframes.keys())
        data = np.column_stack((np.array(self.affiliates),sequences))

        # save dataframes as StringIOs
        sequences_dataset = pd.DataFrame(data,columns=columns)
        sequences_dataset.to_csv(self.preprocessedDataset['afiliados_secuencias_etiquetadas'],index=False)
        sequences_dataset.drop(columns=['id_affiliate']).to_csv(self.preprocessedDataset['afiliados_secuencias'],index=False)
        self.preprocessedDataset['afiliados_secuencias_etiquetadas'].seek(0)
        self.preprocessedDataset['afiliados_secuencias'].seek(0)

        if self.debug:
            print("SEQUENCES DATASET SAVED")
            print("LABELED SEQUENCES DATASET SAVED\n")

    def __get_new_timeframe_state(self) -> dict:
        """
        This method returns a new timeframe state, initialized as 0.
        """
        ids = self.practicesOfInterest_ids + self.drugsOfInterest_ids

        semester_state = dict(zip(ids,[0 for i in ids]))
        return semester_state
    
    def __timeframe_state_to_code(self,semester_state) -> str:
        """
        Given a timeframe state as a binary list, its transform it to its hexadecimal code.

        Parameters:
            - semester_state

        Returns:
            - code
        """
        # transform binary list to binary string
        binary_string = ''.join(str(bit) for bit in semester_state)
        
        # the binary string must have a size multiple of 4
        padded_binary = binary_string.zfill(len(binary_string) + (4 - len(binary_string) % 4) % 4)
        
        # transform binary string into a decimal
        decimal_value = int(padded_binary, 2)
        
        # transform decimal into hexadecimal
        code = format(decimal_value, 'X')  # 'X' is mayuscules
        
        return code

    def __set_timeframe_state(self
                              ,affiliate_id
                              ,timeframe:list
                              ,affiliate_datasets:list[pd.DataFrame]
                              ,affiliate_datasets_ids:list
                              ,current_timeframe_state:dict) -> dict:
        """
        We set a timeframe state to the particular value it corresponds in function of the affiliate consumptions.

        Args:
            - affiliate_id
            - timeframe (list)
                a list with the initial and final date of a timeframr
            -affiliate_datasets (list)
                a list with the affiliate consumptions datasets
            - affiliate_datasets_ids (list)
                a list with the consumption id for its corresponding affiliate datasets. Expexted to zip() with affiliat_datasets.
            - current_timeframe_state (dict)

        Returns:
            - current_timeframe_state
                the setted version of the timeframe state
        """
        # the low and superior dates of the current timeframe
        low_date = timeframe[0]
        sup_date = timeframe[1]

        # given an affiliate and a timeframe, we get the practices done by that affiliate in that timeframe
        filtered_datasets = []
        for dataset,dataset_id in zip(affiliate_datasets,affiliate_datasets_ids):
            filtered_datasets.append(
                dataset[
                (dataset['fecha'] >= low_date)
                & (dataset['fecha'] < sup_date)
                & (dataset['id_afiliado'] == affiliate_id)
                ][dataset_id]
            )

        # we use each practice found to change acordingly to the timeframe state data structure
        # if a practice was found, its corresponding binary value changes to 1
        for fd in filtered_datasets:
            for inst_id in fd:
                current_timeframe_state[inst_id] = 1

        return current_timeframe_state

    def calculate_dissimilarity_matrix(self) -> None:
        """
        This method run the R script that calculate the dissimilarity matrix
        """
        script_dir = os.path.dirname(__file__)+'/../../scripts/optimal_matching.R'

        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.csv') as temp_file:
            temp_file.write(self.preprocessedDataset['afiliados_secuencias'].getvalue())
            temp_file_path = temp_file.name

        try:
            result = subprocess.run(['Rscript', script_dir,
                                    temp_file_path
                                ],
                                check=True, capture_output=True, text=True)
        except Exception as e:
            result = e
        
        l.info('ERR: ',str(result.stderr))

        self.preprocessedDataset['matriz_disimilitud'] = StringIO(result.stdout)

        if self.debug:
            print("DISSIMILARITY MATRIX SAVED")
    #                                           #
    ############################################# 




    #############################################
    ##                 RESULTS                 ##
    ############################################# 
    def get_final_product(self) -> AffiliatesHealthcarePathways:
        """
        This method gets the final product: a ML Domain of Affiliates Healthcare Pathways.

        Returns:
            product (AffiliatesHealthcarePathways)
        """

        files = {}
        files.update(self.rawDataset_affiliatesPractices)
        files.update(self.rawDataset_affiliatesDrugs)
        files.update(self.rawDataset_practicesOfInterest)
        files.update(self.rawDataset_drugsOfInterest)
        files.update(self.preprocessedDataset)

        self.product = AffiliatesHealthcarePathways(
            files
            ,self.timeframe_unity
            ,self.n_timeframes
        )

        return self.product
    #                                           #
    ############################################# 
