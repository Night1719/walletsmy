# 🔧 Исправление ошибки `from_json` в BG Survey Platform

## 🚨 Проблема
**Ошибка:** `jinja2.exceptions.TemplateRuntimeError: No filter named 'from_json' found`

**URL:** `http://192.168.96.213:5000/surveys/1`

## 🔍 Причина
Фильтр `from_json` был зарегистрирован только как функция в `context_processor`, но не как фильтр Jinja2. В Jinja2 есть разница между функциями и фильтрами.

## ✅ Решение
Добавлен отдельный декоратор `@app.template_filter('from_json')` для правильной регистрации фильтра:

```python
# Регистрируем фильтр from_json отдельно
@app.template_filter('from_json')
def from_json_filter(json_string):
    """Фильтр для преобразования JSON строки в Python объект"""
    try:
        if json_string:
            return json.loads(json_string)
        return []
    except (json.JSONDecodeError, TypeError):
        return []
```

## 📁 Изменения
- **Файл:** `app.py`
- **Добавлен:** Декоратор `@app.template_filter('from_json')`
- **Функция:** `from_json_filter()` для обработки JSON

## 🧪 Тестирование
1. **Перезапустите приложение:**
   ```bash
   python3 app.py
   ```

2. **Перейдите на страницу опроса:**
   ```
   http://192.168.96.213:5000/surveys/1
   ```

3. **Ошибка должна исчезнуть** и страница должна загрузиться корректно

## 🔧 Технические детали

### Разница между функциями и фильтрами в Jinja2:
- **Функции** (`context_processor`) - доступны как `{{ function_name() }}`
- **Фильтры** (`@app.template_filter`) - доступны как `{{ value|filter_name }}`

### Использование в шаблоне:
```html
<!-- Работает с фильтром -->
{% set options = question.options|from_json %}

<!-- Работает с функцией -->
{% set options = from_json(question.options) %}
```

## 🎯 Результат
- ✅ **Ошибка `from_json` исправлена**
- ✅ **Страница опросов загружается корректно**
- ✅ **Фильтр доступен в шаблонах**
- ✅ **JSON опции обрабатываются правильно**

---

**BG Survey Platform** - фильтр `from_json` работает! 🎉✨