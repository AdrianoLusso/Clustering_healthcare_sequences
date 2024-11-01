import streamlit as st


class Menu:
    @staticmethod
    def create_Menu():
        return Menu()

    def __init__(self):
        self.__plot_screen()

    def __plot_screen(self):
        st.title('Suite de aplicaciones de datos')
        col1,col2 = st.columns(2)

        if col1.button('🎈 🎈 🎈',use_container_width=True):
            st.balloons()
        if col2.button('❄️ ❄️ ❄️',use_container_width=True):
            st.snow()