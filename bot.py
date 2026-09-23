import os
import logging
import asyncio
from typing import Dict, Any

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Чтение конфигурации
BOT_TOKEN = os.getenv("BOT_TOKEN", "8835724938:AAG1HQdvarR5jFXDe7o1mPHp2r7bdZXhEhM")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "5014057300"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ==========================================
# 1. КАТАЛОГ СИСТЕМ ВОРОТ
# ==========================================
CATALOG_ITEMS = [
    {
        "id": "glass_7400",
        "title": "Hörmann 7400 / Frameless Glass",
        "desc": (
            "Панорамные алюминиевые ворота со стеклом без видимых внешних креплений.\n\n"
            "• Теплоизоляция: R-14.2 (двойной стеклопакет)\n"
            "• Ветровая стойкость: до 120 MPH\n"
            "• Ресурс пружин: 50 000 циклов\n"
            "• Премиальный выбор для Гранит-Бэй и Фолсома"
        ),
        "photo": "https://forta-usa.com/wp-content/uploads/2026/03/7400_BC45-DC_Clear-scaled.jpg"
    },
    {
        "id": "flush_7200",
        "title": "Hörmann 7200 / Graphite Flush Steel",
        "desc": (
            "Минималистичные гладкие стальные панели графитового цвета.\n\n"
            "• Максимальная термоизоляция: ядро R-18.4\n"
            "• Защита от перегрева калифорнийским летом\n"
            "• Ветровая нагрузка: до 135 MPH\n"
            "• Скрытые стыковочные замки"
        ),
        "photo": "https://forta-usa.com/wp-content/uploads/2026/03/7400_BC44_Black-scaled.jpg"
    },
    {
        "id": "cedar_3400",
        "title": "Series 3400 / Architectural Cedar",
        "desc": (
            "Канадский красный кедр ручной сборки на стальном каркасе.\n\n"
            "• Теплоизоляция: R-16.8\n"
            "• Защитная пропитка UV-маслами\n"
            "• Усиленный вал и пружины под вес массива дерева\n"
            "• Классический стиль для резиденций в Эл-Дорадо Хиллс"
        ),
        "photo": "https://forta-usa.com/wp-content/uploads/2026/03/3400_Walnut_Ranch_Cross6_2-scaled.jpg"
    },
    {
        "id": "commercial_9000",
        "title": "Series 9000 / Commercial & Industrial",
        "desc": (
            "Промышленные секционные и рулонные стальные ворота.\n\n"
            "• Интенсивность: 100 000 циклов\n"
            "• Сталь повышенной толщины\n"
            "• Совместимость с 3-фазными приводами LiftMaster\n"
            "• Для складов, автосервисов и терминалов"
        ),
        "photo": "https://forta-usa.com/wp-content/uploads/2026/03/Screenshot-2025-07-28-172110.jpg"
    }
]

# ==========================================
# 2. FSM (МАШИНА СОСТОЯНИЙ ДЛЯ ЗАЯВКИ)
# ==========================================
class OrderForm(StatesGroup):
    choosing_type = State()
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_city = State()
    waiting_for_details = State()

# ==========================================
# 3. КЛАВИАТУРЫ
# ==========================================
def get_main_reply_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="🚪 Каталог ворот"), KeyboardButton(text="🚨 Срочный ремонт 24/7")],
        [KeyboardButton(text="⚡ Автоматика LiftMaster"), KeyboardButton(text="📍 Зона выезда и контакты")],
        [KeyboardButton(text="📝 Заказать расчет / Вызов")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_catalog_inline_kb(index: int, item_id: str) -> InlineKeyboardMarkup:
    total = len(CATALOG_ITEMS)
    prev_idx = (index - 1) % total
    next_idx = (index + 1) % total

    kb = [
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data=f"cat_nav:{prev_idx}"),
            InlineKeyboardButton(text=f"{index + 1} / {total}", callback_data="noop"),
            InlineKeyboardButton(text="Вперед ▶️", callback_data=f"cat_nav:{next_idx}")
        ],
        [
            InlineKeyboardButton(text="📝 Заказать расчет этой модели", callback_data=f"order_model:{item_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_phone_request_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)],
        [KeyboardButton(text="❌ Отмена")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

def get_cancel_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="❌ Отмена")]], resize_keyboard=True)

