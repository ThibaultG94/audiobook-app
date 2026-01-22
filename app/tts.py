"""
Text-to-speech module using Edge-TTS with pyttsx3 fallback.
"""

import asyncio
import os
import edge_tts
import pyttsx3
from typing import List, Dict, Optional
from pathlib import Path

# Output directory for generated audio files
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

async def list_french_voices_edge() -> List[Dict[str, str]]:
    """List available French voices from Edge-TTS."""
    try:
        voices = await edge_tts.list_voices()
        french_voices = []
        for voice in voices:
            if voice.get('Locale', '').startswith('fr-'):
                french_voices.append({
                    'name': voice.get('Name', ''),
                    'locale': voice.get('Locale', ''),
                    'gender': voice.get('Gender', ''),
                    'service': 'edge'
                })
        return french_voices
    except Exception as e:
        print(f"Error listing Edge-TTS voices: {e}")
        return []

def list_french_voices_pyttsx3() -> List[Dict[str, str]]:
    """List available French voices from pyttsx3."""
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        french_voices = []
        for voice in voices:
            if 'fr' in voice.languages or 'French' in voice.name:
                french_voices.append({
                    'name': voice.name,
                    'locale': voice.languages[0] if voice.languages else 'fr',
                    'gender': 'male' if voice.gender == 'VoiceGenderMale' else 'female',
                    'service': 'pyttsx3'
                })
        return french_voices
    except Exception as e:
        print(f"Error listing pyttsx3 voices: {e}")
        return []

async def list_french_voices() -> List[Dict[str, str]]:
    """List all available French voices from all services."""
    voices = await list_french_voices_edge()
    voices.extend(list_french_voices_pyttsx3())
    return voices

async def generate_audio_edge_tts(text: str, output_path: str, voice: str = "fr-FR-DeniseNeural") -> bool:
    """Generate audio using Edge-TTS."""
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        return True
    except Exception as e:
        print(f"Edge-TTS failed: {e}")
        return False

def generate_audio_pyttsx3(text: str, output_path: str, voice_index: int = 0) -> bool:
    """Generate audio using pyttsx3 as fallback."""
    try:
        engine = pyttsx3.init()
        
        # Set voice if available
        voices = engine.getProperty('voices')
        if voices and voice_index < len(voices):
            engine.setProperty('voice', voices[voice_index].id)
        
        # Generate audio
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        return True
    except Exception as e:
        print(f"pyttsx3 failed: {e}")
        return False

async def generate_audio(text: str, filename: str, voice: Optional[str] = None) -> Optional[str]:
    """Generate audio from text, trying Edge-TTS first, then pyttsx3.

    Args:
        text: Text to convert to speech
        filename: Base filename for output (without extension)
        voice: Voice name to use (optional, will use default if not specified)

    Returns:
        Path to generated audio file, or None if failed
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    if not filename or not isinstance(filename, str):
        raise ValueError("Invalid filename")

    # Clean filename
    safe_filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_')).rstrip()
    output_path = OUTPUT_DIR / f"{safe_filename}.mp3"

    # Try Edge-TTS first
    edge_voice = voice or "fr-FR-DeniseNeural"
    if await generate_audio_edge_tts(text, str(output_path), edge_voice):
        return str(output_path)

    # Fallback to pyttsx3
    pyttsx3_output = OUTPUT_DIR / f"{safe_filename}_fallback.wav"
    if generate_audio_pyttsx3(text, str(pyttsx3_output)):
        return str(pyttsx3_output)

    # Both failed
    return None
