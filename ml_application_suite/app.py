import sys
import os
import subprocess
import streamlit as st


# Set the main project directory (main folder)
MAIN_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
# Add the main directory to sys.path so it can be accessed anywhere
sys.path.append(MAIN_DIRECTORY)

script_dir = os.path.dirname(__file__) + '/src/model/scripts/install_traminer.R'


if 'install_R_libs' not in st.session_state:
    st.session_state.install_R_libs = True

if st.session_state.install_R_libs: 
    try:
        result=subprocess.run(['Rscript', script_dir],
                        check=True, capture_output=True, text=True)
        st.session_state.install_R_libs = False
    except Exception as e:
        result = e
        st.write("STDERR:", result.stderr)


from src.ui.screens.SequencesClustering import Screen_SequencesClustering
from src.ui.screens.TimeframesStates import Screen_TimeframesStates
from src.ui.screens.menu import Menu

pages = {
        'Menu':[st.Page(Menu.create_Menu,title='Menu')],
        'Agrupamiento de historiales médicos':
            [
            st.Page(Screen_SequencesClustering.create_Screen_SequencesClustering, title='Principal')
            , st.Page(Screen_TimeframesStates.create_Screen_TimeframesStates, title='Estados de períodos temporales')
            ]
    }
st.session_state.pages = pages
pages = st.navigation(pages,expanded=True)
pages.run()
