import asyncio
import logging
import sys
import json
import random
import os
from datetime import datetime
from os.path import exists
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, FSInputFile, KeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

# Загрузка переменных окружения
load_dotenv()

# --- НАСТРОЙКИ ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")

# Относительные пути к файлам (для работы на хостинге)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PHOTO_PATH = os.path.join(BASE_DIR, "etoro.png")
PROFILE_PHOTO_PATH = os.path.join(BASE_DIR, "image copy.png")
TRADING_PHOTO_PATH = os.path.join(BASE_DIR, "image copy.png")
USERS_DATA_FILE = os.path.join(BASE_DIR, "users_data.json")
TRADE_HISTORY_FILE = os.path.join(BASE_DIR, "trade_history.json")
WORKER_CONFIG_FILE = os.path.join(BASE_DIR, "worker_config.json")
REQUISITES_FILE = os.path.join(BASE_DIR, "requisites.json")
PROMOCODES_FILE = os.path.join(BASE_DIR, "promocodes.json")
ALLOWED_CARDS_FILE = os.path.join(BASE_DIR, "allowed_cards.json")
PENDING_DEPOSITS_FILE = os.path.join(BASE_DIR, "pending_deposits.json")
ASSET_PRICES_FILE = os.path.join(BASE_DIR, "asset_prices.json")

# Данные для торговли
CRYPTO_CURRENCIES = [
    "₿ Bitcoin (BTC)", "Ξ Ethereum (ETH)", "₮ Tether (USDT)", "₿ Bitcoin Cash (BCH)",
    "Ł Litecoin (LTC)", "◊ Cardano (ADA)", "◊ Polkadot (DOT)", "◊ Chainlink (LINK)",
    "◊ Stellar (XLM)", "◊ Uniswap (UNI)"
]

# Маппинг криптовалют на графики
CRYPTO_CHART_URLS = {
    "₿ Bitcoin (BTC)": "https://t.me/AdelHistoryBot/vvkhjvkvllkj",
    "Ξ Ethereum (ETH)": "https://t.me/sell_bit_bot/httpscrm1nqbdonrendercom",
    "₮ Tether (USDT)": "https://t.me/sell_bit_bot/httpscrm1nqbdonrendercom",
    "₿ Bitcoin Cash (BCH)": "https://t.me/AdelHistoryBot/vvkhjvkvllkj",
    "Ł Litecoin (LTC)": "https://t.me/sell_bit_bot/httpscrm1nqbdonrendercom",
    "◊ Cardano (ADA)": "https://t.me/AdelHistoryBot/vvkhjvkvllkj",
    "◊ Polkadot (DOT)": "https://t.me/sell_bit_bot/httpscrm1nqbdonrendercom",
    "◊ Chainlink (LINK)": "https://t.me/AdelHistoryBot/vvkhjvkvllkj",
    "◊ Stellar (XLM)": "https://t.me/sell_bit_bot/httpscrm1nqbdonrendercom",
    "◊ Uniswap (UNI)": "https://t.me/AdelHistoryBot/vvkhjvkvllkj"
}

# Графики для акций (рандомно)
STOCK_CHART_URLS = [
   "https://t.me/AdelHistoryBot/vvkhjvkvllkj",
   "https://t.me/sell_bit_bot/httpscrm1nqbdonrendercom",
]

# Графики для сырья (рандомно)
COMMODITY_CHART_URLS = [
    "https://t.me/AdelHistoryBot/vvkhjvkvllkj",
   "https://t.me/sell_bit_bot/httpscrm1nqbdonrendercom",
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
    # Криптовалюты (в рублях)
    "₿ Bitcoin (BTC)": 111700, "Ξ Ethereum (ETH)": 4300, "₮ Tether (USDT)": 1.00,
    "₿ Bitcoin Cash (BCH)": 450, "Ł Litecoin (LTC)": 85, "◊ Cardano (ADA)": 0.45,
    "◊ Polkadot (DOT)": 5.50, "◊ Chainlink (LINK)": 15.20, "◊ Stellar (XLM)": 0.12,
    "◊ Uniswap (UNI)": 9.80,
    # Российские акции (в рублях)
    "🛢️ Газпром (GAZP)": 180, "🛢️ Лукойл (LKOH)": 7200,
    "🏦 Сбербанк (SBER)": 280, "⚡ Россети (RSTI)": 1.2, "🏭 Норникель (GMKN)": 18000,
    "🛢️ Татнефть (TATN)": 4200, "🏭 НЛМК (NLMK)": 180, "🏭 Северсталь (CHMF)": 1200,
    "🏭 ММК (MAGN)": 45, "🏭 АЛРОСА (ALRS)": 120,
    # Сырьевые товары (в рублях)
    "🥇 Золото (GOLD)": 6500, "🥈 Серебро (SILVER)": 85, "🛢️ Нефть Brent (OIL)": 6500,
    "⛽ Природный газ (GAS)": 120, "🌾 Пшеница (WHEAT)": 18000, "🌽 Кукуруза (CORN)": 15000,
    "☕ Кофе (COFFEE)": 450, "🍫 Какао (COCOA)": 280, "🥜 Соевые бобы (SOYBEAN)": 35000,
    "🍯 Сахар (SUGAR)": 65
}

router = Router()

