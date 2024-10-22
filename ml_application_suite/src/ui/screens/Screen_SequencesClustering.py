import sys
import os
import threading
import queue

from altair.vegalite.v5.theme import theme
from matplotlib.pyplot import xcorr
from streamlit.runtime.uploaded_file_manager import UploadedFile

##############################################
############## CONFIGURATION ################
##############################################
# Set the main project directory (main folder)
MAIN_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
# Add the main directory to sys.path so it can be accessed anywhere
sys.path.append(MAIN_DIRECTORY)

#from src.ui.controllers.Controller_SequencesClustering import Controller_SequencesClustering
# Create the controller
#ctrl = Controller_SequencesClustering()
#parameters = ctrl.get_parameters()

##############################################
############### COMPONENTS ###################
##############################################
import pandas as pd
from typing import Union
import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx
import plotly.graph_objects as go
import numpy as np
import json
from streamlit_plotly_events import plotly_events


def groups_number_input() -> Union[str,int]:
    """

    """
    with st.container(border=True):
        st.text('Número de grupos')
        to_optimize = st.toggle('Optimizado',value=False)#value=True) # TODO esto tiene que ser true, en debug lo dejamos false
        n_groups = st.number_input(label='', disabled=to_optimize, min_value=2,value=5)

        if to_optimize:
            st.session_state.parameters['n_grupos'] = 'optimizado'
        else:
            st.session_state.parameters['n_grupos'] = n_groups

def configuration_submit_button():
    """

    """
    submit=st.button(label='Ejecutar')

    result = st.session_state.result
    if submit:
        th=threading.Thread(target=status_bar)
        add_script_run_ctx(th)
        th.start()

        result = st.session_state.ctrl.run_sequences_clustering(st.session_state.parameters)
        if result == -1:
            st.error('Verifica que los datos fueron ingresados correctamente.')
    return result

def status_bar():
    state_queue = st.session_state.ctrl.get_state_queue()
    all_states = st.session_state.ctrl.get_all_process_states()

    th = threading.Thread(target=st.session_state.ctrl.run_concurrent_process_state_sender)
    add_script_run_ctx(th)
    th.start()

    with st.status('En ejecución...',expanded=True) as status:
        for state in all_states:
            state_queue.get()
            st.write(state)
        state_queue.get()

        status.update(
            label="Proceso completo", state="complete", expanded=False
        )

@st.fragment
def download_buttons():
    st.download_button('Descargar matriz de disimilitud',
                       st.session_state.result['matriz_disimilitud'].getvalue(),
                            file_name='matriz_disimilitud.csv',
                            help='Si reutilizará proximamente los mismos datos de entrada, se recomienda que guarda la matriz de disimilitud y la reutilice para acelerar futuros procesos de cómputo.')

    st.download_button('Descargar dataset de historiales médicos de afiliados',
                           st.session_state.result['afiliados_secuencias_etiquetadas'].getvalue(),
                           file_name='historiales_medicos_afiliados.csv',
                           help='Si reutilizará proximamente los mismos datos de entrada, se recomienda que guarda este dataset y que lo reutilice para acelerar futuros procesos de cómputo.')

def heatmaps_section():
    sequences_dataset = pd.read_csv(st.session_state.result['afiliados_secuencias'])
    st.session_state.result['afiliados_secuencias'].seek(0)
    clustering = json.load(st.session_state.result['agrupamiento_secuencias'])
    st.session_state.result['agrupamiento_secuencias'].seek(0)

    groups_range = range(clustering['n_grupos'])
    tabs = st.tabs( ['Grupo '+str(i) for i in groups_range] )

    st.session_state.click_data = [i for i in groups_range]
    for id_group,tab in zip(groups_range,tabs):
        with tab:
            heatmap(id_group,sequences_dataset,clustering)

