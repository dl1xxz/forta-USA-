import asyncio
import logging
import os
import sys
from typing import Dict, Any

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    InputMediaPhoto,
)

# Загружаем переменные из .env (если файл присутствует)
load_dotenv()

# Считываем переменные окружения либо используем преднастроенные значения
BOT_TOKEN = os.getenv("BOT_TOKEN", "8835724938:AAG1HQdvarR5jFXDe7o1mPHp2r7bdZXhEhM").strip()
ADMIN_CHAT_ID_RAW = os.getenv("ADMIN_CHAT_ID", "5014057300").strip()

try:
    ADMIN_CHAT_ID = int(ADMIN_CHAT_ID_RAW)
except ValueError:
    print("ОШИБКА: ADMIN_CHAT_ID должен быть числом!")
    ADMIN_CHAT_ID = 5014057300

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Каталог премиальных архитектурных систем FORTA & Hörmann
CATALOG_ITEMS = [
    {
        "id": "glass_7400",
        "title": "SERIES 7400 / FRAMELESS GLASS",
        "badge": "ХИТ / САКРАМЕНТО",
        "origin": "Hörmann Germany",
        "desc": "Премиальное безрамочное тонированное стекло в анодированном алюминиевом каркасе. Создает ультрасовременный фасад виллы в Калифорнии.",
        "specs": "• R-14.2 термоизоляция\n• Ветровая стойкость: до 120 MPH\n• Ресурс торсионных пружин: 50,000 циклов",
        "photo": "https://forta-usa.com/wp-content/uploads/2026/03/7400_BC45-DC_Clear-scaled.jpg"
    },
    {
        "id": "steel_7200",
        "title": "CLASSIC SAFE 7200 / GRAPHITE FLUSH",
        "badge": "МАКСИМАЛЬНОЕ ТЕПЛОСБЕРЕЖЕНИЕ",
        "origin": "Hörmann Germany",
        "desc": "Монолитная матовая сталь графитового оттенка с толстым пенополиуретановым терморазрывом. Блокирует калифорнийскую жару летом.",
        "specs": "• R-18.4 Core Polyurethane\n• Бесшумный ход: <38 dB\n• Соответствие California Title 24",
        "photo": "https://forta-usa.com/wp-content/uploads/2026/03/7400_BC44_Black-scaled.jpg"
    },
    {
        "id": "deco_5250",
        "title": "DECO SAFE 5250 / ARCHITECTURAL",
        "badge": "ПОПУЛЯРНАЯ МОДЕЛЬ",
        "origin": "Hörmann Residential",
        "desc": "Гладкие минималистичные панели с защитой от защемления пальцев и антикоррозийным покрытием для частных домов.",
        "specs": "• Pinch-Safe геометрия секций\n• Усиленные направляющие\n• Долговечное порошковое напыление",
        "photo": "https://forta-usa.com/wp-content/uploads/2026/03/DecoSafe_5250_Main.avif"
    },
    {
        "id": "cedar_3400",
        "title": "SERIES 3400 / WESTERN RED CEDAR",
        "badge": "КАНАДСКИЙ КРАСНЫЙ КЕДР",
        "origin": "Estate Edition",
        "desc": "Натуральный канадский кедр ручной подгонки на термоизолированном стальном сердечнике с пропиткой яхтенными UV-маслами.",
        "specs": "• Ручная сборка ламелей\n• Усиленные балансировочные механизмы\n• Защита от рассыхания на солнце",
        "photo": "https://forta-usa.com/wp-content/uploads/2026/03/3400_Walnut_Ranch_Cross6_2-scaled.jpg"
    },
    {
        "id": "commercial_heavy",
        "title": "HEAVY INDUSTRIAL SECTIONAL",
        "badge": "ДЛЯ СКЛАДОВ И БИЗНЕСА",
        "origin": "Commercial Grade",
        "desc": "Сверхпрочные секционные ворота для логистических хабов, коммерческих терминалов и сервисных боксов с интенсивным движением.",
        "specs": "• 100,000 рабочих циклов\n• Поддержка 3-фазных электроприводов LiftMaster\n• Противоударная конструкция",
        "photo": "https://forta-usa.com/wp-content/uploads/2026/03/Screenshot-2025-07-28-172110.jpg"
    }
]

class OrderFSM(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_location = State()

def get_main_reply_kb() -> ReplyKeyboardMarkup:
    """Главная клавиатура бота внизу чата"""
    kb = [
        [KeyboardButton(text="🚪 Каталог ворот"), KeyboardButton(text="🚨 Срочный ремонт (45 мин)")],
        [KeyboardButton(text="⚡ Автоматика LiftMaster"), KeyboardButton(text="📝 Заказать расчет / замер")],
        [KeyboardButton(text="📍 Зоны обслуживания"), KeyboardButton(text="📞 Связаться с диспетчером")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_catalog_inline_kb(index: int, total: int, item_title: str) -> InlineKeyboardMarkup:
    """Инлайн-листалка карточек каталога"""
    prev_idx = (index - 1) % total
    next_idx = (index + 1) % total

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📝 Заказать расчет этой модели", callback_data=f"order_item:{item_title}")
            ],
            [
                InlineKeyboardButton(text="◀ Назад", callback_data=f"cat:{prev_idx}"),
                InlineKeyboardButton(text=f"{index + 1} / {total}", callback_data="noop"),
                InlineKeyboardButton(text="Вперед ▶", callback_data=f"cat:{next_idx}")
            ],
            [
                InlineKeyboardButton(text="📞 Позвонить диспетчеру", url="tel:+12792143077")
            ]
        ]
    )

