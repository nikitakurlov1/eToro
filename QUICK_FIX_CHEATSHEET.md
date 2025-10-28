# ⚡ Шпаргалка: Быстрые исправления

## 🔄 Замены "Найти и заменить"

### 1. Состояния пополнения

```python
# НАЙТИ:
worker_states[user_id] = {'action': 'request_deposit', 'method': 'bank'}

# ЗАМЕНИТЬ НА:
user_states.set_deposit_state(user_id, {'method': 'bank'})
```

```python
# НАЙТИ:
if worker_id in worker_states and worker_states[worker_id].get('action') == 'request_deposit':
    state = worker_states[worker_id]

# ЗАМЕНИТЬ НА:
state = user_states.get_deposit_state(worker_id)
if state:
```

```python
# НАЙТИ (в контексте пополнения):
del worker_states[worker_id]

# ЗАМЕНИТЬ НА:
user_states.clear_deposit_state(worker_id)
```

---

### 2. Состояния вывода

```python
# НАЙТИ:
worker_states[user_id] = {
    'action': 'withdraw_enter_requisites',
    'method': method
}

# ЗАМЕНИТЬ НА:
user_states.set_withdraw_state(user_id, {'method': method})
```

```python
# НАЙТИ:
if worker_id in worker_states and worker_states[worker_id].get('action') == 'withdraw_enter_requisites':
    state = worker_states[worker_id]

# ЗАМЕНИТЬ НА:
state = user_states.get_withdraw_state(worker_id)
if state:
```

---

### 3. Сохранение файлов

```python
# НАЙТИ:
def save_users_data():
    """Сохраняет данные пользователей в файл"""
    try:
        with open(USERS_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Ошибка сохранения данных пользователей: {e}")

# ЗАМЕНИТЬ НА:
def save_users_data():
    """Сохраняет данные пользователей в файл с защитой от race conditions"""
    SafeFileStorage.save_json_safe(USERS_DATA_FILE, users_data)
```

---

### 4. Редактирование сообщений

```python
# НАЙТИ (все вхождения):
try:
    await callback.message.edit_text(
        text,
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )
except TelegramBadRequest:
    await callback.message.answer(
        text,
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )

# ЗАМЕНИТЬ НА:
await safe_edit_message(
    callback=callback,
    text=text,
    reply_markup=builder.as_markup()
)
```

```python
# НАЙТИ (для caption):
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

# ЗАМЕНИТЬ НА:
await safe_edit_message(
    callback=callback,
    text=text,
    reply_markup=builder.as_markup(),
    is_caption=True
)
```

---

## 📋 Список всех замен worker_states

### Поиск по регулярному выражению

Используйте regex для поиска всех использований:

```regex
worker_states\[(\w+)\]\s*=\s*\{[^}]*'action':\s*'([^']+)'
```

### Таблица замен по типу действия

| Старое действие | Новый метод |
|----------------|-------------|
| `'action': 'request_deposit'` | `user_states.set_deposit_state()` |
| `'action': 'withdraw_enter_requisites'` | `user_states.set_withdraw_state()` |
| `'action': 'enter_promo'` | `user_states.set_promo_state()` |
| `'action': 'create_promo_code'` | `user_states.set_admin_state()` |
| `'action': 'create_promo_amount'` | `user_states.set_admin_state()` |
| `'action': 'create_promo_uses'` | `user_states.set_admin_state()` |
| `'action': 'add_card'` | `user_states.set_admin_state()` |
| `'action': 'worker_auth'` | `user_states.worker_auth_states[user_id] = {}` |
| `'action': 'set_balance'` | `user_states.set_admin_state()` |
| `'action': 'send_message'` | `user_states.set_admin_state()` |
| `'action': 'edit_bank_requisites'` | `user_states.set_admin_state()` |
| `'action': 'edit_crypto_requisites'` | `user_states.set_admin_state()` |
| `'action': 'broadcast'` | `user_states.set_admin_state()` |
| `'action': 'update_asset_prices'` | `user_states.set_admin_state()` |

---

## 🎯 Приоритетные замены (делать в первую очередь)

### 1. Добавить импорты (в начало bot.py)

```python
from bot_fixes import (
    UserStates,
    SafeFileStorage,
    NotificationService,
    safe_edit_message,
    handle_telegram_errors,
    UserProfileManager
)

user_states = UserStates()
```

### 2. Заменить все save_* функции

```python
# Для каждой функции save_*():
def save_users_data():
    SafeFileStorage.save_json_safe(USERS_DATA_FILE, users_data)

def save_trade_history(trade_history):
    SafeFileStorage.save_json_safe(TRADE_HISTORY_FILE, trade_history)

def save_worker_config():
    data = {
        'workers': worker_config,
        'authorized_workers': list(authorized_workers),
        'authorized_admins': list(authorized_admins)
    }
    SafeFileStorage.save_json_safe(WORKER_CONFIG_FILE, data)

def save_requisites(requisites):
    SafeFileStorage.save_json_safe(REQUISITES_FILE, requisites)

def save_promocodes(promocodes):
    SafeFileStorage.save_json_safe(PROMOCODES_FILE, promocodes)

def save_allowed_cards(cards):
    SafeFileStorage.save_json_safe(ALLOWED_CARDS_FILE, cards)

def save_pending_deposits(deposits):
    SafeFileStorage.save_json_safe(PENDING_DEPOSITS_FILE, deposits)

def save_asset_prices(prices_data):
    SafeFileStorage.save_json_safe(ASSET_PRICES_FILE, prices_data)
```

