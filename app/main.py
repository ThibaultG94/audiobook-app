"""
FastAPI application for AudioBook conversion.
"""

import os
import shutil
import uuid
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Form
from fastapi.responses import FileResponse
from typing import Optional
from app.text_extraction import extract_text_with_metadata
from app.tts import generate_audio, list_french_voices
from app.database import init_db, save_conversion, update_conversion_status

app = FastAPI(title="AudioBook App", description="Convert documents to audio", version="0.1.0")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
async def root():
    return {"message": "AudioBook App API", "version": "0.1.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/voices")
async def get_voices():
    """List available French voices."""
    try:
        voices = await list_french_voices()
        return {"voices": voices, "count": len(voices)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing voices: {str(e)}")

@app.post("/convert")
async def convert_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Convert uploaded file to audio using default voice."""
    return await _convert_file(file, background_tasks, voice=None)

@app.post("/convert-with-voice")
async def convert_file_with_voice(
    background_tasks: BackgroundTasks,
    voice: str = None,
    file: UploadFile = File(...)
):
    """Convert uploaded file to audio with specified voice."""
    return await _convert_file(file, background_tasks, voice=voice)

async def _convert_file(file: UploadFile, background_tasks: BackgroundTasks, voice: str = None):
    """Internal conversion function."""
    # Validate file type
    allowed_extensions = ['.pdf', '.epub', '.txt']
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size (max 50MB)
    max_size = 50 * 1024 * 1024  # 50MB
    file_content = await file.read()
    if len(file_content) > max_size:
        raise HTTPException(status_code=413, detail="File too large. Maximum size: 50MB")
    
    # Save uploaded file temporarily
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    temp_path = uploads_dir / f"temp_{file.filename}"
    
    try:
        with open(temp_path, "wb") as buffer:
            buffer.write(file_content)
        
        # Extract text and metadata
        try:
            text, metadata = extract_text_with_metadata(str(temp_path))
            if not text or not text.strip():
                raise HTTPException(status_code=422, detail="No text could be extracted from the file")
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Text extraction failed: {str(e)}")
        
        # Save conversion record
        conversion_id = await save_conversion(file.filename)
        
        # Generate audio
        base_filename = Path(file.filename).stem
        try:
            audio_path = await generate_audio(text, base_filename, voice)
            if not audio_path:
                await update_conversion_status(conversion_id, "failed")
                raise HTTPException(status_code=500, detail="Audio generation failed. Try again later.")
            
            await update_conversion_status(conversion_id, "completed")
            
            # Schedule cleanup of temp file
            background_tasks.add_task(os.unlink, temp_path)
            
            # Return result
            return {
                "message": "Conversion successful",
                "audio_file": audio_path,
                "download_url": f"/download/{Path(audio_path).name}",
                "voice_used": voice or "default (fr-FR-DeniseNeural)",
                "text_length": len(text),
                "chapters_detected": metadata['chapter_count'],
                "conversion_id": conversion_id,
                "metadata": metadata  # Include full metadata for future use
            }
            
        except HTTPException:
            raise
        except Exception as e:
            await update_conversion_status(conversion_id, "failed")
            raise HTTPException(status_code=500, detail=f"Audio generation failed: {str(e)}")
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Clean up temp file on any error
        if temp_path.exists():
            background_tasks.add_task(os.unlink, temp_path)
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

@app.post("/test-voice")
async def test_voice(
    background_tasks: BackgroundTasks,
    text: str = Form(..., description="Texte à synthétiser (max 500 caractères)"),
    voice: Optional[str] = Form(None, description="Nom de la voix (optionnel)")
):
    """Test a voice by generating a short audio sample."""
    # Validation
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Le texte ne peut pas être vide")

    if len(text) > 500:
        raise HTTPException(status_code=400, detail="Le texte ne peut pas dépasser 500 caractères")

    # Generate unique filename
    unique_id = uuid.uuid4().hex
    base_filename = f"test_voice_{unique_id}"

    try:
        # Generate audio (no DB saving for tests)
        audio_path = await generate_audio(text, base_filename, voice)

        if not audio_path or not os.path.exists(audio_path):
            raise HTTPException(status_code=500, detail="Échec de la génération audio")

        # Schedule cleanup after response
        background_tasks.add_task(os.unlink, audio_path)

        # Return audio file directly
        return FileResponse(
            path=audio_path,
            media_type='audio/mpeg',
            filename=f"test_voice_{unique_id}.mp3"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du test de voix: {str(e)}")

@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download generated audio file."""
    file_path = Path("outputs") / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        media_type='application/octet-stream',
        filename=filename
    )
