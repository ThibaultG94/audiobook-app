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
if 'test_audio' not in st.session_state:
    st.session_state.test_audio = None

# Country mapping for French locales
COUNTRY_NAMES = {
    'fr-FR': 'France',
    'fr-BE': 'Belgique',
    'fr-CA': 'Canada',
    'fr-CH': 'Suisse',
    'fr-LU': 'Luxembourg'
}

GENDER_NAMES = {
    'male': 'Homme',
    'female': 'Femme',
    'Male': 'Homme',
    'Female': 'Femme'
}

def format_voice_option(voice):
    """Format voice for display in selectbox."""
    name = voice.get('name', 'Unknown')
    locale = voice.get('locale', 'fr')
    gender = GENDER_NAMES.get(voice.get('gender', 'Unknown'), 'Unknown')
    service = voice.get('service', 'unknown').title()
    country = COUNTRY_NAMES.get(locale, locale.split('-')[1] if '-' in locale else 'France')

    return f"{name} ({gender}, {country}) - {service}"

def get_country_order(country):
    """Get sort order for countries."""
    order = {'France': 0, 'Belgique': 1, 'Canada': 2, 'Suisse': 3, 'Luxembourg': 4}
    return order.get(country, 99)

# Load voices on app start
@st.cache_data
def load_voices():
    try:
        response = requests.get(f"{API_BASE}/voices", timeout=10)
        if response.status_code == 200:
            data = response.json()
            voices = data.get('voices', [])

            # Sort by country, then by name
            voices.sort(key=lambda v: (
                get_country_order(COUNTRY_NAMES.get(v.get('locale', 'fr-FR'), 'France')),
                v.get('name', '')
            ))

            return voices
        else:
            st.warning("Impossible de charger les voix. L'API est-elle démarrée ?")
            return []
    except Exception as e:
        st.error(f"Erreur de connexion à l'API: {str(e)}")
        return []

# Load voices
st.session_state.voices = load_voices()

# Voice testing section
st.header("🎤 Tester les voix")

col1, col2 = st.columns([2, 1])

with col1:
    test_text = st.text_input(
        "Texte de test :",
        value="Bonjour, ceci est un test de voix française.",
        help="Texte court pour tester la qualité de la voix"
    )

with col2:
    test_voice_options = ["Voix par défaut (fr-FR-DeniseNeural)"] + [
        format_voice_option(voice) for voice in st.session_state.voices
    ]

    selected_test_voice_display = st.selectbox(
        "Voix à tester :",
        options=test_voice_options,
        key="test_voice_selector"
    )

# Extract test voice name
test_selected_voice = None
if selected_test_voice_display != "Voix par défaut (fr-FR-DeniseNeural)":
    for voice in st.session_state.voices:
        if format_voice_option(voice) == selected_test_voice_display:
            test_selected_voice = voice.get('name')
            break

# Test voice button
if st.button("🔊 Écouter la voix", type="secondary"):
    if not test_text.strip():
        st.error("Veuillez entrer un texte de test.")
    else:
        with st.spinner("Génération de l'audio de test..."):
            try:
                # Use new /test-voice endpoint
                response = requests.post(
                    f"{API_BASE}/test-voice",
                    data={
                        'text': test_text,
                        'voice': test_selected_voice
                    },
                    timeout=60
                )

                if response.status_code == 200:
                    # Response is audio file directly
                    st.session_state.test_audio = response.content
                    st.success("✅ Audio de test généré !")

                    # Display audio player
                    st.audio(st.session_state.test_audio, format='audio/mpeg')
                else:
                    try:
                        error_detail = response.json().get('detail', 'Erreur inconnue')
                    except:
                        error_detail = f"Erreur HTTP {response.status_code}"
                    st.error(f"❌ Erreur de génération : {error_detail}")

            except requests.exceptions.Timeout:
                st.error("⏱️ Timeout : La génération prend trop de temps.")
            except Exception as e:
                st.error(f"❌ Erreur : {str(e)}")

# Separator
st.markdown("---")

# Main conversion section
st.header("📄 Convertir un document")

# Voice selector for conversion (same formatting)
voice_options = ["Voix par défaut (fr-FR-DeniseNeural)"] + [
    format_voice_option(voice) for voice in st.session_state.voices
]

selected_voice_display = st.selectbox(
    "Choisissez une voix pour la conversion :",
    options=voice_options,
    index=0
)

# Extract voice name for API call
selected_voice = None
if selected_voice_display != "Voix par défaut (fr-FR-DeniseNeural)":
    for voice in st.session_state.voices:
        if format_voice_option(voice) == selected_voice_display:
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

    # Chapter splitting option (available for all files)
    split_chapters = st.checkbox("📚 Générer un fichier audio par chapitre (ZIP)", help="Si des chapitres sont détectés, crée un fichier ZIP avec un MP3 par chapitre")

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
                if split_chapters:
                    data['split_chapters'] = 'true'
                    endpoint = "/convert-with-chapters"
                else:
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
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Longueur du texte", f"{result['text_length']} caractères")
                        st.metric("Voix utilisée", result['voice_used'])

                    with col2:
                        st.metric("ID de conversion", str(result['conversion_id']))
                        audio_filename = Path(result['audio_file']).name
                        st.metric("Fichier audio", audio_filename)

                    with col3:
                        chapters = result.get('chapters_detected', 0)
                        st.metric("Chapitres détectés", chapters)
                        if chapters > 0:
                            st.info(f"📖 {chapters} chapitre{'s' if chapters > 1 else ''} trouvé{'s' if chapters > 1 else ''}")

                    # Download section
                    try:
                        download_response = requests.get(f"{API_BASE}{result['download_url']}")
                        if download_response.status_code == 200:
                            file_type = result.get('file_type', 'audio')
                            if file_type == 'zip':
                                label = "📥 Télécharger le ZIP (chapitres)"
                                mime = "application/zip"
                            else:
                                label = "📥 Télécharger l'audio MP3"
                                mime = "audio/mpeg"

                            st.download_button(
                                label=label,
                                data=download_response.content,
                                file_name=audio_filename,
                                mime=mime,
                                type="primary"
                            )
                        else:
                            st.error("Erreur lors de la récupération du fichier.")
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
