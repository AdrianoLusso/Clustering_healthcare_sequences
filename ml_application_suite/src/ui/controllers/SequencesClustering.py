import threading
import queue
import streamlit as st
from time import sleep
import pandas as pd

from src.model.mlApplication.MLApplication import MLApplication
from io import StringIO

import logging
from logging import getLogger

l = getLogger()
l.addHandler(logging.StreamHandler())
l.setLevel(logging.INFO)


class Controller_SequencesClustering():

    def __init__(self):
        """

        """
        self.app = MLApplication()
        self.parameters = {
            'debug':False,
            'matriz_disimilitud_precomputada':False,
            'afiliados_secuencias_etiquetadas_precomputada':False
        }
        self.map_data = {}
        self.state_queue = queue.Queue()


    def get_parameters(self):
        """

        """
        return self.parameters

    def get_state_queue(self):
        return self.state_queue

    def run_sequences_clustering(self,parameters):
        """

        """
        if parameters['practicas_interes'] == []:
            del parameters['practicas_interes']
        else:
            interest_practices = {}
            for practice in parameters['practicas_interes']:
                name = str(practice.name)
                name = name[:name.rfind('.')]
                interest_practices[name] = StringIO(practice.getvalue().decode("utf-8"))

                aux_df = pd.read_csv(interest_practices[name])
                interest_practices[name].seek(0)
                self.map_data.update(dict(zip(aux_df['id_practica'],aux_df['nombre_practica'])))
            parameters['practicas_interes'] = interest_practices

        if parameters['monodrogas_interes'] == []:
            del parameters['monodrogas_interes']
        else:
            interest_drugs = {}
            for drug in parameters['monodrogas_interes']:
                name = str(drug.name)
                name = name[:name.rfind('.')]
                interest_drugs[name] = StringIO(drug.getvalue().decode("utf-8"))

                aux_df = pd.read_csv(interest_drugs[name])
                interest_drugs[name].seek(0)
                self.map_data.update(dict(zip(aux_df['id_monodroga'], aux_df['nombre_monodroga'])))
            parameters['monodrogas_interes'] = interest_drugs

        if parameters['afiliados_practicas'] is not None:
            parameters['afiliados_practicas'] = StringIO(parameters['afiliados_practicas'].getvalue().decode("utf-8"))
        else:
            del parameters['afiliados_practicas']

        if parameters['afiliados_monodrogas'] is not None:
            parameters['afiliados_monodrogas'] = StringIO(parameters['afiliados_monodrogas'].getvalue().decode("utf-8"))
        else:
            del parameters['afiliados_monodrogas']

        if parameters['matriz_disimilitud'] is not None:
            parameters['matriz_disimilitud'] = StringIO(parameters['matriz_disimilitud'].getvalue().decode("utf-8"))

        if parameters['afiliados_secuencias_etiquetadas'] is not None:
            parameters['afiliados_secuencias'] = StringIO()
            df = pd.read_csv(parameters['afiliados_secuencias_etiquetadas'])
            df = df.drop(df.columns[0],axis=1)
            df.to_csv(parameters['afiliados_secuencias'],index=False)
            parameters['afiliados_secuencias_etiquetadas'] = StringIO(parameters['afiliados_secuencias_etiquetadas'].getvalue().decode("utf-8"))
            parameters['afiliados_secuencias_etiquetadas'].seek(0)
            parameters['afiliados_secuencias'].seek(0)

        self.parameters = parameters

        result = self.app.run_affiliatesHealthcarePathways_clustering(parameters)
        return result,self.map_data

    def run_concurrent_process_state_sender(self):
        """

        """
        if threading.current_thread() is threading.main_thread():
            raise RuntimeError("Este metodo solo puede ser ejecutado como un hilo concurrente.")

        while True:
            current_process_state = self.app.process_state.get_new_state()
            self.state_queue.put(current_process_state)
            if current_process_state in ['end','fail']:
                break
        self.app.process_state.initialize()


    def get_all_process_states(self):
        return self.app.process_state.states_sequence[1:-1]
