import asyncio
import logging
import sys
import json
import random
from datetime import datetime
from os.path import exists

from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, FSInputFile, KeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8269461372:AAFt2r92GoVh7tG9uHcsSyh2rG_rH5UJcP8"
PHOTO_PATH = "/Users/nikitakurlov/eToro/etoro.png"
PROFILE_PHOTO_PATH = "/Users/nikitakurlov/eToro/image copy.png"
TRADING_PHOTO_PATH = "/Users/nikitakurlov/eToro/image copy.png"
USERS_DATA_FILE = "/Users/nikitakurlov/eToro/users_data.json"
TRADE_HISTORY_FILE = "/Users/nikitakurlov/eToro/trade_history.json"
WORKER_CONFIG_FILE = "/Users/nikitakurlov/eToro/worker_config.json"
REQUISITES_FILE = "/Users/nikitakurlov/eToro/requisites.json"

# Данные для торговли
CRYPTO_CURRENCIES = [
    "₿ Bitcoin (BTC)", "Ξ Ethereum (ETH)", "₮ Tether (USDT)", "₿ Bitcoin Cash (BCH)",
    "Ł Litecoin (LTC)", "◊ Cardano (ADA)", "◊ Polkadot (DOT)", "◊ Chainlink (LINK)",
    "◊ Stellar (XLM)", "◊ Uniswap (UNI)"
]

# Маппинг криптовалют на графики
CRYPTO_CHART_URLS = {
    "₿ Bitcoin (BTC)": "https://nikitakurlov1.github.io/GraphcoinOKX/ethereum.html",
    "Ξ Ethereum (ETH)": "https://nikitakurlov1.github.io/GraphcoinOKX/ethereum.html",
    "₮ Tether (USDT)": "https://nikitakurlov1.github.io/GraphcoinOKX/tron.html",
    "₿ Bitcoin Cash (BCH)": "https://nikitakurlov1.github.io/GraphcoinOKX/litecoin.html",
    "Ł Litecoin (LTC)": "https://nikitakurlov1.github.io/GraphcoinOKX/litecoin.html",
    "◊ Cardano (ADA)": "https://nikitakurlov1.github.io/GraphcoinOKX/cardano.html",
    "◊ Polkadot (DOT)": "https://nikitakurlov1.github.io/GraphcoinOKX/avalanche.html",
    "◊ Chainlink (LINK)": "https://nikitakurlov1.github.io/GraphcoinOKX/ripple.html",
    "◊ Stellar (XLM)": "https://nikitakurlov1.github.io/GraphcoinOKX/ton.html",
    "◊ Uniswap (UNI)": "https://nikitakurlov1.github.io/GraphcoinOKX/shib.html"
}

# Графики для акций (рандомно)
STOCK_CHART_URLS = [
    "https://nikitakurlov1.github.io/GraphcoinOKX/ethereum.html",
    "https://nikitakurlov1.github.io/GraphcoinOKX/litecoin.html",
    "https://nikitakurlov1.github.io/GraphcoinOKX/cardano.html",
    "https://nikitakurlov1.github.io/GraphcoinOKX/ripple.html",
    "https://nikitakurlov1.github.io/GraphcoinOKX/bnb.html"
]

# Графики для сырья (рандомно)
COMMODITY_CHART_URLS = [
    "https://nikitakurlov1.github.io/GraphcoinOKX/terra.html",
    "https://nikitakurlov1.github.io/GraphcoinOKX/tron.html",
    "https://nikitakurlov1.github.io/GraphcoinOKX/doge.html",
    "https://nikitakurlov1.github.io/GraphcoinOKX/avalanche.html",
    "https://nikitakurlov1.github.io/GraphcoinOKX/ton.html",
    "https://nikitakurlov1.github.io/GraphcoinOKX/shib.html"
]

RUSSIAN_STOCKS = [
    "🛢️ Газпром (GAZP)", "🛢️ Лукойл (LKOH)", "🏦 Сбербанк (SBER)", "⚡ Россети (RSTI)",
    "🏭 Норникель (GMKN)", "🛢️ Татнефть (TATN)", "🏭 НЛМК (NLMK)", "🏭 Северсталь (CHMF)",
    "🏭 ММК (MAGN)", "🏭 АЛРОСА (ALRS)"
]

COMMODITIES = [
    "🥇 Золото (GOLD)", "🥈 Серебро (SILVER)", "🛢️ Нефть Brent (OIL)", "⛽ Природный газ (GAS)",
    "🌾 Пшеница (WHEAT)", "🌽 Кукуруза (CORN)", "☕ Кофе (COFFEE)", "🍫 Какао (COCOA)",
    "🥜 Соевые бобы (SOYBEAN)", "🍯 Сахар (SUGAR)"
]

ASSET_PRICES = {
    "₿ Bitcoin (BTC)": 4500000, "Ξ Ethereum (ETH)": 280000, "₮ Tether (USDT)": 95,
    "₿ Bitcoin Cash (BCH)": 45000, "Ł Litecoin (LTC)": 12000, "◊ Cardano (ADA)": 45,
    "◊ Polkadot (DOT)": 380, "◊ Chainlink (LINK)": 1200, "◊ Stellar (XLM)": 8,
    "◊ Uniswap (UNI)": 180, "🛢️ Газпром (GAZP)": 180, "🛢️ Лукойл (LKOH)": 7200,
    "🏦 Сбербанк (SBER)": 280, "⚡ Россети (RSTI)": 1.2, "🏭 Норникель (GMKN)": 18000,
    "🛢️ Татнефть (TATN)": 4200, "🏭 НЛМК (NLMK)": 180, "🏭 Северсталь (CHMF)": 1200,
    "🏭 ММК (MAGN)": 45, "🏭 АЛРОСА (ALRS)": 120, "🥇 Золото (GOLD)": 6500,
    "🥈 Серебро (SILVER)": 85, "🛢️ Нефть Brent (OIL)": 6500, "⛽ Природный газ (GAS)": 120,
    "🌾 Пшеница (WHEAT)": 18000, "🌽 Кукуруза (CORN)": 15000, "☕ Кофе (COFFEE)": 450,
    "🍫 Какао (COCOA)": 280, "🥜 Соевые бобы (SOYBEAN)": 35000, "🍯 Сахар (SUGAR)": 65
}

router = Router()

# Глобальные хранилища данных
users_data = {}
trading_states = {}
trade_message_ids = {}
authorized_workers = set()
worker_states = {}
worker_config = {}

def load_users_data():
    """Загружает данные пользователей из файла"""
    global users_data
    try:
        if exists(USERS_DATA_FILE):
            with open(USERS_DATA_FILE, 'r', encoding='utf-8') as f:
                users_data = {str(k): v for k, v in json.load(f).items()}
            for user_id, user_data in users_data.items():
                user_data.setdefault('pending_withdrawal', 0.0)
                user_data.setdefault('verified', False)
                user_data.setdefault('username', "")
            save_users_data()
    except Exception as e:
        logging.error(f"Ошибка загрузки данных пользователей: {e}")
        users_data = {}

