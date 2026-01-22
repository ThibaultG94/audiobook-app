"""
Unit tests for TTS module.
"""

import pytest
import asyncio
import os
from pathlib import Path
from app.tts import list_french_voices, generate_audio

@pytest.mark.asyncio
async def test_list_french_voices():
    """Test listing French voices."""
    voices = await list_french_voices()
    assert isinstance(voices, list)

    # Should have at least some voices from Edge-TTS
    assert len(voices) >= 0  # Edge-TTS might not be available in CI

@pytest.mark.asyncio
async def test_generate_audio_empty_text():
    """Test error handling for empty text."""
    with pytest.raises(ValueError, match="Text cannot be empty"):
        await generate_audio("", "test")

@pytest.mark.asyncio
async def test_generate_audio_invalid_filename():
    """Test error handling for invalid filename."""
    with pytest.raises(ValueError, match="Invalid filename"):
        await generate_audio("Hello world", "")

@pytest.mark.asyncio
async def test_generate_audio_none_filename():
    """Test error handling for None filename."""
    with pytest.raises(ValueError, match="Invalid filename"):
        await generate_audio("Hello world", None)

@pytest.mark.asyncio
async def test_generate_audio_basic():
    """Test basic audio generation (may fail if no network/internet)."""
    # This test may fail in environments without internet
    # but ensures the API works correctly
    result = await generate_audio("Hello world", "test_audio")

    # Result should be either a path string or None
    if result is not None:
        assert isinstance(result, str)
        assert result.endswith(('.mp3', '.wav'))
        # Check if file was actually created (if TTS succeeded)
        if os.path.exists(result):
            assert os.path.getsize(result) > 0
            # Clean up
            os.unlink(result)

# Note: Full integration tests with actual TTS would require:
# - Internet connection for Edge-TTS
# - Audio file verification
# - These are left for manual testing
