# import libraries
import streamlit as st
import tkinter as tk
from tkinter import filedialog
import uuid

def directory_chooser(title:str,form = None):
    with st.container():
        # Set up tkinter
        root = tk.Tk()
        root.withdraw()

        # Make folder picker dialog appear on top of other windows
        root.wm_attributes('-topmost', 1)

        # Folder picker button
        st.write(title)
        clicked = st.button('Buscar directorio')
        if clicked:
            if form:
                dirname = form.text_input('Directorio elegido:', filedialog.askdirectory(master=root))
            else:
                dirname = st.text_input('Directorio elegido:', filedialog.askdirectory(master=root))
