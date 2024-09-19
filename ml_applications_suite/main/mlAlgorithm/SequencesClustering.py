
from .MLAlgorithm import MLAlgorithm
from ..utils.Package import Package
from typing import Union
from math import sqrt

from kmedoids import KMedoids,silhouette
from sklearn.metrics import silhouette_samples
import pandas as pd

import subprocess
import json

class SequencesClustering(MLAlgorithm):

    def __init__(self) -> None:
        super().__init__() 
        
        self.datasets_directories = Package(
            types={
                "estados_semestre":str,
                "afiliados_secuencias":str,
                "afiliados_secuencias_etiquetadas":str,
                "matriz_disimilitud":str
            }
        )

        self.hyperparameters = Package(
            types={
            'n_grupos': Union(int,str),
            'umbral_de_filtrado_de_grupos': Union(float,None)
            },
            constraints={
                'n_grupos': lambda x: (x > 1 or x == 'optimizado'),
                'umbral_de_filtrado_de_grupos': lambda x: (x is None or -1 < x < 1)
            }
        )

        self.results_directories = Package(
            types={
                'agrupamientoSecuencias':str
            }
        )

    def apply_ML(self):
        '''
        '''
        # read the input datasets for the clustering
        sequences_dataset = pd.read_csv(self.datasets_directories['afiliados_secuencias'])
        dissimilarity_matrix = pd.read_csv(self.datasets_directories['matriz_disimilitud'])

        # define the number of clusters
        n_clusters = self.hyperparameters['n_grupos']
        n_clusters = self.__optimize_n_clusters(sequences_dataset,dissimilarity_matrix) if n_clusters == 'optimizado' else  n_clusters
    
        #
        solver = KMedoids(n_clusters,method='fasterpam')
        solver.fit(dissimilarity_matrix)
        silh = silhouette(dissimilarity_matrix,solver.labels_)[0]

        #
        n_sequences_per_cluster = [0  for _ in range(solver.n_clusters)]
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
            'silueta':silh,
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
    
    def get_results(self):
        return self.clustering
    
    def save_results(self,output_directories):
        '''
        '''      

        # fit the dictionaries into the Packages
        self.results_directories.fit(output_directories)

        with open(self.results_directories['agrupamientoSecuencias'],'w',encoding='utf-8') as file:
            json.dump(self.clustering,file,indent=4)
    
