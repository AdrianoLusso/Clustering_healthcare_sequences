import sys
import os
import subprocess
import streamlit as st

import logging
from logging import getLogger

##################################
##        MAIN DIRECTORY        ##
##################################
# Set the main project directory (main folder)
MAIN_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(MAIN_DIRECTORY)



##################################
##            LOGGER            ##
##################################
l = getLogger()
l.addHandler(logging.StreamHandler())
l.setLevel(logging.INFO)
script_dir = os.path.dirname(__file__) + '/src/model/scripts/install_traminer.R'



##################################
##    TRAMINER INSTALLATION     ##
##################################
if 'traminer_installed' not in st.session_state:
    st.session_state.traminer_installed = False

if not st.session_state.traminer_installed:
    try:
        result = subprocess.run(['Rscript', script_dir],
                                check=True, capture_output=True, text=True)
        st.session_state.traminer_installed = True
    except Exception as e:
        result = e
        l.info("STDERR:", result.stderr[0])



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
