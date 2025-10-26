# 🚀 Инструкция по деплою бота на хостинг

## 📋 Необходимые файлы для загрузки на хостинг:

### 1. **Основные файлы:**
- `bot.py` - главный файл бота
- `etoro.png` - изображение для приветствия
- `image copy.png` - изображение для профиля и торговли
- `requirements.txt` - зависимости Python

### 2. **JSON файлы (создадутся автоматически, но можно загрузить пустые):**
- `users_data.json`
- `trade_history.json`
- `worker_config.json`
- `requisites.json`

## 📦 Структура папки на хостинге:

```
/home/your_username/bot/
├── bot.py
├── etoro.png
├── image copy.png
├── requirements.txt
├── users_data.json (опционально)
├── trade_history.json (опционально)
├── worker_config.json (опционально)
└── requisites.json (опционально)
```

## ⚙️ Настройка на хостинге:

### 1. Установка зависимостей:
```bash
pip install -r requirements.txt
```

или вручную:
```bash
pip install aiogram
```

### 2. Проверка файлов изображений:
Убедитесь, что файлы изображений находятся в той же папке, что и `bot.py`:
```bash
ls -la
# Должны быть видны: etoro.png и image copy.png
```

### 3. Права доступа:
```bash
chmod 644 *.png
chmod 644 *.json
chmod 755 bot.py
```

### 4. Запуск бота:
```bash
python3 bot.py
```

или с nohup (для работы в фоне):
```bash
nohup python3 bot.py > bot.log 2>&1 &
```

## 🔧 Решение проблем:

### Проблема: "Не могу найти файл изображения"
**Решение:**
1. Проверьте, что файлы `etoro.png` и `image copy.png` находятся в той же папке, что и `bot.py`
2. Проверьте права доступа к файлам: `ls -la *.png`
3. Убедитесь, что имена файлов точно совпадают (включая пробелы и регистр)

### Проблема: "Ошибка при открытии графика"
**Решение:**
1. Убедитесь, что файл `image copy.png` существует
2. Проверьте, что бот имеет права на чтение файла
3. Попробуйте переименовать файл без пробелов: `mv "image copy.png" image_copy.png`
   И обновите в `bot.py`:
   ```python
   PROFILE_PHOTO_PATH = os.path.join(BASE_DIR, "image_copy.png")
   TRADING_PHOTO_PATH = os.path.join(BASE_DIR, "image_copy.png")
   ```

### Проблема: Бот не запускается
**Решение:**
1. Проверьте логи: `tail -f bot.log`
2. Убедитесь, что установлены все зависимости: `pip list | grep aiogram`
3. Проверьте версию Python: `python3 --version` (должна быть 3.8+)

## 📝 Рекомендации:

1. **Используйте systemd для автозапуска** (на Linux):
   Создайте файл `/etc/systemd/system/etoro-bot.service`:
   ```ini
   [Unit]
   Description=eToro Telegram Bot
   After=network.target

   [Service]
   Type=simple
   User=your_username
   WorkingDirectory=/home/your_username/bot
   ExecStart=/usr/bin/python3 /home/your_username/bot/bot.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   Затем:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable etoro-bot
   sudo systemctl start etoro-bot
   sudo systemctl status etoro-bot
   ```

2. **Мониторинг логов:**
   ```bash
   journalctl -u etoro-bot -f
   ```

3. **Резервное копирование данных:**
   Регулярно делайте бэкап JSON файлов:
   ```bash
   tar -czf backup_$(date +%Y%m%d).tar.gz *.json
   ```

## ✅ Проверка работы:

1. Отправьте `/start` боту
2. Проверьте, что отображается изображение приветствия
3. Примите условия и проверьте профиль
4. Попробуйте открыть раздел торговли
5. Проверьте, что графики отображаются

## 🆘 Поддержка:

Если проблемы остаются:
1. Проверьте логи бота
2. Убедитесь, что все файлы на месте
3. Проверьте права доступа
4. Убедитесь, что токен бота правильный