def save_users_data():
    """Сохраняет данные пользователей в файл"""
    try:
        with open(USERS_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Ошибка сохранения данных пользователей: {e}")

def load_trade_history():
    """Загружает историю сделок из файла"""
    try:
        if exists(TRADE_HISTORY_FILE):
            with open(TRADE_HISTORY_FILE, 'r', encoding='utf-8') as f:
                return {str(k): v for k, v in json.load(f).items()}
        return {}
    except Exception as e:
        logging.error(f"Ошибка загрузки истории сделок: {e}")
        return {}

def save_trade_history(trade_history):
    """Сохраняет историю сделок в файл"""
    try:
        with open(TRADE_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(trade_history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Ошибка сохранения истории сделок: {e}")

def load_worker_config():
    """Загружает конфигурацию воркера из файла"""
    global worker_config
    try:
        if exists(WORKER_CONFIG_FILE):
            with open(WORKER_CONFIG_FILE, 'r', encoding='utf-8') as f:
                worker_config = {str(k): v for k, v in json.load(f).items()}
        else:
            worker_config = {}
    except Exception as e:
        logging.error(f"Ошибка загрузки конфигурации воркера: {e}")
        worker_config = {}

def save_worker_config():
    """Сохраняет конфигурацию воркера в файл"""
    try:
        with open(WORKER_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(worker_config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Ошибка сохранения конфигурации воркера: {e}")

def load_requisites():
    """Загружает реквизиты из файла"""
    try:
        if exists(REQUISITES_FILE):
            with open(REQUISITES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "bank_card": "1234 5678 9012 3456",
            "bank_name": "Сбербанк",
            "cardholder_name": "Иван Иванов",
            "crypto_wallet": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
            "crypto_type": "Bitcoin (BTC)"
        }
    except Exception as e:
        logging.error(f"Ошибка загрузки реквизитов: {e}")
        return {}

def save_requisites(requisites):
    """Сохраняет реквизиты в файл"""
    try:
        with open(REQUISITES_FILE, 'w', encoding='utf-8') as f:
            json.dump(requisites, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Ошибка сохранения реквизитов: {e}")

def get_user_worker_config(user_id):
    """Получает конфигурацию воркера для пользователя"""
    user_id_str = str(user_id)
    if user_id_str not in worker_config:
        worker_config[user_id_str] = {
            "trade_mode": "random",
            "win_coefficient": 1.0,
            "custom_balance": None
        }
        save_worker_config()
    return worker_config[user_id_str]

def add_trade_to_history(user_id: int, trade_data: dict, result: str, win_amount: float, new_balance: float):
    """Добавляет сделку в историю"""
    trade_history = load_trade_history()
    user_id_str = str(user_id)
    
    if user_id_str not in trade_history:
        trade_history[user_id_str] = []
    
    trade_record = {
        "id": len(trade_history[user_id_str]) + 1,
        "timestamp": datetime.now().isoformat(),
        "asset": trade_data['asset_name'],
        "direction": trade_data['direction'],
        "amount": trade_data['amount'],
        "time_sec": trade_data['time_sec'],
        "leverage": trade_data.get('leverage', 1.0),  # Добавляем плечо
        "result": result,
        "win_amount": win_amount,
        "new_balance": new_balance
    }
    
    trade_history[user_id_str].append(trade_record)
    save_trade_history(trade_history)

def get_user_data(user_id, username=""):
    """Получает данные пользователя или создает новые"""
    user_id_str = str(user_id)
    if user_id_str not in users_data:
        join_date = datetime.now()
        users_data[user_id_str] = {
            "accepted_terms": False,
            "balance": 0.0,
            "pending_withdrawal": 0.0,
            "verified": False,
            "join_date": join_date.isoformat(),
            "username": username or ""
        }
        save_users_data()
    
    user_data = users_data[user_id_str]
    if username and not user_data.get("username"):
        user_data["username"] = username
        save_users_data()
    
    join_date = datetime.fromisoformat(user_data["join_date"])
    days_on_platform = (datetime.now() - join_date).days
    user_data["days_on_platform"] = max(1, days_on_platform)
    
    return user_data

def create_static_menu():
    """Создает статическое меню внизу"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="📈 Торговля"))
    builder.add(KeyboardButton(text="👤 Профиль"))
    builder.add(KeyboardButton(text="🆘 Поддержка"))
    builder.add(KeyboardButton(text="ℹ️ Информация"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

@router.message(CommandStart())
async def send_welcome(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name or "Пользователь"
    user_data = get_user_data(user_id, username)
    
    if user_data["accepted_terms"]:
        await show_user_profile(message)
        return
    
    if not exists(PHOTO_PATH):
        logging.error(f"Файл не найден по пути: {PHOTO_PATH}")
        await message.answer("Ошибка: Не могу найти файл изображения.\nПожалуйста, свяжитесь с администратором.")
        return

    photo_to_send = FSInputFile(PHOTO_PATH)
    welcome_text = (
        "🎉 <b>Добро пожаловать в eToro!</b>\n\n"
        "📊 <b>Торговая платформа нового поколения</b>\n\n"
        "━━━━━━━━━━━━━\n\n"
        "💡 Перед началом работы необходимо:\n\n"
        "✅ Ознакомиться с условиями использования\n"
        "✅ Принять пользовательское соглашение\n\n"
        "📜 <i>Пожалуйста, внимательно прочитайте условия и примите их для продолжения</i>"
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="Прочитать условия 📜", url="https://telegra.ph/Usloviya-servisa-eTron-10-23")
    builder.button(text="Прочитал(а), согласен(на) ✅", callback_data="accept_terms")
    builder.adjust(1)

    await message.answer_photo(
        photo=photo_to_send,
        caption=welcome_text,
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data == "accept_terms")
async def process_terms_accept(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_data = get_user_data(user_id)
    
    user_data["accepted_terms"] = True
    save_users_data()
    
    await callback.answer("Условия приняты!", show_alert=False)
    
    try:
        await callback.message.delete()
    except TelegramBadRequest as e:
        logging.warning(f"Не удалось удалить сообщение: {e}")

    await show_user_profile(callback.message)

async def show_user_profile(message: Message):
    """Показывает профиль пользователя с обработкой ошибок"""
    try:
        user_id = message.from_user.id
        username = message.from_user.username or message.from_user.first_name or "Пользователь"
        user_data = get_user_data(user_id, username)
    except Exception as e:
        logging.error(f"Error getting user data: {e}")
        await message.answer("❌ Произошла ошибка. Попробуйте позже.")
        return
    
    current_hour = datetime.now().hour
    online_users = random.randint(1200, 1800) if 6 <= current_hour <= 22 else random.randint(800, 1200)
    
    profile_text = (
        f"👤 <b>eToro • Личный кабинет</b>\n\n"
        f"━━━━━━━━━━━━━\n\n"
        f"💰 <b>Баланс:</b> {user_data['balance']:.2f} ₽\n"
        f"📤 <b>На выводе:</b> {user_data['pending_withdrawal']:.2f} ₽\n\n"
        f"━━━━━━━━━━━━━\n\n"
        f"📅 <b>На платформе:</b> {user_data['days_on_platform']} дн.\n"
        f"✅ <b>Верификация:</b> {'✅ Верифицирован' if user_data['verified'] else '⚠️ Не верифицирован'}\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n\n"
        f"━━━━━━━━━━━━━\n\n"
        f"🟢 <i>Пользователей онлайн: {online_users}</i>"
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="🔼 Пополнить", callback_data="deposit"))
    builder.add(types.InlineKeyboardButton(text="🔽 Вывести", callback_data="withdraw"))
    builder.add(types.InlineKeyboardButton(text="🕒 История сделок", callback_data="history"))
    builder.adjust(2, 1)
    
    try:
        if exists(PROFILE_PHOTO_PATH):
            photo = FSInputFile(PROFILE_PHOTO_PATH)
            try:
                await message.answer_photo(
                    photo=photo,
                    caption=profile_text,
                    reply_markup=builder.as_markup(),
                    parse_mode=ParseMode.HTML
                )
            except Exception as photo_error:
                logging.warning(f"Failed to send photo: {photo_error}, sending text only")
                await message.answer(
                    profile_text,
                    reply_markup=builder.as_markup(),
                    parse_mode=ParseMode.HTML
                )
        else:
            await message.answer(
                profile_text,
                reply_markup=builder.as_markup(),
                parse_mode=ParseMode.HTML
            )
        
        await message.answer("Выберите действие:", reply_markup=create_static_menu())
    except Exception as e:
        logging.error(f"Ошибка при отправке профиля: {e}")
        await message.answer("Произошла ошибка. Попробуйте снова.")

@router.callback_query(F.data == "deposit")
async def handle_deposit(callback: CallbackQuery):
    requisites = load_requisites()
    
    text = (
        "💳 <b>Пополнение баланса</b>\n\n"
        "Выберите способ пополнения:"
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="🏦 Банковская карта", callback_data="deposit_bank"))
    builder.add(types.InlineKeyboardButton(text="₿ Криптовалюта", callback_data="deposit_crypto"))
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_profile"))
    builder.adjust(2, 1)
    
    try:
        await callback.message.edit_caption(
            caption=text,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
    except TelegramBadRequest:
        await callback.message.answer(
            text,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
    
    await callback.answer()

@router.callback_query(F.data == "deposit_bank")
async def handle_deposit_bank(callback: CallbackQuery):
    requisites = load_requisites()
    
    text = (
        "💳 <b>Пополнение через банковскую карту</b>\n\n"
        f"🏦 Банк: {requisites.get('bank_name', 'Не указан')}\n"
        f"💳 Номер карты: <code>{requisites.get('bank_card', 'Не указан')}</code>\n"
        f"👤 Получатель: {requisites.get('cardholder_name', 'Не указан')}\n\n"
        "📝 Инструкция:\n"
        "1. Переведите нужную сумму на указанную карту\n"
        "2. Сохраните чек об оплате\n"
        "3. Отправьте скриншот чека в поддержку\n"
        "4. Средства поступят на баланс в течение 5-15 минут"
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="deposit"))
    builder.adjust(1)
    
    try:
        await callback.message.edit_caption(
            caption=text,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
    except TelegramBadRequest:
        await callback.message.answer(
            text,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
    
    await callback.answer()

@router.callback_query(F.data == "deposit_crypto")
async def handle_deposit_crypto(callback: CallbackQuery):
    requisites = load_requisites()
    
    text = (
        "₿ <b>Пополнение через криптовалюту</b>\n\n"
        f"💎 Валюта: {requisites.get('crypto_type', 'Не указан')}\n"
        f"📧 Адрес кошелька:\n<code>{requisites.get('crypto_wallet', 'Не указан')}</code>\n\n"
        "📝 Инструкция:\n"
        "1. Отправьте криптовалюту на указанный адрес\n"
        "2. Сохраните хеш транзакции\n"
        "3. Отправьте хеш в поддержку\n"
        "4. Средства поступят после 3 подтверждений сети"
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="deposit"))
    builder.adjust(1)
    
    try:
        await callback.message.edit_caption(
            caption=text,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
    except TelegramBadRequest:
        await callback.message.answer(
            text,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
    
    await callback.answer()

@router.callback_query(F.data == "withdraw")
async def handle_withdraw(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_data = get_user_data(user_id)
    
    if not user_data.get('verified', False):
        await callback.answer(
            "⚠️ Для вывода средств необходимо пройти верификацию.\n"
            "Обратитесь в поддержку для прохождения верификации.",
            show_alert=True
        )
        return
    
    min_withdraw = 1000.0
    if user_data['balance'] < min_withdraw:
        await callback.answer(
            f"⚠️ Минимальная сумма для вывода: {min_withdraw:.2f} ₽\n"
            f"Ваш баланс: {user_data['balance']:.2f} ₽",
            show_alert=True
        )
        return
    
    text = (
        "💰 <b>Вывод средств</b>\n\n"
        f"💳 Доступно для вывода: {user_data['balance']:.2f} ₽\n"
        f"📤 На выводе: {user_data.get('pending_withdrawal', 0):.2f} ₽\n\n"
        "Выберите способ вывода:"
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="🏦 Банковская карта", callback_data="withdraw_bank"))
    builder.add(types.InlineKeyboardButton(text="₿ Криптовалюта", callback_data="withdraw_crypto"))
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_profile"))
    builder.adjust(2, 1)
    
    try:
        await callback.message.edit_caption(
            caption=text,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
    except TelegramBadRequest:
        await callback.message.answer(
            text,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
    
    await callback.answer()

@router.callback_query(F.data.startswith("withdraw_"))
async def handle_withdraw_method(callback: CallbackQuery):
    method = callback.data.split("_")[1]
    method_name = "банковскую карту" if method == "bank" else "криптовалюту"
    
    text = (
        f"💰 <b>Вывод на {method_name}</b>\n\n"
        "Для вывода средств:\n"
        "1. Обратитесь в поддержку\n"
        "2. Укажите сумму вывода\n"
        "3. Предоставьте реквизиты\n"
        "4. Дождитесь обработки заявки\n\n"
        "⏱ Время обработки: 1-24 часа\n"
        "💼 Комиссия: 0%"
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="withdraw"))
    builder.adjust(1)
    
    try:
        await callback.message.edit_caption(
            caption=text,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
    except TelegramBadRequest:
        await callback.message.answer(
            text,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
    
    await callback.answer()

@router.callback_query(F.data == "history")
async def handle_history(callback: CallbackQuery):
    await show_trade_history(callback)
    await callback.answer()

async def show_trade_history(callback: CallbackQuery):
    user_id = callback.from_user.id
    trade_history = load_trade_history()
    user_id_str = str(user_id)
    
    if user_id_str not in trade_history or not trade_history[user_id_str]:
        empty_text = (
            "📊 История сделок\n\n"
            "📝 У вас пока нет совершенных сделок.\n"
            "Начните торговать, чтобы увидеть историю!"
        )
        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text="⬅️ Назад к профилю", callback_data="back_to_profile"))
        builder.adjust(1)
        
        try:
            await callback.message.edit_caption(
                caption=empty_text,
                reply_markup=builder.as_markup()
            )
        except TelegramBadRequest:
            await callback.message.answer(
                empty_text,
                reply_markup=builder.as_markup()
            )
        return
    
    user_trades = trade_history[user_id_str][-10:]
    user_trades.reverse()
    
    history_text = "📊 История сделок\n\n"
    
    for trade in user_trades:
        trade_date = datetime.fromisoformat(trade['timestamp']).strftime("%d.%m.%Y %H:%M")
        result_emoji = "🎉" if trade['result'] == "Победа" else "😥"
        result_text = f"+{trade['win_amount']:,.2f} RUB" if trade['result'] == "Победа" else f"-{trade['amount']:,.2f} RUB"
        direction_emoji = "⬆️" if "Вверх" in trade['direction'] else "⬇️"
        leverage = trade.get('leverage', 1.0)
        
        history_text += (
            f"{result_emoji} <b>#{trade['id']}</b> • {trade_date}\n"
            f"📊 {trade['asset']}\n"
            f"{direction_emoji} {trade['direction']} • {trade['amount']:,.2f} RUB • {trade['time_sec']} • x{leverage:.1f}\n"
            f"💰 {result_text}\n\n"
        )
    
    total_trades = len(trade_history[user_id_str])
    wins = len([t for t in trade_history[user_id_str] if t['result'] == "Победа"])
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    
    history_text += f"📈 Статистика: {wins}/{total_trades} побед ({win_rate:.1f}%)"
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад к профилю", callback_data="back_to_profile"))
    builder.adjust(1)
    
    try:
        await callback.message.edit_caption(
            caption=history_text,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
    except TelegramBadRequest:
        await callback.message.answer(
            history_text,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )

@router.callback_query(F.data == "back_to_profile")
async def handle_back_to_profile(callback: CallbackQuery):
    await show_user_profile(callback.message)
    await callback.answer()

@router.message(F.text == "👤 Профиль")
async def handle_profile_button(message: Message):
    await show_user_profile(message)

@router.message(F.text == "📈 Торговля")
async def handle_trading_button(message: Message):
    await show_trading_categories(message)

@router.message(F.text == "🆘 Поддержка")
async def handle_support_button(message: Message):
    """Обработчик кнопки поддержки"""
    support_text = (
        "🆘 <b>Служба поддержки</b>\n\n"
        "📧 Для получения помощи свяжитесь с нашей службой поддержки:\n\n"
        "💬 <i>Мы поможем вам решить любые вопросы!</i>"
    )
    await message.answer(support_text, parse_mode=ParseMode.HTML)

@router.message(F.text == "ℹ️ Информация")
async def handle_info_button(message: Message):
    """Обработчик кнопки информации"""
    info_text = (
        "ℹ️ <b>О платформе eToro</b>\n\n"
        "📊 eToro - ведущая платформа для торговли и инвестиций\n\n"
        "✅ Криптовалюты\n"
        "✅ Акции\n"
        "✅ Сырьевые товары\n\n"
        "⚡ Быстрые сделки от 10 секунд!\n"
        "🎯 Кредитное плечо до x10\n"
        "💰 Минимальный депозит от 1 ₽"
    )
    await message.answer(info_text, parse_mode=ParseMode.HTML)

@router.message(Command("worker1236"))
async def handle_worker_auth(message: Message):
    user_id = message.from_user.id
    authorized_workers.add(user_id)
    await show_worker_panel(message)

async def show_worker_panel(message: Message):
    text = (
        "🔧 <b>Панель воркера</b>\n\n"
        "Добро пожаловать в панель управления!\n"
        "Выберите действие:"
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="👥 Мои маммонты", callback_data="worker_mammonts"))
    builder.add(types.InlineKeyboardButton(text="💳 Реквизиты", callback_data="worker_requisites"))
    builder.add(types.InlineKeyboardButton(text="📢 Рассылка", callback_data="worker_broadcast"))
    builder.adjust(1)
    
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)

@router.message(F.text)
async def handle_worker_text_input(message: Message):
    """Обработчик текстовых сообщений для воркеров и пользователей"""
    worker_id = message.from_user.id
    
    # Пропускаем команды
    if message.text and message.text.startswith('/'):
        return
    
    # Приоритет 1: Обработка числового ввода для торговли
    if worker_id in trading_states and trading_states[worker_id].get('step') == 'waiting_amount':
        try:
            # Проверяем, является ли текст числом
            text = message.text.strip().replace(',', '.').replace(' ', '')
            if text.replace('.', '', 1).replace('-', '', 1).isdigit():
                logging.info(f"Processing numeric input '{message.text}' for investment by user {worker_id}")
                await handle_investment_amount(message)
                return
        except Exception as e:
            logging.error(f"Error processing numeric input: {e}")
            await message.answer("❌ Ошибка обработки суммы. Пожалуйста, введите корректное число.")
            return
    
    # Приоритет 2: Обработка действий воркера
    if worker_id in worker_states and worker_id in authorized_workers:
        state = worker_states[worker_id]
        action = state.get('action')
        
        if action == 'set_balance':
            try:
                new_balance = float(message.text)
                target_user_id = state['target_user_id']
                
                if target_user_id in users_data:
                    users_data[target_user_id]['balance'] = new_balance
                    save_users_data()
                    username = users_data[target_user_id].get('username', 'Неизвестно')
                    
                    await message.answer(
                        f"✅ <b>Баланс изменен!</b>\n\n"
                        f"👤 Пользователь: @{username}\n"
                        f"🆔 ID: {target_user_id}\n"
                        f"💰 Новый баланс: {new_balance:,.2f} ₽",
                        parse_mode=ParseMode.HTML
                    )
                    del worker_states[worker_id]
                else:
                    await message.answer("❌ Пользователь не найден в базе данных")
                    del worker_states[worker_id]
            except ValueError:
                await message.answer("❌ Неверный формат. Введите число (например: 1000 или 1000.50)")
            return
        
        elif action == 'send_message':
            target_user_id = state['target_user_id']
            try:
                await message.bot.send_message(
                    chat_id=int(target_user_id),
                    text=f"📨 <b>Сообщение от администрации:</b>\n\n{message.text}",
                    parse_mode=ParseMode.HTML
                )
                await message.answer(f"✅ Сообщение отправлено пользователю {target_user_id}")
                del worker_states[worker_id]
            except (TelegramBadRequest, TelegramForbiddenError) as e:
                await message.answer(f"❌ Ошибка отправки: {e}")
            return
        
        elif action == 'edit_bank_requisites':
            lines = message.text.strip().split('\n')
            if len(lines) >= 3:
                requisites = load_requisites()
                requisites['bank_card'] = lines[0].strip()
                requisites['bank_name'] = lines[1].strip()
                requisites['cardholder_name'] = lines[2].strip()
                save_requisites(requisites)
                await message.answer("✅ Банковские реквизиты обновлены!")
                del worker_states[worker_id]
            else:
                await message.answer("❌ Неверный формат. Отправьте 3 строки: номер карты, банк, владелец")
            return
        
        elif action == 'edit_crypto_requisites':
            lines = message.text.strip().split('\n')
            if len(lines) >= 2:
                requisites = load_requisites()
                requisites['crypto_type'] = lines[0].strip()
                requisites['crypto_wallet'] = lines[1].strip()
                save_requisites(requisites)
                await message.answer("✅ Крипто-реквизиты обновлены!")
                del worker_states[worker_id]
            else:
                await message.answer("❌ Неверный формат. Отправьте 2 строки: тип криптовалюты, адрес кошелька")
            return
        
        elif action == 'broadcast':
            bot = message.bot
            success_count = 0
            fail_count = 0
            
            for user_id in users_data.keys():
                try:
                    await bot.send_message(
                        chat_id=int(user_id),
                        text=f"📢 <b>Сообщение от администрации:</b>\n\n{message.text}",
                        parse_mode=ParseMode.HTML
                    )
                    success_count += 1
                except (TelegramBadRequest, TelegramForbiddenError) as e:
                    fail_count += 1
                    logging.error(f"Ошибка отправки пользователю {user_id}: {e}")
            
            await message.answer(
                f"✅ Рассылка завершена!\n"
                f"Успешно: {success_count}\n"
                f"Ошибок: {fail_count}"
            )
            del worker_states[worker_id]
            return
    
    # Если ничего не подошло - показываем помощь
    # Это предотвратит "игнорирование" сообщений

async def handle_investment_amount(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name or "Пользователь"
    
    logging.info(f"Investment handler called for user {user_id} with text '{message.text}'")
    logging.info(f"User in trading_states: {user_id in trading_states}")
    if user_id in trading_states:
        logging.info(f"Trading state step: {trading_states[user_id].get('step')}")
    
    # Skip if this is a worker setting balance or other worker action
    if user_id in worker_states and user_id in authorized_workers:
        logging.info(f"Skipping - user is worker in worker_states")
        return
    
    # Check if user is in trading state waiting for amount
    if user_id not in trading_states or trading_states[user_id]['step'] != 'waiting_amount':
        logging.info(f"Skipping - user not in correct trading state")
        return
    
    user_data = get_user_data(user_id, username)
    
    try:
        amount = float(message.text)
        
        if amount < 1:
            await message.answer(
                "❌ <b>Ошибка!</b>\n\n"
                "💡 Минимальная сумма инвестиций: <b>1 RUB</b>\n"
                "✏️ Пожалуйста, введите сумму от 1 рубля",
                parse_mode=ParseMode.HTML
            )
            return
        
        # ИСПРАВЛЕНО: Проверяем только базовую сумму, а не с учетом плеча
        # Плечо влияет только на прибыль/убыток, а не на требуемый баланс
        leverage = trading_states[user_id].get('leverage', 1.0)
        
        if amount > user_data['balance']:
            await message.answer(
                f"❌ <b>Недостаточно средств!</b>\n\n"
                f"💳 <b>Ваш баланс:</b> {user_data['balance']:,.2f} RUB\n"
                f"💰 <b>Требуется:</b> {amount:,.2f} RUB\n\n"
                f"💡 Пополните баланс или укажите меньшую сумму",
                parse_mode=ParseMode.HTML
            )
            return
        
        trading_states[user_id]['amount'] = amount
        trading_states[user_id]['step'] = 'configuring'
        
        await show_trade_configurator(message, user_id)
        
    except ValueError:
        await message.answer("❌ Пожалуйста, введите корректную сумму (например: 100 или 100.50)")

async def show_trade_configurator(message: Message, user_id: int):
    user_data = get_user_data(user_id)
    trade_data = trading_states[user_id]
    leverage = trade_data.get('leverage', 1.0)
    
    config_text = (
        "⚙️ <b>Настройка сделки</b>\n\n"
        f"💰 <b>Сумма:</b> {trade_data['amount']:,.2f} RUB\n"
        f"📈 <b>Актив:</b> {trade_data.get('asset_name', 'Не указан')}\n\n"
        f"━━━━━━━━━━━━━\n\n"
        f"↕️ <b>Направление:</b> {trade_data.get('direction', '❌ Не выбрано')}\n"
        f"💡 <i>Прогноз: курс пойдет вверх или вниз?</i>\n\n"
        f"⏱️ <b>Время сделки:</b> {trade_data.get('time_sec', '❌ Не выбрано')}\n"
        f"💡 <i>На какой период открыть сделку?</i>\n\n"
        f"📊 <b>Кредитное плечо:</b> x{leverage:.1f}\n"
        f"💡 <i>Увеличивает прибыль и риск</i>\n\n"
        f"⚡ <b>Выберите параметры и нажмите 'Создать сделку'</b>"
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="⬆️ Вверх", callback_data="trade_set_direction:up"))
    builder.add(types.InlineKeyboardButton(text="⬇️ Вниз", callback_data="trade_set_direction:down"))
    builder.add(types.InlineKeyboardButton(text="10 сек", callback_data="trade_set_time:10"))
    builder.add(types.InlineKeyboardButton(text="30 сек", callback_data="trade_set_time:30"))
    builder.add(types.InlineKeyboardButton(text="60 сек", callback_data="trade_set_time:60"))
    builder.add(types.InlineKeyboardButton(text="x1", callback_data="trade_set_leverage:1.0"))
    builder.add(types.InlineKeyboardButton(text="x2", callback_data="trade_set_leverage:2.0"))
    builder.add(types.InlineKeyboardButton(text="x5", callback_data="trade_set_leverage:5.0"))
    builder.add(types.InlineKeyboardButton(text="x10", callback_data="trade_set_leverage:10.0"))
    builder.add(types.InlineKeyboardButton(text="✅ Создать сделку", callback_data="trade_create_deal"))
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад (к вводу суммы)", callback_data="trade_reset_to_amount"))
    builder.adjust(2, 3, 4, 1, 1)
    
    sent_message = await message.answer(
        config_text,
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )
    trade_message_ids[user_id] = sent_message.message_id

@router.callback_query(F.data.startswith("trade_set_direction:"))
async def handle_direction_selection(callback: CallbackQuery):
    user_id = callback.from_user.id
    direction = callback.data.split(":")[1]
    
    if user_id not in trading_states:
        await callback.answer("❌ Сессия торговли истекла", show_alert=True)
        return
    
    trading_states[user_id]['direction'] = "⬆️ Вверх" if direction == "up" else "⬇️ Вниз"
    await update_trade_configurator(callback, user_id)
    await callback.answer()

@router.callback_query(F.data.startswith("trade_set_time:"))
async def handle_time_selection(callback: CallbackQuery):
    user_id = callback.from_user.id
    time_sec = callback.data.split(":")[1]
    
    if user_id not in trading_states:
        await callback.answer("❌ Сессия торговли истекла", show_alert=True)
        return
    
    trading_states[user_id]['time_sec'] = f"{time_sec} сек"
    await update_trade_configurator(callback, user_id)
    await callback.answer()

@router.callback_query(F.data.startswith("trade_set_leverage:"))
async def handle_leverage_selection(callback: CallbackQuery):
    user_id = callback.from_user.id
    leverage = float(callback.data.split(":")[1])
    
    if user_id not in trading_states:
        await callback.answer("❌ Сессия торговли истекла", show_alert=True)
        return
    
    trading_states[user_id]['leverage'] = leverage
    logging.info(f"User {user_id} selected leverage: x{leverage:.1f}")
    await update_trade_configurator(callback, user_id)
    await callback.answer(f"✅ Плечо установлено: x{leverage:.1f}")

async def update_trade_configurator(callback: CallbackQuery, user_id: int):
    trade_data = trading_states[user_id]
    leverage = trade_data.get('leverage', 1.0)
    
    config_text = (
        "⚙️ <b>Настройка сделки</b>\n\n"
        f"💰 <b>Сумма:</b> {trade_data['amount']:,.2f} RUB\n"
        f"📈 <b>Актив:</b> {trade_data.get('asset_name', 'Не указан')}\n\n"
        f"━━━━━━━━━━━━━\n\n"
        f"↕️ <b>Направление:</b> {trade_data.get('direction', '❌ Не выбрано')}\n"
        f"💡 <i>Прогноз: курс пойдет вверх или вниз?</i>\n\n"
        f"⏱️ <b>Время сделки:</b> {trade_data.get('time_sec', '❌ Не выбрано')}\n"
        f"💡 <i>На какой период открыть сделку?</i>\n\n"
        f"📊 <b>Кредитное плечо:</b> x{leverage:.1f}\n"
        f"💡 <i>Увеличивает прибыль и риск</i>\n\n"
        f"⚡ <b>Выберите параметры и нажмите 'Создать сделку'</b>"
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="⬆️ Вверх", callback_data="trade_set_direction:up"))
    builder.add(types.InlineKeyboardButton(text="⬇️ Вниз", callback_data="trade_set_direction:down"))
    builder.add(types.InlineKeyboardButton(text="10 сек", callback_data="trade_set_time:10"))
    builder.add(types.InlineKeyboardButton(text="30 сек", callback_data="trade_set_time:30"))
    builder.add(types.InlineKeyboardButton(text="60 сек", callback_data="trade_set_time:60"))
    builder.add(types.InlineKeyboardButton(text="x1", callback_data="trade_set_leverage:1.0"))
    builder.add(types.InlineKeyboardButton(text="x2", callback_data="trade_set_leverage:2.0"))
    builder.add(types.InlineKeyboardButton(text="x5", callback_data="trade_set_leverage:5.0"))
    builder.add(types.InlineKeyboardButton(text="x10", callback_data="trade_set_leverage:10.0"))
    builder.add(types.InlineKeyboardButton(text="✅ Создать сделку", callback_data="trade_create_deal"))
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад (к вводу суммы)", callback_data="trade_reset_to_amount"))
    builder.adjust(2, 3, 4, 1, 1)
    
    try:
        await callback.message.edit_text(
            config_text,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
    except TelegramBadRequest as e:
        logging.warning(f"Не удалось обновить конфигуратор: {e}")

@router.callback_query(F.data == "trade_reset_to_amount")
async def handle_reset_to_amount(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    if user_id not in trading_states:
        await callback.answer("❌ Сессия торговли истекла", show_alert=True)
        return
    
    trading_states[user_id]['step'] = 'waiting_amount'
    trading_states[user_id]['amount'] = None
    trading_states[user_id]['direction'] = None
    trading_states[user_id]['time_sec'] = None
    
    user_data = get_user_data(user_id)
    reset_text = f"Ваш баланс: {user_data['balance']:,.2f} RUB\n\n🌐 Введите сумму, которую хотите инвестировать:"
    
    try:
        await callback.message.edit_text(
            reset_text,
            reply_markup=None
        )
    except TelegramBadRequest as e:
        logging.warning(f"Не удалось сбросить к вводу суммы: {e}")
    
    await callback.answer()

@router.callback_query(F.data == "trade_create_deal")
async def handle_create_deal(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    if user_id not in trading_states:
        await callback.answer("❌ Сессия торговли истекла", show_alert=True)
        return
    
    trade_data = trading_states[user_id]
    
    if not trade_data.get('direction') or not trade_data.get('time_sec'):
        await callback.answer("⚠️ Пожалуйста, выберите направление и время ставки!", show_alert=True)
        return
    
    await execute_trade(callback, user_id)
    await callback.answer("✅ Сделка создана!")

async def execute_trade(callback: CallbackQuery, user_id: int):
    trade_data = trading_states[user_id]
    user_data = get_user_data(user_id)
    
    user_config = get_user_worker_config(user_id)
    time_seconds = int(trade_data['time_sec'].split()[0])
    
    await run_trade_timer(callback, user_id, time_seconds)
    
    # Determine trade result based on worker configuration
    trade_mode = user_config.get('trade_mode', 'random')
    
    if trade_mode == 'always_win':
        is_win = True
        logging.info(f"User {user_id} trade mode: always_win - Result: WIN")
    elif trade_mode == 'always_lose':
        is_win = False
        logging.info(f"User {user_id} trade mode: always_lose - Result: LOSE")
    else:  # random mode
        is_win = random.choice([True, False])
        logging.info(f"User {user_id} trade mode: random - Result: {'WIN' if is_win else 'LOSE'}")
    
    leverage = trade_data.get('leverage', 1.0)
    
    if is_win:
        win_coefficient = user_config.get('win_coefficient', 1.0)
        win_amount = trade_data['amount'] * win_coefficient * leverage  # Учитываем плечо
        logging.info(f"User {user_id} WIN: amount={trade_data['amount']}, coefficient={win_coefficient}, leverage={leverage}, win_amount={win_amount}")
        user_data['balance'] += win_amount
        save_users_data()
        
        add_trade_to_history(user_id, trade_data, "Победа", win_amount, user_data['balance'])
        
        result_text = (
            f"🎉 <b>ПОБЕДА!</b> 🎉\n\n"
            f"━━━━━━━━━━━━━\n\n"
            f"✅ <b>Сделка закрыта успешно!</b>\n\n"
            f"💰 <b>Прибыль:</b> +{win_amount:,.2f} RUB\n"
            f"📈 <b>Коэффициент:</b> {win_coefficient}x\n"
            f"📊 <b>Плечо:</b> x{leverage:.1f}\n\n"
            f"━━━━━━━━━━━━━\n\n"
            f"💳 <b>Новый баланс:</b> {user_data['balance']:,.2f} RUB\n\n"
            f"🚀 <i>Продолжайте торговать!</i>"
        )
    else:
        loss_amount = trade_data['amount']  # Убыток равен только введенной сумме
        user_data['balance'] = max(0, user_data['balance'] - loss_amount)
        save_users_data()
        
        add_trade_to_history(user_id, trade_data, "Поражение", 0, user_data['balance'])
        
        result_text = (
            f"😔 <b>ПОРАЖЕНИЕ</b>\n\n"
            f"━━━━━━━━━━━━━\n\n"
            f"❌ <b>Сделка закрыта с убытком</b>\n\n"
            f"📉 <b>Потеря:</b> -{loss_amount:,.2f} RUB\n"
            f"📊 <b>Плечо:</b> x{leverage:.1f}\n\n"
            f"━━━━━━━━━━━━━\n\n"
            f"💳 <b>Текущий баланс:</b> {user_data['balance']:,.2f} RUB\n\n"
            f"💪 <i>Не расстраивайтесь! Следующая сделка может быть успешной!</i>"
        )
    
    await callback.message.answer(result_text, parse_mode=ParseMode.HTML)
    
    if user_id in trading_states:
        del trading_states[user_id]
    if user_id in trade_message_ids:
        del trade_message_ids[user_id]

async def run_trade_timer(callback: CallbackQuery, user_id: int, total_seconds: int):
    trade_data = trading_states[user_id]
    
    for remaining in range(total_seconds, 0, -1):
        progress_bar = create_progress_bar(remaining, total_seconds)
        
        timer_text = (
            f"⏳ <b>СДЕЛКА АКТИВНА</b>\n\n"
            f"━━━━━━━━━━━━━\n\n"
            f"📊 <b>Актив:</b> {trade_data['asset_name']}\n"
            f"↕️ <b>Направление:</b> {trade_data['direction']}\n"
            f"💰 <b>Сумма:</b> {trade_data['amount']:,.2f} RUB\n\n"
            f"━━━━━━━━━━━━━\n\n"
            f"⏱️ <b>Осталось:</b> {remaining} сек\n\n"
            f"{progress_bar}\n\n"
            f"💡 <i>Ожидайте результата...</i>"
        )
        
        try:
            await callback.message.edit_text(
                timer_text,
                reply_markup=None,
                parse_mode=ParseMode.HTML
            )
        except TelegramBadRequest as e:
            logging.warning(f"Не удалось обновить таймер: {e}")
            break
        
        await asyncio.sleep(1)
    
    final_text = (
        f"⏰ <b>СДЕЛКА ЗАВЕРШЕНА!</b>\n\n"
        f"━━━━━━━━━━━━━\n\n"
        f"📊 <b>Актив:</b> {trade_data['asset_name']}\n"
        f"↕️ <b>Направление:</b> {trade_data['direction']}\n"
        f"💰 <b>Сумма:</b> {trade_data['amount']:,.2f} RUB\n\n"
        f"━━━━━━━━━━━━━\n\n"
        f"🔎 <b>Подсчет результата...</b>"
    )
    
    try:
        await callback.message.edit_text(
            final_text,
            reply_markup=None,
            parse_mode=ParseMode.HTML
        )
    except TelegramBadRequest as e:
        logging.warning(f"Не удалось обновить финальное сообщение: {e}")

def create_progress_bar(remaining: int, total: int) -> str:
    percentage = (remaining / total) * 100
    filled_blocks = int((percentage / 100) * 12)
    empty_blocks = 12 - filled_blocks
    filled_char = "🟩"
    empty_char = "⬜"
    progress_bar = filled_char * filled_blocks + empty_char * empty_blocks
    time_emoji = "🟢" if percentage > 80 else "🟡" if percentage > 60 else "🟠" if percentage > 30 else "🔴"
    return f"{time_emoji} {progress_bar} {percentage:.0f}%"

async def show_trading_categories(message: Message):
    """Показывает категории активов для торговли"""
    text = (
        "📊 <b>Выбор категории актива</b>\n\n"
        "💡 <i>Выберите тип актива для инвестирования:</i>\n\n"
        "₿ <b>Криптовалюта</b> - цифровые активы\n"
        "📈 <b>Акции</b> - российские компании\n"
        "🥇 <b>Сырье</b> - природные ресурсы\n\n"
        "⚡ Быстрые сделки от 10 секунд!"
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="₿ Криптовалюта", callback_data="trade_crypto"))
    builder.add(types.InlineKeyboardButton(text="📈 Акции", callback_data="trade_stocks"))
    builder.add(types.InlineKeyboardButton(text="🥇 Сырье", callback_data="trade_commodities"))
    builder.adjust(3)
    
    try:
        if exists(TRADING_PHOTO_PATH):
            photo = FSInputFile(TRADING_PHOTO_PATH)
            try:
                await message.answer_photo(
                    photo=photo,
                    caption=text,
                    reply_markup=builder.as_markup(),
                    parse_mode=ParseMode.HTML
                )
            except Exception as photo_error:
                logging.warning(f"Failed to send trading photo: {photo_error}")
                await message.answer(
                    text,
                    reply_markup=builder.as_markup(),
                    parse_mode=ParseMode.HTML
                )
        else:
            await message.answer(
                text,
                reply_markup=builder.as_markup(),
                parse_mode=ParseMode.HTML
            )
    except Exception as e:
        logging.error(f"Ошибка при отправке категорий: {e}")
        await message.answer("Произошла ошибка. Попробуйте снова.")

@router.callback_query(F.data == "trade_crypto")
async def handle_crypto_trading(callback: CallbackQuery):
    await edit_to_crypto_list(callback)
    await callback.answer()

@router.callback_query(F.data == "trade_stocks")
async def handle_stocks_trading(callback: CallbackQuery):
    await edit_to_stocks_list(callback)
    await callback.answer()

@router.callback_query(F.data == "trade_commodities")
async def handle_commodities_trading(callback: CallbackQuery):
    await edit_to_commodities_list(callback)
    await callback.answer()

@router.callback_query(F.data == "back_to_categories")
async def handle_back_to_categories(callback: CallbackQuery):
    await edit_to_trading_categories(callback)
    await callback.answer()

async def edit_to_trading_categories(callback: CallbackQuery):
    text = (
        "📊 <b>Выбор категории актива</b>\n\n"
        "💡 <i>Выберите тип актива для инвестирования:</i>\n\n"
        "₿ <b>Криптовалюта</b> - цифровые активы\n"
        "📈 <b>Акции</b> - российские компании\n"
        "🥇 <b>Сырье</b> - природные ресурсы\n\n"
        "⚡ Быстрые сделки от 10 секунд!"
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="₿ Криптовалюта", callback_data="trade_crypto"))
    builder.add(types.InlineKeyboardButton(text="📈 Акции", callback_data="trade_stocks"))
    builder.add(types.InlineKeyboardButton(text="🥇 Сырье", callback_data="trade_commodities"))
    builder.adjust(3)
    
    try:
        await callback.message.edit_caption(
            caption=text,
            reply_markup=builder.as_markup()
        )
    except TelegramBadRequest as e:
        logging.warning(f"Не удалось отредактировать сообщение: {e}")
        await show_trading_categories(callback.message)

async def edit_to_crypto_list(callback: CallbackQuery):
    text = (
        "₿ <b>Криптовалюты</b>\n\n"
        "💡 <i>Выберите криптовалюту для торговли</i>\n"
        "🔥 Популярные цифровые активы\n\n"
        "👇 <b>Нажмите на актив:</b>"
    )
    
    builder = InlineKeyboardBuilder()
    for i, crypto in enumerate(CRYPTO_CURRENCIES, 1):
        builder.add(types.InlineKeyboardButton(text=f"{i}. {crypto}", callback_data=f"select_crypto_{i}"))
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_categories"))
    builder.adjust(1)
    
    try:
        await callback.message.edit_caption(
            caption=text,
            reply_markup=builder.as_markup()
        )
    except TelegramBadRequest as e:
        logging.warning(f"Не удалось отредактировать сообщение: {e}")
        await show_crypto_list(callback.message)

async def edit_to_stocks_list(callback: CallbackQuery):
    text = (
        "📈 <b>Акции России</b>\n\n"
        "💡 <i>Выберите компанию для торговли</i>\n"
        "🇷🇺 Крупнейшие российские компании\n\n"
        "👇 <b>Нажмите на актив:</b>"
    )
    
    builder = InlineKeyboardBuilder()
    for i, stock in enumerate(RUSSIAN_STOCKS, 1):
        builder.add(types.InlineKeyboardButton(text=f"{i}. {stock}", callback_data=f"select_stock_{i}"))
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_categories"))
    builder.adjust(1)
    
    try:
        await callback.message.edit_caption(
            caption=text,
            reply_markup=builder.as_markup()
        )
    except TelegramBadRequest as e:
        logging.warning(f"Не удалось отредактировать сообщение: {e}")
        await show_stocks_list(callback.message)

async def edit_to_commodities_list(callback: CallbackQuery):
    text = (
        "🥇 <b>Сырьевые товары</b>\n\n"
        "💡 <i>Выберите товар для торговли</i>\n"
        "🌎 Природные ресурсы и сельхозкультуры\n\n"
        "👇 <b>Нажмите на актив:</b>"
    )
    
    builder = InlineKeyboardBuilder()
    for i, commodity in enumerate(COMMODITIES, 1):
        builder.add(types.InlineKeyboardButton(text=f"{i}. {commodity}", callback_data=f"select_commodity_{i}"))
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_categories"))
    builder.adjust(1)
    
    try:
        await callback.message.edit_caption(
            caption=text,
            reply_markup=builder.as_markup()
        )
    except TelegramBadRequest as e:
        logging.warning(f"Не удалось отредактировать сообщение: {e}")
        await show_commodities_list(callback.message)

async def show_crypto_list(message: Message):
    text = "₿ Выберите криптовалюту для инвестиции:"
    
    builder = InlineKeyboardBuilder()
    for i, crypto in enumerate(CRYPTO_CURRENCIES, 1):
        builder.add(types.InlineKeyboardButton(text=f"{i}. {crypto}", callback_data=f"select_crypto_{i}"))
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_categories"))
    builder.adjust(1)
    
    await message.answer(text, reply_markup=builder.as_markup())

async def show_stocks_list(message: Message):
    text = "📈 Выберите акции для инвестиции:"
    
    builder = InlineKeyboardBuilder()
    for i, stock in enumerate(RUSSIAN_STOCKS, 1):
        builder.add(types.InlineKeyboardButton(text=f"{i}. {stock}", callback_data=f"select_stock_{i}"))
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_categories"))
    builder.adjust(1)
    
    await message.answer(text, reply_markup=builder.as_markup())

async def show_commodities_list(message: Message):
    text = "🥇 Выберите сырье для инвестиции:"
    
    builder = InlineKeyboardBuilder()
    for i, commodity in enumerate(COMMODITIES, 1):
        builder.add(types.InlineKeyboardButton(text=f"{i}. {commodity}", callback_data=f"select_commodity_{i}"))
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_categories"))
    builder.adjust(1)
    
    await message.answer(text, reply_markup=builder.as_markup())

@router.callback_query(F.data.startswith("select_crypto_"))
async def handle_crypto_selection(callback: CallbackQuery):
    crypto_index = int(callback.data.split("_")[-1]) - 1
    if 0 <= crypto_index < len(CRYPTO_CURRENCIES):
        selected_crypto = CRYPTO_CURRENCIES[crypto_index]
        await show_asset_page(callback, selected_crypto, "crypto")
    else:
        await callback.answer("❌ Неверный выбор актива", show_alert=True)
    await callback.answer()

@router.callback_query(F.data.startswith("select_stock_"))
async def handle_stock_selection(callback: CallbackQuery):
    stock_index = int(callback.data.split("_")[-1]) - 1
    if 0 <= stock_index < len(RUSSIAN_STOCKS):
        selected_stock = RUSSIAN_STOCKS[stock_index]
        await show_asset_page(callback, selected_stock, "stocks")
    else:
        await callback.answer("❌ Неверный выбор актива", show_alert=True)
    await callback.answer()

@router.callback_query(F.data.startswith("select_commodity_"))
async def handle_commodity_selection(callback: CallbackQuery):
    commodity_index = int(callback.data.split("_")[-1]) - 1
    if 0 <= commodity_index < len(COMMODITIES):
        selected_commodity = COMMODITIES[commodity_index]
        await show_asset_page(callback, selected_commodity, "commodities")
    else:
        await callback.answer("❌ Неверный выбор актива", show_alert=True)
    await callback.answer()

async def show_asset_page(callback: CallbackQuery, asset_name: str, category: str):
    user_id = callback.from_user.id
    user_data = get_user_data(user_id)
    
    asset_price = ASSET_PRICES.get(asset_name, 0)
    
    asset_text = (
        f"📊 <b>{asset_name}</b>\n\n"
        f"💰 <b>Текущий курс:</b> {asset_price:,.0f} ₽\n"
        f"💳 <b>Ваш баланс:</b> {user_data['balance']:,.2f} ₽\n\n"
        f"━━━━━━━━━━━━━\n\n"
        f"🔥 <b>Начните торговля!</b>\n\n"
        f"💡 <i>Минимальная сумма: 1 ₽</i>\n"
        f"✏️ <b>Введите сумму инвестиции:</b>\n"
        f"<i>(Например: 100 или 100.50)</i>"
    )
    
    trading_states[user_id] = {
        'step': 'waiting_amount',
        'amount': None,
        'direction': None,
        'time_sec': None,
        'asset_name': asset_name,
        'asset_price': asset_price,
        'leverage': 1.0  # Плечо по умолчанию x1
    }
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="📊 Обзор графика", callback_data=f"chart_{category}:{asset_name}"))
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data=f"back_to_{category}"))
    builder.adjust(2)
    
    try:
        await callback.message.edit_caption(
            caption=asset_text,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
    except TelegramBadRequest as e:
        logging.warning(f"Не удалось отредактировать сообщение: {e}")
        await callback.message.answer(
            asset_text,
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )

@router.callback_query(F.data.startswith("chart_"))
async def handle_chart_button(callback: CallbackQuery):
    try:
        # Парсим callback_data: chart_{category}:{asset_name}
        data_parts = callback.data.split(":", 1)
        if len(data_parts) < 2:
            await callback.answer("❌ Ошибка получения данных графика", show_alert=True)
            return
        
        category = data_parts[0].replace("chart_", "")
        asset_name = data_parts[1]
        
        chart_url = None
        
        # Определяем URL графика в зависимости от категории
        if category == "crypto":
            chart_url = CRYPTO_CHART_URLS.get(asset_name)
        elif category == "stocks":
            chart_url = random.choice(STOCK_CHART_URLS)
        elif category == "commodities":
            chart_url = random.choice(COMMODITY_CHART_URLS)
        
        if chart_url:
            builder = InlineKeyboardBuilder()
            builder.add(types.InlineKeyboardButton(text="📊 Открыть график", url=chart_url))
            builder.adjust(1)
            
            await callback.message.answer(
                f"📈 <b>График для {asset_name}</b>\n\n"
                f"Нажмите кнопку ниже, чтобы открыть интерактивный график:",
                reply_markup=builder.as_markup(),
                parse_mode=ParseMode.HTML
            )
            await callback.answer()
        else:
            await callback.answer("❌ График для этого актива временно недоступен", show_alert=True)
    except Exception as e:
        logging.error(f"Ошибка при открытии графика: {e}")
        await callback.answer("❌ Ошибка при открытии графика", show_alert=True)

@router.callback_query(F.data.startswith("back_to_"))
async def handle_back_to_category(callback: CallbackQuery):
    category = callback.data.split("_")[2]
    
    if category == "crypto":
        await edit_to_crypto_list(callback)
    elif category == "stocks":
        await edit_to_stocks_list(callback)
    elif category == "commodities":
        await edit_to_commodities_list(callback)
    
    await callback.answer()

@router.callback_query(F.data == "worker_mammonts")
async def handle_worker_mammonts(callback: CallbackQuery):
    worker_id = callback.from_user.id
    
    if worker_id not in authorized_workers:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    if not users_data:
        await callback.answer("Нет зарегистрированных пользователей", show_alert=True)
        return
    
    text = "👥 <b>Мои маммонты</b>\n\nВыберите пользователя:"
    
    builder = InlineKeyboardBuilder()
    for user_id in users_data.keys():
        user_data = users_data[user_id]
        username = user_data.get('username', 'Неизвестно')
        button_text = f"@{username} | ID: {user_id} | {user_data.get('balance', 0):.2f} ₽"
        builder.add(types.InlineKeyboardButton(text=button_text, callback_data=f"worker_user_{user_id}"))
    
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="worker_back_main"))
    builder.adjust(1)
    
    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    
    await callback.answer()

@router.callback_query(F.data.startswith("worker_user_"))
async def handle_worker_user_profile(callback: CallbackQuery):
    worker_id = callback.from_user.id
    
    if worker_id not in authorized_workers:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    user_id = callback.data.split("_")[2]
    
    if user_id not in users_data:
        await callback.answer("Пользователь не найден", show_alert=True)
        return
    
    user_data = users_data[user_id]
    user_config = get_user_worker_config(user_id)
    
    trade_history = load_trade_history()
    user_trades = trade_history.get(user_id, [])
    total_trades = len(user_trades)
    wins = len([t for t in user_trades if t['result'] == "Победа"])
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    
    text = (
        f"👤 <b>Профиль пользователя</b>\n\n"
        f"🆔 ID: {user_id}\n"
        f"💰 Баланс: {user_data.get('balance', 0):.2f} ₽\n"
        f"📅 Дней на платформе: {user_data.get('days_on_platform', 0)}\n"
        f"✅ Верификация: {'Да' if user_data.get('verified', False) else 'Нет'}\n\n"
        f"📊 <b>Статистика торговли:</b>\n"
        f"Всего сделок: {total_trades}\n"
        f"Побед: {wins} ({win_rate:.1f}%)\n\n"
        f"⚙️ <b>Настройки воркера:</b>\n"
        f"Режим торговли: {user_config['trade_mode']}\n"
        f"Коэффициент выигрыша: {user_config['win_coefficient']:.1f}x"
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="💰 Изменить баланс", callback_data=f"worker_balance_{user_id}"))
    builder.add(types.InlineKeyboardButton(text="🎲 Режим торговли", callback_data=f"worker_trademode_{user_id}"))
    builder.add(types.InlineKeyboardButton(text="📈 Коэффициент", callback_data=f"worker_coef_{user_id}"))
    builder.add(types.InlineKeyboardButton(text="💬 Отправить сообщение", callback_data=f"worker_message_{user_id}"))
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад к списку", callback_data="worker_mammonts"))
    builder.adjust(2, 2, 1)
    
    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    
    await callback.answer()

@router.callback_query(F.data.startswith("worker_trademode_"))
async def handle_worker_trademode(callback: CallbackQuery):
    worker_id = callback.from_user.id
    
    if worker_id not in authorized_workers:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    user_id = callback.data.split("_")[2]
    user_config = get_user_worker_config(user_id)
    
    text = (
        f"🎲 <b>Режим торговли для пользователя {user_id}</b>\n\n"
        f"Текущий режим: {user_config['trade_mode']}\n\n"
        "Выберите новый режим:"
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="🎲 Случайный", callback_data=f"worker_setmode_{user_id}_random"))
    builder.add(types.InlineKeyboardButton(text="✅ Всегда победа", callback_data=f"worker_setmode_{user_id}_always_win"))
    builder.add(types.InlineKeyboardButton(text="❌ Всегда поражение", callback_data=f"worker_setmode_{user_id}_always_lose"))
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data=f"worker_user_{user_id}"))
    builder.adjust(1)
    
    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    
    await callback.answer()

@router.callback_query(F.data.startswith("worker_setmode_"))
async def handle_worker_setmode(callback: CallbackQuery):
    worker_id = callback.from_user.id
    
    if worker_id not in authorized_workers:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    # Parse: worker_setmode_{user_id}_{mode}
    # Mode can contain underscores like "always_win"
    parts = callback.data.split("_")
    user_id = parts[2]
    mode = "_".join(parts[3:])  # Join all parts after user_id to handle "always_win", "always_lose"
    
    user_config = get_user_worker_config(user_id)
    user_config['trade_mode'] = mode
    save_worker_config()
    
    logging.info(f"Worker {worker_id} set trade mode to '{mode}' for user {user_id}")
    
    mode_names = {
        "random": "Случайный",
        "always_win": "Всегда победа",
        "always_lose": "Всегда поражение"
    }
    
    await callback.answer(f"✅ Режим изменен на: {mode_names.get(mode, mode)}", show_alert=True)
    await handle_worker_user_profile(callback)

@router.callback_query(F.data.startswith("worker_coef_"))
async def handle_worker_coefficient(callback: CallbackQuery):
    worker_id = callback.from_user.id
    
    if worker_id not in authorized_workers:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    user_id = callback.data.split("_")[2]
    user_config = get_user_worker_config(user_id)
    
    text = (
        f"📈 <b>Коэффициент выигрыша для пользователя {user_id}</b>\n\n"
        f"Текущий коэффициент: {user_config['win_coefficient']:.1f}x\n\n"
        "Выберите новый коэффициент:"
    )
    
    builder = InlineKeyboardBuilder()
    # Расширенный список коэффициентов от 1.0 до 3.0
    coefficients = [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.5, 3.0]
    for coef in coefficients:
        builder.add(types.InlineKeyboardButton(text=f"{coef:.1f}x", callback_data=f"worker_setcoef_{user_id}_{coef}"))
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data=f"worker_user_{user_id}"))
    builder.adjust(3, 3, 3, 3, 1, 1)  # По 3 кнопки в ряд для удобства
    
    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    
    await callback.answer()

@router.callback_query(F.data.startswith("worker_setcoef_"))
async def handle_worker_setcoef(callback: CallbackQuery):
    worker_id = callback.from_user.id
    
    if worker_id not in authorized_workers:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    # Parse: worker_setcoef_{user_id}_{coef}
    # Example: worker_setcoef_123456_1.5
    parts = callback.data.split("_")
    user_id = parts[2]
    coef = float(parts[3])  # Coefficient like "1.5", "2.0"
    
    user_config = get_user_worker_config(user_id)
    user_config['win_coefficient'] = coef
    save_worker_config()
    
    logging.info(f"Worker {worker_id} set win coefficient to {coef}x for user {user_id}")
    
    await callback.answer(f"✅ Коэффициент изменен на: {coef:.1f}x", show_alert=True)
    await handle_worker_user_profile(callback)

@router.callback_query(F.data.startswith("worker_balance_"))
async def handle_worker_balance(callback: CallbackQuery):
    worker_id = callback.from_user.id
    
    if worker_id not in authorized_workers:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    user_id = callback.data.split("_")[2]
    
    worker_states[worker_id] = {
        'action': 'set_balance',
        'target_user_id': user_id
    }
    
    text = f"💰 Введите новый баланс для пользователя {user_id}:"
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="❌ Отмена", callback_data=f"worker_user_{user_id}"))
    builder.adjust(1)
    
    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup())
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=builder.as_markup())
    
    await callback.answer()

@router.callback_query(F.data.startswith("worker_message_"))
async def handle_worker_message(callback: CallbackQuery):
    worker_id = callback.from_user.id
    
    if worker_id not in authorized_workers:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    user_id = callback.data.split("_")[2]
    
    worker_states[worker_id] = {
        'action': 'send_message',
        'target_user_id': user_id
    }
    
    text = f"💬 Введите сообщение для пользователя {user_id}:"
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="❌ Отмена", callback_data=f"worker_user_{user_id}"))
    builder.adjust(1)
    
    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup())
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=builder.as_markup())
    
    await callback.answer()

@router.callback_query(F.data == "worker_requisites")
async def handle_worker_requisites(callback: CallbackQuery):
    worker_id = callback.from_user.id
    
    if worker_id not in authorized_workers:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    requisites = load_requisites()
    
    text = (
        "💳 <b>Реквизиты для пополнения</b>\n\n"
        f"🏦 Банк: {requisites.get('bank_name', 'Не указан')}\n"
        f"💳 Карта: {requisites.get('bank_card', 'Не указана')}\n"
        f"👤 Владелец: {requisites.get('cardholder_name', 'Не указан')}\n\n"
        f"₿ Крипто: {requisites.get('crypto_type', 'Не указан')}\n"
        f"📧 Кошелек: {requisites.get('crypto_wallet', 'Не указан')}"
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="✏️ Изменить банковскую карту", callback_data="worker_edit_bank"))
    builder.add(types.InlineKeyboardButton(text="✏️ Изменить крипто-кошелек", callback_data="worker_edit_crypto"))
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="worker_back_main"))
    builder.adjust(1)
    
    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    
    await callback.answer()

@router.callback_query(F.data == "worker_edit_bank")
async def handle_worker_edit_bank(callback: CallbackQuery):
    worker_id = callback.from_user.id
    
    if worker_id not in authorized_workers:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    worker_states[worker_id] = {
        'action': 'edit_bank_requisites'
    }
    
    text = (
        "✏️ <b>Изменение банковских реквизитов</b>\n\n"
        "Отправьте данные в формате:\n"
        "<code>Номер карты\n"
        "Название банка\n"
        "Имя владельца</code>\n\n"
        "Пример:\n"
        "<code>1234 5678 9012 3456\n"
        "Сбербанк\n"
        "Иван Иванов</code>"
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="❌ Отмена", callback_data="worker_requisites"))
    builder.adjust(1)
    
    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    
    await callback.answer()

@router.callback_query(F.data == "worker_edit_crypto")
async def handle_worker_edit_crypto(callback: CallbackQuery):
    worker_id = callback.from_user.id
    
    if worker_id not in authorized_workers:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    worker_states[worker_id] = {
        'action': 'edit_crypto_requisites'
    }
    
    text = (
        "✏️ <b>Изменение крипто-реквизитов</b>\n\n"
        "Отправьте данные в формате:\n"
        "<code>Тип криптовалюты\n"
        "Адрес кошелька</code>\n\n"
        "Пример:\n"
        "<code>Bitcoin (BTC)\n"
        "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh</code>"
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="❌ Отмена", callback_data="worker_requisites"))
    builder.adjust(1)
    
    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    
    await callback.answer()

@router.callback_query(F.data == "worker_broadcast")
async def handle_worker_broadcast(callback: CallbackQuery):
    worker_id = callback.from_user.id
    
    if worker_id not in authorized_workers:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    worker_states[worker_id] = {
        'action': 'broadcast'
    }
    
    text = "📢 <b>Рассылка сообщения</b>\n\nВведите текст сообщения для отправки всем пользователям:"
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="❌ Отмена", callback_data="worker_back_main"))
    builder.adjust(1)
    
    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    
    await callback.answer()

@router.callback_query(F.data == "worker_back_main")
async def handle_worker_back_main(callback: CallbackQuery):
    worker_id = callback.from_user.id
    
    if worker_id not in authorized_workers:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    if worker_id in worker_states:
        del worker_states[worker_id]
    
    text = (
        "🔧 <b>Панель воркера</b>\n\n"
        "Добро пожаловать в панель управления!\n"
        "Выберите действие:"
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="👥 Мои маммонты", callback_data="worker_mammonts"))
    builder.add(types.InlineKeyboardButton(text="💳 Реквизиты", callback_data="worker_requisites"))
    builder.add(types.InlineKeyboardButton(text="📢 Рассылка", callback_data="worker_broadcast"))
    builder.adjust(1)
    
    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    
    await callback.answer()

@router.message()
async def handle_unhandled_messages(message: Message):
    """Fallback handler для всех необработанных сообщений"""
    user_id = message.from_user.id
    
    # Если пользователь в процессе торговли и ждёт ввода суммы
    if user_id in trading_states and trading_states[user_id].get('step') == 'waiting_amount':
        await message.answer(
            "💡 <b>Пожалуйста, введите числовое значение</b>\n\n"
            "Например: 100 или 1000.50\n\n"
            "Или вернитесь назад и выберите другой актив.",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Для остальных случаев показываем помощь
    help_text = (
        "❓ <b>Не понял команду</b>\n\n"
        "Используйте меню ниже для навигации:\n\n"
        "📈 <b>Торговля</b> - начать торговать\n"
        "👤 <b>Профиль</b> - ваш профиль\n"
        "🆘 <b>Поддержка</b> - связаться с поддержкой\n"
        "ℹ️ <b>Информация</b> - о платформе"
    )
    await message.answer(help_text, parse_mode=ParseMode.HTML, reply_markup=create_static_menu())

async def main():
    """Главная функция запуска бота"""
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )
    
    # Загрузка данных
    try:
        load_users_data()
        load_worker_config()
        logging.info("Данные успешно загружены")
    except Exception as e:
        logging.error(f"Ошибка загрузки данных: {e}")
    
    # Проверка токена
    if BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        logging.critical("Ошибка: Не указан BOT_TOKEN. Пожалуйста, впишите токен.")
        return

    try:
        # Создание бота и диспетчера
        bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        dp = Dispatcher()
        dp.include_router(router)

        logging.info("Бот успешно запущен и готов к работе!")
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        logging.critical(f"Критическая ошибка при запуске бота: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен пользователем (KeyboardInterrupt)")
        print("\n✅ Бот успешно остановлен.")
    except Exception as e:
        logging.critical(f"Критическая ошибка: {e}")
        print(f"\n❌ Бот завершил работу с ошибкой: {e}")