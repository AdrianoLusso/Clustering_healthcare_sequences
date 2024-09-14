from MLApplication import MLApplication
from Package import Package

import numpy as np
import pandas as pd
import itertools

import os
import subprocess

from typing import Dict



class AffiliateHealthcarePatways_MLApplication(MLApplication):

    def __init__(self) -> None:
        super().__init__()
        self.input_directories = Package(props={
            'afiliados_practicas':str,
            'practicas_diabetes':str
        })
        self.output_directories = Package(props={
            "estados_semestre":str,
            "afiliados_secuencias":str,
            "afiliados_secuencias_etiquetadas":str,
            "matriz_disimilitud":str
        })

    # PREPROCCESING AND ITS AUXILIARY METHODS

    def preprocess_raw_dataset(self,input_directories:Dict, output_directories:Dict) -> bool:
        '''
        ESPECIFICAR QUE ESTRUCTURA DICTIONARIA SE MECESITA
        '''

        self.input_directories.fit(input_directories)
        self.output_directories.fit(output_directories)

        # affiliantes and practices datasets
        ap_raw_dataset = pd.read_csv(self.input_directories['afiliados_practicas'])

        # diabetes practices to analyze dataset
        # and other important data
        dp_raw_dataset = pd.read_csv(self.input_directories['practicas_diabetes'])
        dp_ids = list(dp_raw_dataset.get('id_practica'))
        n_dp_ids = len(dp_ids)

        # define as attributes
        self.ap_raw_dataset = ap_raw_dataset
        self.dp_raw_dataset = dp_raw_dataset
        self.dp_ids = dp_ids
        self.n_dp_ids = n_dp_ids

        # create and save the semester states preprocessed dataset
        self.__create_semester_states_dataset(self.output_directories['estados_semestre'])

        # filter dataset
        self.ap_filtered_dataset = self.__filter_raw_dataset()

        
        # define the sets of affiliates and semester to work with
        affiliates,semesters = self.__define_affiliates_and_semesters()
        self.affiliates = affiliates
        self.semesters = semesters
        
        # create and save the sequences datasets (the most important one)
        self.__create_sequences_dataset()

        # Do the Optimal Matching algorithm over the sequences dataset to calculate the dissimilarity matrix.
        subprocess.run(['Rscript', 'optimal_matching.R',
                        self.output_directories['afiliados_secuencias'],
                        self.output_directories['matriz_disimilitud']], check=True)

    def __create_semester_states_dataset(self,output_directory):
        '''
        '''
        # defines the columns names, and the tuples data
        num_combinations = 2 ** len(self.dp_ids)
        codes = [hex(i) for i in range(num_combinations)]
        combinations = list(itertools.product([0, 1], repeat=len(self.dp_ids)))
        data = [combination + (code,) for combination,code in zip(combinations,codes)]

        # create the semester states structure
        columns = self.dp_ids.copy()
        columns.append('code')
        semester_states_dataset = pd.DataFrame(data,columns=columns)
        semester_states_dataset.to_csv(output_directory,index=False)

    def __filter_raw_dataset(self):
        '''
        '''
        # cast 'fecha' attribute to date
        aux_ap = self.ap_raw_dataset.copy()
        aux_ap['fecha'] = pd.to_datetime(aux_ap['fecha'],format='%d/%m/%Y')

        # define the dates interval
        sup_date = pd.to_datetime('01/07/2024', format='%d/%m/%Y')
        low_date = pd.to_datetime('31/12/2020', format='%d/%m/%Y')

        # filter dates outside the interval
        aux_ap = aux_ap[aux_ap['fecha'] < sup_date]
        aux_ap = aux_ap[aux_ap['fecha'] > low_date]

        #filter all the tuples in which its 'id_practica' is not part of the practices of interest
        aux_ap = aux_ap[aux_ap['id_practica'].isin(self.dp_ids)]

        return aux_ap
    
    def __define_affiliates_and_semesters(self):
        '''
        '''
        # getting the ids of the affiliates and how many them are
        affiliate_ids = list(set(self.ap_filtered_dataset['id_afiliado']))

        # TODO: GENERALIZE THIS - FOR NOW ONLY FOR 7 SEMESTERS

        # define the 7 semesters
        # each semesters is formed by a interval [a,b).
        semesters = {       
            'semester_1': [pd.Timestamp(f'2021-01-01'), pd.Timestamp(f'2021-07-01')],
            'semester_2': [pd.Timestamp(f'2021-07-01'), pd.Timestamp(f'2022-01-01')],
            'semester_3':[pd.Timestamp(f'2022-01-01'), pd.Timestamp(f'2022-07-01')],
            'semester_4':[pd.Timestamp(f'2022-07-01'), pd.Timestamp(f'2023-01-01')],
            'semester_5':[pd.Timestamp(f'2023-01-01'), pd.Timestamp(f'2023-07-01')],
            'semester_6':[pd.Timestamp(f'2023-07-01'), pd.Timestamp(f'2024-01-01')],
            'semester_7':[pd.Timestamp(f'2024-01-01'), pd.Timestamp(f'2024-07-01')]
        }

        return affiliate_ids,semesters

    def __get_new_semester_state(self):
        '''
        Return a initialized semester state represented as a dictionary of 0 values.
        It's 0s values will be changing to 1 accordingly.
        '''
        semester_state = dict(zip(self.dp_ids,[0 for i in self.dp_ids]))
        return semester_state
    
    def __semester_state_to_code(self,semester_state):
        '''
        Given a semeter state as a binary list, its transform it to its hexadecimal code.
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
    
    def __create_sequences_dataset(self):
        '''
        '''

        sequences = []
        ap = self.ap_filtered_dataset

        for itr,affiliate_id in enumerate(self.affiliates):
            
            sequence = []
            for semester in self.semesters.values():
                # initializa a semester state structure
                current_semester_state = self.__get_new_semester_state()

                # the low and superior dates of the current semester
                low_date = semester[0]
                sup_date = semester[1]

                # given an affiliate an a semester, we get the practices done by that affiliate in that semester
                practices = self.ap_filtered_dataset[ 
                        (ap['fecha'] >= low_date)
                        & (ap['fecha'] < sup_date)
                        & (ap['id_afiliado'] == affiliate_id)
                        ]['id_practica']

                # we use each practice found to change acordingly the semester state data structure
                # if a practice was found, its corresponding binary value changes to 1
                for practice in practices:
                    current_semester_state[practice] = 1
                # translate the semester state to its code and append to the sequence
                sequence.append(self.__semester_state_to_code(list(current_semester_state.values())))
            # append the resulting sequence to the general data structure
            sequences.append(sequence)
            
        # pass dataset to numpy
        sequences = np.array(sequences)

        # pass dataset to pandas
        columns = ['id_affiliate']+list(self.semesters.keys())
        data = np.column_stack((np.array(self.affiliates),sequences))
        sequences_dataset = pd.DataFrame(data,columns=columns)

        sequences_dataset.to_csv(self.output_directories['afiliados_secuencias_etiquetadas'],index=False)
        sequences_dataset.drop(columns=['id_affiliate']).to_csv(self.output_directories['afiliados_secuencias'],index=False)


    # UPLOAD OF ALREDY PREPROCESSED DATASETS