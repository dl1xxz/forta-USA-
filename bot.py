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
    InlineKeyboardButton,
    InputMediaPhoto
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "8835724938:AAG1HQdvarR5jFXDe7o1mPHp2r7bdZXhEhM")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "5014057300"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ==========================================
# 1. ПРОВЕРЕННЫЙ КАТАЛОГ С ПОДДЕРЖИВАЕМЫМИ JPG/PNG ФОТО
# ==========================================
CATALOG_ITEMS = [
    {
        "id": "frameless_7400",
        "category": "residential",
        "photo": "https://forta-usa.com/wp-content/uploads/2026/03/7400_BC45-DC_Clear-scaled.jpg",
        "en": {
            "title": "Hörmann 7400 / Frameless Glass",
            "desc": (
                "<b>Series:</b> Full-View Panoramic Glass\n"
                "• <b>Glass:</b> Double-pane insulated tinted safety glass\n"
                "• <b>Frame:</b> Anodized aluminum with concealed fasteners\n"
                "• <b>Wind Load:</b> Engineered for up to 120 MPH gusts\n"
                "• <b>Best For:</b> Luxury residences in Folsom Lake &amp; Granite Bay"
            )
        },
        "ru": {
            "title": "Hörmann 7400 / Frameless Glass",
            "desc": (
                "<b>Серия:</b> Панорамное тонированное стекло Full-View\n"
                "• <b>Стекло:</b> Двойной энергосберегающий безопасный стеклопакет\n"
                "• <b>Каркас:</b> Анодированный алюминий со скрытыми креплениями\n"
                "• <b>Ветровая стойкость:</b> Расчетная нагрузка до 120 MPH\n"
                "• <b>Идеально для:</b> Вилл в Фолсом-Лейк и Гранит-Бэй"
            )
        },
        "es": {
            "title": "Hörmann 7400 / Frameless Glass",
            "desc": (
                "<b>Serie:</b> Vidrio panorámico de visión completa\n"
                "• <b>Vidrio:</b> Doble acristalamiento templado de seguridad\n"
                "• <b>Marco:</b> Aluminio anodizado con fijaciones ocultas\n"
                "• <b>Carga de viento:</b> Resistencia certificada hasta 120 MPH\n"
                "• <b>Ideal para:</b> Residencias de lujo en Folsom y Granite Bay"
            )
        }
    },
    {
        "id": "flush_7200",
        "category": "residential",
        "photo": "https://forta-usa.com/wp-content/uploads/2026/03/7400_BC44_Black-scaled.jpg",
        "en": {
            "title": "Hörmann Classic Safe 7200 / Flush Steel",
            "desc": (
                "<b>Series:</b> Contemporary Architectural Sectional\n"
                "• <b>Thermal Core:</b> German polyurethane insulation R-18.4\n"
                "• <b>Hardware:</b> High-cycle 50,000 cycles torsion springs\n"
                "• <b>Finish:</b> Graphite matte architectural powder-coat\n"
                "• <b>Best For:</b> Premium custom homes across Sacramento"
            )
        },
        "ru": {
            "title": "Hörmann Classic Safe 7200 / Flush Steel",
            "desc": (
                "<b>Серия:</b> Современные архитектурные секционные ворота\n"
                "• <b>Теплоизоляция:</b> Полиуретановое ядро R-18.4 (защита от жары)\n"
                "• <b>Ресурс пружин:</b> 50 000 рабочих циклов\n"
                "• <b>Покрытие:</b> Матовый графитовый архитектурный слой\n"
                "• <b>Идеально для:</b> Особняков в Сакраменто и Розвилле"
            )
        },
        "es": {
            "title": "Hörmann Classic Safe 7200 / Flush Steel",
            "desc": (
                "<b>Serie:</b> Puertas de garaje seccionales arquitectónicas\n"
                "• <b>Aislamiento térmico:</b> Núcleo de poliuretano R-18.4\n"
                "• <b>Muelles de torsión:</b> 50,000 ciclos de alta durabilidad\n"
                "• <b>Acabado:</b> Pintura en polvo arquitectónica color grafito\n"
                "• <b>Ideal para:</b> Residencias en Sacramento y Roseville"
            )
        }
    },
    {
        "id": "cedar_3400",
        "category": "residential",
        "photo": "https://forta-usa.com/wp-content/uploads/2026/03/3400_Walnut_Ranch_Cross6_2-scaled.jpg",
        "en": {
            "title": "Series 3400 / Architectural Cedar",
            "desc": (
                "<b>Series:</b> Handcrafted Western Red Cedar\n"
                "• <b>Wood:</b> Solid natural cedar mounted on commercial steel subframe\n"
                "• <b>Protection:</b> Marine-grade UV oil weatherproofing\n"
                "• <b>Springs:</b> Custom-weighted heavy-duty torsion assembly\n"
                "• <b>Aesthetic:</b> Estate craftsman styling for El Dorado Hills"
            )
        },
        "ru": {
            "title": "Series 3400 / Architectural Cedar",
            "desc": (
                "<b>Серия:</b> Массив канадского красного кедра ручной работы\n"
                "• <b>Конструкция:</b> Натуральный кедр на усиленном стальном каркасе\n"
                "• <b>Обработка:</b> Глубокая пропитка UV-маслами от рассыхания\n"
                "• <b>Механика:</b> Усиленный торсионный вал под вес массива\n"
                "• <b>Стиль:</b> Классическая калифорнийская усадьба (Эл-Дорадо Хиллс)"
            )
        },
        "es": {
            "title": "Series 3400 / Architectural Cedar",
            "desc": (
                "<b>Serie:</b> Madera natural de cedro rojo canadiense\n"
                "• <b>Construcción:</b> Cedro macizo sobre subchasis de acero\n"
                "• <b>Protección:</b> Sellado marino con aceites contra radiación UV\n"
                "• <b>Mecanismo:</b> Eje de torsión calibrado para madera maciza"
            )
        }
    },
    {
        "id": "stockbridge_3400",
        "category": "residential",
        "photo": "https://forta-usa.com/wp-content/uploads/2026/03/3400_White_Ranch_Stockbridge-scaled.jpg",
        "en": {
            "title": "Hörmann Carriage Stockbridge",
            "desc": (
                "<b>Series:</b> Traditional Carriage House Styling\n"
                "• <b>Design:</b> Decorative hardware and classic top-row window inserts\n"
                "• <b>Insulation:</b> High-density thermal polyurethane foam\n"
                "• <b>Seals:</b> Weather-tight perimeter rubber compression seals"
            )
        },
        "ru": {
            "title": "Hörmann Carriage Stockbridge",
            "desc": (
                "<b>Серия:</b> Традиционный стиль Carriage House\n"
                "• <b>Дизайн:</b> Декоративная кованая фурнитура и верхнее остекление\n"
                "• <b>Изоляция:</b> Плотный термоизолирующий пенополиуретан\n"
                "• <b>Уплотнители:</b> Защита от пыли, ветра и осадков по периметру"
            )
        },
        "es": {
            "title": "Hörmann Carriage Stockbridge",
            "desc": (
                "<b>Serie:</b> Estilo clásico tradicional Carriage House\n"
                "• <b>Diseño:</b> Herrajes decorativos y ventanas superiores integradas\n"
                "• <b>Aislamiento:</b> Poliuretano térmico de alta densidad\n"
                "• <b>Sellado:</b> Juntas de compresión perimetrales resistentes al clima"
            )
        }
    },
    {
        "id": "comm_heavy",
        "category": "commercial",
        "photo": "https://forta-usa.com/wp-content/uploads/2026/03/Screenshot-2025-07-28-172110.jpg",
        "en": {
            "title": "Commercial Heavy-Duty Sectional",
            "desc": (
                "<b>Series:</b> Industrial Logistics &amp; Warehouses\n"
                "• <b>Rating:</b> Continuous duty 100,000 cycles springs\n"
                "• <b>Steel:</b> Heavy 20-gauge hot-dipped galvanized steel panels\n"
                "• <b>Operator:</b> Compatible with LiftMaster 3-phase industrial openers"
            )
        },
        "ru": {
            "title": "Промышленные Heavy-Duty секционные",
            "desc": (
                "<b>Серия:</b> Промышленные ворота для складов и логистических хабов\n"
                "• <b>Ресурс:</b> 100 000 циклов непрерывной эксплуатации\n"
                "• <b>Сталь:</b> Оцинкованная сталь 20-го калибра повышенной толщины\n"
                "• <b>Привод:</b> Прямое подключение 3-фазных моторов LiftMaster"
            )
        },
        "es": {
            "title": "Seccional Comercial Heavy-Duty",
            "desc": (
                "<b>Serie:</b> Puertas industriales para almacenes y talleres\n"
                "• <b>Resistencia:</b> 100,000 ciclos de apertura continua\n"
                "• <b>Acero:</b> Paneles de acero galvanizado calibre 20 de alta resistencia\n"
                "• <b>Automatización:</b> Compatible con motores trifásicos LiftMaster"
            )
        }
    },
    {
        "id": "comm_rolling",
        "category": "commercial",
        "photo": "https://forta-usa.com/wp-content/uploads/2026/03/Screenshot-2025-07-28-172217.jpg",
        "en": {
            "title": "Commercial Rolling Steel Doors",
            "desc": (
                "<b>Series:</b> Space-Saving Coiling Security\n"
                "• <b>Security:</b> Interlocking galvanized steel slats\n"
                "• <b>Form-Factor:</b> Compact overhead roll, zero ceiling rail obstruction\n"
                "• <b>Best For:</b> Storefronts, service bays, forklift loading docks"
            )
        },
        "ru": {
            "title": "Рулонные стальные ворота Rolling Steel",
            "desc": (
                "<b>Серия:</b> Компактные рулонные бронированные ворота\n"
                "• <b>Защита:</b> Взаимозацепляемые стальные ламели высокой жесткости\n"
                "• <b>Габариты:</b> Компактный верхний рулон, потолок свободен от балок\n"
                "• <b>Применение:</b> Автосервисы, погрузочные зоны, склады"
            )
        },
        "es": {
            "title": "Puertas Enrollables de Acero",
            "desc": (
                "<b>Serie:</b> Seguridad enrollable de máxima resistencia\n"
                "• <b>Seguridad:</b> Lamas de acero entrelazadas para protección\n"
                "• <b>Espacio:</b> Enrollamiento superior compacto sin rieles en techo\n"
                "• <b>Ideal para:</b> Muelles de carga, comercios y talleres"
            )
        }
    },
    {
        "id": "comm_grille",
        "category": "commercial",
        "photo": "https://forta-usa.com/wp-content/uploads/2026/03/Screenshot-2025-07-28-172323.jpg",
        "en": {
            "title": "High-Speed Security Grilles",
            "desc": (
                "<b>Series:</b> Rapid Automated Perimeter Control\n"
                "• <b>Speed:</b> Fast-cycle open/close for high vehicle traffic\n"
                "• <b>Airflow:</b> Full ventilation with anti-climb security curtain\n"
                "• <b>Best For:</b> Parking structures, shopping centers, auto facilities"
            )
        },
        "ru": {
            "title": "Скоростные решетки High-Speed Grilles",
            "desc": (
                "<b>Серия:</b> Скоростные вентилируемые защитные системы\n"
                "• <b>Скорость:</b> Быстрый подъем/опускание при плотном трафике машин\n"
                "• <b>Воздухообмен:</b> Постоянная циркуляция воздуха без риска проникновения\n"
                "• <b>Применение:</b> Паркинги, автосалоны, коммерческие въезды"
            )
        },
        "es": {
            "title": "Rejas de Seguridad de Alta Velocidad",
            "desc": (
                "<b>Serie:</b> Control perimetral de alta frecuencia\n"
                "• <b>Velocidad:</b> Ciclo rápido para intenso tránsito vehicular\n"
                "• <b>Ventilación:</b> Máxima visibilidad y flujo de aire continuo\n"
                "• <b>Uso:</b> Estacionamientos subterráneos y accesos comerciales"
            )
        }
    },
    {
        "id": "comm_operator",
        "category": "commercial",
        "photo": "https://forta-usa.com/wp-content/uploads/2026/03/Screenshot-2025-07-28-172928-1.jpg",
        "en": {
            "title": "LiftMaster Industrial Operators",
            "desc": (
                "<b>Series:</b> Heavy Commercial Direct-Drive Openers\n"
                "• <b>Duty:</b> Continuous 24/7 duty cycle rated motor\n"
                "• <b>Safety:</b> Optical safety light curtains &amp; monitored reversing\n"
                "• <b>Connectivity:</b> myQ Facility cloud management &amp; access tracking"
            )
        },
        "ru": {
            "title": "Промышленные приводы LiftMaster",
            "desc": (
                "<b>Серия:</b> Мощная автоматика для интенсивной работы\n"
                "• <b>Нагрузка:</b> Беспрерывный круглосуточный цикл 24/7\n"
                "• <b>Безопасность:</b> Световые барьеры и датчики моментальной остановки\n"
                "• <b>Управление:</b> Облачная платформа myQ Facility со смартфона"
            )
        },
        "es": {
            "title": "Motores Industriales LiftMaster",
            "desc": (
                "<b>Serie:</b> Automatización comercial de servicio continuo\n"
                "• <b>Motor:</b> Diseñado para operación constante las 24 horas\n"
                "• <b>Seguridad:</b> Fotocélulas y cortinas ópticas de detención\n"
                "• <b>Conectividad:</b> Control en la nube myQ Facility"
            )
        }
    }
]

