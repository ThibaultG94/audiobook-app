"""
Streamlit frontend for AudioBook App.
"""

import streamlit as st
import requests
import time
from pathlib import Path

# API base URL
API_BASE = "http://localhost:8000"

st.title("🎧 AudioBook App")
st.write("Convertissez vos documents en audio de qualité")

# Initialize session state
if 'conversion_result' not in st.session_state:
    st.session_state.conversion_result = None
if 'voices' not in st.session_state:
    st.session_state.voices = []

# Load voices on app start
@st.cache_data
def load_voices():
    try:
        response = requests.get(f"{API_BASE}/voices", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('voices', [])
        else:
            st.warning("Impossible de charger les voix. L'API est-elle démarrée ?")
            return []
    except Exception as e:
        st.error(f"Erreur de connexion à l'API: {str(e)}")
        return []

# Load voices
st.session_state.voices = load_voices()

# Voice selector
voice_options = ["Voix par défaut (fr-FR-DeniseNeural)"] + [
    f"{voice.get('name', 'Unknown')} ({voice.get('service', 'unknown')})"
    for voice in st.session_state.voices
]

selected_voice_display = st.selectbox(
    "Choisissez une voix :",
    options=voice_options,
    index=0
)

# Extract voice name for API call
selected_voice = None
if selected_voice_display != "Voix par défaut (fr-FR-DeniseNeural)":
    # Find the corresponding voice object
    for voice in st.session_state.voices:
        if f"{voice.get('name', 'Unknown')} ({voice.get('service', 'unknown')})" == selected_voice_display:
            selected_voice = voice.get('name')
            break

# File uploader
uploaded_file = st.file_uploader(
    "Choisissez un fichier (PDF, EPUB, TXT) :",
    type=['pdf', 'epub', 'txt'],
    help="Fichier maximum : 50MB"
)

if uploaded_file is not None:
    st.write(f"📄 Fichier sélectionné : **{uploaded_file.name}**")
    st.write(f"📏 Taille : **{len(uploaded_file.getvalue()) / 1024:.1f} KB**")
    
    # Convert button
    if st.button("🚀 Convertir en audio", type="primary"):
        if not uploaded_file:
            st.error("Veuillez sélectionner un fichier d'abord.")
            st.stop()
        
        with st.spinner("Conversion en cours... Veuillez patienter..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Prepare file for upload
                files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                data = {'voice': selected_voice} if selected_voice else {}
                
                status_text.text("📤 Envoi du fichier à l'API...")
                progress_bar.progress(25)
                
                # Call API
                endpoint = "/convert-with-voice" if selected_voice else "/convert"
                response = requests.post(
                    f"{API_BASE}{endpoint}",
                    files=files,
                    data=data,
                    timeout=300  # 5 minutes timeout
                )
                
                progress_bar.progress(75)
                status_text.text("🎵 Génération de l'audio...")
                
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.conversion_result = result
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Conversion terminée !")
                    
                    st.success("🎉 Conversion réussie !")
                    
                    # Display results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric("Longueur du texte", f"{result['text_length']} caractères")
                        st.metric("Voix utilisée", result['voice_used'])
                    
                    with col2:
                        st.metric("ID de conversion", str(result['conversion_id']))
                        audio_filename = Path(result['audio_file']).name
                        st.metric("Fichier audio", audio_filename)
                    
                    # Download button
                    download_url = result['download_url']
                    if st.button("📥 Télécharger l'audio", type="primary"):
                        try:
                            download_response = requests.get(f"{API_BASE}{download_url}")
                            if download_response.status_code == 200:
                                st.download_button(
                                    label="📥 Télécharger maintenant",
                                    data=download_response.content,
                                    file_name=audio_filename,
                                    mime="audio/mpeg"
                                )
                            else:
                                st.error("Erreur lors du téléchargement.")
                        except Exception as e:
                            st.error(f"Erreur de téléchargement: {str(e)}")
                
                else:
                    error_detail = response.json().get('detail', 'Erreur inconnue')
                    st.error(f"❌ Erreur de conversion : {error_detail}")
                    
            except requests.exceptions.Timeout:
                st.error("⏱️ Timeout : La conversion prend trop de temps. Réessayez avec un fichier plus petit.")
            except requests.exceptions.ConnectionError:
                st.error("🔌 Erreur de connexion : Vérifiez que l'API FastAPI est démarrée sur le port 8000.")
            except Exception as e:
                st.error(f"❌ Erreur inattendue : {str(e)}")
            finally:
                progress_bar.empty()
                status_text.empty()

# Footer
st.markdown("---")
st.markdown("*Interface créée avec Streamlit • API FastAPI • TTS Edge-TTS*")

# Debug info (collapsible)
with st.expander("🔧 Informations de debug"):
    st.write("URL API :", API_BASE)
    st.write("Voix disponibles :", len(st.session_state.voices))
    if st.session_state.conversion_result:
        st.json(st.session_state.conversion_result)