# ==========================================
# 4. ОБРАБОТЧИКИ КОМАНД И МЕНЮ
# ==========================================
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    # Обратите внимание: &lt;45 вместо <45, чтобы Telegram HTML-парсер не падал
    welcome_text = (
        "<b>FORTA / Architectural Garage Systems</b>\n"
        "<i>Немецкие секционные ворота Hörmann и автоматика LiftMaster в Сакраменто.</i>\n\n"
        "• <b>24/7 Экстренный выезд</b> при поломке пружин и тросов (45–60 мин)\n"
        "• <b>Установка под ключ</b> с гарантией 12 месяцев на работу\n"
        "• <b>Тихие настенные приводы</b> с уровнем шума менее 45 дБ (&lt;45 dB)\n"
        "• <b>Округ:</b> Sacramento, Placer &amp; El Dorado Counties\n\n"
        "Выберите раздел в меню ниже:"
    )
    await message.answer(welcome_text, parse_mode=ParseMode.HTML, reply_markup=get_main_reply_kb())

@dp.message(F.text == "❌ Отмена")
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено.", reply_markup=get_main_reply_kb())

@dp.message(F.text == "🚪 Каталог ворот")
async def show_catalog(message: Message):
    item = CATALOG_ITEMS[0]
    caption = f"<b>{item['title']}</b>\n\n{item['desc']}"
    await message.answer_photo(
        photo=item["photo"],
        caption=caption,
        parse_mode=ParseMode.HTML,
        reply_markup=get_catalog_inline_kb(0, item["id"])
    )

@dp.callback_query(F.data.startswith("cat_nav:"))
async def catalog_navigate(call: CallbackQuery):
    idx = int(call.data.split(":")[1])
    item = CATALOG_ITEMS[idx]
    caption = f"<b>{item['title']}</b>\n\n{item['desc']}"

    from aiogram.types import InputMediaPhoto
    media = InputMediaPhoto(media=item["photo"], caption=caption, parse_mode=ParseMode.HTML)
    
    await call.message.edit_media(media=media, reply_markup=get_catalog_inline_kb(idx, item["id"]))
    await call.answer()

@dp.callback_query(F.data == "noop")
async def noop_click(call: CallbackQuery):
    await call.answer()

@dp.message(F.text == "🚨 Срочный ремонт 24/7")
async def emergency_service(message: Message, state: FSMContext):
    await state.clear()
    text = (
        "🚨 <b>АВАРИЙНЫЙ ВЫЕЗД ТЕХНИКА 24/7</b>\n\n"
        "• <b>Среднее время прибытия:</b> 45–60 минут\n"
        "• <b>Запчасти в наличии на траке:</b> пружины 50 000 циклов, тросы, ролики, шестерни\n"
        "• <b>Устранение проблемы за 1 визит</b>\n\n"
        "📞 Телефон экстренной связи: <b>+1 (279) 214-3077</b>\n\n"
        "Хотите вызвать дежурного мастера прямо сейчас?"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚨 Вызвать мастера на адрес", callback_data="order_emergency")],
        [InlineKeyboardButton(text="📞 Позвонить напрямую", url="tel:12792143077")]
    ])
    await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=kb)

@dp.message(F.text == "⚡ Автоматика LiftMaster")
async def liftmaster_info(message: Message):
    text = (
        "⚡ <b>Автоматика LiftMaster Direct-Drive</b>\n\n"
        "• <b>Настенный монтаж:</b> направляющие под потолком больше не гремят\n"
        "• <b>Ультра-тихий ход:</b> громкость менее 45 дБ (&lt;45 dB)\n"
        "• <b>Смарт-контроль:</b> приложение myQ (управление с iPhone/Android)\n"
        "• <b>Стандарт Калифорнии (SB-969):</b> встроенный аккумулятор резервного питания\n"
        "• <b>Авто-ригель:</b> замок запирается электромотором при закрытии\n\n"
        "Подходит как для новых ворот, так и для апгрейда уже установленных."
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Заказать установку автоматики", callback_data="order_automation")]
    ])
    await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=kb)

@dp.message(F.text == "📍 Зона выезда и контакты")
async def contact_info(message: Message):
    text = (
        "📍 <b>FORTA / Контакты и сервис</b>\n\n"
        "• <b>Телефон:</b> +1 (279) 214-3077 (24/7)\n"
        "• <b>Email:</b> company.forta.usa@gmail.com\n"
        "• <b>Официальный сайт:</b> https://forta-usa.com\n\n"
        "<b>Зона обслуживания:</b>\n"
        "Sacramento, Roseville, Rocklin, Folsom, El Dorado Hills, Granite Bay, Fair Oaks."
    )
    await message.answer(text, parse_mode=ParseMode.HTML)

# ==========================================
# 5. СЦЕНАРИЙ СБОРА ЗАЯВКИ
# ==========================================
@dp.message(F.text == "📝 Заказать расчет / Вызов")
async def start_general_order(message: Message, state: FSMContext):
    await state.clear()
    await state.update_data(order_type="Общая заявка / Расчет ворот")
    await state.set_state(OrderForm.waiting_for_name)
    await message.answer("Как к вам обращаться? (Имя):", reply_markup=get_cancel_kb())

