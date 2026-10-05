import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message, 
    InlineKeyboardButton, 
    LabeledPrice, 
    PreCheckoutQuery,
    CallbackQuery
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Токен вашего бота от @BotFather
TOKEN = "8991213129:AAG0BnRT8XmtZXnmz71GWuomB32Qfpddhvc"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 🎁 КАТАЛОГ ТОВАРОВ
PRODUCTS = {
    "item_1": {
        "title": "Золотой подарок",
        "description": "Эксклюзивный золотой подарок для профиля.",
        "price": 10,
        "photo": "https://images.unsplash.com/photo-1513519245088-0e12902e5a38?w=500"
    },
    "item_2": {
        "title": "Бриллиантовый набор",
        "description": "Роскошный набор с бриллиантами.",
        "price": 25,
        "photo": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=500"
    }
}

# 1. Команда /start создает кнопки каталога
@dp.message(CommandStart())
async def cmd_start(message: Message):
    keyboard = InlineKeyboardBuilder()
    
    for key, product in PRODUCTS.items():
        keyboard.row(
            InlineKeyboardButton(
                text=f"{product['title']} ({product['price']} ⭐️)", 
                callback_data=f"buy_{key}"
            )
        )
    
    await message.answer(
        "Привет! Выберите подарок для покупки за Telegram Stars ⭐️:",
        reply_markup=keyboard.as_markup()
    )

# 2. Обработка нажатия на товар и отправка счета
@dp.callback_query(F.data.startswith("buy_"))
async def process_buy(callback: CallbackQuery):
    item_key = callback.data.split("_", 1)[1]
    product = PRODUCTS.get(item_key)
    
    if not product:
        await callback.answer("Товар не найден!", show_alert=True)
        return
    
    prices = [LabeledPrice(label=product['title'], amount=product['price'])]
    
    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title=product['title'],
        description=product['description'],
        payload=f"order_{item_key}",
        provider_token="",  # Для Telegram Stars ВСЕГДА пусто!
        currency="XTR",     # Валюта — Telegram Stars
        prices=prices,
        photo_url=product['photo'],
        photo_size=500,
        photo_width=500,
        photo_height=500
    )
    await callback.answer()

# 3. Обязательный шаг перед оплатой
@dp.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# 4. УСПЕШНАЯ ОПЛАТА И ОТПРАВКА ИНСТРУКЦИИ ДЛЯ ПОЛУЧЕНИЯ
@dp.message(F.successful_payment)
async def successful_payment(message: Message):
    payment = message.successful_payment
    
    # Красивое сообщение с поздравлением и ссылкой/инструкцией
    await message.answer(
        f"🎉 <b>Поздравляем с покупкой!</b>\n"
        f"Вы успешно оплатили {payment.total_amount} ⭐️️.\n\n"
        f"🎁 Ваш подарок успешно получен!\n"
        f"👉 Перейдите по ссылке ниже, чтобы забрать его:\n"
        f"https://t.me/@Misha6767676767",
        parse_mode="HTML"
    )

# Запуск бота
async def main():
    logging.basicConfig(level=logging.INFO)
    print("Бот запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
