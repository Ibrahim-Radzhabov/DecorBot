from fastapi import APIRouter, Body, Depends, HTTPException
from aiogram import Bot
from config import BOT_TOKEN, MANAGER_ID
from api.validation import validate_telegram_data

router = APIRouter()
bot = Bot(token=BOT_TOKEN)


@router.post("/create-order")
async def create_order(
        order_data: dict = Body(...),
        # Валидация: проверяем, что запрос от Телеграма
        tg_data: dict = Depends(validate_telegram_data)
):
    try:
        # 1. Достаем данные пользователя из initData (кто нажал кнопку)
        user = tg_data.get("user", {})
        user_id = user.get("id")
        username = user.get("username", "Не указан")
        first_name = user.get("first_name", "")

        # 2. Достаем данные формы
        form = order_data.get("form", {})
        cart = order_data.get("cart", [])
        total_price = order_data.get("total_price", 0)

        # 3. Формируем текст сообщения для менеджера
        text = (
            f"🛒 <b>НОВЫЙ ЗАКАЗ!</b>\n"
            f"👤 <b>Клиент:</b> <a href='tg://user?id={user_id}'>{first_name}</a> (@{username})\n"
            f"📞 <b>Телефон:</b> {form.get('phone')}\n"
            f"📝 <b>Имя в заказе:</b> {form.get('name')}\n"
            f"📍 <b>Адрес/Коммент:</b> {form.get('comment')}\n"
            f"➖➖➖➖➖➖➖➖\n"
        )

        for item in cart:
            text += f"▫️ {item['title']} x{item['count']} — {item['price'] * item['count']} руб.\n"

        text += f"➖➖➖➖➖➖➖➖\n"
        text += f"💰 <b>ИТОГО: {total_price} руб.</b>"

        # 4. Отправляем МЕНЕДЖЕРУ
        await bot.send_message(chat_id=MANAGER_ID, text=text, parse_mode="HTML")

        # 5. (Опционально) Отправляем ПОЛЬЗОВАТЕЛЮ подтверждение
        await bot.send_message(chat_id=user_id, text="✅ Ваш заказ принят! Менеджер скоро свяжется с вами.")

        return {"status": "ok", "message": "Заказ отправлен"}

    except Exception as e:
        print(f"Order Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))