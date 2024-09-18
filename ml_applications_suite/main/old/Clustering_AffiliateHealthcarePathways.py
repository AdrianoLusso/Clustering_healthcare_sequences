from MLApplication import MLApplication
from Package import Package

from math import sqrt
import numpy as np
import pandas as pd
import itertools

from kmedoids import pam,KMedoids,silhouette
from sklearn.metrics import silhouette_samples

import json
import os
import subprocess

from typing import Dict, Union



class Clustering_AffiliateHealthcarePathways(MLApplication):

    def __init__(self) -> None:
        super().__init__()

        self.debug = False
        self.raw_dataset_directories = {}
        self.preprocessed_dataset_directories = {}
        self.hyperparameters = None
        self.clustering = None

    #############################################
    ## PREPROCCESING AND ITS AUXILIARY METHODS ##
    ############################################# 
    def preprocess_raw_dataset(self,input_directories:Dict, output_directories:Dict,debug=False) -> bool:
        '''
        ESPECIFICAR QUE ESTRUCTURA DICTIONARIA SE MECESITA
        '''
        self.debug = debug

        # define Package structures
        input_dirs_package = Package(props={
            'afiliados_practicas':str,
            'practicas_diabetes':str
        })
        output_dirs_package = Package(props={
            "estados_semestre":str,
            "afiliados_secuencias":str,
            "afiliados_secuencias_etiquetadas":str,
            "matriz_disimilitud":str
        })

        # fit the dictionaries into the Packages
        input_dirs_package.fit(input_directories)
        output_dirs_package.fit(output_directories)

        # save directories as object attributes
        self.raw_dataset_directories = self.raw_dataset_directories | input_dirs_package
        self.preprocessed_dataset_directories = self.preprocessed_dataset_directories | output_dirs_package

        # read affiliantes and practices datasets
        ap_raw_dataset = pd.read_csv(input_dirs_package['afiliados_practicas'])

        # read diabetes practices to analyze dataset
        # and other important data
        dp_raw_dataset = pd.read_csv(input_dirs_package['practicas_diabetes'])
        dp_ids = list(dp_raw_dataset.get('id_practica'))

        # create and save the semester states preprocessed dataset
        self.__create_semester_states_dataset(output_dirs_package['estados_semestre'],dp_ids)

        # filter dataset
        ap_filtered_dataset = self.__filter_raw_dataset(ap_raw_dataset,dp_ids)

        
        # define the sets of affiliates and semester to work with
        affiliates,semesters = self.__define_affiliates_and_semesters(ap_filtered_dataset)
        
        # create and save the sequences datasets (the most important one)
        self.__create_sequences_dataset(ap_filtered_dataset,affiliates,semesters,dp_ids,output_dirs_package)

        # Do the Optimal Matching algorithm over the sequences dataset to calculate the dissimilarity matrix.
        subprocess.run(['Rscript', 'optimal_matching.R',
                        output_dirs_package['afiliados_secuencias'],
                        output_dirs_package['matriz_disimilitud']], check=True)
        if self.debug:
            print("DISSIMILARITY MATRIX SAVED IN "+output_dirs_package['matriz_disimilitud'])

    def __create_semester_states_dataset(self,output_directory,dp_ids):
        '''
        '''
        # defines the columns names, and the tuples data
        num_combinations = 2 ** len(dp_ids)
        codes = [hex(i) for i in range(num_combinations)]
        combinations = list(itertools.product([0, 1], repeat=len(dp_ids)))
        data = [combination + (code,) for combination,code in zip(combinations,codes)]

        # create the semester states structure
        columns = dp_ids.copy()
        columns.append('code')
        semester_states_dataset = pd.DataFrame(data,columns=columns)
        semester_states_dataset.to_csv(output_directory,index=False)

        if self.debug:
            print("SEMESTER STATES DATASET SAVED IN "+output_directory+'\n')

    def __filter_raw_dataset(self,ap_raw_dataset,dp_ids):
        '''
        '''
        # cast 'fecha' attribute to date
        aux_ap = ap_raw_dataset.copy()
        aux_ap['fecha'] = pd.to_datetime(aux_ap['fecha'],format='%d/%m/%Y')

        # define the dates interval
        sup_date = pd.to_datetime('01/07/2024', format='%d/%m/%Y')
        low_date = pd.to_datetime('31/12/2020', format='%d/%m/%Y')

        # filter dates outside the interval
        aux_ap = aux_ap[aux_ap['fecha'] < sup_date]
        aux_ap = aux_ap[aux_ap['fecha'] > low_date]

        #filter all the tuples in which its 'id_practica' is not part of the practices of interest
        aux_ap = aux_ap[aux_ap['id_practica'].isin(dp_ids)]

        return aux_ap
    
    def __define_affiliates_and_semesters(self,ap_filtered_dataset):
        '''
        '''
        # getting the ids of the affiliates and how many them are
        affiliate_ids = list(set(ap_filtered_dataset['id_afiliado']))

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

    def __get_new_semester_state(self,dp_ids):
        '''
        Return a initialized semester state represented as a dictionary of 0 values.
        It's 0s values will be changing to 1 accordingly.
        '''
        semester_state = dict(zip(dp_ids,[0 for i in dp_ids]))
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
    
    def __create_sequences_dataset(self,ap_filtered_dataset,affiliates,semesters,dp_ids,output_dirs_package):
        '''
        '''

        sequences = []
        ap = ap_filtered_dataset

        for _,affiliate_id in enumerate(affiliates):
            
            sequence = []
            for semester in semesters.values():
                # initializa a semester state structure
                current_semester_state = self.__get_new_semester_state(dp_ids)

                # the low and superior dates of the current semester
                low_date = semester[0]
                sup_date = semester[1]

                # given an affiliate an a semester, we get the practices done by that affiliate in that semester
                practices = ap_filtered_dataset[ 
                        (ap_filtered_dataset['fecha'] >= low_date)
                        & (ap_filtered_dataset['fecha'] < sup_date)
                        & (ap_filtered_dataset['id_afiliado'] == affiliate_id)
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
        columns = ['id_affiliate']+list(semesters.keys())
        data = np.column_stack((np.array(affiliates),sequences))
        sequences_dataset = pd.DataFrame(data,columns=columns)

        sequences_dataset.to_csv(output_dirs_package['afiliados_secuencias_etiquetadas'],index=False)
        sequences_dataset.drop(columns=['id_affiliate']).to_csv(output_dirs_package['afiliados_secuencias'],index=False)

        if self.debug:
            print("LABELED SEQUENCES DATASET SAVED IN "+output_dirs_package['afiliados_secuencias_etiquetadas'])
            print("LABELED SEQUENCES DATASET SAVED IN "+output_dirs_package['afiliados_secuencias']+'\n')
    #                                           #
    ############################################# 




    #############################################
    ## UPLOAD OF ALREDY PREPROCESSED DATASETS  ##
    ############################################# 
    def upload_preprocessed_dataset(self,input_directories:Dict) -> bool:
        '''
        '''
        # define Package structures
        input_dirs_packages = Package(props={
            "estados_semestre":str,
            "afiliados_secuencias":str,
            "afiliados_secuencias_etiquetadas":str,
            "matriz_disimilitud":str
        })

        # fit the dictionaries into the Packages
        input_dirs_packages.fit(input_directories)

        # save directories as object attributes
        self.preprocessed_dataset_directories = self.preprocessed_dataset_directories | input_dirs_packages
    #                                           #
    ############################################# 




    #############################################
    ##          DEFINE HYPERPARAMETERS         ##
    ############################################# 
    def define_hyperparameters(self,params_dict) -> bool:
        '''
        '''
        params_package = Package(
            types={
            'n_grupos': Union(int,str),
            'umbral_de_filtrado_de_grupos': Union(float,None)
            },
            constraints={
                'n_grupos': lambda x: (x > 1 or x == 'optimizado'),
                'umbral_de_filtrado_de_grupos': lambda x: (x is None or -1 < x < 1)
            }
        )

        params_package.fit(params_dict)
        self.hyperparameters = params_package
    #                                           #
    ############################################# 




    #############################################
    ##        APPLY THE PAM CLUSTERING         ##
    ############################################# 
    def apply_ML(self) -> bool:
        '''
        '''
        # read the input datasets for the clustering
        sequences_dataset = pd.read_csv(self.preprocessed_dataset_directories['afiliados_secuencias'])
        dissimilarity_matrix = pd.read_csv(self.preprocessed_dataset_directories['matriz_disimilitud'])

        # define the number of clusters
        n_clusters = self.hyperparameters['n_grupos']
        n_clusters = self.__optimize_n_clusters(sequences_dataset,dissimilarity_matrix) if n_clusters == 'optimizado' else  n_clusters
    
        #
        solver = KMedoids(n_clusters,method='fasterpam')
        solver.fit(dissimilarity_matrix)
        silhouette = silhouette(dissimilarity_matrix,solver.labels_)[0]

        #
        n_sequences_per_cluster = [0  for i in range(solver.n_clusters)]
        for i in solver.labels_:
            n_sequences_per_cluster[i] += 1

        # reading the clustering parameters and results
        clustering_method = solver.method
        n_clusters_definition_method = "optimizado" if self.hyperparameters['n_grupos'] == 'optimizado' else 'manual'
        n_clusters = solver.n_clusters
        labels = solver.labels_
        n_sequences_per_label = n_sequences_per_cluster
        loss = solver.inertia_
        medoids = solver.medoid_indices_

        # creating the data structure and saving it
        clustering = {
            'metodo_agrupamiento': clustering_method,
            'metodo_definicion_n_grupos':n_clusters_definition_method,
            'n_grupos':n_clusters,
            'etiquetas_grupo':labels.tolist(),
            'n_secuencias_por_etiquetas_grupo':n_sequences_per_label,
            'perdida':loss,
            'silueta':silhouette,
            'medoides':medoids.tolist()
        }
        self.clustering = clustering

    def __optimize_n_clusters(self,sequences_dataset,dissimilarity_matrix):
        '''
        '''
        best_silhouette = -2
        
        # for each number of clusters between two and the squared root of the dataset size.
        # this maximum number of clusters is heuristically set it.
        for n_clusters in range(2,   round(sqrt(sequences_dataset.shape[0]))+1 ):
            
            # define the PAM solver and fit for the dissimilarity matrix
            solver = KMedoids(n_clusters=n_clusters,method='fasterpam')
            solver.fit(dissimilarity_matrix)

            # calculate the average silhouette
            silhouette = silhouette(dissimilarity_matrix,solver.labels_)[0]

            # save the n_clusters and the silhouette if they are the best found
            if silhouette > best_silhouette:
                best_silhouette =silhouette
                best_n_clusters = n_clusters
            #print('n_clusters: ',n_clusters,'  , sil: ',sil)
        

        return best_n_clusters
    #                                           #
    ############################################# 




    #############################################
    ##            RESULTS OPERATIONS           ##
    ############################################# 
    def get_results(self):
        return self.clustering
    
    def save_results(self,output_directories):
        '''
        '''      
        # define Package structure
        output_dirs_package = Package(props={
            "agrupamiento":str
        })

        # fit the dictionaries into the Packages
        output_dirs_package.fit(output_directories)
   

        with open(output_dirs_package['agrupamiento'],'w',encoding='utf-8') as file:
            json.dump(self.clustering,file,indent=4)
    #                                           #
    ############################################# 