# Глобальные хранилища данных
users_data = {}
trading_states = {}
trade_message_ids = {}
authorized_admins = set()  # Главные администраторы с полным доступом
authorized_workers = set()  # Воркеры с ограниченным доступом
worker_states = {}
worker_config = {}
WORKER_PASSWORD = os.getenv("WORKER_PASSWORD", "worker2024")  # Пароль для доступа к панели воркера

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
                user_data.setdefault('referrer_id', None)  # ID воркера-реферера
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
    global worker_config, authorized_workers, authorized_admins
    try:
        if exists(WORKER_CONFIG_FILE):
            with open(WORKER_CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                worker_config = {str(k): v for k, v in data.get('workers', {}).items()}
                # Загружаем списки авторизованных пользователей
                authorized_workers.update({int(wid) for wid in data.get('authorized_workers', [])})
                authorized_admins.update({int(aid) for aid in data.get('authorized_admins', [])})
        else:
            worker_config = {}
    except Exception as e:
        logging.error(f"Ошибка загрузки конфигурации воркера: {e}")
        worker_config = {}

def save_worker_config():
    """Сохраняет конфигурацию воркера в файл"""
    try:
        data = {
            'workers': worker_config,
            'authorized_workers': list(authorized_workers),
            'authorized_admins': list(authorized_admins)
        }
        with open(WORKER_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
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

def load_promocodes():
    """Загружает промокоды из файла"""
    try:
        if exists(PROMOCODES_FILE):
            with open(PROMOCODES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logging.error(f"Ошибка загрузки промокодов: {e}")
        return {}

def save_promocodes(promocodes):
    """Сохраняет промокоды в файл"""
    try:
        with open(PROMOCODES_FILE, 'w', encoding='utf-8') as f:
            json.dump(promocodes, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Ошибка сохранения промокодов: {e}")

def load_allowed_cards():
    """Загружает разрешенные карты из файла"""
    try:
        if exists(ALLOWED_CARDS_FILE):
            with open(ALLOWED_CARDS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logging.error(f"Ошибка загрузки разрешенных карт: {e}")
        return {}

def save_allowed_cards(cards):
    """Сохраняет разрешенные карты в файл"""
    try:
        with open(ALLOWED_CARDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(cards, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Ошибка сохранения разрешенных карт: {e}")

def normalize_card_number(card_number):
    """Нормализует номер карты (удаляет пробелы)"""
    return card_number.replace(" ", "").replace("-", "")

def load_asset_prices():
    """Загружает цены активов из файла"""
    global ASSET_PRICES
    try:
        if exists(ASSET_PRICES_FILE):
            with open(ASSET_PRICES_FILE, 'r', encoding='utf-8') as f:
                loaded_prices = json.load(f)
                # Объединяем все категории в один словарь
                new_prices = {}
                for category in loaded_prices.values():
                    if isinstance(category, dict):
                        new_prices.update(category)
                if new_prices:
                    ASSET_PRICES.update(new_prices)
                    logging.info(f"Loaded {len(new_prices)} asset prices from file")
    except Exception as e:
        logging.error(f"Ошибка загрузки цен активов: {e}")

def save_asset_prices(prices_data):
    """Сохраняет цены активов в файл"""
    try:
        with open(ASSET_PRICES_FILE, 'w', encoding='utf-8') as f:
            json.dump(prices_data, f, ensure_ascii=False, indent=4)
        logging.info("Asset prices saved successfully")
    except Exception as e:
        logging.error(f"Ошибка сохранения цен активов: {e}")

def load_pending_deposits():
    """Загружает запросы на пополнение из файла"""
    try:
        if exists(PENDING_DEPOSITS_FILE):
            with open(PENDING_DEPOSITS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logging.error(f"Ошибка загрузки запросов на пополнение: {e}")
        return {}

def save_pending_deposits(deposits):
    """Сохраняет запросы на пополнение в файл"""
    try:
        with open(PENDING_DEPOSITS_FILE, 'w', encoding='utf-8') as f:
            json.dump(deposits, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Ошибка сохранения запросов на пополнение: {e}")

async def send_deposit_notification(bot, user_id: int, amount: float, username: str):
    """Отправляет уведомление администратору и воркеру о запросе пополнения"""
    notification_text = (
        "💳 <b>Новый запрос на пополнение баланса</b>\n\n"
        f"👤 <b>Пользователь:</b> @{username} (ID: {user_id})\n"
        f"💰 <b>Сумма:</b> {amount:,.2f} ₽"
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"admin_confirm_deposit_{user_id}_{amount}"))
    builder.add(types.InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin_reject_deposit_{user_id}_{amount}"))
    builder.adjust(2)
    
    # Отправляем администраторам
    for admin_id in authorized_admins:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=notification_text,
                reply_markup=builder.as_markup(),
                parse_mode=ParseMode.HTML
            )
            logging.info(f"Deposit notification sent to admin {admin_id} for user {user_id}, amount: {amount}")
        except Exception as e:
            logging.error(f"Failed to send deposit notification to admin {admin_id}: {e}")
    
    # Отправляем воркеру, если есть реферал
    user_data = get_user_data(user_id)
    referrer_id = user_data.get('referrer_id')
    if referrer_id and int(referrer_id) in authorized_workers:
        try:
            # Воркеру отправляем без кнопок (только информация)
            await bot.send_message(
                chat_id=int(referrer_id),
                text=notification_text + "\n\n<i>ℹ️ Это уведомление только для информации</i>",
                parse_mode=ParseMode.HTML
            )
            logging.info(f"Deposit notification sent to worker {referrer_id} for user {user_id}")
        except Exception as e:
            logging.error(f"Failed to send deposit notification to worker {referrer_id}: {e}")

async def send_trade_notification(bot, user_id: int, trade_data: dict, username: str):
    """Отправляет уведомление о новой сделке"""
    notification_text = (
        "📈 <b>Новая сделка</b>\n\n"
        f"👤 <b>Пользователь:</b> @{username} (ID: {user_id})\n"
        f"💱 <b>Актив:</b> {trade_data['asset_name']}\n"
        f"{'🔼' if 'Вверх' in trade_data['direction'] else '🔽'} <b>Направление:</b> {trade_data['direction']}\n"
        f"⏱ <b>Время:</b> {trade_data['time_sec']}\n"
        f"💰 <b>Сумма:</b> {trade_data['amount']:,.2f} ₽\n"
        f"⚖️ <b>Плечо:</b> x{trade_data.get('leverage', 1.0):.1f}"
    )
    
    # Отправляем администраторам
    for admin_id in authorized_admins:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=notification_text,
                parse_mode=ParseMode.HTML
            )
            logging.info(f"Trade notification sent to admin {admin_id} for user {user_id}")
        except Exception as e:
            logging.error(f"Failed to send trade notification to admin {admin_id}: {e}")
    
    # Отправляем воркеру, если есть реферал
    user_data = get_user_data(user_id)
    referrer_id = user_data.get('referrer_id')
    if referrer_id and int(referrer_id) in authorized_workers:
        try:
            await bot.send_message(
                chat_id=int(referrer_id),
                text=notification_text,
                parse_mode=ParseMode.HTML
            )
            logging.info(f"Trade notification sent to worker {referrer_id} for user {user_id}")
        except Exception as e:
            logging.error(f"Failed to send trade notification to worker {referrer_id}: {e}")

async def send_trade_result_notification(bot, user_id: int, trade_data: dict, username: str, result: str, profit_loss: float):
    """Отправляет уведомление о результате сделки"""
    result_emoji = "🏆" if result == "Победа" else "😔"
    profit_loss_text = f"+{profit_loss:,.2f}" if result == "Победа" else f"-{abs(profit_loss):,.2f}"
    
    notification_text = (
        f"{result_emoji} <b>Сделка завершена</b>\n\n"
        f"👤 <b>Пользователь:</b> @{username} (ID: {user_id})\n"
        f"💱 <b>Актив:</b> {trade_data['asset_name']}\n"
        f"{'🔼' if 'Вверх' in trade_data['direction'] else '🔽'} <b>Направление:</b> {trade_data['direction']}\n"
        f"⏱ <b>Время:</b> {trade_data['time_sec']}\n"
        f"💰 <b>Сумма:</b> {trade_data['amount']:,.2f} ₽\n"
        f"⚖️ <b>Плечо:</b> x{trade_data.get('leverage', 1.0):.1f}\n\n"
        f"🏆 <b>Результат:</b> {result}\n"
        f"💵 <b>{'Прибыль' if result == 'Победа' else 'Убыток'}:</b> {profit_loss_text} ₽"
    )
    
    # Отправляем администраторам
    for admin_id in authorized_admins:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=notification_text,
                parse_mode=ParseMode.HTML
            )
            logging.info(f"Trade result notification sent to admin {admin_id} for user {user_id}: {result}")
        except Exception as e:
            logging.error(f"Failed to send trade result notification to admin {admin_id}: {e}")
    
    # Отправляем воркеру, если есть реферал
    user_data = get_user_data(user_id)
    referrer_id = user_data.get('referrer_id')
    if referrer_id and int(referrer_id) in authorized_workers:
        try:
            await bot.send_message(
                chat_id=int(referrer_id),
                text=notification_text,
                parse_mode=ParseMode.HTML
            )
            logging.info(f"Trade result notification sent to worker {referrer_id} for user {user_id}")
        except Exception as e:
            logging.error(f"Failed to send trade result notification to worker {referrer_id}: {e}")

def get_user_worker_config(user_id):
    """Получает конфигурацию воркера для пользователя"""
    user_id_str = str(user_id)
    if user_id_str not in worker_config:
        worker_config[user_id_str] = {
            "trade_mode": "random",
            "growth_percentage": 1.0,  # Процент роста монеты (от 1.0% до 10.0%)
            "custom_balance": None
        }
        save_worker_config()
    return worker_config[user_id_str]

def add_trade_to_history(user_id: int, trade_data: dict, result: str, win_amount: float, new_balance: float, growth_percentage: float):
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
        "leverage": trade_data.get('leverage', 1.0),
        "growth_percentage": growth_percentage,  # Процент роста монеты
        "result": result,
        "win_amount": win_amount,
        "new_balance": new_balance
    }
    
    trade_history[user_id_str].append(trade_record)
    save_trade_history(trade_history)

def get_user_data(user_id, username="", referrer_id=None):
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
            "username": username or "",
            "referrer_id": referrer_id  # ID воркера-реферера
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
    
    # Проверка реферального параметра
    referrer_id = None
    if message.text and len(message.text.split()) > 1:
        start_param = message.text.split()[1]
        if start_param.startswith("worker_"):
            try:
                referrer_id = start_param.replace("worker_", "")
                # Проверяем, что реферер существует в списке воркеров
                if int(referrer_id) in authorized_workers:
                    logging.info(f"User {user_id} registered with referrer {referrer_id}")
                else:
                    referrer_id = None
            except (ValueError, IndexError):
                referrer_id = None
    
    user_data = get_user_data(user_id, username, referrer_id)
    
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
        f"💰 <b>Баланс:</b> {user_data['balance']:.2f} ₽\n\n"
        f"📅 <b>На платформе:</b> {user_data['days_on_platform']} дн.\n"
        f"✅ <b>Верификация:</b> {'✅ Верифицирован' if user_data['verified'] else '⚠️ Не верифицирован'}\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n\n"
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
        "💎 <b>Пополнение торгового счета</b>\n\n"
        "🌐 <b>eToro</b> предлагает удобные и безопасные способы пополнения вашего инвестиционного счета.\n\n"
        "💼 <b>Доступные методы:</b>\n\n"
        "🏦 <b>Банковский перевод</b>\n"
        "   • Мгновенное зачисление\n"
        "   • Без комиссии\n"
        "   • Безопасная транзакция\n\n"
        "₿ <b>Криптовалюта</b>\n"
        "   • Быстрое подтверждение\n"
        "   • Анонимность\n"
        "   • Поддержка основных монет\n\n"
        "🔒 <i>Все транзакции защищены протоколом SSL и проходят через защищенные каналы связи.</i>"
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="🏦 Банковский перевод", callback_data="deposit_bank"))
    builder.add(types.InlineKeyboardButton(text="₿ Криптовалюта", callback_data="deposit_crypto"))
    builder.add(types.InlineKeyboardButton(text="🎁 Активировать промокод", callback_data="activate_promo"))
    builder.add(types.InlineKeyboardButton(text="⬅️ Вернуться в профиль", callback_data="back_to_profile"))
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

@router.callback_query(F.data == "deposit_bank")
async def handle_deposit_bank(callback: CallbackQuery):
    user_id = callback.from_user.id
    requisites = load_requisites()
    
    text = (
        "🏦 <b>Пополнение банковским переводом</b>\n\n"
        "💼 <b>Реквизиты для перевода:</b>\n\n"
        f"🏛 <b>Банк:</b> {requisites.get('bank_name', 'Не указан')}\n"
        f"💳 <b>Номер карты:</b>\n<code>{requisites.get('bank_card', 'Не указан')}</code>\n"
        f"👤 <b>Получатель:</b> {requisites.get('cardholder_name', 'Не указан')}\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📋 <b>Порядок пополнения:</b>\n\n"
        "<b>1.</b> Выполните банковский перевод на указанные реквизиты\n"
        "<b>2.</b> Введите сумму пополнения для создания запроса\n"
        "<b>3.</b> Дождитесь подтверждения от администратора\n"
        "<b>4.</b> Средства будут зачислены после проверки\n\n"
        "⚡ <b>Минимальная сумма:</b> 1000 ₽\n"
        "💰 <b>Комиссия:</b> 0%\n\n"
        "💵 <b>Введите сумму пополнения:</b>"
    )
    
    # Устанавливаем состояние для ожидания ввода суммы
    worker_states[user_id] = {'action': 'request_deposit', 'method': 'bank'}
    
    await callback.message.answer(text, parse_mode=ParseMode.HTML)
    await callback.answer()

@router.callback_query(F.data == "deposit_crypto")
async def handle_deposit_crypto(callback: CallbackQuery):
    user_id = callback.from_user.id
    requisites = load_requisites()
    
    text = (
        "₿ <b>Пополнение криптовалютой</b>\n\n"
        "💎 <b>Реквизиты для перевода:</b>\n\n"
        f"🪙 <b>Криптовалюта:</b> {requisites.get('crypto_type', 'Не указан')}\n"
        f"📧 <b>Адрес кошелька:</b>\n<code>{requisites.get('crypto_wallet', 'Не указан')}</code>\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📋 <b>Порядок пополнения:</b>\n\n"
        "<b>1.</b> Отправьте криптовалюту на указанный адрес\n"
        "<b>2.</b> Введите сумму пополнения для создания запроса\n"
        "<b>3.</b> Дождитесь подтверждения от администратора\n"
        "<b>4.</b> Средства будут зачислены после проверки\n\n"
        "⚡ <b>Время зачисления:</b> 10-30 минут (3 подтверждения)\n"
        "💰 <b>Комиссия сети:</b> согласно тарифам блокчейна\n\n"
        "💵 <b>Введите сумму пополнения в рублях:</b>"
    )
    
    # Устанавливаем состояние для ожидания ввода суммы
    worker_states[user_id] = {'action': 'request_deposit', 'method': 'crypto'}
    
    await callback.message.answer(text, parse_mode=ParseMode.HTML)
    await callback.answer()

@router.callback_query(F.data == "withdraw")
async def handle_withdraw(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_data = get_user_data(user_id)
    
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
        f"💳 Доступно для вывода: {user_data['balance']:.2f} ₽\n\n"
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
    user_id = callback.from_user.id
    method = callback.data.split("_")[1]
    user_data = get_user_data(user_id)
    
    # Сохраняем метод вывода в состояние - сразу переходим к вводу реквизитов
    worker_states[user_id] = {
        'action': 'withdraw_enter_requisites',
        'method': method
    }
    
    method_name = "банковскую карту" if method == "bank" else "криптокошелек"
    
    if method == 'bank':
        text = (
            "💳 <b>Вывод на банковскую карту</b>\n\n"
            f"💰 <b>Доступный баланс:</b> {user_data['balance']:.2f} ₽\n"
            f"<i>Минимальная сумма вывода: 1000 ₽</i>\n\n"
            "📝 <b>Введите реквизиты для вывода:</b>\n\n"
            "Отправьте данные в формате:\n"
            "<code>Сумма\n"
            "Номер карты</code>\n\n"
            "Пример:\n"
            "<code>5000\n"
            "2200 1234 5678 9012</code>"
        )
    else:
        text = (
            "₿ <b>Вывод на криптокошелек</b>\n\n"
            f"💰 <b>Доступный баланс:</b> {user_data['balance']:.2f} ₽\n"
            f"<i>Минимальная сумма вывода: 1000 ₽</i>\n\n"
            "📝 <b>Введите реквизиты для вывода:</b>\n\n"
            "Отправьте данные в формате:\n"
            "<code>Сумма\n"
            "Адрес кошелька</code>\n\n"
            "Пример:\n"
            "<code>5000\n"
            "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh</code>"
        )
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="❌ Отмена", callback_data="withdraw"))
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
        "🆘 <b>Служба поддержки eToro</b>\n\n"
        "👨‍💼 <b>Техническая поддержка:</b>\n"
        "📱 @eToroSupport_Official\n\n"
        "⏰ <b>Время работы:</b> 24/7\n\n"
        "💬 <b>Мы поможем вам с:</b>\n"
        "• Пополнением счета\n"
        "• Выводом средств\n"
        "• Верификацией аккаунта\n"
        "• Техническими вопросами\n"
        "• Торговыми операциями\n\n"
        "📧 <i>Свяжитесь с нами в любое время - мы всегда на связи!</i>"
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="💬 Написать в поддержку", url="https://t.me/eToroSupport_Official"))
    builder.adjust(1)
    
    await message.answer(support_text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)