### 3. Заменить все load_* функции

```python
def load_users_data():
    global users_data
    loaded_data = SafeFileStorage.load_json_safe(USERS_DATA_FILE)
    users_data = {str(k): v for k, v in loaded_data.items()}
    for user_id, user_data in users_data.items():
        user_data.setdefault('pending_withdrawal', 0.0)
        user_data.setdefault('verified', False)
        user_data.setdefault('username', "")
        user_data.setdefault('referrer_id', None)
    if users_data:
        save_users_data()

def load_trade_history():
    data = SafeFileStorage.load_json_safe(TRADE_HISTORY_FILE)
    return {str(k): v for k, v in data.items()}

def load_worker_config():
    global worker_config, authorized_workers, authorized_admins
    data = SafeFileStorage.load_json_safe(WORKER_CONFIG_FILE)
    worker_config = {str(k): v for k, v in data.get('workers', {}).items()}
    authorized_workers.update({int(wid) for wid in data.get('authorized_workers', [])})
    authorized_admins.update({int(aid) for aid in data.get('authorized_admins', [])})

def load_requisites():
    data = SafeFileStorage.load_json_safe(REQUISITES_FILE)
    if not data:
        return {
            "bank_card": "1234 5678 9012 3456",
            "bank_name": "Сбербанк",
            "cardholder_name": "Иван Иванов",
            "crypto_wallet": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
            "crypto_type": "Bitcoin (BTC)"
        }
    return data

def load_promocodes():
    return SafeFileStorage.load_json_safe(PROMOCODES_FILE)

def load_allowed_cards():
    return SafeFileStorage.load_json_safe(ALLOWED_CARDS_FILE)

def load_pending_deposits():
    return SafeFileStorage.load_json_safe(PENDING_DEPOSITS_FILE)

def load_asset_prices():
    global ASSET_PRICES
    loaded_prices = SafeFileStorage.load_json_safe(ASSET_PRICES_FILE)
    new_prices = {}
    for category in loaded_prices.values():
        if isinstance(category, dict):
            new_prices.update(category)
    if new_prices:
        ASSET_PRICES.update(new_prices)
```

---

## 🔍 Поиск и замена в VS Code / PyCharm

### VS Code

1. Нажмите `Ctrl+H` (Windows/Linux) или `Cmd+H` (Mac)
2. Включите regex: нажмите `.*` кнопку
3. Используйте паттерны из таблицы выше

### PyCharm

1. Нажмите `Ctrl+R` (Windows/Linux) или `Cmd+R` (Mac)
2. Включите regex: поставьте галочку "Regex"
3. Используйте паттерны из таблицы выше

---

## ✅ Чеклист применения

- [ ] 1. Создан файл `bot_fixes.py` в той же папке что и `bot.py`
- [ ] 2. Добавлены импорты в начало `bot.py`
- [ ] 3. Создан экземпляр `user_states = UserStates()`
- [ ] 4. Заменены все функции `save_*()` (8 функций)
- [ ] 5. Заменены все функции `load_*()` (8 функций)
- [ ] 6. Заменены состояния пополнения (3 места)
- [ ] 7. Заменены состояния вывода (3 места)
- [ ] 8. Заменены состояния промокодов (6 мест)
- [ ] 9. Заменены состояния админа (10+ мест)
- [ ] 10. Заменены все блоки `try-except` для `edit_text/edit_caption` (30+ мест)
- [ ] 11. Заменены функции отправки уведомлений (3 функции)
- [ ] 12. Объединены функции админов и воркеров (2 функции → 1)
- [ ] 13. Протестированы все основные функции

---

## 🧪 Быстрый тест

После применения исправлений запустите эти тесты:

```python
# Тест 1: Проверка состояний
user_states.set_deposit_state(123, {'method': 'bank'})
assert user_states.get_deposit_state(123) == {'method': 'bank'}
user_states.clear_deposit_state(123)
assert user_states.get_deposit_state(123) is None
print("✅ Тест состояний пройден")

# Тест 2: Проверка файлов
test_data = {'test': 'data'}
SafeFileStorage.save_json_safe('test.json', test_data)
loaded = SafeFileStorage.load_json_safe('test.json')
assert loaded == test_data
print("✅ Тест файлов пройден")

# Тест 3: Проверка уведомлений
# (требует запущенного бота)
await NotificationService.send_notification(
    bot=bot,
    recipients=[YOUR_TELEGRAM_ID],
    template_name='deposit_request',
    data={'username': 'test', 'user_id': 123, 'amount': 1000}
)
print("✅ Тест уведомлений пройден")
```

---

## 📞 Поддержка

Если возникли проблемы:
1. Проверьте логи: `logging.error` покажет ошибки
2. Убедитесь, что все импорты на месте
3. Проверьте, что `bot_fixes.py` в той же папке что и `bot.py`
4. Для Windows: замените `fcntl` на `msvcrt` (см. APPLY_FIXES_GUIDE.md)

---

**Время применения**: ~30-60 минут  
**Сложность**: Средняя  
**Результат**: -650 строк кода, +100% надёжность
