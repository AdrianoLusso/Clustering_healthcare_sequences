from src.ui.components.SequencesClustering import *
from src.ui.controllers.SequencesClustering import Controller_SequencesClustering

class Screen_SequencesClustering():
    """
    This class represents the screen for Healthcare pathways clustering.
    """

    @staticmethod
    def create_Screen_SequencesClustering():
        """Static method that created a menu and return it"""
        return Screen_SequencesClustering()

    def __init__(self):
        self.__init_session_state()
        self.__plot_screen()

    def __plot_screen(self):
        """
        The method plots the visual elements of the UI.
        It mustn't involve complex components control, just the plotting.
        """
        st.title('Agrupamiento de historiales médicos')

        # this empty block is for having just one element in the main screen
        if 'main_screen_empty_block' not in st.session_state:
            st.session_state.main_screen_empty_block = st.empty()

        with st.sidebar:
            with st.expander('Datos de entrada'):
                st.session_state.parameters['afiliados_practicas'] = st.file_uploader(
                    'Dataset de consumo de practicas por afiliado',
                    type=['csv'])

                st.session_state.parameters['afiliados_monodrogas'] = st.file_uploader(
                    'Dataset de consumo de monodrogas por afiliado',
                    type=['csv'])

                st.session_state.parameters['practicas_interes'] = st.file_uploader(
                    'Practicas de interes',
                    type=['csv'],
                    accept_multiple_files=True)

                st.session_state.parameters['monodrogas_interes'] = st.file_uploader(
                    'Monodrogas de interes', type=['csv'],
                    accept_multiple_files=True)

                st.session_state.parameters['matriz_disimilitud'] = st.file_uploader(
                    'Matriz de disimilitud precomputada',
                    type=['csv'],
                    help='Crear la matriz de disimilitud puede llevar algunos minutos. Si usted ya ha usado los mismos datos de entrada previamente y ha guardado la matriz, puede subirla aquí y acelerar el proceso de cómputo.')
                st.session_state.parameters['matriz_disimilitud_precomputada'] = st.session_state.parameters['matriz_disimilitud'] is not None

                st.session_state.parameters['afiliados_secuencias_etiquetadas'] = st.file_uploader(
                    'Dataset de historiales médicos de afiliados',
                    type=['csv'],
                    help='Crear los historiales medicos de los afiliados puede llevar algunos minutos. Si usted ya ha usado los mismos datos de entrada previamente y ha guardado este dataset, puede subirlo aquí y acelerar el proceso de cómputo.')
                st.session_state.parameters['afiliados_secuencias_etiquetadas_precomputada'] = st.session_state.parameters['afiliados_secuencias_etiquetadas'] is not None

                st.session_state.parameters['unidad_timeframe'] = st.selectbox(
                    'Unidad para período temporal', ['mes', 'semestre', 'anio'],
                    index=1)
                st.session_state.parameters['numero_timeframes'] = st.number_input(
                    'Cantidad de períodos',
                    min_value=2,
                    max_value=100,
                    value=7)
                st.session_state.parameters['fecha_superior_ultimo_timeframe'] = sup_date_input() #st.date_input("Fecha de limite superior (exclusivo)",format='DD/MM/YYYY')

            with st.expander('Hyperparámetros'):
                groups_number_input()

            st.session_state.result, st.session_state.map_data = configuration_submit_handler()

        if type(st.session_state.result) == dict:
            with st.session_state.main_screen_empty_block.container():
                Clusters_panel()
                st.divider()
                download_buttons()
        else:
            st.session_state.main_screen_empty_block.info('Complete los datos de entrada e hyperparámetros para obtener un agrupamiento.')

    def __init_session_state(self):
        """
        This method initialize the session state variables for this screen.
        """
        if 'result' not in st.session_state:
            st.session_state.result = 0

        if 'ctrl' not in st.session_state:
            st.session_state.ctrl = Controller_SequencesClustering()

        if 'parameters' not in st.session_state:
            st.session_state.parameters = st.session_state.ctrl.get_parameters()

        if 'map_data' not in st.session_state:
            st.session_state.map_data = {}