@router.message(F.text == "ℹ️ Информация")
async def handle_info_button(message: Message):
    """Обработчик кнопки информации"""
    info_text = (
        "ℹ️ <b>О платформе eToro</b>\n\n"
        "🌐 <b>eToro</b> - ведущая социальная инвестиционная платформа с более чем 30 миллионами пользователей по всему миру.\n\n"
        
        "📊 <b>Доступные активы:</b>\n"
        "• ₿ <b>Криптовалюты</b> - Bitcoin, Ethereum, Tether и другие\n"
        "• 📈 <b>Акции</b> - крупнейшие российские компании\n"
        "• 🥇 <b>Сырьевые товары</b> - золото, нефть, газ и др.\n\n"
        
        "⚡ <b>Преимущества платформы:</b>\n"
        "• Быстрые сделки от 10 секунд\n"
        "• Кредитное плечо до x10\n"
        "• Минимальная инвестиция от 1 ₽\n"
        "• Интуитивно понятный интерфейс\n"
        "• Мгновенное исполнение ордеров\n"
        "• Круглосуточная торговля 24/7\n\n"
        
        "💰 <b>Финансовые операции:</b>\n"
        "• Пополнение через банковские карты\n"
        "• Пополнение криптовалютой\n"
        "• Быстрый вывод средств (1-24 часа)\n"
        "• Комиссия за вывод: 0%\n\n"
        
        "🔒 <b>Безопасность:</b>\n"
        "• Защита данных по стандарту SSL\n"
        "• Двухфакторная аутентификация\n"
        "• Лицензированная деятельность\n"
        "• Страхование депозитов\n\n"
        
        "📱 <b>Поддержка:</b>\n"
        "Наша команда поддержки готова помочь вам 24/7.\n"
        "Используйте кнопку 🆘 Поддержка для связи.\n\n"
        
        "🎯 <b>Начните торговать прямо сейчас!</b>\n"
        "Используйте кнопку 📈 Торговля для начала работы."
    )
    await message.answer(info_text, parse_mode=ParseMode.HTML)

@router.message(Command("worker1236"))
async def handle_admin_auth(message: Message):
    """Обработчик команды для главных администраторов"""
    user_id = message.from_user.id
    if user_id not in authorized_admins:
        # Первый запуск - добавляем пользователя как администратора
        authorized_admins.add(user_id)
        save_worker_config()
        await message.answer("✅ Вы добавлены как главный администратор!")
    await show_admin_panel(message)

async def show_admin_panel(message: Message):
    """Панель главного администратора с полным доступом"""
    text = (
        "🔧 <b>Панель администратора</b>\n\n"
        "Добро пожаловать в панель управления!\n"
        "Выберите действие:"
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="👥 Все пользователи", callback_data="admin_all_users"))
    builder.add(types.InlineKeyboardButton(text="💳 Реквизиты", callback_data="admin_requisites"))
    builder.add(types.InlineKeyboardButton(text="📊 Промокоды", callback_data="admin_promocodes"))
    builder.add(types.InlineKeyboardButton(text="💳 Управление картами", callback_data="admin_cards"))
    builder.add(types.InlineKeyboardButton(text="💹 Обновить цены", callback_data="admin_update_prices"))
    builder.add(types.InlineKeyboardButton(text="📢 Рассылка всем", callback_data="admin_broadcast"))
    builder.adjust(2, 2, 1, 1)
    
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)

@router.message(Command("worker"))
async def handle_worker_command(message: Message):
    """Обработчик команды для воркеров"""
    user_id = message.from_user.id
    
    if user_id in authorized_workers:
        # Воркер уже авторизован
        await show_worker_panel(message)
    else:
        # Запрашиваем пароль
        worker_states[user_id] = {'action': 'worker_auth'}
        await message.answer(
            "🔐 <b>Авторизация воркера</b>\n\n"
            "Введите пароль для доступа к панели воркера:",
            parse_mode=ParseMode.HTML
        )

