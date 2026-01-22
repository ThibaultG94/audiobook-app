"""
Streamlit frontend for AudioBook App.
"""

import streamlit as st
import requests

st.title("🎧 AudioBook App")
st.write("Convertissez vos documents en audio de qualité")

uploaded_file = st.file_uploader("Choisissez un fichier (PDF, EPUB, TXT)", type=['pdf', 'epub', 'txt'])

if uploaded_file is not None:
    st.write("Fichier uploadé :", uploaded_file.name)

    if st.button("Convertir en audio"):
        with st.spinner("Conversion en cours..."):
            # TODO: Send file to FastAPI backend
            st.success("Conversion terminée !")
            # TODO: Provide download link
