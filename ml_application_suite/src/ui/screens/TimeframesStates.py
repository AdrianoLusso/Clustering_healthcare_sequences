import streamlit as st
import pandas as pd
from src.ui.components.TimeframesStates import *

class Screen_TimeframesStates():

    @staticmethod
    def create_Screen_TimeframesStates():
        return Screen_TimeframesStates()

    def __init__(self):
        self.__init_session_state()
        self.__plot_screen()

    def __plot_screen(self):

        st.title('Estados de períodos temporales')

        if type(st.session_state.result) is not dict:
            st.info("En la ventana principal de la sección, complete los datos de entrada e hyperparámetros para obtener un agrupamiento.")
        else:
            timeframes_states_console()



    def __init_session_state(self):
        if 'default_state' not in st.session_state:
            st.session_state.default_state = None