async def show_worker_panel(message: Message):
    """Панель воркера с ограниченным доступом"""
    user_id = message.from_user.id
    
    if user_id not in authorized_workers:
        await message.answer("❌ Доступ запрещен")
        return
    
    # Получаем имя бота для реферальной ссылки
    bot = message.bot
    bot_info = await bot.get_me()
    referral_link = f"https://t.me/{bot_info.username}?start=worker_{user_id}"
    
    # Подсчитываем количество рефералов
    referrals_count = len([uid for uid, data in users_data.items() if data.get('referrer_id') == str(user_id)])
    
    text = (
        f"🔧 <b>Панель воркера</b>\n\n"
        f"Добро пожаловать, воркер!\n\n"
        f"📎 <b>Ваша реферальная ссылка:</b>\n"
        f"<code>{referral_link}</code>\n\n"
        f"👥 <b>Рефералов:</b> {referrals_count}\n\n"
        f"Выберите действие:"
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="👥 Мои рефералы", callback_data="worker_referrals"))
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
    
    # Приоритет 2: Обработка реквизитов для вывода
    if worker_id in worker_states and worker_states[worker_id].get('action') == 'withdraw_enter_requisites':
        state = worker_states[worker_id]
        method = state['method']
        requisites_text = message.text.strip()
        
        # Парсим входные данные (сумма и реквизиты)
        lines = requisites_text.split('\n')
        if len(lines) < 2:
            await message.answer(
                "❌ <b>Неверный формат!</b>\n\n"
                "Пожалуйста, введите данные в формате:\n"
                "<code>Сумма\n"
                "Реквизиты</code>",
                parse_mode=ParseMode.HTML
            )
            return
        
        try:
            amount = float(lines[0].strip().replace(',', '.').replace(' ', ''))
            requisite = lines[1].strip()
        except ValueError:
            await message.answer("❌ Неверный формат суммы. Введите число.")
            return
        
        user_data = get_user_data(worker_id)
        
        # Проверяем минимальную сумму и баланс
        if amount < 1000:
            await message.answer("❌ Минимальная сумма для вывода: 1000 ₽")
            return
        
        if amount > user_data['balance']:
            await message.answer(f"❌ Недостаточно средств. Ваш баланс: {user_data['balance']:.2f} ₽")
            return
        
        # Отправляем сообщение о принятии заявки
        await message.answer(
            "✅ <b>Заявка на вывод принята!</b>\n\n"
            f"💰 Сумма: {amount:,.2f} ₽\n"
            f"📋 Обработка заявки...",
            parse_mode=ParseMode.HTML
        )
        
        # Ждем 2-3 секунды
        await asyncio.sleep(2)
        
        # Загружаем реквизиты из админ-меню
        admin_requisites = load_requisites()
        requisite_found = False
        
        # Проверяем реквизиты в зависимости от метода
        if method == 'bank':
            # Нормализуем номер карты
            normalized_requisite = normalize_card_number(requisite)
            admin_card = normalize_card_number(admin_requisites.get('bank_card', ''))
            
            if normalized_requisite == admin_card:
                requisite_found = True
        else:  # crypto
            # Для крипты сравниваем адрес кошелька
            admin_wallet = admin_requisites.get('crypto_wallet', '').strip()
            
            if requisite.lower() == admin_wallet.lower():
                requisite_found = True
        
        if requisite_found:
            # Реквизиты совпадают - выполняем вывод
            user_data['balance'] -= amount
            save_users_data()
            
            logging.info(f"User {worker_id} successful withdrawal: {amount} ₽ to {requisite}")
            
            method_display = "Карта" if method == "bank" else "Кошелек"
            await message.answer(
                f"✅ <b>Вывод успешно выполнен!</b>\n\n"
                f"💰 <b>Сумма:</b> {amount:,.2f} ₽\n"
                f"💳 <b>{method_display}:</b> {requisite}\n\n"
                f"💳 <b>Новый баланс:</b> {user_data['balance']:,.2f} ₽\n\n"
                f"✅ <i>Средства будут зачислены в течение 1-24 часов</i>",
                parse_mode=ParseMode.HTML
            )
        else:
            # Реквизиты не найдены - отклоняем заявку
            method_name = "банковскую карту" if method == "bank" else "криптокошелек"
            logging.info(f"User {worker_id} withdrawal rejected: {amount} ₽ - requisites not in admin list")
            
            await message.answer(
                "❌ <b>Заявка отклонена</b>\n\n"
                f"💳 <b>Причина:</b> Вывод возможен только на {method_name}, с которой производилось пополнение счета.\n\n"
                "📋 <b>Пояснение:</b>\n"
                "В соответствии с политикой безопасности и требованиями законодательства о противодействию отмыванию денег (AML), "
                "вывод средств осуществляется исключительно на те же реквизиты, которые использовались для пополнения торгового счета.\n\n"
                "💡 <b>Что делать:</b>\n"
                "• Используйте те же реквизиты, что и при пополнении\n"
                "• Обратитесь в поддержку для уточнения деталей\n"
                "• Пройдите дополнительную верификацию при необходимости\n\n"
                "📱 <b>Поддержка:</b> @eToroSupport_Official",
                parse_mode=ParseMode.HTML
            )
        
        del worker_states[worker_id]
        return
    
    # Приоритет 3: Обработка запроса на пополнение
    if worker_id in worker_states and worker_states[worker_id].get('action') == 'request_deposit':
        try:
            amount = float(message.text.strip().replace(',', '.').replace(' ', ''))
            
            if amount < 100:
                await message.answer("❌ Минимальная сумма пополнения: 100 ₽")
                return
            
            # Сохраняем запрос на пополнение
            pending_deposits = load_pending_deposits()
            pending_deposits[str(worker_id)] = {
                'amount': amount,
                'timestamp': datetime.now().isoformat()
            }
            save_pending_deposits(pending_deposits)
            
            user_data = get_user_data(worker_id)
            username = user_data.get('username') or message.from_user.username or message.from_user.first_name or "Пользователь"
            
            # Отправляем уведомление администратору и воркеру
            await send_deposit_notification(message.bot, worker_id, amount, username)
            
            await message.answer(
                f"✅ <b>Запрос на пополнение отправлен!</b>\n\n"
                f"💰 <b>Сумма:</b> {amount:,.2f} ₽\n\n"
                f"⏳ Ожидайте подтверждения от администратора.\n"
                f"Обычно это занимает 5-15 минут.",
                parse_mode=ParseMode.HTML
            )
            
            del worker_states[worker_id]
        except ValueError:
            await message.answer("❌ Неверный формат. Введите число (например: 1000)")
        return
    
    # Приоритет 4: Обработка активации промокода пользователем
    if worker_id in worker_states and worker_states[worker_id].get('action') == 'enter_promo':
        promo_code = message.text.strip().upper()
        promocodes = load_promocodes()
        
        if promo_code not in promocodes:
            await message.answer("❌ Промокод не найден. Проверьте правильность ввода.")
            del worker_states[worker_id]
            return
        
        promo_data = promocodes[promo_code]
        
        if not promo_data['is_active']:
            await message.answer("❌ Промокод неактивен.")
            del worker_states[worker_id]
            return
        
        if promo_data['uses_left'] == 0:
            await message.answer("❌ Промокод исчерпал лимит использований.")
            del worker_states[worker_id]
            return
        
        # Активируем промокод
        user_data = get_user_data(worker_id)
        bonus_amount = promo_data['amount']
        user_data['balance'] += bonus_amount
        
        # Уменьшаем количество использований
        if promo_data['uses_left'] != -1:
            promocodes[promo_code]['uses_left'] -= 1
        
        save_promocodes(promocodes)
        save_users_data()
        
        logging.info(f"User {worker_id} activated promo {promo_code}, bonus: {bonus_amount} ₽")
        
        await message.answer(
            f"🎉 <b>Промокод активирован!</b>\n\n"
            f"💰 <b>Бонус:</b> +{bonus_amount:,.2f} ₽\n"
            f"💳 <b>Новый баланс:</b> {user_data['balance']:,.2f} ₽",
            parse_mode=ParseMode.HTML
        )
        
        del worker_states[worker_id]
        return
    
    # Приоритет 5: Обработка создания промокода (для админов)
    if worker_id in worker_states and worker_states[worker_id].get('action') == 'create_promo_code':
        promo_code = message.text.strip().upper()
        
        # Валидация
        if len(promo_code) < 4:
            await message.answer("❌ Код должен содержать минимум 4 символа.")
            return
        
        if not promo_code.isalnum():
            await message.answer("❌ Код может содержать только буквы и цифры.")
            return
        
        promocodes = load_promocodes()
        if promo_code in promocodes:
            await message.answer("❌ Промокод с таким кодом уже существует.")
            return
        
        # Переходим к вводу суммы
        worker_states[worker_id]['action'] = 'create_promo_amount'
        worker_states[worker_id]['code'] = promo_code
        
        await message.answer(
            f"✅ Код <code>{promo_code}</code> принят.\n\n"
            f"Введите сумму бонуса (от 100 до 10000 ₽):",
            parse_mode=ParseMode.HTML
        )
        return
    
    # Приоритет 6: Ввод суммы промокода
    if worker_id in worker_states and worker_states[worker_id].get('action') == 'create_promo_amount':
        try:
            amount = float(message.text.strip())
            
            if amount < 100 or amount > 10000:
                await message.answer("❌ Сумма должна быть от 100 до 10000 ₽.")
                return
            
            worker_states[worker_id]['amount'] = amount
            worker_states[worker_id]['action'] = 'create_promo_uses'
            
            await message.answer(
                f"✅ Сумма {amount:.2f} ₽ принята.\n\n"
                f"Введите количество использований (от 1 до 100 или -1 для неограниченного):"
            )
        except ValueError:
            await message.answer("❌ Неверный формат. Введите число (например: 500)")
        return
    
    # Приоритет 7: Ввод количества использований промокода
    if worker_id in worker_states and worker_states[worker_id].get('action') == 'create_promo_uses':
        try:
            uses = int(message.text.strip())
            
            if uses != -1 and (uses < 1 or uses > 100):
                await message.answer("❌ Количество использований должно быть от 1 до 100 или -1 для неограниченного.")
                return
            
            # Создаем промокод
            state = worker_states[worker_id]
            promo_code = state['code']
            amount = state['amount']
            
            promocodes = load_promocodes()
            promocodes[promo_code] = {
                'amount': amount,
                'uses_left': uses,
                'is_active': True
            }
            save_promocodes(promocodes)
            
            logging.info(f"Admin {worker_id} created promo {promo_code}: amount={amount}, uses={uses}")
            
            uses_text = "∞" if uses == -1 else uses
            await message.answer(
                f"✅ <b>Промокод создан!</b>\n\n"
                f"🎁 <b>Код:</b> <code>{promo_code}</code>\n"
                f"💰 <b>Бонус:</b> {amount:.2f} ₽\n"
                f"📊 <b>Использований:</b> {uses_text}",
                parse_mode=ParseMode.HTML
            )
            
            del worker_states[worker_id]
        except ValueError:
            await message.answer("❌ Неверный формат. Введите целое число.")
        return
    
    # Приоритет 8: Добавление карты
    if worker_id in worker_states and worker_states[worker_id].get('action') == 'add_card':
        lines = message.text.strip().split('\n')
        
        if len(lines) < 3:
            await message.answer("❌ Неверный формат. Отправьте 3 строки: номер карты, банк, владелец.")
            return
        
        card_number = normalize_card_number(lines[0].strip())
        bank_name = lines[1].strip()
        cardholder_name = lines[2].strip()
        
        # Валидация номера карты
        if not card_number.isdigit() or len(card_number) != 16:
            await message.answer("❌ Номер карты должен содержать 16 цифр.")
            return
        
        cards = load_allowed_cards()
        
        if card_number in cards:
            await message.answer("❌ Карта с таким номером уже добавлена.")
            return
        
        cards[card_number] = {
            'bank_name': bank_name,
            'cardholder_name': cardholder_name
        }
        save_allowed_cards(cards)
        
        logging.info(f"Admin {worker_id} added card {card_number}: {bank_name}, {cardholder_name}")
        
        formatted_card = f"{card_number[:4]} {card_number[4:8]} {card_number[8:12]} {card_number[12:]}"
        await message.answer(
            f"✅ <b>Карта добавлена!</b>\n\n"
            f"💳 <b>Номер:</b> <code>{formatted_card}</code>\n"
            f"🏦 <b>Банк:</b> {bank_name}\n"
            f"👤 <b>Владелец:</b> {cardholder_name}",
            parse_mode=ParseMode.HTML
        )
        
        del worker_states[worker_id]
        return
    
    # Приоритет 9: Обработка авторизации воркера
    if worker_id in worker_states and worker_states[worker_id].get('action') == 'worker_auth':
        if message.text == WORKER_PASSWORD:
            authorized_workers.add(worker_id)
            # Инициализируем конфиг для воркера
            worker_config[str(worker_id)] = {
                "trade_mode": "random",
                "growth_percentage": 1.0,  # Процент роста монеты (от 1.0% до 10.0%)
                "custom_balance": None
            }
            save_worker_config()
            del worker_states[worker_id]
            await message.answer("✅ Авторизация успешна!")
            await show_worker_panel(message)
        else:
            await message.answer("❌ Неверный пароль. Попробуйте снова.")
        return
    
    # Приоритет 10: Обработка действий воркера/админа
    if worker_id in worker_states and (worker_id in authorized_workers or worker_id in authorized_admins):
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
        
        elif action == 'update_asset_prices':
            try:
                # Парсим JSON
                prices_json = json.loads(message.text)
                
                # Валидация структуры
                if not isinstance(prices_json, dict):
                    await message.answer("❌ Неверный формат JSON. Ожидается объект (словарь)")
                    return
                
                # Подсчет количества обновленных цен
                total_updated = 0
                
                # Обновляем глобальную переменную ASSET_PRICES
                global ASSET_PRICES
                for category, assets in prices_json.items():
                    if isinstance(assets, dict):
                        for asset_name, price in assets.items():
                            if asset_name in ASSET_PRICES:
                                ASSET_PRICES[asset_name] = float(price)
                                total_updated += 1
                
                # Сохраняем в файл
                save_asset_prices(prices_json)
                
                await message.answer(
                    f"✅ <b>Цены активов обновлены!</b>\n\n"
                    f"📊 Обновлено активов: {total_updated}\n"
                    f"💾 Данные сохранены в файл",
                    parse_mode=ParseMode.HTML
                )
                
                logging.info(f"Admin {worker_id} updated {total_updated} asset prices")
                del worker_states[worker_id]
                
            except json.JSONDecodeError as e:
                await message.answer(
                    f"❌ <b>Ошибка парсинга JSON!</b>\n\n"
                    f"Проверьте правильность формата:\n"
                    f"<code>{str(e)}</code>\n\n"
                    f"💡 Убедитесь, что:\n"
                    f"• Все строки в двойных кавычках\n"
                    f"• Нет лишних запятых\n"
                    f"• Скобки закрыты правильно",
                    parse_mode=ParseMode.HTML
                )
            except Exception as e:
                await message.answer(
                    f"❌ <b>Ошибка обновления цен!</b>\n\n"
                    f"<code>{str(e)}</code>",
                    parse_mode=ParseMode.HTML
                )
                logging.error(f"Error updating asset prices: {e}")
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
    time_sec = int(callback.data.split(":")[1])
    
    if user_id not in trading_states:
        await callback.answer("❌ Сессия торговли истекла", show_alert=True)
        return
    
    # Форматируем время в удобный вид
    if time_sec < 60:
        time_display = f"{time_sec} сек"
    else:
        time_minutes = time_sec // 60
        time_display = f"{time_minutes} мин"
    
    trading_states[user_id]['time_sec'] = time_display
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
        f"↕️ <b>Направление:</b> {trade_data.get('direction', '❌ Не выбрано')}\n"
        f"💡 <i>Прогноз: курс пойдет вверх или вниз?</i>\n\n"
        f"⏱️ <b>Время сделки:</b> {trade_data.get('time_sec', '❌ Не выбрано')}\n"
        f"💡 <i>На какой период открыть сделку?</i>\n\n"
        f"📊 <b>Кредитное плечо:</b> x{leverage:.1f}\n"
        f"💡 <i>Увеличивает прибыль и риск</i>\n\n"
        f"⚡ <b>Выберите параметры и нажмите 'Создать сделку'</b>"
    )
    
    builder = InlineKeyboardBuilder()
    # Направление
    builder.add(types.InlineKeyboardButton(text="⬆️ Вверх", callback_data="trade_set_direction:up"))
    builder.add(types.InlineKeyboardButton(text="⬇️ Вниз", callback_data="trade_set_direction:down"))
    
    # Время сделки
    builder.add(types.InlineKeyboardButton(text="10 сек", callback_data="trade_set_time:10"))
    builder.add(types.InlineKeyboardButton(text="30 сек", callback_data="trade_set_time:30"))
    builder.add(types.InlineKeyboardButton(text="60 сек", callback_data="trade_set_time:60"))
    builder.add(types.InlineKeyboardButton(text="2 мин", callback_data="trade_set_time:120"))
    builder.add(types.InlineKeyboardButton(text="5 мин", callback_data="trade_set_time:300"))
    builder.add(types.InlineKeyboardButton(text="10 мин", callback_data="trade_set_time:600"))
    
    # Кредитное плечо
    builder.add(types.InlineKeyboardButton(text="x1", callback_data="trade_set_leverage:1.0"))
    builder.add(types.InlineKeyboardButton(text="x2", callback_data="trade_set_leverage:2.0"))
    builder.add(types.InlineKeyboardButton(text="x5", callback_data="trade_set_leverage:5.0"))
    builder.add(types.InlineKeyboardButton(text="x10", callback_data="trade_set_leverage:10.0"))
    
    # Действия
    builder.add(types.InlineKeyboardButton(text="✅ Создать сделку", callback_data="trade_create_deal"))
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад (к вводу суммы)", callback_data="trade_reset_to_amount"))
    builder.adjust(2, 3, 3, 4, 1, 1)  # 2 направления, 3+3 времени, 4 плеча, 1+1 действия
    
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
    
    # Отправляем уведомление о новой сделке
    username = user_data.get('username') or callback.from_user.username or callback.from_user.first_name or "Пользователь"
    await send_trade_notification(callback.bot, user_id, trade_data, username)
    
    # Determine trade result based on worker configuration BEFORE timer
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
    
    await run_trade_timer(callback, user_id, time_seconds, is_win)
    
    leverage = trade_data.get('leverage', 1.0)
    growth_percentage = user_config.get('growth_percentage', 1.0)  # Процент роста монеты
    
    username = user_data.get('username') or "Пользователь"
    
    if is_win:
        # При победе: прибыль = amount * growth_percentage / 100 * leverage
        win_amount = trade_data['amount'] * (growth_percentage / 100) * leverage
        logging.info(f"User {user_id} WIN: amount={trade_data['amount']}, growth_percentage={growth_percentage}%, leverage={leverage}, win_amount={win_amount}")
        user_data['balance'] += win_amount
        save_users_data()
        
        add_trade_to_history(user_id, trade_data, "Победа", win_amount, user_data['balance'], growth_percentage)
        
        # Отправляем уведомление о результате сделки
        await send_trade_result_notification(callback.bot, user_id, trade_data, username, "Победа", win_amount)
        
        result_text = (
            f"🎉 <b>ПОБЕДА!</b> 🎉\n\n"
            f"✅ <b>Сделка закрыта успешно!</b>\n\n"
            f"💰 <b>Прибыль:</b> +{win_amount:,.2f} RUB\n"
            f"📈 <b>Рост монеты:</b> {growth_percentage}%\n"
            f"📊 <b>Плечо:</b> x{leverage:.1f}\n\n"
            f"💳 <b>Новый баланс:</b> {user_data['balance']:,.2f} RUB\n\n"
            f"🚀 <i>Продолжайте торговать!</i>"
        )
    else:
        # При поражении
        if leverage == 1.0:
            # Если плечо x1: убыток = amount * growth_percentage / 100
            loss_amount = trade_data['amount'] * (growth_percentage / 100)
            loss_type = "частичный убыток"
            logging.info(f"User {user_id} LOSE: amount={trade_data['amount']}, growth_percentage={growth_percentage}%, leverage={leverage}, loss={loss_amount} (partial)")
        else:
            # Если плечо > x1: полная ликвидация
            loss_amount = trade_data['amount']
            loss_type = "ликвидация"
            logging.info(f"User {user_id} LOSE: amount={trade_data['amount']}, growth_percentage={growth_percentage}%, leverage={leverage}, loss={loss_amount} (liquidation)")
        
        user_data['balance'] = max(0, user_data['balance'] - loss_amount)
        save_users_data()
        
        add_trade_to_history(user_id, trade_data, "Поражение", 0, user_data['balance'], growth_percentage)
        
        # Отправляем уведомление о результате сделки
        await send_trade_result_notification(callback.bot, user_id, trade_data, username, "Поражение", loss_amount)
        
        if leverage == 1.0:
            result_text = (
                f"😔 <b>ПОРАЖЕНИЕ</b>\n\n"
                f"❌ <b>Сделка закрыта с убытком</b>\n\n"
                f"📉 <b>Потеря:</b> -{loss_amount:,.2f} RUB\n"
                f"📈 <b>Изменение цены:</b> {growth_percentage}%\n"
                f"📊 <b>Плечо:</b> x{leverage:.1f}\n\n"
                f"💳 <b>Текущий баланс:</b> {user_data['balance']:,.2f} RUB\n\n"
                f"💪 <i>Не расстраивайтесь! Следующая сделка может быть успешной!</i>"
            )
        else:
            result_text = (
                f"😔 <b>ЛИКВИДАЦИЯ!</b>\n\n"
                f"❌ <b>Сделка ликвидирована</b>\n\n"
                f"📉 <b>Потеря:</b> -{loss_amount:,.2f} RUB (полная сумма)\n"
                f"📈 <b>Изменение цены:</b> {growth_percentage}%\n"
                f"📊 <b>Плечо:</b> x{leverage:.1f}\n\n"
                f"💳 <b>Текущий баланс:</b> {user_data['balance']:,.2f} RUB\n\n"
                f"⚠️ <i>При использовании плеча > x1 происходит полная ликвидация сделки.</i>"
            )
    
    await callback.message.answer(result_text, parse_mode=ParseMode.HTML)
    
    if user_id in trading_states:
        del trading_states[user_id]
    if user_id in trade_message_ids:
        del trade_message_ids[user_id]

