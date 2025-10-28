# ============================================
# ИСПРАВЛЕНИЯ ДЛЯ BOT.PY
# Этот файл содержит исправленные функции
# ============================================

import asyncio
import logging
import fcntl  # Для Linux/Mac (для Windows использовать msvcrt)
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from aiogram import Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError


# ============================================
# ИСПРАВЛЕНИЕ #5: Разделение состояний по типам
# ============================================

class UserStates:
    """Класс для управления состояниями пользователей с разделением по типам"""
    
    def __init__(self):
        self.deposit_states: Dict[int, Dict[str, Any]] = {}
        self.withdraw_states: Dict[int, Dict[str, Any]] = {}
        self.promo_states: Dict[int, Dict[str, Any]] = {}
        self.admin_states: Dict[int, Dict[str, Any]] = {}
        self.worker_auth_states: Dict[int, Dict[str, Any]] = {}
        self.card_states: Dict[int, Dict[str, Any]] = {}
        self.broadcast_states: Dict[int, Dict[str, Any]] = {}
    
    def set_deposit_state(self, user_id: int, data: Dict[str, Any]):
        """Устанавливает состояние пополнения"""
        self.deposit_states[user_id] = data
    
    def get_deposit_state(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получает состояние пополнения"""
        return self.deposit_states.get(user_id)
    
    def clear_deposit_state(self, user_id: int):
        """Очищает состояние пополнения"""
        self.deposit_states.pop(user_id, None)
    
    def set_withdraw_state(self, user_id: int, data: Dict[str, Any]):
        """Устанавливает состояние вывода"""
        self.withdraw_states[user_id] = data
    
    def get_withdraw_state(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получает состояние вывода"""
        return self.withdraw_states.get(user_id)
    
    def clear_withdraw_state(self, user_id: int):
        """Очищает состояние вывода"""
        self.withdraw_states.pop(user_id, None)
    
    def set_promo_state(self, user_id: int, data: Dict[str, Any]):
        """Устанавливает состояние промокода"""
        self.promo_states[user_id] = data
    
    def get_promo_state(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получает состояние промокода"""
        return self.promo_states.get(user_id)
    
    def clear_promo_state(self, user_id: int):
        """Очищает состояние промокода"""
        self.promo_states.pop(user_id, None)
    
    def set_admin_state(self, user_id: int, data: Dict[str, Any]):
        """Устанавливает состояние админа"""
        self.admin_states[user_id] = data
    
    def get_admin_state(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получает состояние админа"""
        return self.admin_states.get(user_id)
    
    def clear_admin_state(self, user_id: int):
        """Очищает состояние админа"""
        self.admin_states.pop(user_id, None)
    
    def clear_all_states(self, user_id: int):
        """Очищает все состояния пользователя"""
        self.clear_deposit_state(user_id)
        self.clear_withdraw_state(user_id)
        self.clear_promo_state(user_id)
        self.clear_admin_state(user_id)
        self.worker_auth_states.pop(user_id, None)
        self.card_states.pop(user_id, None)
        self.broadcast_states.pop(user_id, None)


# Глобальный экземпляр
user_states = UserStates()


# ============================================
# ИСПРАВЛЕНИЕ #6: Безопасная работа с файлами
# ============================================

class SafeFileStorage:
    """Класс для безопасной работы с JSON файлами с защитой от race conditions"""
    
    @staticmethod
    def save_json_safe(filepath: str, data: Dict[str, Any]):
        """Безопасное сохранение JSON с блокировкой файла"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # Блокируем файл для эксклюзивной записи
                fcntl.flock(f, fcntl.LOCK_EX)
                try:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
            logging.info(f"Successfully saved data to {filepath}")
        except Exception as e:
            logging.error(f"Error saving data to {filepath}: {e}")
            raise
    
    @staticmethod
    def load_json_safe(filepath: str) -> Dict[str, Any]:
        """Безопасная загрузка JSON с блокировкой файла"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                # Блокируем файл для чтения
                fcntl.flock(f, fcntl.LOCK_SH)
                try:
                    data = json.load(f)
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
            return data
        except FileNotFoundError:
            logging.warning(f"File {filepath} not found, returning empty dict")
            return {}
        except Exception as e:
            logging.error(f"Error loading data from {filepath}: {e}")
            return {}


# ============================================
# ИСПРАВЛЕНИЕ #8: Унифицированная отправка уведомлений
# ============================================

class NotificationService:
    """Сервис для отправки уведомлений"""
    
    TEMPLATES = {
        'deposit_request': (
            "💳 <b>Новый запрос на пополнение баланса</b>\n\n"
            "👤 <b>Пользователь:</b> @{username} (ID: {user_id})\n"
            "💰 <b>Сумма:</b> {amount:,.2f} ₽"
        ),
        'deposit_confirmed': (
            "✅ <b>Пополнение успешно выполнено!</b>\n\n"
            "💰 <b>Сумма:</b> {amount:,.2f} ₽\n"
            "💳 <b>Новый баланс:</b> {balance:,.2f} ₽"
        ),
        'deposit_rejected': (
            "❌ <b>Запрос на пополнение отклонен</b>\n\n"
            "💰 <b>Сумма:</b> {amount:,.2f} ₽\n\n"
            "📋 <b>Причина:</b> Ваш запрос на пополнение не был одобрен.\n\n"
            "💡 <b>Что делать:</b>\n"
            "• Проверьте правильность реквизитов\n"
            "• Обратитесь в поддержку для уточнения\n\n"
            "📱 <b>Поддержка:</b> @eToroSupport_Official"
        ),
        'trade_opened': (
            "📈 <b>Новая сделка</b>\n\n"
            "👤 <b>Пользователь:</b> @{username} (ID: {user_id})\n"
            "💱 <b>Актив:</b> {asset_name}\n"
            "{direction_emoji} <b>Направление:</b> {direction}\n"
            "⏱ <b>Время:</b> {time_sec}\n"
            "💰 <b>Сумма:</b> {amount:,.2f} ₽\n"
            "⚖️ <b>Плечо:</b> x{leverage:.1f}"
        ),
        'trade_result': (
            "{result_emoji} <b>Сделка завершена</b>\n\n"
            "👤 <b>Пользователь:</b> @{username} (ID: {user_id})\n"
            "💱 <b>Актив:</b> {asset_name}\n"
            "{direction_emoji} <b>Направление:</b> {direction}\n"
            "⏱ <b>Время:</b> {time_sec}\n"
            "💰 <b>Сумма:</b> {amount:,.2f} ₽\n"
            "⚖️ <b>Плечо:</b> x{leverage:.1f}\n\n"
            "🏆 <b>Результат:</b> {result}\n"
            "💵 <b>{profit_loss_label}:</b> {profit_loss_text} ₽"
        )
    }
    
    @staticmethod
    async def send_notification(
        bot: Bot,
        recipients: List[int],
        template_name: str,
        data: Dict[str, Any],
        buttons: Optional[InlineKeyboardMarkup] = None,
        info_only: bool = False
    ):
        """
        Универсальная функция отправки уведомлений
        
        Args:
            bot: Экземпляр бота
            recipients: Список ID получателей
            template_name: Название шаблона из TEMPLATES
            data: Данные для форматирования шаблона
            buttons: Клавиатура (опционально)
            info_only: Если True, добавляет пометку "только для информации"
        """
        if template_name not in NotificationService.TEMPLATES:
            logging.error(f"Unknown template: {template_name}")
            return
        
        text = NotificationService.TEMPLATES[template_name].format(**data)
        
        if info_only:
            text += "\n\n<i>ℹ️ Это уведомление только для информации</i>"
        
        success_count = 0
        fail_count = 0
        
        for recipient_id in recipients:
            try:
                await bot.send_message(
                    chat_id=recipient_id,
                    text=text,
                    reply_markup=buttons,
                    parse_mode=ParseMode.HTML
                )
                success_count += 1
                logging.info(f"Notification '{template_name}' sent to {recipient_id}")
            except (TelegramBadRequest, TelegramForbiddenError) as e:
                fail_count += 1
                logging.error(f"Failed to send notification to {recipient_id}: {e}")
            except Exception as e:
                fail_count += 1
                logging.error(f"Unexpected error sending to {recipient_id}: {e}")
        
        logging.info(f"Notification '{template_name}': {success_count} sent, {fail_count} failed")


# ============================================
# ИСПРАВЛЕНИЕ #13: Безопасное редактирование сообщений
# ============================================

async def safe_edit_message(
    callback: CallbackQuery,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    parse_mode: ParseMode = ParseMode.HTML,
    is_caption: bool = False
) -> bool:
    """
    Безопасное редактирование сообщения с fallback на отправку нового
    
    Args:
        callback: CallbackQuery объект
        text: Текст сообщения
        reply_markup: Клавиатура (опционально)
        parse_mode: Режим парсинга (по умолчанию HTML)
        is_caption: True если редактируем caption, False если text
    
    Returns:
        bool: True если успешно отредактировано, False если отправлено новое
    """
    try:
        if is_caption:
            await callback.message.edit_caption(
                caption=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
        else:
            await callback.message.edit_text(
                text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
        return True
    except TelegramBadRequest as e:
        logging.warning(f"Failed to edit message: {e}, sending new message")
        try:
            await callback.message.answer(
                text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
            return False
        except Exception as send_error:
            logging.error(f"Failed to send fallback message: {send_error}")
            return False
    except Exception as e:
        logging.error(f"Unexpected error in safe_edit_message: {e}")
        return False


# ============================================
# ИСПРАВЛЕНИЕ #10: Декоратор для обработки ошибок API
# ============================================

def handle_telegram_errors(func):
    """Декоратор для обработки ошибок Telegram API"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except TelegramBadRequest as e:
            logging.error(f"TelegramBadRequest in {func.__name__}: {e}")
            # Можно добавить уведомление пользователю
        except TelegramForbiddenError as e:
            logging.error(f"TelegramForbiddenError in {func.__name__}: {e}")
            # Пользователь заблокировал бота
        except Exception as e:
            logging.error(f"Unexpected error in {func.__name__}: {e}", exc_info=True)
    return wrapper


# ============================================
# ИСПРАВЛЕНИЕ #7: Унифицированная функция для админов/воркеров
# ============================================

class UserProfileManager:
    """Менеджер для работы с профилями пользователей (для админов и воркеров)"""
    
    @staticmethod
    def check_access(user_id: int, authorized_admins: set, authorized_workers: set) -> str:
        """
        Проверяет уровень доступа пользователя
        
        Returns:
            'admin' | 'worker' | 'none'
        """
        if user_id in authorized_admins:
            return 'admin'
        elif user_id in authorized_workers:
            return 'worker'
        return 'none'
    
    @staticmethod
    async def show_user_profile(
        callback: CallbackQuery,
        target_user_id: str,
        users_data: dict,
        worker_config: dict,
        trade_history: dict,
        caller_role: str  # 'admin' or 'worker'
    ):
        """
        Универсальная функция показа профиля пользователя
        
        Args:
            callback: CallbackQuery объект
            target_user_id: ID пользователя для просмотра
            users_data: Данные всех пользователей
            worker_config: Конфигурация воркеров
            trade_history: История сделок
            caller_role: Роль вызывающего ('admin' или 'worker')
        """
        if target_user_id not in users_data:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        user_data = users_data[target_user_id]
        user_config = worker_config.get(target_user_id, {
            'trade_mode': 'random',
            'growth_percentage': 1.0,
            'custom_balance': None
        })
        
        # Статистика торговли
        user_trades = trade_history.get(target_user_id, [])
        total_trades = len(user_trades)
        wins = len([t for t in user_trades if t['result'] == "Победа"])
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        
        # Информация о реферере
        referrer_info = "Нет"
        if user_data.get('referrer_id'):
            referrer_info = f"Воркер ID: {user_data['referrer_id']}"
        
        # Формируем текст
        text = (
            f"👤 <b>Профиль пользователя</b>\n\n"
            f"🆔 ID: {target_user_id}\n"
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
        
        # Формируем кнопки в зависимости от роли
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        from aiogram import types
        
        builder = InlineKeyboardBuilder()
        
        # Общие кнопки для админов и воркеров
        builder.add(types.InlineKeyboardButton(
            text="💰 Изменить баланс",
            callback_data=f"{caller_role}_balance_{target_user_id}"
        ))
        builder.add(types.InlineKeyboardButton(
            text="🎲 Режим торговли",
            callback_data=f"{caller_role}_trademode_{target_user_id}"
        ))
        builder.add(types.InlineKeyboardButton(
            text="📈 Процент роста",
            callback_data=f"{caller_role}_coef_{target_user_id}"
        ))
        builder.add(types.InlineKeyboardButton(
            text="💬 Отправить сообщение",
            callback_data=f"{caller_role}_message_{target_user_id}"
        ))
        
        # Кнопка "Назад" зависит от роли
        if caller_role == 'admin':
            builder.add(types.InlineKeyboardButton(
                text="⬅️ Назад к списку",
                callback_data="admin_all_users"
            ))
        else:
            builder.add(types.InlineKeyboardButton(
                text="⬅️ Назад к рефералам",
                callback_data="worker_referrals"
            ))
        
        builder.adjust(2, 2, 1, 1)
        
        await safe_edit_message(callback, text, builder.as_markup())


# ============================================
# ПРИМЕР ИСПОЛЬЗОВАНИЯ В КОДЕ
# ============================================

"""
# Вместо старого кода:
worker_states[user_id] = {'action': 'request_deposit', 'method': 'bank'}

# Используйте:
user_states.set_deposit_state(user_id, {'method': 'bank'})

# Вместо:
if user_id in worker_states and worker_states[user_id].get('action') == 'request_deposit':
    state = worker_states[user_id]

# Используйте:
state = user_states.get_deposit_state(user_id)
if state:
    # обработка

# Вместо:
del worker_states[user_id]

# Используйте:
user_states.clear_deposit_state(user_id)

# Для сохранения файлов:
SafeFileStorage.save_json_safe(USERS_DATA_FILE, users_data)

# Для загрузки файлов:
users_data = SafeFileStorage.load_json_safe(USERS_DATA_FILE)

# Для отправки уведомлений:
await NotificationService.send_notification(
    bot=bot,
    recipients=[admin_id, worker_id],
    template_name='deposit_request',
    data={
        'username': username,
        'user_id': user_id,
        'amount': amount
    },
    buttons=builder.as_markup()
)

# Для редактирования сообщений:
await safe_edit_message(
    callback=callback,
    text="Новый текст",
    reply_markup=builder.as_markup(),
    is_caption=False
)
"""
