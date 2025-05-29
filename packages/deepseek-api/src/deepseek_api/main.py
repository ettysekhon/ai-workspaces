import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from deepseek_api.chat import router as chat_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-5s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api", tags=["api"])


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
