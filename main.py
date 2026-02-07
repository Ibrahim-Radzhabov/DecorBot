import logging
import sys
import os  # <--- Добавили модуль OS
from contextlib import asynccontextmanager
from aiogram.filters import Command

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# Импортируем наши настройки и роутеры
from config import BOT_TOKEN, WEBHOOK_URL, WEB_SERVER_PORT, WEB_SERVER_HOST
from bot.handlers import router as bot_router
from api.routes import router as api_router

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

# --- ВАЖНО: ОПРЕДЕЛЯЕМ ПУТЬ К ПАПКЕ ПРОЕКТА ---
# Это решит проблему с тем, что программа не видит папку web
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")
STATIC_DIR = os.path.join(WEB_DIR, "static")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.include_router(bot_router)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Старт
    logger.info(f"Setting webhook to: {WEBHOOK_URL}")
    await bot.set_webhook(url=WEBHOOK_URL, allowed_updates=dp.resolve_used_update_types())
    yield
    # Стоп
    logger.info("Deleting webhook...")
    await bot.delete_webhook()

app = FastAPI(lifespan=lifespan)

# --- ИСПРАВЛЕННАЯ РАЗДАЧА СТАТИКИ ---
# Проверяем, существует ли папка, чтобы не падало молча
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
else:
    logger.error(f"Directory not found: {STATIC_DIR}")

app.include_router(api_router, prefix="/api")

@app.get("/")
async def read_root():
    # --- ИСПРАВЛЕННЫЙ ПУТЬ К INDEX.HTML ---
    index_path = os.path.join(WEB_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return JSONResponse(content={"error": f"File not found: {index_path}"}, status_code=404)

@app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        update = types.Update.model_validate(await request.json(), context={"bot": bot})
        await dp.feed_update(bot, update)
        return JSONResponse(content={"status": "ok"})
    except Exception as e:
        logger.error(f"Error handling webhook: {e}")
        return JSONResponse(content={"status": "error"}, status_code=500)

if __name__ == "__main__":
    try:
        uvicorn.run(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)
    except KeyboardInterrupt:
        pass