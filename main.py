import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Hello FastAPI Service",
    description="A simple FastAPI service designed for easy deployment on Render.",
    version="1.0.0"
)

# Enable CORS for convenience
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    # Render sets the PORT environment variable automatically
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