# ==========================================
# 2. МУЛЬТИЯЗЫЧНЫЙ ТЕКСТОВЫЙ ПАКЕТ
# ==========================================
I18N = {
    "en": {
        "welcome": (
            "<b>FORTA / Architectural Garage Systems</b>\n"
            "<i>European Hörmann engineering &amp; American LiftMaster automation.</i>\n\n"
            "• <b>24/7 Emergency Dispatch:</b> 45–60 min arrival (broken springs/cables)\n"
            "• <b>1-Visit Resolution:</b> Fully stocked mobile technician trucks\n"
            "• <b>Whisper-Quiet:</b> Direct-drive wall-mount openers (&lt;45 dB)\n"
            "• <b>Coverage:</b> Sacramento, Roseville, Rocklin, Folsom &amp; El Dorado Hills\n\n"
            "Select an option from the menu below:"
        ),
        "menu_catalog": "🚪 Door Catalog",
        "menu_emergency": "🚨 Emergency Repair 24/7",
        "menu_automation": "⚡ LiftMaster Openers",
        "menu_contacts": "📍 Service Area & Contacts",
        "menu_quote": "📝 Request Quote / Service",
        "menu_lang": "🌐 Language / Idioma",
        "catalog_nav_prev": "◀️ Prev",
        "catalog_nav_next": "Next ▶️",
        "catalog_btn_order": "📝 Request Quote for this Model",
        "emergency_title": "🚨 <b>24/7 EMERGENCY ON-SITE DISPATCH</b>",
        "emergency_body": (
            "• <b>Average Arrival Time:</b> 45–60 minutes in Sacramento region\n"
            "• <b>Parts in Stock:</b> 50K-cycle torsion springs, cables, nylon rollers\n"
            "• <b>Same-Day Resolution:</b> Fixed in 1 visit\n\n"
            "📞 Dispatch Phone: <b>+1 (279) 214-3077</b>"
        ),
        "emergency_btn_call": "📞 Call Technician Now",
        "emergency_btn_order": "🚨 Request Immediate Dispatch",
        "automation_title": "⚡ <b>LiftMaster Direct-Drive Systems</b>",
        "automation_body": (
            "• <b>Wall-Mount Design:</b> Eliminates ceiling rail rattles\n"
            "• <b>Whisper Quiet:</b> Ultra-smooth motion &lt;45 dB\n"
            "• <b>Smart Access:</b> myQ App control with real-time phone alerts\n"
            "• <b>California SB-969:</b> Integrated emergency battery backup included\n"
            "• <b>Automatic Deadbolt:</b> Motor-driven lock seals door upon closure"
        ),
        "automation_btn_order": "📝 Order LiftMaster Installation",
        "contacts_title": "📍 <b>FORTA / Service & Coverage</b>",
        "contacts_body": (
            "• <b>Direct Phone:</b> +1 (279) 214-3077 (24/7 Line)\n"
            "• <b>Email:</b> company.forta.usa@gmail.com\n"
            "• <b>Official Site:</b> https://forta-usa.com\n"
            "• <b>Service Hours:</b> Mon–Sat: 9:00 AM – 5:00 PM (Emergency 24/7)\n\n"
            "<b>Service Areas:</b>\n"
            "Sacramento, Roseville, Rocklin, Folsom, El Dorado Hills, Granite Bay, Fair Oaks."
        ),
        "order_ask_name": "Please enter your name:",
        "order_ask_phone": "Please tap below to send your phone number, or type it manually:",
        "btn_send_contact": "📱 Share Phone Number",
        "order_ask_city": "Which city/zip code are you located in? (e.g. Folsom 95630, Roseville, Sacramento):",
        "order_ask_details": "Please describe your project or issue (or type '-' to skip):",
        "order_success": (
            "✅ <b>Your request has been received by FORTA Dispatch!</b>\n\n"
            "Our technician will contact you within 5–15 minutes to confirm the appointment."
        ),
        "btn_cancel": "❌ Cancel",
        "cancelled": "Operation cancelled."
    },
    "ru": {
        "welcome": (
            "<b>FORTA / Архитектурные гаражные ворота</b>\n"
            "<i>Немецкие системы Hörmann и американская автоматика LiftMaster.</i>\n\n"
            "• <b>Аварийный выезд 24/7:</b> 45–60 минут (лопнувшие пружины, обрыв тросов)\n"
            "• <b>Ремонт за 1 визит:</b> Склад сертифицированных запчастей прямо в траке\n"
            "• <b>Бесшумный ход:</b> Настенные приводы прямого монтажа (&lt;45 dB)\n"
            "• <b>Округа обслуживания:</b> Sacramento, Roseville, Rocklin, Folsom, El Dorado Hills\n\n"
            "Выберите интересующий пункт в меню ниже:"
        ),
        "menu_catalog": "🚪 Каталог ворот",
        "menu_emergency": "🚨 Срочный ремонт 24/7",
        "menu_automation": "⚡ Автоматика LiftMaster",
        "menu_contacts": "📍 Зона выезда и контакты",
        "menu_quote": "📝 Заказать расчет / Вызов",
        "menu_lang": "🌐 Выбрать язык / Language",
        "catalog_nav_prev": "◀️ Назад",
        "catalog_nav_next": "Вперед ▶️",
        "catalog_btn_order": "📝 Заказать расчет этой модели",
        "emergency_title": "🚨 <b>АВАРИЙНЫЙ ВЫЕЗД ДЕЖУРНОГО МАСТЕРА 24/7</b>",
        "emergency_body": (
            "• <b>Время прибытия:</b> 45–60 минут по региону Сакраменто\n"
            "• <b>Запчасти в наличии:</b> Пружины на 50 000 циклов, тросы, ролики\n"
            "• <b>Решение за 1 визит:</b> Устранение аварии в день обращения\n\n"
            "📞 Телефон дежурного: <b>+1 (279) 214-3077</b>"
        ),
        "emergency_btn_call": "📞 Позвонить дежурному мастеру",
        "emergency_btn_order": "🚨 Оформить срочный выезд",
        "automation_title": "⚡ <b>Системы приводов LiftMaster Direct-Drive</b>",
        "automation_body": (
            "• <b>Настенный монтаж:</b> Убирает дребезжащие потолочные направляющие\n"
            "• <b>Тихий ход:</b> Плавное скольжение с громкостью &lt;45 dB\n"
            "• <b>Смарт-контроль:</b> Управление со смартфона через приложение myQ\n"
            "• <b>Закон Калифорнии (SB-969):</b> Встроенный аккумулятор резервного хода\n"
            "• <b>Авторигель:</b> Электрозамок блокирует ворота при закрытии"
        ),
        "automation_btn_order": "📝 Заказать установку автоматики",
        "contacts_title": "📍 <b>FORTA / Контакты и сервис</b>",
        "contacts_body": (
            "• <b>Телефон:</b> +1 (279) 214-3077 (Линия 24/7)\n"
            "• <b>Email:</b> company.forta.usa@gmail.com\n"
            "• <b>Сайт:</b> https://forta-usa.com\n"
            "• <b>Часы работы:</b> Пн–Сб: 9:00 – 17:00 (Аварийная служба 24/7)\n\n"
            "<b>Города обслуживания:</b>\n"
            "Sacramento, Roseville, Rocklin, Folsom, El Dorado Hills, Granite Bay, Fair Oaks."
        ),
        "order_ask_name": "Как к вам обращаться? (Ваше имя):",
        "order_ask_phone": "Пожалуйста, нажмите кнопку ниже для отправки номера или введите его вручную:",
        "btn_send_contact": "📱 Поделиться контактом",
        "order_ask_city": "В каком городе или районе вы находитесь? (например: Folsom 95630, Roseville, Sacramento):",
        "order_ask_details": "Опишите подробности задачи или поломки (или отправьте '-', если нет комментария):",
        "order_success": (
            "✅ <b>Ваша заявка передана дежурному диспетчеру FORTA!</b>\n\n"
            "Мастер свяжется с вами в течение 5–15 минут для подтверждения времени выезда."
        ),
        "btn_cancel": "❌ Отмена",
        "cancelled": "Действие отменено."
    },
    "es": {
        "welcome": (
            "<b>FORTA / Puertas de Garaje Arquitectónicas</b>\n"
            "<i>Ingeniería alemana Hörmann y automatización americana LiftMaster.</i>\n\n"
            "• <b>Servicio de Emergencia 24/7:</b> Llegada en 45–60 min (muelles y cables rotos)\n"
            "• <b>Solución en 1 Visita:</b> Camiones equipados con repuestos originales\n"
            "• <b>Silencio Absoluto:</b> Motores de montaje lateral ultra silenciosos (&lt;45 dB)\n"
            "• <b>Área de Cobertura:</b> Sacramento, Roseville, Rocklin, Folsom y El Dorado Hills\n\n"
            "Seleccione una opción del menú:"
        ),
        "menu_catalog": "🚪 Catálogo de Puertas",
        "menu_emergency": "🚨 Reparación Urgente 24/7",
        "menu_automation": "⚡ Motores LiftMaster",
        "menu_contacts": "📍 Zonas de Servicio y Contacto",
        "menu_quote": "📝 Solicitar Presupuesto / Visita",
        "menu_lang": "🌐 Idioma / Language",
        "catalog_nav_prev": "◀️ Anterior",
        "catalog_nav_next": "Siguiente ▶️",
        "catalog_btn_order": "📝 Cotizar este Modelo",
        "emergency_title": "🚨 <b>SERVICIO DE ASISTENCIA TÉCNICA URGENTE 24/7</b>",
        "emergency_body": (
            "• <b>Tiempo Estimado:</b> 45–60 minutos en la región de Sacramento\n"
            "• <b>Repuestos en Stock:</b> Muelles de torsión de 50,000 ciclos y cables\n"
            "• <b>Reparación Inmediata:</b> Resuelto en la primera visita\n\n"
            "📞 Teléfono directo: <b>+1 (279) 214-3077</b>"
        ),
        "emergency_btn_call": "📞 Llamar al Técnico Ahora",
        "emergency_btn_order": "🚨 Solicitar Visita Urgente",
        "automation_title": "⚡ <b>Sistemas de Automatización LiftMaster Direct-Drive</b>",
        "automation_body": (
            "• <b>Montaje en Pared:</b> Libera espacio y elimina ruidos de rieles\n"
            "• <b>Ultra Silencioso:</b> Movimiento suave a menos de 45 dB (&lt;45 dB)\n"
            "• <b>Control Inteligente:</b> App myQ con alertas en tiempo real en su móvil\n"
            "• <b>Norma California SB-969:</b> Batería de respaldo integrada ante apagones\n"
            "• <b>Cerrojo Eléctrico:</b> Traba motorizada automática al cerrarse"
        ),
        "automation_btn_order": "📝 Solicitar Instalación LiftMaster",
        "contacts_title": "📍 <b>FORTA / Contacto y Cobertura</b>",
        "contacts_body": (
            "• <b>Teléfono:</b> +1 (279) 214-3077 (Línea 24/7)\n"
            "• <b>Correo:</b> company.forta.usa@gmail.com\n"
            "• <b>Sitio Web:</b> https://forta-usa.com\n"
            "• <b>Horario:</b> Lun–Sáb: 9:00 – 17:00 (Emergencias 24/7)\n\n"
            "<b>Áreas de Cobertura:</b>\n"
            "Sacramento, Roseville, Rocklin, Folsom, El Dorado Hills, Granite Bay, Fair Oaks."
        ),
        "order_ask_name": "¿Cuál es su nombre?:",
        "order_ask_phone": "Por favor pulse el botón inferior para enviar su teléfono o escríbalo:",
        "btn_send_contact": "📱 Compartir Teléfono",
        "order_ask_city": "¿En qué ciudad o código postal se encuentra? (ej. Folsom 95630, Roseville, Sacramento):",
        "order_ask_details": "Describa brevemente la reparación o modelo deseado (o envíe '-' para omitir):",
        "order_success": (
            "✅ <b>¡Su solicitud ha sido enviada al técnico de guardia de FORTA!</b>\n\n"
            "Nos comunicaremos con usted en 5–15 minutos para coordinar la visita."
        ),
        "btn_cancel": "❌ Cancelar",
        "cancelled": "Operación cancelada."
    }
}

