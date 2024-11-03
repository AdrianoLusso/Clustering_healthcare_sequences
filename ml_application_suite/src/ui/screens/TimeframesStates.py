import streamlit as st
import pandas as pd
from src.ui.components.TimeframesStates import *

class Screen_TimeframesStates():
    """
    This class represents the screen for seeing the timeframes states of a
    previously done healthcare pathways clustering.
    """

    @staticmethod
    def create_Screen_TimeframesStates():
        """Static method that created a menu and return it"""
        return Screen_TimeframesStates()

    def __init__(self):
        self.__init_session_state()
        self.__plot_screen()

    def __plot_screen(self):
        """
        The method plots the visual elements of the UI.
        It mustn't involve complex components control, just the plotting.
        """
        st.title('Estados de períodos temporales')

        if type(st.session_state.result) is not dict:
            st.info("En la ventana principal de la sección, complete los datos de entrada e hyperparámetros para obtener un agrupamiento.")
        else:
            timeframes_states_console()

    def __init_session_state(self):
        """
        This method initialize the session state variables for this screen.
        """
        pass