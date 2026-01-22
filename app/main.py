from fastapi import FastAPI

app = FastAPI(title="AudioBook App", description="Convert documents to audio", version="0.1.0")

@app.get("/")
async def root():
    return {"message": "AudioBook App API"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