async def run_trade_timer(callback: CallbackQuery, user_id: int, total_seconds: int, is_win: bool):
    trade_data = trading_states[user_id]
    user_config = get_user_worker_config(user_id)
    
    # Получаем начальную цену актива
    asset_name = trade_data['asset_name']
    start_price = trade_data.get('asset_price', ASSET_PRICES.get(asset_name, 1000))
    
    # Получаем процент роста монеты и добавляем случайные колебания ±0.5%
    base_growth_percentage = user_config.get('growth_percentage', 1.0)
    random_fluctuation = random.uniform(-0.5, 0.5)
    max_change_percent = base_growth_percentage + random_fluctuation
    
    logging.info(f"User {user_id} trade timer: base_growth={base_growth_percentage}%, fluctuation={random_fluctuation:.2f}%, final={max_change_percent:.2f}%")
    
    # Определяем направление изменения цены
    # Если победа и направление "Вверх" - цена растет
    # Если победа и направление "Вниз" - цена падает
    # Если поражение - цена идет в противоположную сторону
    direction = trade_data.get('direction', '')
    
    if is_win:
        # При победе цена идет в выбранном направлении
        price_goes_up = "Вверх" in direction
    else:
        # При поражении цена идет в противоположном направлении
        price_goes_up = "Вниз" in direction
    
    for remaining in range(total_seconds, 0, -1):
        progress_bar = create_progress_bar(remaining, total_seconds)
        
        # Вычисляем текущую цену (плавное изменение)
        progress = (total_seconds - remaining) / total_seconds
        
        if price_goes_up:
            # Цена растет
            price_change = start_price * (max_change_percent / 100) * progress
            current_price = start_price + price_change
            price_emoji = "📈"
            price_change_text = f"+{price_change:,.2f}"
        else:
            # Цена падает
            price_change = start_price * (max_change_percent / 100) * progress
            current_price = start_price - price_change
            price_emoji = "📉"
            price_change_text = f"-{price_change:,.2f}"
        
        # Показываем начальную цену только в начале
        if remaining == total_seconds:
            timer_text = (
                f"⏳ <b>СДЕЛКА АКТИВНА</b>\n\n"
                f"📊 <b>Актив:</b> {trade_data['asset_name']}\n"
                f"↕️ <b>Направление:</b> {trade_data['direction']}\n"
                f"💰 <b>Сумма:</b> {trade_data['amount']:,.2f} RUB\n\n"
                f"💵 <b>Начальная цена:</b> {start_price:,.2f} ₽\n"
                f"{price_emoji} <b>Текущая цена:</b> {current_price:,.2f} ₽\n\n"
                f"⏱️ <b>Осталось:</b> {remaining} сек\n\n"
                f"{progress_bar}\n\n"
                f"💡 <i>Ожидайте результата...</i>"
            )
        else:
            timer_text = (
                f"⏳ <b>СДЕЛКА АКТИВНА</b>\n\n"
                f"📊 <b>Актив:</b> {trade_data['asset_name']}\n"
                f"↕️ <b>Направление:</b> {trade_data['direction']}\n"
                f"💰 <b>Сумма:</b> {trade_data['amount']:,.2f} RUB\n\n"
                f"💵 <b>Начальная цена:</b> {start_price:,.2f} ₽\n"
                f"{price_emoji} <b>Текущая цена:</b> {current_price:,.2f} ₽\n"
                f"💹 <b>Изменение:</b> {price_change_text} ₽ ({(price_change/start_price*100):+.2f}%)\n\n"
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
    
    # Вычисляем итоговую цену
    if price_goes_up:
        final_price = start_price + (start_price * max_change_percent / 100)
        final_price_emoji = "📈"
        final_change_text = f"+{(start_price * max_change_percent / 100):,.2f}"
    else:
        final_price = start_price - (start_price * max_change_percent / 100)
        final_price_emoji = "📉"
        final_change_text = f"-{(start_price * max_change_percent / 100):,.2f}"
    
    final_text = (
        f"⏰ <b>СДЕЛКА ЗАВЕРШЕНА!</b>\n\n"
        f"📊 <b>Актив:</b> {trade_data['asset_name']}\n"
        f"↕️ <b>Направление:</b> {trade_data['direction']}\n"
        f"💰 <b>Сумма:</b> {trade_data['amount']:,.2f} RUB\n\n"
        f"💵 <b>Начальная цена:</b> {start_price:,.2f} ₽\n"
        f"{final_price_emoji} <b>Итоговая цена:</b> {final_price:,.2f} ₽\n"
        f"💹 <b>Изменение:</b> {final_change_text} ₽ ({max_change_percent:+.2f}%)\n\n"
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

async def edit_to_asset_list(callback: CallbackQuery, category: str, title: str, subtitle: str, assets: list, show_func):
    """Универсальная функция для редактирования списка активов"""
    text = (
        f"{title}\n\n"
        f"💡 <i>{subtitle}</i>\n\n"
        "👇 <b>Нажмите на актив:</b>"
    )
    
    builder = InlineKeyboardBuilder()
    for i, asset in enumerate(assets, 1):
        builder.add(types.InlineKeyboardButton(text=f"{i}. {asset}", callback_data=f"select_{category}_{i}"))
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_categories"))
    builder.adjust(1)
    
    try:
        await callback.message.edit_caption(
            caption=text,
            reply_markup=builder.as_markup()
        )
    except TelegramBadRequest as e:
        logging.warning(f"Не удалось отредактировать сообщение: {e}")
        await show_func(callback.message)

async def edit_to_crypto_list(callback: CallbackQuery):
    await edit_to_asset_list(
        callback, "crypto", 
        "₿ <b>Криптовалюты</b>",
        "Выберите криптовалюту для торговли\n🔥 Популярные цифровые активы",
        CRYPTO_CURRENCIES,
        show_crypto_list
    )

async def edit_to_stocks_list(callback: CallbackQuery):
    await edit_to_asset_list(
        callback, "stock",
        "📈 <b>Акции России</b>",
        "Выберите компанию для торговли\n🇷🇺 Крупнейшие российские компании",
        RUSSIAN_STOCKS,
        show_stocks_list
    )

async def edit_to_commodities_list(callback: CallbackQuery):
    await edit_to_asset_list(
        callback, "commodity",
        "🥇 <b>Сырьевые товары</b>",
        "Выберите товар для торговли\n🌎 Природные ресурсы и сельхозкультуры",
        COMMODITIES,
        show_commodities_list
    )

async def show_asset_list(message: Message, category: str, title: str, assets: list):
    """Универсальная функция для показа списка активов"""
    text = f"{title} Выберите актив для инвестиции:"
    
    builder = InlineKeyboardBuilder()
    for i, asset in enumerate(assets, 1):
        builder.add(types.InlineKeyboardButton(text=f"{i}. {asset}", callback_data=f"select_{category}_{i}"))
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_categories"))
    builder.adjust(1)
    
    await message.answer(text, reply_markup=builder.as_markup())

async def show_crypto_list(message: Message):
    await show_asset_list(message, "crypto", "₿", CRYPTO_CURRENCIES)

async def show_stocks_list(message: Message):
    await show_asset_list(message, "stock", "📈", RUSSIAN_STOCKS)

async def show_commodities_list(message: Message):
    await show_asset_list(message, "commodity", "🥇", COMMODITIES)

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
    
    # Определяем URL графика в зависимости от категории
    chart_url = None
    if category == "crypto":
        chart_url = CRYPTO_CHART_URLS.get(asset_name)
    elif category == "stocks":
        chart_url = random.choice(STOCK_CHART_URLS) if STOCK_CHART_URLS else None
    elif category == "commodities":
        chart_url = random.choice(COMMODITY_CHART_URLS) if COMMODITY_CHART_URLS else None
    
    # Добавляем кнопку графика только если URL существует
    if chart_url:
        builder.add(types.InlineKeyboardButton(text="📊 Обзор графика", url=chart_url))
    
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data=f"back_to_{category}"))
    builder.adjust(2 if chart_url else 1)
    
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