def heatmap(id_group,sequences_dataset,clustering):
    indexes = [
                index
                for index,group in enumerate(clustering['etiquetas_grupo'])
                if id_group == group
               ]

    sequences_dataset = sequences_dataset.loc[indexes]
    sequences_dataset2 = sequences_dataset.applymap(lambda x: int(x,16)).values
    fig = go.Figure(data=go.Heatmap(
            z=sequences_dataset2,
            x=[i for i in range(sequences_dataset.shape[1])],
            y = None,
            text= sequences_dataset,
            colorscale='Viridis',
            showscale=False,
            hovertemplate="Semestre: %{x}<br>Afiliado: %{y}<br>Estado: %{text}<extra></extra>"
            ))

    tickvals = np.array([i for i in range(st.session_state.parameters['numero_timeframes'])])
    fig.update_layout(
        #title='Group'+str(id_group),
        paper_bgcolor='rgba(0, 0, 0, 0)',
        font_color='white',

        xaxis=dict(
            title= st.session_state.parameters['unidad_timeframe'],
            tickvals=tickvals,
            ticktext=tickvals+1
        )
    )

    st.session_state.click_data[id_group] = plotly_events(fig) # CLICK DATA TO USE MUST BE ONLY 'X' AND 'Y'.
    if len(st.session_state.click_data[id_group]) > 0:
        timeframe = st.session_state.click_data[id_group][0]['x']
        affiliate = st.session_state.click_data[id_group][0]['y']
        state = hex(sequences_dataset2[affiliate][timeframe])[2:]


##############################################
############## SESSION STATE #################
##############################################
from src.ui.controllers.Controller_SequencesClustering import Controller_SequencesClustering

if 'result' not in st.session_state:
    st.session_state.result = 0

if 'ctrl' not in st.session_state:
    st.session_state.ctrl = Controller_SequencesClustering()

if 'parameters' not in st.session_state:
    st.session_state.parameters = st.session_state.ctrl.get_parameters()

##############################################
################### SCREEN ###################
##############################################

st.title('Prueba')

# SIDEBAR
with st.sidebar:
    # INPUT
    with st.expander('Datos de entrada'):
        st.session_state.parameters['afiliados_practicas'] = st.file_uploader('Dataset de consumo de practicas por afiliado',
                                                             type=['csv'])
        st.session_state.parameters['afiliados_monodrogas'] = st.file_uploader('Dataset de consumo de monodrogas por afiliado',
                                                              type=['csv'])

        st.session_state.parameters['practicas_interes'] = st.file_uploader('Practicas de interes', type=['csv'],
                                                           accept_multiple_files=True)
        st.session_state.parameters['monodrogas_interes'] = st.file_uploader('Monodrogas de interes', type=['csv'],
                                                            accept_multiple_files=True)

        st.session_state.parameters['matriz_disimilitud'] = st.file_uploader('Matriz de disimilitud precomputada',
                                                              type=['csv'],
                                                            help='Crear la matriz de disimilitud puede llevar algunos minutos. Si usted ya ha usado los mismos datos de entrada previamente y ha guardado la matriz, puede subirla aquí y acelerar el proceso de cómputo.')
        st.session_state.parameters['matriz_disimilitud_precomputada'] = st.session_state.parameters['matriz_disimilitud'] is not None


        st.session_state.parameters['afiliados_secuencias_etiquetadas'] = st.file_uploader('Dataset de historiales médicos de afiliados',
                                                            type=['csv'],
                                                            help='Crear los historiales medicos de los afiliados puede llevar algunos minutos. Si usted ya ha usado los mismos datos de entrada previamente y ha guardado este dataset, puede subirlo aquí y acelerar el proceso de cómputo.')
        st.session_state.parameters['afiliados_secuencias_etiquetadas_precomputada'] = st.session_state.parameters['afiliados_secuencias_etiquetadas'] is not None

        st.session_state.parameters['unidad_timeframe'] = st.selectbox('Unidad para período temporal', ['mes', 'semestre', 'anio'],index=1)
        st.session_state.parameters['numero_timeframes'] = st.number_input('Cantidad de períodos', min_value=2, max_value=100,value=7)
        st.session_state.parameters['fecha_superior_ultimo_timeframe'] = st.date_input("Fecha de limite superior (exclusivo)",format='DD/MM/YYYY')

    # HYPERPARAMETERS
    with st.expander('Hyperparámetros'):
        groups_number_input()
        st.session_state.parameters['umbral_de_filtrado_de_grupos'] = None # TODO

    # OUTPUT
    with st.expander('Salidas'):
        #parameters[''] = st.text_input('Directorio para guardar') #TODO
        st.title('Nombres de archivos')
        st.text_input('Historiales médicos de afiliados')
        st.text_input('Historiales médicos identificados de afiliados')
        st.text_input('Agrupamiento de historiales médicos')

    st.session_state.result = configuration_submit_button()

st.write(st.session_state)
if type(st.session_state.result) == dict:
    heatmaps_section()
    download_buttons()
