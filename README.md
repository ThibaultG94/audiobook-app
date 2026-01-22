# 🎧 AudioBook App

Convertissez vos documents (PDF, EPUB, TXT) en fichiers audio de qualité professionnelle grâce à la synthèse vocale.

**Application complète** : Interface web intuitive + API REST puissante + Base de données SQLite.

## ✨ Fonctionnalités

- 🔄 **Formats supportés** : PDF, EPUB et TXT (extraction automatique du texte)
- 🎵 **Synthèse vocale** : Edge-TTS (qualité Microsoft) avec fallback pyttsx3
- 🎭 **Voix françaises** : Sélection de voix naturelles pour le français
- 🌐 **Interface web** : Streamlit pour une expérience utilisateur fluide
- 🔌 **API REST** : FastAPI avec documentation interactive (/docs)
- 💾 **Historique** : Base de données SQLite pour suivre les conversions
- 📥 **Téléchargement** : Récupération directe des fichiers audio générés
- ⚡ **Performance** : Traitement asynchrone et gestion des gros fichiers (jusqu'à 50MB)

## 🚀 Installation rapide

### Prérequis
- Python 3.8+
- Git

### Étapes d'installation

1. **Clonez le repository** :
```bash
git clone https://github.com/ThibaultG94/audiobook-app.git
cd audiobook-app
```

2. **Créez un environnement virtuel** :
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Installez les dépendances** :
```bash
pip install -r requirements.txt
```

## 🎯 Utilisation

### Lancer l'application complète

1. **Démarrez l'API backend** (dans un terminal) :
```bash
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

2. **Démarrez l'interface web** (dans un autre terminal) :
```bash
source venv/bin/activate
streamlit run frontend/app.py
```

3. **Accédez à l'application** :
   - Interface web : http://localhost:8501
   - Documentation API : http://localhost:8000/docs

### Utilisation de l'interface web

1. **Sélectionnez une voix** : Choisissez parmi les voix françaises disponibles
2. **Uploadez un fichier** : PDF, EPUB ou TXT (max 50MB)
3. **Lancez la conversion** : Suivez la progression en temps réel
4. **Téléchargez l'audio** : Récupérez votre fichier MP3 généré

## 🏗️ Architecture

```
audiobook-app/
├── app/                    # Backend FastAPI
│   ├── main.py            # Endpoints API REST
│   ├── text_extraction.py # Extraction texte (PDF/EPUB/TXT)
│   ├── tts.py            # Synthèse vocale (Edge-TTS + pyttsx3)
│   └── database.py       # Gestion base de données SQLite
├── frontend/              # Interface utilisateur Streamlit
├── tests/                 # Tests unitaires
├── uploads/               # Fichiers temporaires (nettoyés auto)
├── outputs/               # Fichiers audio générés
├── requirements.txt       # Dépendances Python
└── README.md             # Cette documentation
```

## 🔌 API Endpoints

### Points de terminaison principaux

- `GET /` - Informations sur l'API
- `GET /health` - Vérification de santé
- `GET /voices` - Liste des voix françaises disponibles
- `POST /convert` - Conversion avec voix par défaut
- `POST /convert-with-voice` - Conversion avec voix spécifique
- `GET /download/{filename}` - Téléchargement des fichiers audio

### Exemple d'utilisation API

```python
import requests

# Lister les voix
response = requests.get("http://localhost:8000/voices")
voices = response.json()

# Convertir un fichier
files = {'file': open('document.pdf', 'rb')}
response = requests.post("http://localhost:8000/convert", files=files)
result = response.json()
```

## 🧪 Tests

Exécutez les tests unitaires :

```bash
source venv/bin/activate
python -m pytest tests/ -v
```

## 🤝 Contribution

1. Forkez le projet
2. Créez une branche feature (`git checkout -b feature/amazing-feature`)
3. Commitez vos changements (`git commit -m 'Add amazing feature'`)
4. Pushez vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrez une Pull Request

## 📝 Notes techniques

- **Edge-TTS** : Nécessite une connexion internet pour la synthèse vocale
- **pyttsx3** : Fallback hors-ligne mais qualité moindre
- **Base de données** : SQLite créée automatiquement au premier lancement
- **Nettoyage automatique** : Fichiers temporaires supprimés après conversion
- **Limites** : Fichiers max 50MB, timeout 5 minutes par conversion

## 📄 Licence

Distribué sous licence MIT. Voir `LICENSE` pour plus d'informations.

---

**Créé avec ❤️ en Python • FastAPI • Streamlit • Edge-TTS**
