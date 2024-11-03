import subprocess
import os
import logging
from logging import getLogger

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
try:
    result = subprocess.run(['Rscript', script_dir],
                            check=True, capture_output=True, text=True)
    #st.session_state.install_R_libs = False
except Exception as e:
    result = e
    l.info("STDERR:", result.stderr)