# ==========================================
# 3. FSM (СОСТОЯНИЯ)
# ==========================================
class OrderForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_city = State()
    waiting_for_details = State()

USER_LANG: Dict[int, str] = {}

def get_lang(user_id: int) -> str:
    return USER_LANG.get(user_id, "en")

# ==========================================
# 4. КЛАВИАТУРЫ
# ==========================================
def get_language_inline_kb() -> InlineKeyboardMarkup:
    kb = [
        [
            InlineKeyboardButton(text="🇺🇸 English", callback_data="set_lang:en"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang:ru"),
            InlineKeyboardButton(text="🇪🇸 Español", callback_data="set_lang:es")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_main_reply_kb(lang: str) -> ReplyKeyboardMarkup:
    t = I18N[lang]
    kb = [
        [KeyboardButton(text=t["menu_catalog"]), KeyboardButton(text=t["menu_emergency"])],
        [KeyboardButton(text=t["menu_automation"]), KeyboardButton(text=t["menu_contacts"])],
        [KeyboardButton(text=t["menu_quote"]), KeyboardButton(text=t["menu_lang"])]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_catalog_inline_kb(index: int, item_id: str, lang: str) -> InlineKeyboardMarkup:
    total = len(CATALOG_ITEMS)
    prev_idx = (index - 1) % total
    next_idx = (index + 1) % total
    t = I18N[lang]

    kb = [
        [
            InlineKeyboardButton(text=t["catalog_nav_prev"], callback_data=f"cat_nav:{prev_idx}"),
            InlineKeyboardButton(text=f"{index + 1} / {total}", callback_data="noop"),
            InlineKeyboardButton(text=t["catalog_nav_next"], callback_data=f"cat_nav:{next_idx}")
        ],
        [
            InlineKeyboardButton(text=t["catalog_btn_order"], callback_data=f"order_model:{item_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def get_phone_request_kb(lang: str) -> ReplyKeyboardMarkup:
    t = I18N[lang]
    kb = [
        [KeyboardButton(text=t["btn_send_contact"], request_contact=True)],
        [KeyboardButton(text=t["btn_cancel"])]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

def get_cancel_kb(lang: str) -> ReplyKeyboardMarkup:
    t = I18N[lang]
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=t["btn_cancel"])]], resize_keyboard=True)

# ==========================================
# 5. СТАРТ И ВЫБОР ЯЗЫКА
# ==========================================
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    intro_text = (
        "<b>FORTA / Architectural Garage Systems</b>\n"
        "<i>Sacramento • Roseville • Folsom • El Dorado Hills</i>\n\n"
        "🇺🇸 Please select your preferred language:\n"
        "🇷🇺 Пожалуйста, выберите язык обслуживания:\n"
        "🇪🇸 Por favor, seleccione su idioma preferido:"
    )
    await message.answer(intro_text, parse_mode=ParseMode.HTML, reply_markup=get_language_inline_kb())

@dp.callback_query(F.data.startswith("set_lang:"))
async def process_language_select(call: CallbackQuery, state: FSMContext):
    lang = call.data.split(":")[1]
    USER_LANG[call.from_user.id] = lang
    await state.update_data(lang=lang)
    
    t = I18N[lang]
    try:
        await call.message.delete()
    except Exception:
        pass
    await call.message.answer(t["welcome"], parse_mode=ParseMode.HTML, reply_markup=get_main_reply_kb(lang))
    await call.answer()

@dp.message(F.text.in_(["🌐 Language / Idioma", "🌐 Выбрать язык / Language", "🌐 Idioma / Language"]))
@dp.message(Command("language"))
@dp.message(Command("lang"))
async def change_language(message: Message, state: FSMContext):
    await state.clear()
    intro_text = (
        "🇺🇸 Select language:\n"
        "🇷🇺 Выберите язык:\n"
        "🇪🇸 Seleccione idioma:"
    )
    await message.answer(intro_text, reply_markup=get_language_inline_kb())

@dp.message(F.text.in_(["❌ Cancel", "❌ Отмена", "❌ Cancelar"]))
async def cancel_handler(message: Message, state: FSMContext):
    lang = get_lang(message.from_user.id)
    t = I18N[lang]
    await state.clear()
    await message.answer(t["cancelled"], reply_markup=get_main_reply_kb(lang))

# ==========================================
# 6. КАТАЛОГ ВОРОТ (С ЗАЩИТОЙ ОТ СБОЕВ СЕТИ)
# ==========================================
@dp.message(F.text.in_(["🚪 Door Catalog", "🚪 Каталог ворот", "🚪 Catálogo de Puertas"]))
async def show_catalog(message: Message):
    lang = get_lang(message.from_user.id)
    item = CATALOG_ITEMS[0]
    data = item.get(lang, item["en"])
    caption = f"<b>{data['title']}</b>\n\n{data['desc']}"
    
    try:
        await message.answer_photo(
            photo=item["photo"],
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=get_catalog_inline_kb(0, item["id"], lang)
        )
    except Exception as e:
        logger.warning(f"Failed to send image directly, falling back: {e}")
        await message.answer(
            f"{caption}\n\n🔗 <i>Photo Preview:</i> {item['photo']}",
            parse_mode=ParseMode.HTML,
            reply_markup=get_catalog_inline_kb(0, item["id"], lang)
        )

@dp.callback_query(F.data.startswith("cat_nav:"))
async def catalog_navigate(call: CallbackQuery):
    lang = get_lang(call.from_user.id)
    idx = int(call.data.split(":")[1])
    item = CATALOG_ITEMS[idx]
    data = item.get(lang, item["en"])
    caption = f"<b>{data['title']}</b>\n\n{data['desc']}"

    try:
        media = InputMediaPhoto(media=item["photo"], caption=caption, parse_mode=ParseMode.HTML)
        await call.message.edit_media(media=media, reply_markup=get_catalog_inline_kb(idx, item["id"], lang))
    except Exception as e:
        logger.warning(f"Error editing media in catalog: {e}")
        try:
            await call.message.edit_caption(caption=caption, parse_mode=ParseMode.HTML, reply_markup=get_catalog_inline_kb(idx, item["id"], lang))
        except Exception:
            pass
    await call.answer()

@dp.callback_query(F.data == "noop")
async def noop_click(call: CallbackQuery):
    await call.answer()

# ==========================================
# 7. АВАРИЙНЫЙ РЕМОНТ И АВТОМАТИКА
# ==========================================
@dp.message(F.text.in_(["🚨 Emergency Repair 24/7", "🚨 Срочный ремонт 24/7", "🚨 Reparación Urgente 24/7"]))
async def emergency_service(message: Message, state: FSMContext):
    await state.clear()
    lang = get_lang(message.from_user.id)
    t = I18N[lang]

    text = f"{t['emergency_title']}\n\n{t['emergency_body']}"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t["emergency_btn_order"], callback_data="order_emergency")],
        [InlineKeyboardButton(text=t["emergency_btn_call"], url="tel:12792143077")]
    ])
    await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=kb)