@dp.callback_query(F.data == "order_emergency")
async def start_emergency_order(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.update_data(order_type="🚨 СРОЧНЫЙ АВАРИЙНЫЙ РЕМОНТ")
    await state.set_state(OrderForm.waiting_for_name)
    await call.message.answer("🚨 Заявка на аварийный выезд. Как вас зовут?", reply_markup=get_cancel_kb())
    await call.answer()

@dp.callback_query(F.data == "order_automation")
async def start_auto_order(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.update_data(order_type="⚡ Установка автоматики LiftMaster")
    await state.set_state(OrderForm.waiting_for_name)
    await call.message.answer("Укажите ваше имя для заявки на автоматику:", reply_markup=get_cancel_kb())
    await call.answer()

@dp.callback_query(F.data.startswith("order_model:"))
async def start_model_order(call: CallbackQuery, state: FSMContext):
    item_id = call.data.split(":")[1]
    item = next((x for x in CATALOG_ITEMS if x["id"] == item_id), None)
    model_name = item["title"] if item else item_id

    await state.clear()
    await state.update_data(order_type=f"Ворота: {model_name}")
    await state.set_state(OrderForm.waiting_for_name)
    await call.message.answer(f"Вы выбрали расчет для <b>{model_name}</b>.\nКак к вам обращаться (Ваше имя)?", parse_mode=ParseMode.HTML, reply_markup=get_cancel_kb())
    await call.answer()

@dp.message(OrderForm.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    await state.update_data(user_name=name)
    await state.set_state(OrderForm.waiting_for_phone)
    await message.answer(
        f"Приятно познакомиться, {name}! Пожалуйста, поделитесь контактом или напишите ваш номер телефона:",
        reply_markup=get_phone_request_kb()
    )

@dp.message(OrderForm.waiting_for_phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    await state.update_data(user_phone=phone)
    await state.set_state(OrderForm.waiting_for_city)
    await message.answer("В каком городе или районе вы находитесь? (например: Folsom 95630, Roseville, Sacramento):", reply_markup=get_cancel_kb())

@dp.message(OrderForm.waiting_for_phone, F.text)
async def process_phone_text(message: Message, state: FSMContext):
    phone = message.text.strip()
    await state.update_data(user_phone=phone)
    await state.set_state(OrderForm.waiting_for_city)
    await message.answer("В каком городе или районе вы находитесь? (например: Folsom 95630, Roseville, Sacramento):", reply_markup=get_cancel_kb())

@dp.message(OrderForm.waiting_for_city)
async def process_city(message: Message, state: FSMContext):
    city = message.text.strip()
    await state.update_data(user_city=city)
    await state.set_state(OrderForm.waiting_for_details)
    await message.answer("Опишите детали заказа или поломки (или отправьте '-', если нет комментария):", reply_markup=get_cancel_kb())

@dp.message(OrderForm.waiting_for_details)
async def process_details(message: Message, state: FSMContext):
    details = message.text.strip()
    data = await state.get_data()
    await state.clear()

    order_type = data.get("order_type", "Заявка")
    user_name = data.get("user_name", "Клиент")
    user_phone = data.get("user_phone", "Не указан")
    user_city = data.get("user_city", "Не указан")
    username = f"@{message.from_user.username}" if message.from_user.username else "нет username"

    # Ответ клиенту
    await message.answer(
        "✅ <b>Ваша заявка успешно передана дежурному диспетчеру FORTA!</b>\n\n"
        "Мы свяжемся с вами в течение 5–15 минут для согласования времени выезда или расчета стоимости.",
        parse_mode=ParseMode.HTML,
        reply_markup=get_main_reply_kb()
    )

    # Уведомление администратору
    admin_alert = (
        f"🚨 <b>НОВАЯ ЗАЯВКА / TELEGRAM BOT</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🛠 <b>Тип:</b> {order_type}\n"
        f"👤 <b>Имя:</b> {user_name}\n"
        f"📞 <b>Телефон:</b> <code>{user_phone}</code>\n"
        f"📍 <b>Локация:</b> {user_city}\n"
        f"💬 <b>Комментарий:</b> {details}\n"
        f"👤 <b>Профиль:</b> {username} (ID: <code>{message.from_user.id}</code>)\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )

    try:
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_alert, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"Не удалось отправить уведомление админу: {e}")

# ==========================================
# 6. ТОЧКА ВХОДА
# ==========================================
async def main():
    logger.info("Бот FORTA запускается...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
