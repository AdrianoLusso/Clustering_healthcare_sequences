from .MLAlgorithm import MLAlgorithm
from src.utils.Package import Package

import pandas as pd
from kmedoids import KMedoids,silhouette

from typing import Union
from math import sqrt

import json
from io import StringIO

import logging
from logging import getLogger

##################################
##            LOGGER            ##
##################################
l = getLogger()
l.addHandler(logging.StreamHandler())
l.setLevel(logging.INFO)



class SequencesClustering(MLAlgorithm):
    """
    An algorithm for doing sequences clustering.

    Attributes:
        - datasets (Package)
            datasets that works as input for the algorithm.
        - hyperparameters (Package)
            the algorithm hyperparameters.
    """

    def __init__(self) -> None:
        super().__init__()
        self.datasets = Package(
            types={
                "estados_timeframes":StringIO,
                "afiliados_secuencias":StringIO,
                "afiliados_secuencias_etiquetadas":StringIO,
                "matriz_disimilitud":StringIO
            }
        )

        self.hyperparameters = Package(
            types={
            'n_grupos': Union[int,str],
            'umbral_de_filtrado_de_grupos': Union[float,None]
            },
            constraints={
                'n_grupos': lambda x: (x == 'optimizado' or x > 1),
                'umbral_de_filtrado_de_grupos': lambda x: (x is None or -1 < x < 1)
            }
        )

    def apply_ML(self) -> None:
        """
        Applies the ML algorithm
        """
        # read the input datasets for the clustering
        sequences_dataset = pd.read_csv(self.datasets['afiliados_secuencias'])
        self.datasets['afiliados_secuencias'].seek(0)
        dissimilarity_matrix = pd.read_csv(self.datasets['matriz_disimilitud'])
        self.datasets['matriz_disimilitud'].seek(0)

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
            'n_secuencias_por_grupo':n_sequences_per_label,
            'perdida':loss,
            'silueta':silh,
            'medoides':medoids.tolist()
        }
        self.clustering = clustering

    def __optimize_n_clusters(self,sequences_dataset,dissimilarity_matrix) -> int:
        """
        Runs the protocol that optimal the number of clusters, analyzing from 2 up to the squared root of
        the size of the dataset (and heuristical top limit). The optimal value is calculated in function
        of the silhouette of the clustering achieved.

        Args:
            sequences_dataset (DataFrame): Dataframe containing the sequences.
            dissimilarity_matrix (DataFrame): Dataframe containing the dissimilarity matrix for the sequences.

        Returns: The optimal number of clusters.
        """
        best_silh = -2
        
        # for each number of clusters between two and the squared root of the dataset size.
        # this maximum number of clusters is heuristically set it.
        for n_clusters in range(2,   round(sqrt(sequences_dataset.shape[0]))+1 ):

            # define the PAM solver and fit for the dissimilarity matrix
            solver = KMedoids(n_clusters=n_clusters,method='fasterpam')
            solver.fit(dissimilarity_matrix)

            # calculate the average silhouette
            silh = silhouette(dissimilarity_matrix,solver.labels_)[0]

            # save the n_clusters and the silhouette if they are the best found
            if silh > best_silh:
                best_silh = silh
                best_n_clusters = n_clusters
            #print('n_clusters: ',n_clusters,'  , sil: ',sil)
        

        return best_n_clusters
    
    def get_results(self) -> StringIO:
        return StringIO(json.dumps(self.clustering))

    
