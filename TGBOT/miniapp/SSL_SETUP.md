# Настройка SSL сертификата для bot.bunter.ru

## Шаг 1: Подготовка сертификата

У вас есть wildcard сертификат для `*.bunter.ru`. Нужно:

1. **Извлечь сертификат и ключ** из вашего wildcard сертификата
2. **Сохранить в формате PEM**

### Формат файлов:
- **Сертификат:** `bot.bunter.ru.crt` (или `.pem`)
- **Приватный ключ:** `bot.bunter.ru.key` (или `.pem`)

## Шаг 2: Размещение файлов

Создайте папку `certificates` в `miniapp/` и поместите туда:

```
miniapp/
├── certificates/
│   ├── bot.bunter.ru.crt    # Сертификат
│   └── bot.bunter.ru.key    # Приватный ключ
└── ...
```

## Шаг 3: Настройка .env

В файле `miniapp/.env` добавьте:

```env
SSL_CERT_PATH=certificates/bot.bunter.ru.crt
SSL_KEY_PATH=certificates/bot.bunter.ru.key
```

## Шаг 4: Запуск

```cmd
cd miniapp
python run.py
```

## Проверка

Mini App должен быть доступен по:
- **URL:** `https://bot.bunter.ru:4477`
- **Web App:** `https://bot.bunter.ru:4477/miniapp`

## Устранение неполадок

### Ошибка "Certificate not found"
- Проверьте пути к файлам в .env
- Убедитесь, что файлы существуют

### Ошибка "Invalid certificate"
- Проверьте формат файлов (должны быть PEM)
- Убедитесь, что сертификат действителен для bot.bunter.ru

### Ошибка "Permission denied"
- Проверьте права доступа к файлам сертификата
- Убедитесь, что приложение может читать файлы