@dp.message(F.text.in_(["⚡ LiftMaster Openers", "⚡ Автоматика LiftMaster", "⚡ Motores LiftMaster"]))
async def liftmaster_info(message: Message):
    lang = get_lang(message.from_user.id)
    t = I18N[lang]
    text = f"{t['automation_title']}\n\n{t['automation_body']}"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t["automation_btn_order"], callback_data="order_automation")]
    ])
    await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=kb)

@dp.message(F.text.in_(["📍 Service Area & Contacts", "📍 Зона выезда и контакты", "📍 Zonas de Servicio y Contacto"]))
async def contact_info(message: Message):
    lang = get_lang(message.from_user.id)
    t = I18N[lang]
    await message.answer(t["contacts_body"], parse_mode=ParseMode.HTML)

# ==========================================
# 8. СЦЕНАРИЙ ОФОРМЛЕНИЯ ЗАЯВКИ
# ==========================================
@dp.message(F.text.in_(["📝 Request Quote / Service", "📝 Заказать расчет / Вызов", "📝 Solicitar Presupuesto / Visita"]))
async def start_general_order(message: Message, state: FSMContext):
    await state.clear()
    lang = get_lang(message.from_user.id)
    t = I18N[lang]
    await state.update_data(order_type="General Quote / Request", lang=lang)
    await state.set_state(OrderForm.waiting_for_name)
    await message.answer(t["order_ask_name"], reply_markup=get_cancel_kb(lang))