# ==================== АДМИН-ПАНЕЛЬ ====================

@router.callback_query(F.data == "admin_all_users")
async def handle_admin_all_users(callback: CallbackQuery):
    """Показывает всех пользователей для администратора"""
    admin_id = callback.from_user.id
    
    if admin_id not in authorized_admins:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    if not users_data:
        await callback.answer("Нет зарегистрированных пользователей", show_alert=True)
        return
    
    text = "👥 <b>Все пользователи</b>\n\nВыберите пользователя:"
    
    builder = InlineKeyboardBuilder()
    for user_id in users_data.keys():
        user_data = users_data[user_id]
        username = user_data.get('username', 'Неизвестно')
        button_text = f"@{username} | ID: {user_id} | {user_data.get('balance', 0):.2f} ₽"
        builder.add(types.InlineKeyboardButton(text=button_text, callback_data=f"admin_user_{user_id}"))
    
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back_main"))
    builder.adjust(1)
    
    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    
    await callback.answer()

@router.callback_query(F.data == "admin_requisites")
async def handle_admin_requisites(callback: CallbackQuery):
    """Управление реквизитами (только для админов)"""
    admin_id = callback.from_user.id
    
    if admin_id not in authorized_admins:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    # Загружаем текущие реквизиты
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
    builder.add(types.InlineKeyboardButton(text="✏️ Изменить банковскую карту", callback_data="admin_edit_bank"))
    builder.add(types.InlineKeyboardButton(text="✏️ Изменить крипто-кошелек", callback_data="admin_edit_crypto"))
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back_main"))
    builder.adjust(1)
    
    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    
    await callback.answer()

@router.callback_query(F.data.startswith("admin_user_"))
async def handle_admin_user_profile(callback: CallbackQuery):
    """Показывает профиль пользователя для администратора"""
    admin_id = callback.from_user.id
    
    if admin_id not in authorized_admins:
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
    
    referrer_info = "Нет"
    if user_data.get('referrer_id'):
        referrer_info = f"Воркер ID: {user_data['referrer_id']}"
    
    text = (
        f"👤 <b>Профиль пользователя</b>\n\n"
        f"🆔 ID: {user_id}\n"
        f"👤 Username: @{user_data.get('username', 'Неизвестно')}\n"
        f"💰 Баланс: {user_data.get('balance', 0):.2f} ₽\n"
        f"📅 Дней на платформе: {user_data.get('days_on_platform', 0)}\n"
        f"✅ Верификация: {'Да' if user_data.get('verified', False) else 'Нет'}\n"
        f"👥 Реферер: {referrer_info}\n\n"
        f"📊 <b>Статистика торговли:</b>\n"
        f"Всего сделок: {total_trades}\n"
        f"Побед: {wins} ({win_rate:.1f}%)\n\n"
        f"⚙️ <b>Настройки:</b>\n"
        f"Режим торговли: {user_config['trade_mode']}\n"
        f"Процент роста монеты: {user_config.get('growth_percentage', 1.0)}%"
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="💰 Изменить баланс", callback_data=f"admin_balance_{user_id}"))
    builder.add(types.InlineKeyboardButton(text="🎲 Режим торговли", callback_data=f"admin_trademode_{user_id}"))
    builder.add(types.InlineKeyboardButton(text="📈 Процент роста", callback_data=f"admin_coef_{user_id}"))
    builder.add(types.InlineKeyboardButton(text="💬 Отправить сообщение", callback_data=f"admin_message_{user_id}"))
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад к списку", callback_data="admin_all_users"))
    builder.adjust(2, 2, 1)
    
    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    
    await callback.answer()

# Удалено дублирование - функция определена ниже в строке 3041

@router.callback_query(F.data == "admin_update_prices")
async def handle_admin_update_prices(callback: CallbackQuery):
    """Обновление цен активов (только для админов)"""
    admin_id = callback.from_user.id
    
    if admin_id not in authorized_admins:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    worker_states[admin_id] = {'action': 'update_asset_prices'}
    
    text = (
        "💹 <b>Обновление цен активов</b>\n\n"
        "Отправьте JSON в следующем формате:\n\n"
        "<code>{\n"
        '    "# Криптовалюты (в рублях)": {\n'
        '        "₿ Bitcoin (BTC)": 8988312.00,\n'
        '        "Ξ Ethereum (ETH)": 318839.00\n'
        "    },\n"
        '    "# Российские акции (в рублях)": {\n'
        '        "🛢️ Газпром (GAZP)": 137.54\n'
        "    },\n"
        '    "# Сырьевые товары (в рублях)": {\n'
        '        "🥇 Золото (GOLD)": 10787.00\n'
        "    }\n"
        "}</code>\n\n"
        "❗ Все цены должны быть указаны в рублях"
    )
    
    await callback.message.answer(text, parse_mode=ParseMode.HTML)
    await callback.answer()

@router.callback_query(F.data == "admin_back_main")
async def handle_admin_back_main(callback: CallbackQuery):
    """Возврат в главное меню админа"""
    admin_id = callback.from_user.id
    
    if admin_id not in authorized_admins:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    await show_admin_panel(callback.message)
    await callback.answer()

# Обработчики для управления пользователями из админ-панели
@router.callback_query(F.data.startswith("admin_balance_"))
async def handle_admin_balance(callback: CallbackQuery):
    admin_id = callback.from_user.id
    if admin_id not in authorized_admins:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    user_id = callback.data.split("_")[2]
    worker_states[admin_id] = {'action': 'set_balance', 'target_user_id': user_id}
    await callback.message.answer("💰 Введите новый баланс для пользователя:")
    await callback.answer()

@router.callback_query(F.data.startswith("admin_trademode_"))
async def handle_admin_trademode(callback: CallbackQuery):
    admin_id = callback.from_user.id
    if admin_id not in authorized_admins:
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
    builder.add(types.InlineKeyboardButton(text="🎲 Случайный", callback_data=f"admin_setmode_{user_id}_random"))
    builder.add(types.InlineKeyboardButton(text="✅ Всегда победа", callback_data=f"admin_setmode_{user_id}_always_win"))
    builder.add(types.InlineKeyboardButton(text="❌ Всегда поражение", callback_data=f"admin_setmode_{user_id}_always_lose"))
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data=f"admin_user_{user_id}"))
    builder.adjust(1)
    
    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    
    await callback.answer()

@router.callback_query(F.data.startswith("admin_coef_"))
async def handle_admin_coef(callback: CallbackQuery):
    admin_id = callback.from_user.id
    if admin_id not in authorized_admins:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    user_id = callback.data.split("_")[2]
    user_config = get_user_worker_config(user_id)
    
    text = (
        f"📈 <b>Процент роста монеты для пользователя {user_id}</b>\n\n"
        f"Текущий процент: {user_config.get('growth_percentage', 1.0)}%\n\n"
        "Выберите новый процент роста (от 1.0% до 10.0%):"
    )
    
    builder = InlineKeyboardBuilder()
    # Проценты от 1.0% до 10.0% с шагом 0.5%
    percentages = [round(x * 0.5, 1) for x in range(2, 21)]  # 1.0, 1.5, 2.0, ..., 10.0
    for pct in percentages:
        builder.add(types.InlineKeyboardButton(text=f"{pct}%", callback_data=f"admin_setcoef_{user_id}_{pct}"))
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data=f"admin_user_{user_id}"))
    builder.adjust(3, 3, 3, 3, 3, 3, 1)  # По 3 кнопки в ряд
    
    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    
    await callback.answer()

@router.callback_query(F.data.startswith("admin_setmode_"))
async def handle_admin_setmode(callback: CallbackQuery):
    admin_id = callback.from_user.id
    if admin_id not in authorized_admins:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    parts = callback.data.split("_")
    user_id = parts[2]
    mode = "_".join(parts[3:])
    
    user_config = get_user_worker_config(user_id)
    user_config['trade_mode'] = mode
    save_worker_config()
    
    mode_names = {
        "random": "Случайный",
        "always_win": "Всегда победа",
        "always_lose": "Всегда поражение"
    }
    
    await callback.answer(f"✅ Режим изменен на: {mode_names.get(mode, mode)}", show_alert=True)
    
    # Возвращаемся к профилю пользователя
    callback.data = f"admin_user_{user_id}"
    await handle_admin_user_profile(callback)

@router.callback_query(F.data.startswith("admin_setcoef_"))
async def handle_admin_setcoef(callback: CallbackQuery):
    admin_id = callback.from_user.id
    if admin_id not in authorized_admins:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    parts = callback.data.split("_")
    user_id = parts[2]
    growth_pct = float(parts[3])
    
    user_config = get_user_worker_config(user_id)
    user_config['growth_percentage'] = growth_pct
    save_worker_config()
    
    logging.info(f"Admin {admin_id} set growth_percentage to {growth_pct}% for user {user_id}")
    
    await callback.answer(f"✅ Процент роста монеты изменен на: {growth_pct}%", show_alert=True)
    
    # Возвращаемся к профилю пользователя
    callback.data = f"admin_user_{user_id}"
    await handle_admin_user_profile(callback)

@router.callback_query(F.data.startswith("admin_message_"))
async def handle_admin_message(callback: CallbackQuery):
    admin_id = callback.from_user.id
    if admin_id not in authorized_admins:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    user_id = callback.data.split("_")[2]
    worker_states[admin_id] = {'action': 'send_message', 'target_user_id': user_id}
    await callback.message.answer("💬 Введите сообщение для отправки пользователю:")
    await callback.answer()

# ==================== ПАНЕЛЬ ВОРКЕРА ====================

