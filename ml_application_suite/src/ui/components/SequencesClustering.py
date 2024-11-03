import streamlit as st
from streamlit.runtime.scriptrunner import add_script_run_ctx # for adding a new thread to the streamlit envirioment
from streamlit_plotly_events import plotly_events # for deploying click events on charts

import plotly.graph_objects as go

import threading
import asyncio
semaphore = threading.Semaphore(1)

import numpy as np
import pandas as pd

import threading
import json
from datetime import datetime


def groups_number_input() -> None:
    """
    Input for the clustering number of groups. It also permits to user to set an optimization loop for it.
    """
    with st.container(border=True):
        st.text('Número de grupos')
        to_optimize = st.toggle('Optimizado',value=False)
        n_groups = st.number_input(label='', disabled=to_optimize, min_value=2,value=5)

        if to_optimize:
            st.session_state.parameters['n_grupos'] = 'optimizado'
        else:
            st.session_state.parameters['n_grupos'] = n_groups



##################################
##   CLUSTERING STATUS HANDLER  ##
##################################
def configuration_submit_handler():
    """
    This handle the complete workflow of submitting the clustering configuration.
    The workflow has 3 threads:
        - main, which runs the ML application process. Here, not just the clustering is done, but also
          the process state is updated during the execution
        - status bar, which plots the current process state through streamlit.
        - the state sender, which works as a bridge between the process state of the ML application and
          the status bar.
    """
    submit = st.button(label='Ejecutar',use_container_width=True)

    result = st.session_state.result  # previous result of the clustering
    map_data = st.session_state.map_data # previous data map.

    if submit:
        # create the StatusBar thread and start it
        th=threading.Thread(target=status_bar,daemon=True,name="StatusBar")
        add_script_run_ctx(th)
        th.start()

        # run the main workflow of the Main thread
        result,map_data = st.session_state.ctrl.run_sequences_clustering(st.session_state.parameters)
        if result == -1:
            st.error('Verifica que los datos fueron ingresados correctamente.')

        th.join()

    return result,map_data
def status_bar():
    """
    This component manage the status bar for the clustering process, plotting the states is achieves.
    """

    # gets the state queue from the controller
    # it will be used for concurrent reading of the new process states.
    state_queue = st.session_state.ctrl.get_state_queue()
    # gets all the states defined the ML application process
    all_states = st.session_state.ctrl.get_all_process_states()

    # create the ProcessStateSender thread and start it
    th = threading.Thread(target=st.session_state.ctrl.run_concurrent_process_state_sender,daemon=True,name="ProcessStateSender")
    add_script_run_ctx(th)
    th.start()

    with st.session_state.main_screen_empty_block.status('En ejecución...',expanded=True) as status:
        fail = False
        for state in all_states:
            received_state = state_queue.get()
            if received_state == 'fail':
                fail = True
                break
            st.write(received_state)

        if fail:
            status.update(
                label="Error en el proceso", state="error", expanded=False
            )
        else:
            state_queue.get()
            status.update(
                label="Proceso completo", state="complete", expanded=False
            )
        th.join()


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

