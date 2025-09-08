# Ограничения файлов в разделе "Инструкции"

## Обзор

Система валидации файлов предотвращает загрузку скриншотов и других нежелательных файлов в разделе инструкций.

## Типы ограничений

### 1. Ограничения по расширениям файлов

#### Разрешенные расширения (по умолчанию):
- `pdf` - PDF документы
- `docx` - Word документы (новый формат)
- `doc` - Word документы (старый формат)
- `txt` - Текстовые файлы

#### Запрещенные расширения (по умолчанию):
- `png`, `jpg`, `jpeg` - Изображения
- `gif`, `bmp`, `tiff`, `webp` - Другие форматы изображений
- `ico`, `svg` - Иконки и векторная графика
- `psd`, `ai`, `sketch` - Файлы дизайна

### 2. Ограничения по размеру

- **Максимальный размер**: 50 MB (настраивается)
- Файлы больше указанного размера отклоняются

### 3. Обнаружение скриншотов

#### Проверка имени файла:
- Ключевые слова: `screenshot`, `скриншот`, `screen`, `экран`, `capture`, `захват`
- Паттерны: `screenshot_2024-01-01`, `screen_20240101`, `img_20240101`
- Русские паттерны: `скриншот_2024-01-01`, `фото_20240101`

#### Проверка содержимого:
- **MIME-типы**: Обнаружение изображений по магическим числам
- **Метаданные**: Поиск упоминаний инструментов скриншотов
- **Размеры**: Обнаружение стандартных разрешений экранов
- **Заголовки файлов**: Проверка сигнатур изображений

#### Обнаруживаемые инструменты:
- Snipping Tool (Ножницы)
- Snagit, Greenshot, Lightshot
- PicPick, FastStone Capture
- ShareX, Bandicam, OBS Studio
- И другие инструменты захвата экрана

## Конфигурация

### Переменные окружения

```env
# Разрешенные расширения (через запятую)
ALLOWED_FILE_EXTENSIONS=pdf,docx,doc,txt

# Запрещенные расширения (через запятую)
FORBIDDEN_FILE_EXTENSIONS=png,jpg,jpeg,gif,bmp,tiff,webp,ico,svg,psd,ai,sketch

# Максимальный размер файла в MB
MAX_FILE_SIZE_MB=50

# Включить проверку содержимого
ENABLE_CONTENT_VALIDATION=true
```

### Настройка для продакшена

```env
# Строгие ограничения
ALLOWED_FILE_EXTENSIONS=pdf,docx
FORBIDDEN_FILE_EXTENSIONS=png,jpg,jpeg,gif,bmp,tiff,webp,ico,svg,psd,ai,sketch,exe,zip,rar,7z
MAX_FILE_SIZE_MB=25
ENABLE_CONTENT_VALIDATION=true
```

## Логирование

### Уровни логирования

- **INFO**: Успешная валидация файлов
- **WARNING**: Отклонение файлов с указанием причины
- **ERROR**: Ошибки в процессе валидации

### Примеры логов

```
INFO: File validation passed for instructions/1c/ar2.pdf: File validation passed
WARNING: File validation failed for instructions/1c/screenshot.png: File appears to be an image (screenshot)
WARNING: File safety validation failed for instructions/email/screen_capture.pdf: File appears to be a screenshot or image. Details: Filename pattern: screen_capture, Metadata pattern: created by screenshot tool
```

## Обработка ошибок

### Сообщения пользователю

При отклонении файлов пользователь получает информативные сообщения:

```
❌ Не удалось загрузить файлы инструкций.

Причины:
• PDF: файл недоступен или не прошел проверку
• DOCX: File appears to be a screenshot or image. Details: Filename pattern: screenshot_2024
```

### Fallback механизм

Если продвинутая валидация не работает:
1. Система переключается на базовую проверку
2. Файл может быть разрешен с предупреждением
3. Ошибка логируется для анализа

## Тестирование

### Проверка валидации

```python
# Тест разрешенного файла
from file_server import validate_instruction_file
is_valid, reason = validate_instruction_file("instruction.pdf", pdf_content)
assert is_valid == True

# Тест запрещенного файла
is_valid, reason = validate_instruction_file("screenshot.png", image_content)
assert is_valid == False
assert "screenshot" in reason.lower()
```

### Тестовые файлы

Создайте тестовые файлы для проверки:

1. **Разрешенные**:
   - `instruction.pdf` - обычный PDF
   - `manual.docx` - Word документ
   - `guide.txt` - текстовый файл

2. **Запрещенные**:
   - `screenshot.png` - изображение
   - `screen_capture.pdf` - PDF со скриншотом
   - `photo_20240101.jpg` - фото с датой

## Мониторинг

### Метрики

- Количество отклоненных файлов
- Причины отклонения
- Время валидации
- Ошибки валидации

### Алерты

Настройте алерты на:
- Высокий процент отклоненных файлов
- Ошибки в процессе валидации
- Попытки загрузки подозрительных файлов

## Устранение неполадок

### Частые проблемы

1. **"File validation failed"**
   - Проверьте логи для детальной информации
   - Убедитесь, что файл не является скриншотом
   - Проверьте имя файла на наличие ключевых слов

2. **"File too large"**
   - Увеличьте `MAX_FILE_SIZE_MB` или уменьшите размер файла
   - Проверьте, что файл действительно нужен

3. **"Content validation failed"**
   - Проверьте зависимости (python-magic)
   - Временно отключите `ENABLE_CONTENT_VALIDATION`

### Отладка

```bash
# Включить подробное логирование
export LOG_LEVEL=DEBUG

# Проверить конкретный файл
python3 -c "
from file_server import validate_instruction_file
with open('test_file.pdf', 'rb') as f:
    content = f.read()
is_valid, reason = validate_instruction_file('test_file.pdf', content)
print(f'Valid: {is_valid}, Reason: {reason}')
"
```

## Безопасность

### Рекомендации

1. **Регулярно обновляйте** списки ключевых слов и паттернов
2. **Мониторьте логи** на предмет новых типов атак
3. **Тестируйте** новые файлы перед добавлением в продакшен
4. **Обучайте пользователей** правильному именованию файлов

### Дополнительные меры

- Сканирование на вирусы
- Проверка цифровых подписей
- Анализ содержимого на предмет вредоносного кода
- Ограничение доступа к файловому серверу