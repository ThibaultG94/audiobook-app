"""
Text-to-speech module using Edge-TTS with Piper fallback.
"""

import asyncio
import edge_tts
import piper_tts

async def generate_audio_edge_tts(text: str, output_path: str, voice: str = "fr-FR-DeniseNeural") -> bool:
    """Generate audio using Edge-TTS."""
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        return True
    except Exception as e:
        print(f"Edge-TTS failed: {e}")
        return False

def generate_audio_piper_tts(text: str, output_path: str, model: str = "fr_FR_siwis") -> bool:
    """Generate audio using Piper TTS as fallback."""
    try:
        # TODO: Implement Piper TTS
        return False
    except Exception as e:
        print(f"Piper TTS failed: {e}")
        return False

async def generate_audio(text: str, output_path: str) -> bool:
    """Generate audio from text, trying Edge-TTS first, then Piper."""
    # Try Edge-TTS first
    if await generate_audio_edge_tts(text, output_path):
        return True

    # Fallback to Piper
    return generate_audio_piper_tts(text, output_path)