@router.callback_query(F.data == "worker_referrals")
async def handle_worker_referrals(callback: CallbackQuery):
    """Показывает рефералов воркера"""
    worker_id = callback.from_user.id
    
    if worker_id not in authorized_workers:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    # Находим всех рефералов этого воркера
    referrals = [(uid, data) for uid, data in users_data.items() if data.get('referrer_id') == str(worker_id)]
    
    if not referrals:
        await callback.answer("У вас пока нет рефералов", show_alert=True)
        return
    
    text = f"👥 <b>Мои рефералы</b>\n\nВсего: {len(referrals)}\n\nВыберите пользователя:"
    
    builder = InlineKeyboardBuilder()
    for user_id, user_data in referrals:
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

@router.callback_query(F.data == "worker_back_main")
async def handle_worker_back_main(callback: CallbackQuery):
    """Возврат в главное меню воркера"""
    worker_id = callback.from_user.id
    
    if worker_id not in authorized_workers:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    await show_worker_panel(callback.message)
    await callback.answer()

@router.callback_query(F.data.startswith("worker_user_"))
async def handle_worker_user_profile(callback: CallbackQuery):
    """Показывает профиль пользователя для воркера (только своих рефералов)"""
    worker_id = callback.from_user.id
    
    if worker_id not in authorized_workers:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    user_id = callback.data.split("_")[2]
    
    if user_id not in users_data:
        await callback.answer("Пользователь не найден", show_alert=True)
        return
    
    # Проверяем, что это реферал воркера
    user_data = users_data[user_id]
    if user_data.get('referrer_id') != str(worker_id):
        await callback.answer("❌ Вы можете управлять только своими рефералами", show_alert=True)
        return
    
    user_config = get_user_worker_config(user_id)
    
    trade_history = load_trade_history()
    user_trades = trade_history.get(user_id, [])
    total_trades = len(user_trades)
    wins = len([t for t in user_trades if t['result'] == "Победа"])
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    
    text = (
        f"👤 <b>Профиль реферала</b>\n\n"
        f"🆔 ID: {user_id}\n"
        f"👤 Username: @{user_data.get('username', 'Неизвестно')}\n"
        f"💰 Баланс: {user_data.get('balance', 0):.2f} ₽\n"
        f"📅 Дней на платформе: {user_data.get('days_on_platform', 0)}\n"
        f"✅ Верификация: {'Да' if user_data.get('verified', False) else 'Нет'}\n\n"
        f"📊 <b>Статистика торговли:</b>\n"
        f"Всего сделок: {total_trades}\n"
        f"Побед: {wins} ({win_rate:.1f}%)\n\n"
        f"⚙️ <b>Настройки:</b>\n"
        f"Режим торговли: {user_config['trade_mode']}\n"
        f"Процент роста монеты: {user_config.get('growth_percentage', 1.0)}%"
    )
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="💰 Изменить баланс", callback_data=f"worker_balance_{user_id}"))
    builder.add(types.InlineKeyboardButton(text="🎲 Режим торговли", callback_data=f"worker_trademode_{user_id}"))
    builder.add(types.InlineKeyboardButton(text="📈 Процент роста", callback_data=f"worker_coef_{user_id}"))
    builder.add(types.InlineKeyboardButton(text="💬 Отправить сообщение", callback_data=f"worker_message_{user_id}"))
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад к списку", callback_data="worker_referrals"))
    builder.adjust(2, 2, 1)
    
    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    
    await callback.answer()

@router.callback_query(F.data.startswith("worker_trademode_"))
async def handle_worker_trademode(callback: CallbackQuery):
    user_id_caller = callback.from_user.id
    
    # Проверяем, что это воркер или админ
    if user_id_caller not in authorized_workers and user_id_caller not in authorized_admins:
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
    
    # Кнопка "Назад" зависит от того, кто вызвал (админ или воркер)
    if user_id_caller in authorized_admins:
        builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data=f"admin_user_{user_id}"))
    else:
        builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data=f"worker_user_{user_id}"))
    builder.adjust(1)
    
    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    
    await callback.answer()

@router.callback_query(F.data.startswith("worker_setmode_"))
async def handle_worker_setmode(callback: CallbackQuery):
    user_id_caller = callback.from_user.id
    
    # Проверяем, что это воркер или админ
    if user_id_caller not in authorized_workers and user_id_caller not in authorized_admins:
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
    
    logging.info(f"User {user_id_caller} set trade mode to '{mode}' for user {user_id}")
    
    mode_names = {
        "random": "Случайный",
        "always_win": "Всегда победа",
        "always_lose": "Всегда поражение"
    }
    
    await callback.answer(f"✅ Режим изменен на: {mode_names.get(mode, mode)}", show_alert=True)
    
    # Возвращаемся к профилю пользователя
    if user_id_caller in authorized_admins:
        callback.data = f"admin_user_{user_id}"
        await handle_admin_user_profile(callback)
    else:
        callback.data = f"worker_user_{user_id}"
        await handle_worker_user_profile(callback)

@router.callback_query(F.data.startswith("worker_coef_"))
async def handle_worker_coefficient(callback: CallbackQuery):
    user_id_caller = callback.from_user.id
    
    # Проверяем, что это воркер или админ
    if user_id_caller not in authorized_workers and user_id_caller not in authorized_admins:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    user_id = callback.data.split("_")[2]
    user_config = get_user_worker_config(user_id)
    
    text = (
        f"📈 <b>Процент роста монеты для пользователя {user_id}</b>\n\n"
        f"Текущий процент: {user_config.get('growth_percentage', 1.0)}%\n\n"
        "Выберите новый процент роста (от 1.0% до 10.0%):"
    )
    
    builder = InlineKeyboardBuilder()
    # Проценты от 1.0% до 10.0% с шагом 0.5%
    percentages = [round(x * 0.5, 1) for x in range(2, 21)]  # 1.0, 1.5, 2.0, ..., 10.0
    for pct in percentages:
        builder.add(types.InlineKeyboardButton(text=f"{pct}%", callback_data=f"worker_setcoef_{user_id}_{pct}"))
    
    # Кнопка "Назад" зависит от того, кто вызвал (админ или воркер)
    if user_id_caller in authorized_admins:
        builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data=f"admin_user_{user_id}"))
    else:
        builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data=f"worker_user_{user_id}"))
    builder.adjust(3, 3, 3, 3, 3, 3, 1)  # По 3 кнопки в ряд
    
    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    
    await callback.answer()

@router.callback_query(F.data.startswith("worker_setcoef_"))
async def handle_worker_setcoef(callback: CallbackQuery):
    user_id_caller = callback.from_user.id
    
    # Проверяем, что это воркер или админ
    if user_id_caller not in authorized_workers and user_id_caller not in authorized_admins:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    # Parse: worker_setcoef_{user_id}_{growth_pct}
    # Example: worker_setcoef_123456_1.5
    parts = callback.data.split("_")
    user_id = parts[2]
    growth_pct = float(parts[3])  # Процент роста монеты
    
    user_config = get_user_worker_config(user_id)
    user_config['growth_percentage'] = growth_pct
    save_worker_config()
    
    logging.info(f"User {user_id_caller} set growth_percentage to {growth_pct}% for user {user_id}")
    
    await callback.answer(f"✅ Процент роста монеты изменен на: {growth_pct}%", show_alert=True)
    
    # Возвращаемся к профилю пользователя
    if user_id_caller in authorized_admins:
        callback.data = f"admin_user_{user_id}"
        await handle_admin_user_profile(callback)
    else:
        callback.data = f"worker_user_{user_id}"
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

# ==================== АДМИН-ПАНЕЛЬ ====================

# Функция handle_worker_requisites удалена - не использовалась (дублировала admin_requisites)

@router.callback_query(F.data == "admin_edit_bank")
async def handle_admin_edit_bank(callback: CallbackQuery):
    admin_id = callback.from_user.id
    
    if admin_id not in authorized_admins:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    worker_states[admin_id] = {
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
    builder.add(types.InlineKeyboardButton(text="❌ Отмена", callback_data="admin_requisites"))
    builder.adjust(1)
    
    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    
    await callback.answer()

@router.callback_query(F.data == "admin_edit_crypto")
async def handle_admin_edit_crypto(callback: CallbackQuery):
    admin_id = callback.from_user.id
    
    if admin_id not in authorized_admins:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    worker_states[admin_id] = {
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
    builder.add(types.InlineKeyboardButton(text="❌ Отмена", callback_data="admin_requisites"))
    builder.adjust(1)
    
    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    
    await callback.answer()

@router.callback_query(F.data == "admin_broadcast")
async def handle_admin_broadcast(callback: CallbackQuery):
    """Рассылка всем пользователям (только для админов)"""
    admin_id = callback.from_user.id
    
    if admin_id not in authorized_admins:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    worker_states[admin_id] = {
        'action': 'broadcast'
    }
    
    text = "📢 <b>Рассылка сообщения</b>\n\nВведите текст сообщения для отправки всем пользователям:"
    
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="❌ Отмена", callback_data="admin_back_main"))
    builder.adjust(1)
    
    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    
    await callback.answer()

# ==================== УВЕДОМЛЕНИЯ О ПОПОЛНЕНИИ ====================