@dp.callback_query(F.data == "order_emergency")
async def start_emergency_order(call: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = get_lang(call.from_user.id)
    t = I18N[lang]
    await state.update_data(order_type="🚨 24/7 EMERGENCY DISPATCH", lang=lang)
    await state.set_state(OrderForm.waiting_for_name)
    await call.message.answer(f"{t['emergency_title']}\n\n{t['order_ask_name']}", parse_mode=ParseMode.HTML, reply_markup=get_cancel_kb(lang))
    await call.answer()

@dp.callback_query(F.data == "order_automation")
async def start_auto_order(call: CallbackQuery, state: FSMContext):
    await state.clear()
    lang = get_lang(call.from_user.id)
    t = I18N[lang]
    await state.update_data(order_type="⚡ LiftMaster Automation Setup", lang=lang)
    await state.set_state(OrderForm.waiting_for_name)
    await call.message.answer(t["order_ask_name"], reply_markup=get_cancel_kb(lang))
    await call.answer()

@dp.callback_query(F.data.startswith("order_model:"))
async def start_model_order(call: CallbackQuery, state: FSMContext):
    item_id = call.data.split(":")[1]
    lang = get_lang(call.from_user.id)
    t = I18N[lang]

    item = next((x for x in CATALOG_ITEMS if x["id"] == item_id), None)
    model_name = item[lang]["title"] if (item and lang in item) else (item["en"]["title"] if item else item_id)

    await state.clear()
    await state.update_data(order_type=f"Model: {model_name}", lang=lang)
    await state.set_state(OrderForm.waiting_for_name)
    await call.message.answer(f"<b>{model_name}</b>\n\n{t['order_ask_name']}", parse_mode=ParseMode.HTML, reply_markup=get_cancel_kb(lang))
    await call.answer()

@dp.message(OrderForm.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    lang = get_lang(message.from_user.id)
    t = I18N[lang]
    name = message.text.strip()
    await state.update_data(user_name=name)
    await state.set_state(OrderForm.waiting_for_phone)
    await message.answer(t["order_ask_phone"], reply_markup=get_phone_request_kb(lang))

@dp.message(OrderForm.waiting_for_phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext):
    lang = get_lang(message.from_user.id)
    t = I18N[lang]
    phone = message.contact.phone_number
    await state.update_data(user_phone=phone)
    await state.set_state(OrderForm.waiting_for_city)
    await message.answer(t["order_ask_city"], reply_markup=get_cancel_kb(lang))

@dp.message(OrderForm.waiting_for_phone, F.text)
async def process_phone_text(message: Message, state: FSMContext):
    lang = get_lang(message.from_user.id)
    t = I18N[lang]
    phone = message.text.strip()
    await state.update_data(user_phone=phone)
    await state.set_state(OrderForm.waiting_for_city)
    await message.answer(t["order_ask_city"], reply_markup=get_cancel_kb(lang))

@dp.message(OrderForm.waiting_for_city)
async def process_city(message: Message, state: FSMContext):
    lang = get_lang(message.from_user.id)
    t = I18N[lang]
    city = message.text.strip()
    await state.update_data(user_city=city)
    await state.set_state(OrderForm.waiting_for_details)
    await message.answer(t["order_ask_details"], reply_markup=get_cancel_kb(lang))

@dp.message(OrderForm.waiting_for_details)
async def process_details(message: Message, state: FSMContext):
    lang = get_lang(message.from_user.id)
    t = I18N[lang]
    details = message.text.strip()
    data = await state.get_data()
    await state.clear()

    order_type = data.get("order_type", "Lead")
    user_name = data.get("user_name", "Customer")
    user_phone = data.get("user_phone", "Not provided")
    user_city = data.get("user_city", "Not provided")
    username = f"@{message.from_user.username}" if message.from_user.username else "no username"

    await message.answer(t["order_success"], parse_mode=ParseMode.HTML, reply_markup=get_main_reply_kb(lang))

    admin_alert = (
        f"🚨 <b>НОВАЯ ЗАЯВКА / FORTA DISPATCH</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🌐 <b>Язык:</b> {lang.upper()}\n"
        f"🛠 <b>Услуга/Модель:</b> {order_type}\n"
        f"👤 <b>Имя:</b> {user_name}\n"
        f"📞 <b>Телефон:</b> <code>{user_phone}</code>\n"
        f"📍 <b>Локация / ZIP:</b> {user_city}\n"
        f"💬 <b>Детали:</b> {details}\n"
        f"👤 <b>Профиль:</b> {username} (ID: <code>{message.from_user.id}</code>)\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )

    try:
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_alert, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"Failed to alert admin: {e}")

# ==========================================
# 9. ТОЧКА ВХОДА
# ==========================================
async def main():
    logger.info("FORTA Bot running with verified JPG photo assets...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
