import streamlit as st


class Menu:
    """
    This class represents the menu of the UI
    """

    @staticmethod
    def create_Menu():
        """Static method that created a menu and return it"""
        return Menu()

    def __init__(self):
        self.__plot_screen()

    def __plot_screen(self):
        """
        The method plots the visual elements of the UI.
        It mustn't involve complex components control, just the plotting.
        """
        st.title('Suite de aplicaciones de datos')
        col1,col2 = st.columns(2)

        if col1.button('🎈 🎈 🎈',use_container_width=True):
            st.balloons()
        if col2.button('❄️ ❄️ ❄️',use_container_width=True):
            st.snow()