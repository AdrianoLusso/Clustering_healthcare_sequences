import streamlit as st
import pandas as pd

def timeframes_states_console():
    col1, col2 = st.columns(2, vertical_alignment="bottom")
    state = col1.text_input(
        label="Escriba un estado de historial médico"
        , placeholder="Escriba un estado de historial médico"
        , label_visibility='hidden'
        ,value=st.session_state.default_state)

    btn = col2.button('Buscar')

    st.session_state.result['estados_timeframes'].seek(0)
    timesframes_states = pd.read_csv(st.session_state.result['estados_timeframes'])
    if btn or st.session_state.default_state is not None:
        selected_state = timesframes_states[timesframes_states['code'].str[2:] == state]
        selected_state = selected_state.columns[(selected_state==1).any(axis=0)]
        selected_state = [st.session_state.map_data[str(id)] for id in selected_state]

        st.write(selected_state,hide_index=True)