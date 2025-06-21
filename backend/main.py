from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router as chat_router
import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

print("CORS_ORIGIN:", os.getenv("CORS_ORIGIN"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api") # tags=["chat"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8030,
        reload=True
    )