def format_item_caption(item: Dict[str, Any]) -> str:
    """Текстовая карточка ворот со спецификациями"""
    return (
        f"🏷 <b>[{item['badge']}]</b>\n"
        f"🚪 <b>{item['title']}</b>\n"
        f"🏭 <i>Производитель: {item['origin']}</i>\n\n"
        f"{item['desc']}\n\n"
        f"<b>Характеристики:</b>\n"
        f"{item['specs']}\n\n"
        f"📍 <i>Доставка и сертифицированный монтаж по округам Sacramento, Placer и El Dorado.</i>"
    )

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    welcome_text = (
        "🇺🇸 <b>FORTA / Architectural Garage Systems</b>\n"
        "<i>Sacramento, Placer & El Dorado Counties</i>\n\n"
        "Добро пожаловать в официальный сервис FORTA.\n\n"
        "• Немецкие секционные ворота <b>Hörmann</b>\n"
        "• Бесшумные настенные приводы <b>LiftMaster</b> (<45 dB)\n"
        "• Экстренная замена лопнувших пружин за <b>45–60 минут</b>\n\n"
        "Выберите действие в меню ниже:"
    )
    await message.answer(welcome_text, parse_mode=ParseMode.HTML, reply_markup=get_main_reply_kb())

@dp.message(F.text == "🚪 Каталог ворот")
async def show_catalog(message: types.Message):
    item = CATALOG_ITEMS[0]
    caption = format_item_caption(item)
    markup = get_catalog_inline_kb(0, len(CATALOG_ITEMS), item["title"])

    try:
        await message.answer_photo(
            photo=item["photo"],
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=markup
        )
    except Exception:
        # Резервный вывод текстом, если Telegram временно недоступен к внешнему фото
        await message.answer(
            f"{caption}\n\n📷 Фото: {item['photo']}",
            parse_mode=ParseMode.HTML,
            reply_markup=markup
        )

@dp.callback_query(F.data.startswith("cat:"))
async def handle_catalog_pagination(call: types.CallbackQuery):
    try:
        idx = int(call.data.split(":")[1])
    except (IndexError, ValueError):
        idx = 0

    item = CATALOG_ITEMS[idx]
    caption = format_item_caption(item)
    markup = get_catalog_inline_kb(idx, len(CATALOG_ITEMS), item["title"])

    media = InputMediaPhoto(media=item["photo"], caption=caption, parse_mode=ParseMode.HTML)
    try:
        await call.message.edit_media(media=media, reply_markup=markup)
    except Exception:
        pass
    await call.answer()

@dp.callback_query(F.data == "noop")
async def handle_noop(call: types.CallbackQuery):
    await call.answer()

@dp.message(F.text == "⚡ Автоматика LiftMaster")
async def show_liftmaster_info(message: types.Message):
    text = (
        "⚡ <b>Настенные приводы LiftMaster Direct-Drive</b>\n\n"
        "Устанавливаем премиальную автоматику без потолочных рельсов:\n"
        "• <b>Абсолютная тишина:</b> уровень шума <45 dB (в спальне над гаражом ничего не слышно).\n"
        "• <b>Свободное пространство:</b> потолок остается свободным для хранения или высоких авто.\n"
        "• <b>Умный дом MyQ:</b> контроль открытия/закрытия со смартфона из любой точки мира.\n"
        "• <b>Резервный аккумулятор:</b> обязательное соответствие закону California SB-969 при отключении света."
    )
    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⚡ Заказать установку LiftMaster", callback_data="order_item:LiftMaster Automation")],
            [InlineKeyboardButton(text="📞 Консультация инженера", url="tel:+12792143077")]
        ]
    )
    await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=inline_kb)

@dp.message(F.text == "📍 Зоны обслуживания")
async def show_service_areas(message: types.Message):
    text = (
        "📍 <b>Регион выезда сервисных траков FORTA (Северная Калифорния)</b>\n\n"
        "Машины укомплектованы пружинами, тросами и роликами для ремонта за 1 визит:\n"
        "• <b>Sacramento County:</b> Sacramento, Fair Oaks, Carmichael, Citrus Heights, Elk Grove.\n"
        "• <b>Placer County:</b> Roseville, Rocklin, Granite Bay, Lincoln, Loomis.\n"
        "• <b>El Dorado County:</b> Folsom, El Dorado Hills, Cameron Park.\n\n"
        "⏱ <b>Среднее время прибытия мастера при поломке:</b> 45–60 минут."
    )
    await message.answer(text, parse_mode=ParseMode.HTML)