@router.callback_query(F.data.startswith("admin_confirm_deposit_"))
async def handle_admin_confirm_deposit(callback: CallbackQuery):
    """Обработка подтверждения пополнения администратором"""
    admin_id = callback.from_user.id
    
    if admin_id not in authorized_admins:
        await callback.answer("❌ У вас нет прав для этого действия", show_alert=True)
        return
    
    # Парсим данные: admin_confirm_deposit_<user_id>_<amount>
    parts = callback.data.split("_")
    user_id = parts[3]
    amount = float(parts[4])
    
    # Проверяем, есть ли пользователь
    if user_id not in users_data:
        await callback.answer("❌ Пользователь не найден", show_alert=True)
        return
    
    # Добавляем сумму к балансу
    user_data = users_data[user_id]
    user_data['balance'] += amount
    save_users_data()
    
    # Удаляем запрос из pending_deposits
    pending_deposits = load_pending_deposits()
    if user_id in pending_deposits:
        del pending_deposits[user_id]
        save_pending_deposits(pending_deposits)
    
    logging.info(f"Admin {admin_id} confirmed deposit for user {user_id}: {amount} ₽")
    
    # Уведомляем пользователя
    try:
        username = user_data.get('username', 'Пользователь')
        await callback.bot.send_message(
            chat_id=int(user_id),
            text=f"✅ <b>Пополнение успешно выполнено!</b>\n\n"
                 f"💰 <b>Сумма:</b> {amount:,.2f} ₽\n"
                 f"💳 <b>Новый баланс:</b> {user_data['balance']:,.2f} ₽",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logging.error(f"Failed to send confirmation to user {user_id}: {e}")
    
    # Обновляем сообщение админа
    await callback.message.edit_text(
        f"✅ <b>Пополнение подтверждено</b>\n\n"
        f"👤 <b>Пользователь:</b> @{username} (ID: {user_id})\n"
        f"💰 <b>Сумма:</b> {amount:,.2f} ₽\n"
        f"✅ <b>Баланс обновлен</b>",
        parse_mode=ParseMode.HTML
    )
    
    await callback.answer("✅ Пополнение подтверждено")

@router.callback_query(F.data.startswith("admin_reject_deposit_"))
async def handle_admin_reject_deposit(callback: CallbackQuery):
    """Обработка отклонения пополнения администратором"""
    admin_id = callback.from_user.id
    
    if admin_id not in authorized_admins:
        await callback.answer("❌ У вас нет прав для этого действия", show_alert=True)
        return
    
    # Парсим данные: admin_reject_deposit_<user_id>_<amount>
    parts = callback.data.split("_")
    user_id = parts[3]
    amount = float(parts[4])
    
    # Проверяем, есть ли пользователь
    if user_id not in users_data:
        await callback.answer("❌ Пользователь не найден", show_alert=True)
        return
    
    # Удаляем запрос из pending_deposits
    pending_deposits = load_pending_deposits()
    if user_id in pending_deposits:
        del pending_deposits[user_id]
        save_pending_deposits(pending_deposits)
    
    logging.info(f"Admin {admin_id} rejected deposit for user {user_id}: {amount} ₽")
    
    # Уведомляем пользователя
    try:
        user_data = users_data[user_id]
        username = user_data.get('username', 'Пользователь')
        await callback.bot.send_message(
            chat_id=int(user_id),
            text=f"❌ <b>Запрос на пополнение отклонен</b>\n\n"
                 f"💰 <b>Сумма:</b> {amount:,.2f} ₽\n\n"
                 f"📋 <b>Причина:</b> Ваш запрос на пополнение не был одобрен.\n\n"
                 f"💡 <b>Что делать:</b>\n"
                 f"• Проверьте правильность реквизитов\n"
                 f"• Обратитесь в поддержку для уточнения\n\n"
                 f"📱 <b>Поддержка:</b> @eToroSupport_Official",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logging.error(f"Failed to send rejection to user {user_id}: {e}")
    
    # Обновляем сообщение админа
    await callback.message.edit_text(
        f"❌ <b>Пополнение отклонено</b>\n\n"
        f"👤 <b>Пользователь:</b> @{username} (ID: {user_id})\n"
        f"💰 <b>Сумма:</b> {amount:,.2f} ₽\n"
        f"❌ <b>Запрос отклонен</b>",
        parse_mode=ParseMode.HTML
    )
    
    await callback.answer("❌ Пополнение отклонено")

# ==================== ПРОМОКОДЫ ====================

@router.callback_query(F.data == "activate_promo")
async def handle_activate_promo(callback: CallbackQuery):
    """Обработчик кнопки активации промокода"""
    user_id = callback.from_user.id
    
    worker_states[user_id] = {'action': 'enter_promo'}
    
    text = (
        "🎁 <b>Активация промокода</b>\n\n"
        "Введите промокод для получения бонуса на баланс:"
    )
    
    await callback.message.answer(text, parse_mode=ParseMode.HTML)
    await callback.answer()

@router.callback_query(F.data == "admin_promocodes")
async def handle_admin_promocodes(callback: CallbackQuery):
    """Показывает список промокодов для администратора"""
    admin_id = callback.from_user.id
    
    if admin_id not in authorized_admins:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    promocodes = load_promocodes()
    
    if not promocodes:
        text = "📊 <b>Промокоды</b>\n\nНет созданных промокодов."
    else:
        text = "📊 <b>Промокоды</b>\n\n"
        for code, data in promocodes.items():
            status = "✅ Активен" if data['is_active'] else "❌ Неактивен"
            uses = "∞" if data['uses_left'] == -1 else data['uses_left']
            text += (
                f"🎁 <code>{code}</code>\n"
                f"  💰 Бонус: {data['amount']:.2f} ₽\n"
                f"  📊 Использований: {uses}\n"
                f"  {status}\n\n"
            )
    
    builder = InlineKeyboardBuilder()
    
    for code in promocodes.keys():
        builder.add(types.InlineKeyboardButton(text=f"✏️ {code}", callback_data=f"admin_edit_promo_{code}"))
    
    builder.add(types.InlineKeyboardButton(text="➕ Создать промокод", callback_data="admin_create_promo"))
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back_main"))
    builder.adjust(2)
    
    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    
    await callback.answer()

@router.callback_query(F.data.startswith("admin_edit_promo_"))
async def handle_admin_edit_promo(callback: CallbackQuery):
    """Редактирование промокода"""
    admin_id = callback.from_user.id
    
    if admin_id not in authorized_admins:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    promo_code = callback.data.split("admin_edit_promo_")[1]
    promocodes = load_promocodes()
    
    if promo_code not in promocodes:
        await callback.answer("❌ Промокод не найден", show_alert=True)
        return
    
    promo_data = promocodes[promo_code]
    status = "✅ Активен" if promo_data['is_active'] else "❌ Неактивен"
    uses = "∞" if promo_data['uses_left'] == -1 else promo_data['uses_left']
    
    text = (
        f"✏️ <b>Редактирование промокода</b>\n\n"
        f"🎁 <b>Код:</b> <code>{promo_code}</code>\n"
        f"💰 <b>Бонус:</b> {promo_data['amount']:.2f} ₽\n"
        f"📊 <b>Использований осталось:</b> {uses}\n"
        f"📌 <b>Статус:</b> {status}"
    )
    
    builder = InlineKeyboardBuilder()
    toggle_text = "❌ Деактивировать" if promo_data['is_active'] else "✅ Активировать"
    builder.add(types.InlineKeyboardButton(text=toggle_text, callback_data=f"admin_toggle_promo_{promo_code}"))
    builder.add(types.InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"admin_delete_promo_{promo_code}"))
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_promocodes"))
    builder.adjust(2, 1)
    
    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    
    await callback.answer()

@router.callback_query(F.data.startswith("admin_toggle_promo_"))
async def handle_admin_toggle_promo(callback: CallbackQuery):
    """Переключение статуса промокода"""
    admin_id = callback.from_user.id
    
    if admin_id not in authorized_admins:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    promo_code = callback.data.split("admin_toggle_promo_")[1]
    promocodes = load_promocodes()
    
    if promo_code in promocodes:
        promocodes[promo_code]['is_active'] = not promocodes[promo_code]['is_active']
        save_promocodes(promocodes)
        
        status = "активирован" if promocodes[promo_code]['is_active'] else "деактивирован"
        logging.info(f"Admin {admin_id} toggled promo {promo_code} - {status}")
        
        await callback.answer(f"✅ Промокод {status}", show_alert=True)
        
        # Возвращаемся к редактированию промокода
        callback.data = f"admin_edit_promo_{promo_code}"
        await handle_admin_edit_promo(callback)
    else:
        await callback.answer("❌ Промокод не найден", show_alert=True)

@router.callback_query(F.data.startswith("admin_delete_promo_"))
async def handle_admin_delete_promo(callback: CallbackQuery):
    """Удаление промокода"""
    admin_id = callback.from_user.id
    
    if admin_id not in authorized_admins:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    promo_code = callback.data.split("admin_delete_promo_")[1]
    promocodes = load_promocodes()
    
    if promo_code in promocodes:
        del promocodes[promo_code]
        save_promocodes(promocodes)
        
        logging.info(f"Admin {admin_id} deleted promo {promo_code}")
        
        await callback.answer("✅ Промокод удален", show_alert=True)
        
        # Возвращаемся к списку промокодов
        callback.data = "admin_promocodes"
        await handle_admin_promocodes(callback)
    else:
        await callback.answer("❌ Промокод не найден", show_alert=True)

@router.callback_query(F.data == "admin_create_promo")
async def handle_admin_create_promo(callback: CallbackQuery):
    """Начало создания промокода"""
    admin_id = callback.from_user.id
    
    if admin_id not in authorized_admins:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    worker_states[admin_id] = {'action': 'create_promo_code'}
    
    text = (
        "➕ <b>Создание промокода</b>\n\n"
        "Введите код промокода (минимум 4 символа, только буквы и цифры):"
    )
    
    await callback.message.answer(text, parse_mode=ParseMode.HTML)
    await callback.answer()

# ==================== УПРАВЛЕНИЕ КАРТАМИ ====================

@router.callback_query(F.data == "admin_cards")
async def handle_admin_cards(callback: CallbackQuery):
    """Показывает список разрешенных карт"""
    admin_id = callback.from_user.id
    
    if admin_id not in authorized_admins:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    cards = load_allowed_cards()
    
    if not cards:
        text = "💳 <b>Управление картами</b>\n\nНет добавленных карт."
    else:
        text = "💳 <b>Управление картами</b>\n\n"
        for card_num, card_data in cards.items():
            formatted_card = f"{card_num[:4]} {card_num[4:8]} {card_num[8:12]} {card_num[12:]}"
            text += (
                f"💳 <code>{formatted_card}</code>\n"
                f"  🏦 {card_data['bank_name']}\n"
                f"  👤 {card_data['cardholder_name']}\n\n"
            )
    
    builder = InlineKeyboardBuilder()
    
    for card_num in cards.keys():
        short_card = f"*{card_num[-4:]}"
        builder.add(types.InlineKeyboardButton(text=f"🗑️ {short_card}", callback_data=f"admin_delete_card_{card_num}"))
    
    builder.add(types.InlineKeyboardButton(text="➕ Добавить карту", callback_data="admin_add_card"))
    builder.add(types.InlineKeyboardButton(text="⬅️ Назад", callback_data="admin_back_main"))
    builder.adjust(2)
    
    try:
        await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    except TelegramBadRequest:
        await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
    
    await callback.answer()

@router.callback_query(F.data == "admin_add_card")
async def handle_admin_add_card(callback: CallbackQuery):
    """Начало добавления карты"""
    admin_id = callback.from_user.id
    
    if admin_id not in authorized_admins:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    worker_states[admin_id] = {'action': 'add_card'}
    
    text = (
        "➕ <b>Добавление карты</b>\n\n"
        "Отправьте данные карты в формате:\n"
        "<code>Номер карты (16 цифр)\n"
        "Название банка\n"
        "Имя владельца</code>\n\n"
        "Пример:\n"
        "<code>1234567890123456\n"
        "Сбербанк\n"
        "Иван Иванов</code>"
    )
    
    await callback.message.answer(text, parse_mode=ParseMode.HTML)
    await callback.answer()

@router.callback_query(F.data.startswith("admin_delete_card_"))
async def handle_admin_delete_card(callback: CallbackQuery):
    """Удаление карты"""
    admin_id = callback.from_user.id
    
    if admin_id not in authorized_admins:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    card_num = callback.data.split("admin_delete_card_")[1]
    cards = load_allowed_cards()
    
    if card_num in cards:
        del cards[card_num]
        save_allowed_cards(cards)
        
        logging.info(f"Admin {admin_id} deleted card {card_num}")
        
        await callback.answer("✅ Карта удалена", show_alert=True)
        
        # Возвращаемся к списку карт
        callback.data = "admin_cards"
        await handle_admin_cards(callback)
    else:
        await callback.answer("❌ Карта не найдена", show_alert=True)

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
        # Проверяем наличие файлов промокодов, карт и запросов на пополнение
        load_promocodes()
        load_allowed_cards()
        load_pending_deposits()
        load_asset_prices()
        logging.info("Данные успешно загружены (пользователи, конфиг, промокоды, карты, запросы на пополнение, цены активов)")
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