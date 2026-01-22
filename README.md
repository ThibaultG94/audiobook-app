# AudioBook App

Convert documents (PDF, EPUB, TXT) to high-quality audio files using text-to-speech technology.

## Features

- Support for PDF, EPUB, and TXT files
- High-quality French text-to-speech using Edge-TTS
- Fallback to Piper TTS for reliability
- Web interface built with Streamlit
- REST API with FastAPI
- SQLite database for conversion history

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd audiobook-app
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Start the API server:
```bash
uvicorn app.main:app --reload
```

### Start the web interface:
```bash
streamlit run frontend/app.py
```

## Project Structure

```
audiobook-app/
├── app/                    # FastAPI backend
│   ├── main.py            # API endpoints
│   ├── text_extraction.py # Document text extraction
│   ├── tts.py            # Text-to-speech functionality
│   └── database.py       # Database operations
├── frontend/              # Streamlit web interface
├── uploads/               # Temporary uploaded files
├── outputs/               # Generated audio files
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## API Endpoints

- `GET /` - API information
- `GET /health` - Health check

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.