@dp.message(F.text == "📞 Связаться с диспетчером")
async def show_contacts(message: types.Message):
    text = (
        "📞 <b>Контакты диспетчерской службы FORTA</b>\n\n"
        "• <b>Телефон (24/7):</b> +1 (279) 214-3077\n"
        "• <b>Email:</b> company.forta.usa@gmail.com\n"
        "• <b>График работы:</b> Пн–Сб: 9:00 – 17:00 (Аварийный выезд — круглосуточно 24/7)"
    )
    call_kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="📞 Позвонить +1 (279) 214-3077", url="tel:+12792143077")]]
    )
    await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=call_kb)

@dp.message(F.text == "🚨 Срочный ремонт (45 мин)")
@dp.message(F.text == "📝 Заказать расчет / замер")
@dp.callback_query(F.data.startswith("order_item:"))
async def start_order_wizard(event: types.Message | types.CallbackQuery, state: FSMContext):
    if isinstance(event, types.CallbackQuery):
        service = event.data.replace("order_item:", "")
        user = event.from_user
        msg = event.message
        await event.answer()
    else:
        service = "Срочный ремонт (Аварийный выезд)" if "Срочный" in event.text else "Расчет / Замер ворот"
        user = event.from_user
        msg = event

    await state.update_data(service=service)
    await state.set_state(OrderFSM.waiting_for_name)

    user_name = user.first_name or ""
    name_kb = None
    if user_name:
        name_kb = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=user_name)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )

    await msg.answer(
        f"📝 <b>Оформление заявки: {service}</b>\n\n"
        "<b>Шаг 1 из 3:</b> Как к вам обращаться?\n"
        "<i>(Напишите имя или нажмите кнопку с вашим именем ниже)</i>",
        parse_mode=ParseMode.HTML,
        reply_markup=name_kb
    )

@dp.message(OrderFSM.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(OrderFSM.waiting_for_phone)

    phone_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Отправить мой номер телефона", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer(
        "<b>Шаг 2 из 3:</b> Укажите контактный номер телефона для диспетчера:\n"
        "<i>(Нажмите кнопку «Отправить мой номер телефона» или введите вручную)</i>",
        parse_mode=ParseMode.HTML,
        reply_markup=phone_kb
    )

@dp.message(OrderFSM.waiting_for_phone, F.contact)
async def process_phone_contact(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await ask_location_step(message, state)

@dp.message(OrderFSM.waiting_for_phone, F.text)
async def process_phone_text(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text.strip())
    await ask_location_step(message, state)

async def ask_location_step(message: types.Message, state: FSMContext):
    await state.set_state(OrderFSM.waiting_for_location)
    cities_kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Сакраменто"), KeyboardButton(text="Розвилл")],
            [KeyboardButton(text="Фолсом"), KeyboardButton(text="Эль-Дорадо Хиллс")],
            [KeyboardButton(text="Гранит Бэй"), KeyboardButton(text="Другой район / ZIP")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(
        "<b>Шаг 3 из 3:</b> В каком городе или районе находится ваш гараж?\n"
        "<i>(Выберите кнопку или введите адрес/ZIP-код)</i>",
        parse_mode=ParseMode.HTML,
        reply_markup=cities_kb
    )

@dp.message(OrderFSM.waiting_for_location)
async def process_location_and_finish(message: types.Message, state: FSMContext):
    location = message.text.strip()
    data = await state.get_data()

    service = data.get("service", "Не указана")
    name = data.get("name", "Клиент")
    phone = data.get("phone", "Не указан")
    tg_user = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"

    # Отправляем готовую карточку заявки администратору в личный Telegram
    dispatch_card = (
        "🚨 <b>НОВАЯ ЗАЯВКА / FORTA DISPATCH BOT</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"🛠 <b>Направление:</b> {service}\n"
        f"👤 <b>Клиент:</b> {name}\n"
        f"📞 <b>Телефон:</b> <code>{phone}</code>\n"
        f"📍 <b>Локация:</b> {location}\n"
        f"💬 <b>Telegram:</b> {tg_user}\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ <i>Свяжитесь с клиентом в течение 5–10 минут!</i>"
    )

    try:
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=dispatch_card, parse_mode=ParseMode.HTML)
    except Exception as e:
        logging.error(f"Не удалось отправить уведомление админу: {e}")

    # Подтверждение клиенту в чат
    confirmation = (
        "✅ <b>Ваша заявка передана дежурному инженеру FORTA!</b>\n\n"
        f"• Выбрано: <b>{service}</b>\n"
        f"• Телефон: <b>{phone}</b>\n"
        f"• Район: <b>{location}</b>\n\n"
        "⏱ Мастер перезвонит вам в течение 5–10 минут для подтверждения времени визита."
    )

    await message.answer(confirmation, parse_mode=ParseMode.HTML, reply_markup=get_main_reply_kb())
    await state.clear()

async def main():
    logging.info(f"FORTA Dispatch Bot запускается... Уведомления настроены на ID: {ADMIN_CHAT_ID}")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())