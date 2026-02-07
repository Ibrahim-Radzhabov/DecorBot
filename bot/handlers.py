from idlelib.undo import Command

from aiogram import Router, F, Bot
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery

router = Router()



@router.message(F.content_type == "web_app_data")
async def handle_webapp_data(message: Message, bot: Bot):
    # Если данные пришли через sendData (Вариант 1)
    pass

# Хендлер для PreCheckoutQuery (обязателен для подтверждения платежа)
@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# Хендлер успешного платежа
@router.message(F.successful_payment)
async def process_successful_payment(message: Message):
    payment_info = message.successful_payment
    # Тут логика выдачи цифрового товара (ключ, ссылка, файл)
    await message.answer(f"Оплата прошла! Сумма: {payment_info.total_amount} {payment_info.currency}.")