class Clusters_panel():
    """

    """
    def __init__(self):
        """

        """
        # datasets to work with.
        self.sequences_dataset = pd.read_csv(st.session_state.result['afiliados_secuencias'])
        st.session_state.result['afiliados_secuencias'].seek(0)
        self.clustering = json.load(st.session_state.result['agrupamiento_secuencias'])
        st.session_state.result['agrupamiento_secuencias'].seek(0)
        self.clicked_heatblock_data = None

        # min. silhouette slider for setting the min. silhouette of the cluster's heatmaps to plot.
        self.min_silh = st.slider("Silueta mínima",min_value=-1.0,max_value=1.0,value=-1.0,step=0.05,
                                 help="Se mostrarán unicamente los grupos cuya silueta sea igual o mayor a la marcada como mínima.")

        self.__heatmaps_section()

    def __heatmaps_section(self):
        """
        This method involves the logic of plotting the section of heatmaps for the clusters.
        """

        # dict. of groups to plot. The key is the index for clustering['silueta_por_grupo'],
        # and the value is the label for the heatmap.
        groups = {
            i:'Grupo ' + str(i + 1)
            for i in range(self.clustering['n_grupos'])
            if self.clustering['silueta_por_grupo'][i] >= self.min_silh
        }

        # only plot heatmaps if there is at least one to plot.
        if len(groups) > 0:
            tabs = st.tabs(groups.values())
            for id_group,tab in zip(groups.keys(),tabs):
                with tab:
                    self.__heatmap(id_group)
        else:
            st.info('No se encontró ningun grupo con una silueta igual o mayor a '+str(self.min_silh)+'.')


    def __heatmap(self,id_group):
        """
        This component plot a heatmap for a particular cluster.

        Args:
            - id_group
            - sequences_dataset
            - clustering
        """

        # save the list indexes where we can find affiliates that are part of the current cluster
        indexes = [
                    index
                    for index,group in enumerate(self.clustering['etiquetas_grupo'])
                    if id_group == group
                   ]

        # filter the sequences dataset to only have affiliates in the current cluster
        sequences_dataset = self.sequences_dataset.loc[indexes]
        # takes the sequences dataset and change it from hexadecimals to ints
        sequences_dataset2 = sequences_dataset.applymap(lambda x: int(x,16)).values

        # create the heatmap
        heatmap = go.Figure(data=go.Heatmap(
                z=sequences_dataset2,
                x=[i for i in range(sequences_dataset.shape[1])],
                y = None,
                text= sequences_dataset,
                colorscale='Viridis',
                showscale=False,
                hovertemplate="Semestre: %{x}<br>Afiliado: %{y}<br>Estado: %{text}<extra></extra>"
                ))

        # modify the heatmap for having certain visual properties.
        tickvals = np.array([i for i in range(st.session_state.parameters['numero_timeframes'])])
        heatmap.update_layout(
            paper_bgcolor='rgba(0, 0, 0, 0)',
            font_color='white',

            xaxis=dict(
                title= st.session_state.parameters['unidad_timeframe'],
                tickvals=tickvals,
                ticktext=tickvals+1
            )
        )

        # plot heatmap through a plotly_events wrapper. This is used for knowing the heatblock
        # clicked by the user
        self.clicked_heatblock_data = plotly_events(heatmap)  # CLICK DATA TO USE MUST BE ONLY 'X' AND 'Y'.
        self.more_info_bar(id_group,sequences_dataset2)
        '''
        col1,col2,col3,col4,col5 = st.columns(5)

        more_info = col1.button(key="timeframe_state_button"+str(id_group),label='Más info.')
        if more_info:
            more_info_button_action(click_data,sequences_dataset2)

        col2.metric('silueta',str(clustering['silueta_por_grupo'][id_group]),
                    help='La silueta indica la calidad del grupo encontrado. Toma valores entre -1 y 1, donde 1 indica la máxima calidad y -1 la mínima calidad. A más cercanos entre sí sean los puntos de un grupo y a más lejanos esten de los puntos de otros grupos, mayor sera la silueta.')
        with col3:
            try:
                timeframe = click_data[0]['x']+1
                st.metric(
                    st.session_state.parameters['unidad_timeframe'],
                    timeframe
                )
            except:
                pass
        with col4:
            try:
                affiliate = click_data[0]['y']
                st.metric(
                    'afiliado',
                    affiliate
                )
            except:
                pass
        with col5:
            try:
                affiliate = click_data[0]['y']
                timeframe = click_data[0]['x']
                st.metric(
                    'estado',
                    hex(sequences_dataset2[affiliate][timeframe])[2:]
                )
            except:
                pass
        '''

    def more_info_bar(self,id_group,sequences_dataset):
        """

        """
        col1, col2, col3, col4, col5 = st.columns(5)

        more_info = col1.button(key="timeframe_state_button" + str(id_group), label='Más info.')
        if more_info:
            self.more_info_button_action(sequences_dataset)

        col2.metric('silueta', str(self.clustering['silueta_por_grupo'][id_group]),
                    help='La silueta indica la calidad del grupo encontrado. Toma valores entre -1 y 1, donde 1 indica la máxima calidad y -1 la mínima calidad. A más cercanos entre sí sean los puntos de un grupo y a más lejanos esten de los puntos de otros grupos, mayor sera la silueta.')
        with col3:
            try:
                timeframe = self.clicked_heatblock_data[0]['x'] + 1
                st.metric(
                    st.session_state.parameters['unidad_timeframe'],
                    timeframe
                )
            except:
                pass
        with col4:
            try:
                affiliate = self.clicked_heatblock_data[0]['y']
                st.metric(
                    'afiliado',
                    affiliate
                )
            except:
                pass
        with col5:
            try:
                affiliate = self.clicked_heatblock_data[0]['y']
                timeframe = self.clicked_heatblock_data[0]['x']
                st.metric(
                    'estado',
                        hex(sequences_dataset[affiliate][timeframe])[2:]
                    )
            except:
                pass

    def more_info_button_action(self,sequences_dataset):
        try:
            affiliate = self.clicked_heatblock_data[0]['y']
            timeframe = self.clicked_heatblock_data[0]['x']
        except Exception as e:
            st.error("No puede ver mas información sin haber hecho click sobre un estado del gráfico.")
            return
        state = hex(sequences_dataset[affiliate][timeframe])[2:]
        st.session_state.default_state = state
        st.switch_page(st.session_state.pages['Agrupamiento de historiales médicos'][1])

def sup_date_input():

    current_date = datetime.now()
    if current_date > datetime(current_date.year, 6, 30):
        date = datetime(current_date.year,7,1)
    else:
        date = datetime(current_date.year,1,1)

    return st.date_input("Fecha de limite superior"
                  ,format='DD/MM/YYYY'
                  ,help="Se debe ingresar la fecha más reciente del período temporal más reciente."
                  ,value = date)
