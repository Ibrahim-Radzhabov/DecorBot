import json
from urllib.parse import parse_qsl
from aiogram.utils.web_app import check_webapp_signature
from config import BOT_TOKEN
from fastapi import HTTPException, Header


def validate_telegram_data(x_telegram_init_data: str = Header(...)):
    """
    Проверяем подпись данных, пришедших от WebApp, и превращаем их в словарь.
    """
    try:
        # 1. Проверяем валидность хеша (подписи)
        if not check_webapp_signature(BOT_TOKEN, x_telegram_init_data):
            raise HTTPException(status_code=403, detail="Invalid signature")

        # 2. Парсим query-строку (превращаем "a=1&b=2" в словарь {"a": "1", "b": "2"})
        web_app_data = dict(parse_qsl(x_telegram_init_data))

        # 3. Поле 'user' приходит как JSON-строка, декодируем её в объект
        if "user" in web_app_data:
            web_app_data["user"] = json.loads(web_app_data["user"])

        return web_app_data

    except Exception as e:
        # Логируем ошибку, чтобы видеть в консоли, что пошло не так
        print(f"Auth Error: {e}")
        raise HTTPException(status_code=403, detail="Auth failed")