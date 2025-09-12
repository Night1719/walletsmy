# Настройка SSL сертификата

## Шаг 1: Получите файлы сертификата

У вас есть wildcard сертификат для `*.bunter.ru`. Нужно извлечь файлы для `bot.bunter.ru`:

### Если у вас PKCS#12 файл (.p12 или .pfx):
```bash
# Извлечь сертификат
openssl pkcs12 -in your_certificate.p12 -clcerts -nokeys -out certificates/bot.bunter.ru.crt

# Извлечь приватный ключ
openssl pkcs12 -in your_certificate.p12 -nocerts -nodes -out certificates/bot.bunter.ru.key
```

### Если у вас отдельные файлы:
Скопируйте их в папку `certificates/`:
- `bot.bunter.ru.crt` - сертификат
- `bot.bunter.ru.key` - приватный ключ

## Шаг 2: Проверьте файлы

Убедитесь, что файлы существуют:
```cmd
dir certificates\
```

Должны быть:
- `bot.bunter.ru.crt`
- `bot.bunter.ru.key`

## Шаг 3: Запустите Mini App

```cmd
python run.py
```

Если сертификат найден, увидите:
```
🔒 Используется сертификат: certificates/bot.bunter.ru.crt
```

Если нет, увидите:
```
⚠️  Используется самоподписной сертификат
```

## Шаг 4: Проверьте в браузере

Откройте: `https://bot.bunter.ru:4477`

- ✅ **С wildcard сертификатом** - зеленый замок, без предупреждений
- ❌ **С самоподписным** - предупреждение о безопасности

## Устранение неполадок

### "Certificate not found"
- Проверьте пути в .env файле
- Убедитесь, что файлы существуют

### "Invalid certificate"
- Проверьте формат файлов (должны быть PEM)
- Убедитесь, что сертификат действителен для bot.bunter.ru

### "Permission denied"
- Проверьте права доступа к файлам
- Убедитесь, что приложение может читать файлы